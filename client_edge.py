"""
Client Edge Device for Code Offloading
Generates images and sends them to the server for inference
Measures end-to-end latency and compares with baseline
"""

import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import time
import psutil
import json
import platform
from datetime import datetime
import os
import requests

class ClientEdge:
    def __init__(self, server_url="http://localhost:8000/predict"):
        self.server_url = server_url
        self.results = {
            'system_info': self.get_system_info(),
            'offloading_test': {}
        }

    def get_system_info(self):
        """Collect system information"""
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'ram_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat(),
            'server_url': self.server_url
        }
        return info

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

    def run_offloading_test(self, num_images=100):
        """Run offloading test with performance monitoring"""
        print(f"\n{'='*60}")
        print(f"Running Code Offloading Test")
        print(f"{'='*60}")
        print(f"Server URL: {self.server_url}")
        print(f"Number of images: {num_images}\n")

        # Check server health
        try:
            health_response = requests.get(self.server_url.replace('/predict', '/health'), timeout=5)
            if health_response.status_code == 200:
                print("[OK] Server is healthy and ready")
            else:
                print(f"[ERROR] Server health check failed: {health_response.status_code}")
                return
        except Exception as e:
            print(f"[ERROR] Cannot connect to server: {str(e)}")
            print("Please ensure the server is running:")
            print("  uvicorn server_surrogate:app --host 0.0.0.0 --port 8000")
            return

        # Record initial resources
        initial_resources = self.monitor_resources()
        print(f"\nInitial Resources:")
        print(f"  CPU: {initial_resources['cpu_percent']:.1f}%")
        print(f"  Memory: {initial_resources['memory_used_gb']} GB ({initial_resources['memory_percent']:.1f}%)\n")

        # Generate all images upfront
        print("Generating images...")
        images = [self.generate_dummy_image(seed=i) for i in range(num_images)]
        print(f"Generated {num_images} images\n")

        # Start timing (requests only)
        start_time = time.time()

        # Perform requests
        request_results = []
        resource_samples = []

        print("Sending requests to server...")
        for i in range(num_images):
            # Convert image to Python list for JSON serialization
            image_list = images[i].tolist()

            # Create request payload
            payload = {
                "image": image_list,
                "request_id": f"request_{i}",
                "timestamp": datetime.now().isoformat()
            }

            # Record "Sending Request" timestamp
            send_time = time.time()

            try:
                # Send POST request
                response = requests.post(self.server_url, json=payload, timeout=10)

                # Record "Receiving Response" timestamp
                receive_time = time.time()

                # Calculate loopback time
                loopback_time_ms = (receive_time - send_time) * 1000

                # Extract server response
                if response.status_code == 200:
                    response_data = response.json()
                    request_results.append({
                        "request_id": i,
                        "loopback_time_ms": loopback_time_ms,
                        "server_inference_time_ms": response_data["inference_time_ms"],
                        "network_overhead_ms": loopback_time_ms - response_data["inference_time_ms"],
                        "confidence": response_data["confidence"],
                        "top_class": response_data["top_class"]
                    })
                else:
                    print(f"[ERROR] Request {i} failed: {response.status_code}")
                    request_results.append({
                        "request_id": i,
                        "loopback_time_ms": loopback_time_ms,
                        "error": f"HTTP {response.status_code}"
                    })

            except requests.exceptions.Timeout:
                print(f"[ERROR] Request {i} timed out")
                request_results.append({
                    "request_id": i,
                    "error": "Timeout"
                })
            except Exception as e:
                print(f"[ERROR] Request {i} error: {str(e)}")
                request_results.append({
                    "request_id": i,
                    "error": str(e)
                })

            # Sample resources every 10 requests
            if (i + 1) % 10 == 0:
                resource_samples.append(self.monitor_resources())
                print(f"Progress: {i+1}/{num_images} requests completed")

        # End timing
        end_time = time.time()
        total_time = end_time - start_time

        # Record final resources
        final_resources = self.monitor_resources()

        # Calculate statistics (only for successful requests)
        successful_results = [r for r in request_results if 'error' not in r]
        num_successful = len(successful_results)

        if num_successful == 0:
            print("\n[ERROR] All requests failed. Cannot calculate statistics.")
            return

        loopback_times = [r['loopback_time_ms'] for r in successful_results]
        server_times = [r['server_inference_time_ms'] for r in successful_results]
        network_overheads = [r['network_overhead_ms'] for r in successful_results]

        avg_loopback_time = np.mean(loopback_times)
        avg_server_time = np.mean(server_times)
        avg_network_overhead = np.mean(network_overheads)
        throughput = num_successful / total_time

        # Calculate average resources during inference
        if resource_samples:
            avg_cpu = np.mean([r['cpu_percent'] for r in resource_samples])
            avg_memory = np.mean([r['memory_used_gb'] for r in resource_samples])
        else:
            avg_cpu = final_resources['cpu_percent']
            avg_memory = final_resources['memory_used_gb']

        # Load baseline for comparison
        baseline_avg_ms = 83.66  # From Task 1
        try:
            baseline_file = "output/edge_benchmark_results_20260126_112648.json"
            if os.path.exists(baseline_file):
                with open(baseline_file, 'r') as f:
                    baseline_data = json.load(f)
                    baseline_avg_ms = baseline_data['same_images_test']['avg_time_per_image_ms']
        except Exception as e:
            print(f"Note: Could not load baseline data: {e}")

        # Store results
        self.results['offloading_test'] = {
            'num_images': num_images,
            'num_successful': num_successful,
            'num_failed': num_images - num_successful,
            'total_time_seconds': round(total_time, 3),
            'avg_loopback_time_ms': round(avg_loopback_time, 2),
            'avg_server_inference_time_ms': round(avg_server_time, 2),
            'avg_network_overhead_ms': round(avg_network_overhead, 2),
            'throughput_images_per_sec': round(throughput, 2),
            'baseline_comparison': {
                'baseline_avg_ms': baseline_avg_ms,
                'loopback_avg_ms': round(avg_loopback_time, 2),
                'difference_ms': round(avg_loopback_time - baseline_avg_ms, 2),
                'difference_percent': round(((avg_loopback_time - baseline_avg_ms) / baseline_avg_ms) * 100, 2)
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

        # Print results
        self.print_results()

    def print_results(self):
        """Print test results"""
        test = self.results['offloading_test']

        print(f"\n{'='*60}")
        print("Code Offloading Test Results")
        print(f"{'='*60}\n")

        print(f"Requests:")
        print(f"  Total: {test['num_images']}")
        print(f"  Successful: {test['num_successful']}")
        print(f"  Failed: {test['num_failed']}\n")

        print(f"Timing:")
        print(f"  Total time: {test['total_time_seconds']:.3f} seconds")
        print(f"  Avg loopback time: {test['avg_loopback_time_ms']:.2f} ms")
        print(f"  Avg server inference time: {test['avg_server_inference_time_ms']:.2f} ms")
        print(f"  Avg network overhead: {test['avg_network_overhead_ms']:.2f} ms")
        print(f"  Throughput: {test['throughput_images_per_sec']:.2f} images/sec\n")

        print(f"Baseline Comparison:")
        baseline = test['baseline_comparison']
        print(f"  Baseline (Task 1): {baseline['baseline_avg_ms']:.2f} ms")
        print(f"  Offloading (Task 2): {baseline['loopback_avg_ms']:.2f} ms")
        print(f"  Difference: {baseline['difference_ms']:.2f} ms ({baseline['difference_percent']:.2f}%)\n")

        print(f"Client Resources:")
        res = test['resources']
        print(f"  Initial CPU: {res['initial']['cpu_percent']:.1f}%")
        print(f"  Avg CPU during test: {res['avg_during_test']['cpu_percent']:.1f}%")
        print(f"  Avg Memory during test: {res['avg_during_test']['memory_used_gb']:.2f} GB\n")

        print(f"Analysis:")
        diff_ms = baseline['difference_ms']
        diff_pct = baseline['difference_percent']
        print(f"  The time difference of {diff_ms:.2f} ms ({diff_pct:.2f}%) represents")
        print(f"  the cost of offloading, which includes:")
        print(f"    - Serialization overhead: ~{test['avg_network_overhead_ms']/2:.2f} ms")
        print(f"    - Network latency (localhost): ~{test['avg_network_overhead_ms']/2:.2f} ms")
        print(f"    - Total overhead: {test['avg_network_overhead_ms']:.2f} ms\n")

        if diff_pct < 50:
            print(f"  [OK] Overhead is reasonable ({diff_pct:.1f}%) for localhost testing")
        else:
            print(f"  [WARNING] Overhead is significant ({diff_pct:.1f}%)")

        print(f"\n{'='*60}\n")

    def save_results(self):
        """Save results to JSON file"""
        os.makedirs('output', exist_ok=True)
        filename = f"offloading_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('output', filename)

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {filepath}")

def main():
    """Main execution"""
    print("="*60)
    print("Edge Client - Code Offloading Test")
    print("="*60)

    # Create client instance
    client = ClientEdge(server_url="http://localhost:8000/predict")

    # Run offloading test with 100 images
    client.run_offloading_test(num_images=100)

    # Save results
    client.save_results()

if __name__ == "__main__":
    main()
