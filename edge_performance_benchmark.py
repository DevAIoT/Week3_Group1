"""
Edge Computing Performance Evaluation Script
Benchmarks MobileNetV2 inference on local hardware
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

class EdgePerformanceBenchmark:
    def __init__(self):
        self.model = None
        self.results = {
            'system_info': self.get_system_info(),
            'same_images_test': {},
            'different_images_test': {}
        }
    
    def get_system_info(self):
        """Collect system information"""
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'ram_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': platform.python_version(),
            'tensorflow_version': tf.__version__,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check for GPU
        gpus = tf.config.list_physical_devices('GPU')
        info['gpu_available'] = len(gpus) > 0
        info['gpu_count'] = len(gpus)
        if gpus:
            info['gpu_names'] = [gpu.name for gpu in gpus]
        
        return info
    
    def initialize_model(self):
        """Initialize MobileNetV2 model"""
        print("Initializing MobileNetV2 model...")
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
        dummy = self.generate_dummy_image()
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
    
    def run_inference_test(self, num_images=100, use_same_image=True, test_name=""):
        """Run inference test with performance monitoring"""
        print(f"\n{'='*60}")
        print(f"Running Test: {test_name}")
        print(f"{'='*60}")
        print(f"Number of images: {num_images}")
        print(f"Using same image: {use_same_image}\n")
        
        # Pre-generate images if using different images
        if use_same_image:
            print("Generating single test image...")
            images = [self.generate_dummy_image(seed=37)]
        else:
            print(f"Generating {num_images} different images...")
            images = [self.generate_dummy_image(seed=i) for i in range(num_images)]
        
        print("Starting predictions...\n")
        
        # Record initial resources
        initial_resources = self.monitor_resources()
        
        # Start timing (predictions only)
        start_time = time.time()
        
        # Perform predictions
        predictions = []
        resource_samples = []
        
        for i in range(num_images):
            # Select image
            img = images[0] if use_same_image else images[i]
            
            # Predict
            pred = self.model.predict(img, verbose=0)
            predictions.append(pred)
            
            # Sample resources every 10 predictions
            if (i + 1) % 10 == 0:
                resource_samples.append(self.monitor_resources())
                print(f"Progress: {i+1}/{num_images} predictions completed")
        
        # End timing
        end_time = time.time()
        total_time = end_time - start_time
        
        # Record final resources
        final_resources = self.monitor_resources()
        
        # Calculate metrics
        avg_time_per_image = total_time / num_images
        throughput = num_images / total_time  # images per second
        
        # Calculate average resource usage during predictions
        if resource_samples:
            avg_cpu = np.mean([r['cpu_percent'] for r in resource_samples])
            avg_memory = np.mean([r['memory_percent'] for r in resource_samples])
            avg_memory_gb = np.mean([r['memory_used_gb'] for r in resource_samples])
        else:
            avg_cpu = (initial_resources['cpu_percent'] + final_resources['cpu_percent']) / 2
            avg_memory = (initial_resources['memory_percent'] + final_resources['memory_percent']) / 2
            avg_memory_gb = (initial_resources['memory_used_gb'] + final_resources['memory_used_gb']) / 2
        
        results = {
            'num_images': num_images,
            'use_same_image': use_same_image,
            'total_time_seconds': round(total_time, 3),
            'avg_time_per_image_ms': round(avg_time_per_image * 1000, 2),
            'throughput_images_per_sec': round(throughput, 2),
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'resources': {
                'initial': initial_resources,
                'final': final_resources,
                'average_during_inference': {
                    'cpu_percent': round(avg_cpu, 2),
                    'memory_percent': round(avg_memory, 2),
                    'memory_used_gb': round(avg_memory_gb, 2)
                }
            }
        }
        
        # Print results
        print(f"\n{'-'*60}")
        print("TEST RESULTS")
        print(f"{'-'*60}")
        print(f"Total inference time: {total_time:.3f} seconds")
        print(f"Average time per image: {avg_time_per_image*1000:.2f} ms")
        print(f"Throughput: {throughput:.2f} images/second")
        print(f"\nResource Usage (Average during inference):")
        print(f"  CPU: {avg_cpu:.2f}%")
        print(f"  Memory: {avg_memory:.2f}% ({avg_memory_gb:.2f} GB)")
        print(f"{'-'*60}\n")
        
        return results
    
    def run_full_benchmark(self, num_images=100):
        """Run complete benchmark suite"""
        print("\n" + "="*60)
        print("EDGE COMPUTING PERFORMANCE BENCHMARK")
        print("="*60)
        print(f"\nSystem Information:")
        for key, value in self.results['system_info'].items():
            print(f"  {key}: {value}")
        
        # Initialize model
        load_time = self.initialize_model()
        self.results['model_load_time'] = load_time
        
        # Test 1: Same images for all predictions
        self.results['same_images_test'] = self.run_inference_test(
            num_images=num_images,
            use_same_image=True,
            test_name="Same Image Test (Caching Scenario)"
        )
        
        # Small delay between tests
        time.sleep(2)
        
        # Test 2: Different images for each prediction
        self.results['different_images_test'] = self.run_inference_test(
            num_images=num_images,
            use_same_image=False,
            test_name="Different Images Test (Real-world Scenario)"
        )
        
        # Save results
        self.save_results()
        
        # Print analysis
        self.print_analysis()
    
    def save_results(self):
        """Save results to JSON file"""
        filename = f"edge_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # create a output directory if it doesn't exist
        if not os.path.exists('output'):
            os.makedirs('output')
            
        filepath = os.path.join('output', filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nResults saved to: {filepath}")
        return filepath
    
    def print_analysis(self):
        """Print comparative analysis"""
        print("\n" + "="*60)
        print("COMPARATIVE ANALYSIS")
        print("="*60)
        
        same_img = self.results['same_images_test']
        diff_img = self.results['different_images_test']
        
        # Performance comparison
        time_diff = diff_img['total_time_seconds'] - same_img['total_time_seconds']
        time_diff_pct = (time_diff / same_img['total_time_seconds']) * 100
        
        throughput_diff = same_img['throughput_images_per_sec'] - diff_img['throughput_images_per_sec']
        throughput_diff_pct = (throughput_diff / same_img['throughput_images_per_sec']) * 100
        
        print("\n1. INFERENCE TIME COMPARISON:")
        print(f"   Same Image: {same_img['total_time_seconds']:.3f}s")
        print(f"   Different Images: {diff_img['total_time_seconds']:.3f}s")
        print(f"   Difference: {time_diff:+.3f}s ({time_diff_pct:+.1f}%)")
        
        print("\n2. THROUGHPUT COMPARISON:")
        print(f"   Same Image: {same_img['throughput_images_per_sec']:.2f} images/sec")
        print(f"   Different Images: {diff_img['throughput_images_per_sec']:.2f} images/sec")
        print(f"   Difference: {throughput_diff:+.2f} images/sec ({throughput_diff_pct:+.1f}%)")
        
        print("\n3. RESOURCE USAGE COMPARISON:")
        same_cpu = same_img['resources']['average_during_inference']['cpu_percent']
        diff_cpu = diff_img['resources']['average_during_inference']['cpu_percent']
        same_mem = same_img['resources']['average_during_inference']['memory_percent']
        diff_mem = diff_img['resources']['average_during_inference']['memory_percent']
        
        print(f"   CPU Usage:")
        print(f"     Same Image: {same_cpu:.2f}%")
        print(f"     Different Images: {diff_cpu:.2f}%")
        print(f"     Difference: {diff_cpu - same_cpu:+.2f}%")
        
        print(f"   Memory Usage:")
        print(f"     Same Image: {same_mem:.2f}%")
        print(f"     Different Images: {diff_mem:.2f}%")
        print(f"     Difference: {diff_mem - same_mem:+.2f}%")
        
        print("\n" + "="*60)
        print("AIoT APPLICATION IMPLICATIONS")
        print("="*60)
        
        print("""
