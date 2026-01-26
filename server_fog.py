"""
Fog Server for Three-Tier Smart Routing
Dual-role: FastAPI server (receives from Edge) AND HTTP client (forwards to Cloud)
Makes routing decisions based on image complexity
Runs on port 8000 (Laptop 2 - Medium Capabilities)
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import time
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
from router_utils import ImageComplexityRouter
from config_routing import (
    FOG_COMPLEXITY_THRESHOLD,
    CLOUD_SERVER_URL,
    REQUEST_TIMEOUT,
    FOG_SERVER_PORT
)

# Global model variable
model = None

# Initialize router
fog_router = ImageComplexityRouter(FOG_COMPLEXITY_THRESHOLD)

# Pydantic Models
class PredictionRequest(BaseModel):
    image: List  # 1x224x224x3 nested list
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    complexity: Optional[float] = None  # May be provided by edge client

class PredictionResponse(BaseModel):
    prediction: List[List[float]]  # 1x1000 predictions
    confidence: float  # Top-1 confidence score
    top_class: int  # Index of highest probability class
    inference_time_ms: float  # Inference time
    inference_source: str  # "fog" or "cloud"
    complexity: float  # Image complexity metric
    request_id: Optional[str] = None
    server_timestamp: str

# FastAPI app
app = FastAPI(
    title="Fog MobileNetV2 Inference Server",
    description="Fog server with smart routing to Cloud (Three-Tier Architecture)",
    version="1.0.0"
)

def initialize_model():
    """Initialize MobileNetV2 model"""
    global model
    print("Initializing MobileNetV2 model on Fog Server...")
    start_time = time.time()

    model = MobileNetV2(
        weights='imagenet',
        include_top=True,
        input_shape=(224, 224, 3)
    )

    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds")

    # Warm-up prediction
    print("Performing warm-up inference...")
    dummy = np.random.rand(1, 224, 224, 3).astype(np.float32)
    dummy = preprocess_input(dummy)
    _ = model.predict(dummy, verbose=0)
    print("Warm-up complete\n")

    return load_time

@app.on_event("startup")
async def startup_event():
    """Initialize model on server startup"""
    initialize_model()
    print(f"Fog Server ready and waiting for requests...")
    print(f"Complexity Threshold: {FOG_COMPLEXITY_THRESHOLD}")
    print(f"Cloud Server URL: {CLOUD_SERVER_URL}\n")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fog MobileNetV2 Inference Server",
        "tier": "fog",
        "status": "running",
        "complexity_threshold": FOG_COMPLEXITY_THRESHOLD,
        "cloud_server": CLOUD_SERVER_URL,
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tier": "fog",
        "model_loaded": model is not None,
        "cloud_server": CLOUD_SERVER_URL,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Perform image classification with smart routing

    Decision logic:
    - If complexity < threshold: Process locally on fog
    - If complexity >= threshold: Forward to cloud

    Args:
        request: PredictionRequest containing image data

    Returns:
        PredictionResponse with predictions and routing information
    """
    try:
        # Extract image data and convert to NumPy array
        image_array = np.array(request.image, dtype=np.float32)

        # Validate shape
        if image_array.shape != (1, 224, 224, 3):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image shape. Expected (1, 224, 224, 3), got {image_array.shape}"
            )

        # Calculate complexity and make routing decision
        routing_decision = fog_router.get_routing_decision(image_array)
        complexity = routing_decision['complexity']
        process_locally = routing_decision['process_locally']

        if process_locally:
            # Process on fog server
            print(f"[FOG] Processing locally (complexity: {complexity:.2f})")

            # Preprocess image for MobileNetV2
            preprocessed_image = preprocess_input(image_array.copy())

            start_time = time.time()
            prediction = model.predict(preprocessed_image, verbose=0)
            end_time = time.time()
            inference_time_ms = (end_time - start_time) * 1000

            # Extract top prediction
            top_class = int(np.argmax(prediction[0]))
            confidence = float(prediction[0][top_class])
            prediction_list = prediction.tolist()
            inference_source = "fog"

        else:
            # Forward to cloud server
            print(f"[FOG] Forwarding to cloud (complexity: {complexity:.2f})")

            try:
                # Prepare payload for cloud
                cloud_payload = {
                    'image': image_array.tolist(),
                    'request_id': request.request_id,
                    'timestamp': datetime.now().isoformat()
                }

                # Forward to cloud
                cloud_response = requests.post(
                    CLOUD_SERVER_URL,
                    json=cloud_payload,
                    timeout=REQUEST_TIMEOUT
                )

                if cloud_response.status_code == 200:
                    cloud_data = cloud_response.json()

                    # Extract cloud response data
                    prediction_list = cloud_data['prediction']
                    confidence = cloud_data['confidence']
                    top_class = cloud_data['top_class']
                    inference_time_ms = cloud_data['inference_time_ms']
                    inference_source = "cloud"

                    print(f"[FOG] Cloud processing successful")

                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Cloud server error: HTTP {cloud_response.status_code}"
                    )

            except requests.exceptions.Timeout:
                # Fallback: Process locally if cloud times out
                print(f"[FOG] Cloud timeout - processing locally as fallback")

                # Preprocess image for MobileNetV2
                preprocessed_image = preprocess_input(image_array.copy())

                start_time = time.time()
                prediction = model.predict(preprocessed_image, verbose=0)
                end_time = time.time()
                inference_time_ms = (end_time - start_time) * 1000

                top_class = int(np.argmax(prediction[0]))
                confidence = float(prediction[0][top_class])
                prediction_list = prediction.tolist()
                inference_source = "fog"  # Fallback to fog

            except requests.exceptions.RequestException as e:
                # Fallback: Process locally if cloud is unreachable
                print(f"[FOG] Cloud unreachable - processing locally as fallback: {str(e)}")

                # Preprocess image for MobileNetV2
                preprocessed_image = preprocess_input(image_array.copy())

                start_time = time.time()
                prediction = model.predict(preprocessed_image, verbose=0)
                end_time = time.time()
                inference_time_ms = (end_time - start_time) * 1000

                top_class = int(np.argmax(prediction[0]))
                confidence = float(prediction[0][top_class])
                prediction_list = prediction.tolist()
                inference_source = "fog"  # Fallback to fog

        # Create response with inference_source
        response = PredictionResponse(
            prediction=prediction_list,
            confidence=confidence,
            top_class=top_class,
            inference_time_ms=inference_time_ms,
            inference_source=inference_source,  # CRITICAL: fog or cloud
            complexity=complexity,
            request_id=request.request_id,
            server_timestamp=datetime.now().isoformat()
        )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    print("="*60)
    print("Fog MobileNetV2 Inference Server")
    print("Three-Tier Smart Routing - Fog Tier")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=FOG_SERVER_PORT)
