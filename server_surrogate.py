"""
Server Surrogate for Code Offloading
FastAPI server that performs MobileNetV2 inference on received images
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

# Global model variable
model = None

# Pydantic Models
class PredictionRequest(BaseModel):
    image: List  # 1x224x224x3 nested list
    request_id: Optional[str] = None
    timestamp: Optional[str] = None

class PredictionResponse(BaseModel):
    prediction: List[List[float]]  # 1x1000 predictions
    confidence: float  # Top-1 confidence score
    top_class: int  # Index of highest probability class
    inference_time_ms: float  # Server-side inference time only
    request_id: Optional[str] = None
    server_timestamp: str

# FastAPI app
app = FastAPI(
    title="MobileNetV2 Inference Server",
    description="Server for offloading MobileNetV2 image classification",
    version="1.0.0"
)

def initialize_model():
    """Initialize MobileNetV2 model"""
    global model
    print("Initializing MobileNetV2 model...")
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
    print("Server ready and waiting for requests...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MobileNetV2 Inference Server",
        "status": "running",
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
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Perform image classification using MobileNetV2

    Args:
        request: PredictionRequest containing image data

    Returns:
        PredictionResponse with predictions and timing information
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

        # Record start time
        start_time = time.time()

        # Perform inference
        prediction = model.predict(image_array, verbose=0)

        # Record end time
        end_time = time.time()
        inference_time_ms = (end_time - start_time) * 1000

        # Extract top prediction
        top_class = int(np.argmax(prediction[0]))
        confidence = float(prediction[0][top_class])

        # Convert prediction to list for JSON serialization
        prediction_list = prediction.tolist()

        # Create response
        response = PredictionResponse(
            prediction=prediction_list,
            confidence=confidence,
            top_class=top_class,
            inference_time_ms=inference_time_ms,
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
    print("MobileNetV2 Inference Server")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
