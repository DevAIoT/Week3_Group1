"""
Smart Edge Client for Three-Tier Routing
Performs local inference for simple images, forwards complex images to Fog
Laptop 1 - Standard Capabilities
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import time
import psutil
import json
import platform
from datetime import datetime
import os
import requests
from router_utils import ImageComplexityRouter
from config_routing import (
    EDGE_COMPLEXITY_THRESHOLD,
    FOG_SERVER_URL,
    REQUEST_TIMEOUT,
    NUM_TEST_IMAGES
)


class SmartEdgeClient:
    """
    Smart Edge Client with local inference and fog offloading
    Routes images based on complexity threshold
    """

    def __init__(self, fog_server_url=FOG_SERVER_URL, edge_threshold=EDGE_COMPLEXITY_THRESHOLD):
        self.fog_server_url = fog_server_url
        self.edge_threshold = edge_threshold
        self.router = ImageComplexityRouter(edge_threshold)
        self.model = None
        self.results = {
            'system_info': self.get_system_info(),
            'routing_config': {
                'edge_threshold': edge_threshold,
                'fog_server_url': fog_server_url
            },
            'smart_routing_test': {}
        }

    def get_system_info(self):
        """Collect system information"""
        info = {
            'device_type': 'edge',
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'ram_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat()
        }
        return info

    def initialize_model(self):
        """Initialize MobileNetV2 model for local inference"""
        print("\nInitializing local model for edge processing...")
        start_time = time.time()

        self.model = MobileNetV2(
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
        _ = self.model.predict(dummy, verbose=0)
        print("Warm-up complete\n")

        return load_time

    def generate_dummy_image(self, seed=None):
        """Generate a dummy image of shape 224x224x3"""
        if seed is not None:
            np.random.seed(seed)

        # Generate random image with values in [0, 255]
        image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)

        # Expand dimensions for batch processing
        image = np.expand_dims(image, axis=0)

        # Preprocess for MobileNetV2
        image = preprocess_input(image.astype(np.float32))

        return image

    def monitor_resources(self):
        """Monitor current resource usage"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2)
        }

    def process_locally(self, image, request_id):
        """
        Process image locally on edge device

        Args:
            image: Preprocessed image array
            request_id: Request identifier

        Returns:
            dict: Processing result with inference_source="local"
        """
        start_time = time.time()
        prediction = self.model.predict(image, verbose=0)
        end_time = time.time()

        inference_time_ms = (end_time - start_time) * 1000

        # Extract top prediction
        top_class = int(np.argmax(prediction[0]))
        confidence = float(prediction[0][top_class])

        return {
            'prediction': prediction.tolist(),
            'confidence': confidence,
            'top_class': top_class,
            'inference_time_ms': inference_time_ms,
            'inference_source': 'local',
            'request_id': request_id
        }

    def forward_to_fog(self, image, request_id):
        """
        Forward image to fog server for processing

        Args:
            image: Preprocessed image array
            request_id: Request identifier

        Returns:
            dict: Processing result from fog (may be "fog" or "cloud" source)
        """
        # Convert image to Python list for JSON serialization
        image_list = image.tolist()

        # Create request payload
        payload = {
            "image": image_list,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }

        # Send POST request to fog server
        response = requests.post(
            self.fog_server_url,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Fog server error: HTTP {response.status_code}")

    def run_smart_routing_test(self, num_images=NUM_TEST_IMAGES):
        """
        Run smart routing test with performance monitoring

        Args:
            num_images: Number of test images to process
        """
        print(f"\n{'='*60}")
        print(f"Smart Edge Client - Task 4 Three-Tier Routing Test")
        print(f"{'='*60}")
        print(f"Edge Threshold: {self.edge_threshold}")
        print(f"Fog Server: {self.fog_server_url}")

        # Initialize local model
        model_load_time = self.initialize_model()

        # Check fog server health
        try:
            health_url = self.fog_server_url.replace('/predict', '/health')
            health_response = requests.get(health_url, timeout=5)
            if health_response.status_code == 200:
                print("[OK] Fog server is healthy and ready")
            else:
                print(f"[WARNING] Fog server health check returned: {health_response.status_code}")
        except Exception as e:
            print(f"[WARNING] Cannot connect to fog server: {str(e)}")
            print("Continuing with local-only processing...")

        # Record initial resources
        initial_resources = self.monitor_resources()
        print(f"\nInitial Resources:")
        print(f"  CPU: {initial_resources['cpu_percent']:.1f}%")
        print(f"  Memory: {initial_resources['memory_used_gb']} GB ({initial_resources['memory_percent']:.1f}%)\n")

        # Generate all images upfront
        print(f"Generating {num_images} test images...")
        images = [self.generate_dummy_image(seed=i) for i in range(num_images)]
        print(f"Generated {num_images} images\n")

        # Start smart routing test
        print("Running smart routing test...")
        start_time = time.time()

        request_results = []
        resource_samples = []
        num_local = 0
        num_fog = 0
        num_cloud = 0

        for i in range(num_images):
            image = images[i]

            # Calculate complexity and make routing decision
            routing_decision = self.router.get_routing_decision(image)
            complexity = routing_decision['complexity']
            process_locally = routing_decision['process_locally']

            # Record request start time
            request_start = time.time()

            try:
                if process_locally:
                    # Process locally on edge
                    result = self.process_locally(image, f"request_{i}")
                    inference_source = 'local'
                    num_local += 1
                else:
                    # Forward to fog server
                    result = self.forward_to_fog(image, f"request_{i}")
                    inference_source = result.get('inference_source', 'fog')
                    if inference_source == 'fog':
                        num_fog += 1
                    elif inference_source == 'cloud':
                        num_cloud += 1

                # Record request end time
                request_end = time.time()
                latency_ms = (request_end - request_start) * 1000

                # Store result
                request_results.append({
                    'request_id': i,
                    'complexity': complexity,
                    'routing_decision': 'local' if process_locally else 'forward',
                    'inference_source': inference_source,
                    'latency_ms': round(latency_ms, 2),
                    'inference_time_ms': round(result.get('inference_time_ms', 0), 2),
                    'confidence': result.get('confidence', 0),
                    'top_class': result.get('top_class', -1)
                })

                # Print progress
                if inference_source == 'local':
                    print(f"[Request {i}] Complexity: {complexity:.2f} → LOCAL ({latency_ms:.1f}ms)")
                elif inference_source == 'fog':
                    print(f"[Request {i}] Complexity: {complexity:.2f} → FOG ({latency_ms:.1f}ms)")
                elif inference_source == 'cloud':
                    print(f"[Request {i}] Complexity: {complexity:.2f} → CLOUD ({latency_ms:.1f}ms)")

            except Exception as e:
                print(f"[ERROR] Request {i} failed: {str(e)}")
                request_results.append({
                    'request_id': i,
                    'complexity': complexity,
                    'error': str(e)
                })

            # Sample resources periodically
            if (i + 1) % 10 == 0:
                resource_samples.append(self.monitor_resources())

        # End timing
        end_time = time.time()
        total_time = end_time - start_time

        # Record final resources
        final_resources = self.monitor_resources()

        # Calculate statistics
        successful_results = [r for r in request_results if 'error' not in r]
        num_successful = len(successful_results)

        if num_successful == 0:
            print("\n[ERROR] All requests failed. Cannot calculate statistics.")
            return

        # Calculate latencies by tier
        local_latencies = [r['latency_ms'] for r in successful_results if r['inference_source'] == 'local']
        fog_latencies = [r['latency_ms'] for r in successful_results if r['inference_source'] == 'fog']
        cloud_latencies = [r['latency_ms'] for r in successful_results if r['inference_source'] == 'cloud']

        avg_local = np.mean(local_latencies) if local_latencies else 0
        avg_fog = np.mean(fog_latencies) if fog_latencies else 0
        avg_cloud = np.mean(cloud_latencies) if cloud_latencies else 0
        avg_total = np.mean([r['latency_ms'] for r in successful_results])

        # Calculate average resources
        if resource_samples:
            avg_cpu = np.mean([r['cpu_percent'] for r in resource_samples])
            avg_memory = np.mean([r['memory_used_gb'] for r in resource_samples])
        else:
            avg_cpu = final_resources['cpu_percent']
            avg_memory = final_resources['memory_used_gb']

        # Store results
        self.results['smart_routing_test'] = {
            'num_images': num_images,
            'num_successful': num_successful,
            'num_failed': num_images - num_successful,
            'total_time_seconds': round(total_time, 3),
            'model_load_time_seconds': round(model_load_time, 3),
            'distribution': {
                'num_local': num_local,
                'num_fog': num_fog,
                'num_cloud': num_cloud,
                'percent_local': round((num_local / num_successful) * 100, 1) if num_successful > 0 else 0,
                'percent_fog': round((num_fog / num_successful) * 100, 1) if num_successful > 0 else 0,
                'percent_cloud': round((num_cloud / num_successful) * 100, 1) if num_successful > 0 else 0
            },
            'latency': {
                'avg_local_ms': round(avg_local, 2) if local_latencies else None,
                'avg_fog_ms': round(avg_fog, 2) if fog_latencies else None,
                'avg_cloud_ms': round(avg_cloud, 2) if cloud_latencies else None,
                'avg_total_ms': round(avg_total, 2)
            },
            'resources': {
                'initial': initial_resources,
                'final': final_resources,
                'avg_during_test': {
                    'cpu_percent': round(avg_cpu, 2),
                    'memory_used_gb': round(avg_memory, 2)
                }
            },
            'individual_requests': request_results
        }

        # Print summary
        self.print_results()

    def print_results(self):
        """Print test results summary"""
        test = self.results['smart_routing_test']

        print(f"\n{'='*60}")
        print("Smart Routing Test Results")
        print(f"{'='*60}\n")

        print(f"Requests:")
        print(f"  Total: {test['num_images']}")
        print(f"  Successful: {test['num_successful']}")
        print(f"  Failed: {test['num_failed']}\n")

        dist = test['distribution']
        print(f"Inference Source Distribution:")
        print(f"  Local (Edge): {dist['num_local']} requests ({dist['percent_local']}%)")
        print(f"  Fog: {dist['num_fog']} requests ({dist['percent_fog']}%)")
        print(f"  Cloud: {dist['num_cloud']} requests ({dist['percent_cloud']}%)\n")

        lat = test['latency']
        print(f"Average Latency by Tier:")
        if lat['avg_local_ms'] is not None:
            print(f"  Local: {lat['avg_local_ms']:.2f} ms")
        if lat['avg_fog_ms'] is not None:
            print(f"  Fog: {lat['avg_fog_ms']:.2f} ms")
        if lat['avg_cloud_ms'] is not None:
            print(f"  Cloud: {lat['avg_cloud_ms']:.2f} ms")
        print(f"  Overall: {lat['avg_total_ms']:.2f} ms\n")

        print(f"Total Time: {test['total_time_seconds']:.3f} seconds")
        print(f"Model Load Time: {test['model_load_time_seconds']:.3f} seconds\n")

        res = test['resources']
        print(f"Edge Client Resources:")
        print(f"  Avg CPU: {res['avg_during_test']['cpu_percent']:.1f}%")
        print(f"  Avg Memory: {res['avg_during_test']['memory_used_gb']:.2f} GB\n")

        print(f"{'='*60}\n")

    def save_results(self):
        """Save results to JSON file"""
        os.makedirs('output', exist_ok=True)
        filename = f"task4_smart_routing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('output', filename)

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {filepath}")
        return filepath


def main():
    """Main execution"""
    print("="*60)
    print("Smart Edge Client - Three-Tier Routing Test")
    print("="*60)

    # Create smart edge client
    client = SmartEdgeClient(
        fog_server_url=FOG_SERVER_URL,
        edge_threshold=EDGE_COMPLEXITY_THRESHOLD
    )

    # Run smart routing test
    client.run_smart_routing_test(num_images=NUM_TEST_IMAGES)

    # Save results
    client.save_results()


if __name__ == "__main__":
    main()