1. CACHING BENEFITS:
   - Using the same image shows potential caching benefits in memory/CPU
   - Real-world AIoT may not always benefit from this in streaming scenarios
   
2. EDGE PROCESSING CAPABILITY:
   - Average latency per image indicates real-time processing capability
   - For video processing (30 fps), need <33ms per frame
   - Current performance: {:.2f}ms per image
   
3. POWER MODE IMPLICATIONS:
   - Power Saver Mode: Reduces CPU frequency, increases latency
   - High Performance Mode: Maximum CPU, better throughput, higher power
   - Trade-off between battery life and inference speed
   
4. VERTICAL SCALING CONSIDERATIONS:
   - Better hardware (more cores, faster CPU) improves throughput
   - GPU acceleration can provide 10-100x speedup for inference
   - Memory bandwidth affects batch processing capability
   
5. MODEL SELECTION:
   - MobileNetV2: Optimized for mobile/edge devices
   - Lighter models (MobileNetV3, EfficientNet-Lite): Lower latency
   - Heavier models (ResNet, EfficientNet): Better accuracy, higher latency
        """.format(same_img['avg_time_per_image_ms']))
        
        print("="*60)


def main():
    """Main execution function"""
    # Create benchmark instance
    benchmark = EdgePerformanceBenchmark()
    
    # Run full benchmark with 100 images
    benchmark.run_full_benchmark(num_images=100)
    
    print("\nBenchmark complete!")
    print("Please run this script in both Power Saver and High Performance modes")
    print("to compare the results.\n")


if __name__ == "__main__":
    main()
