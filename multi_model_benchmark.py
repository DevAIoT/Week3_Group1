"""
Multi-Model Benchmark Script
Tests different models for edge computing comparison
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import (
    MobileNetV2, MobileNetV3Small, MobileNetV3Large,
    EfficientNetB0, EfficientNetB1, ResNet50
)
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as preprocess_mobilenetv2
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input as preprocess_mobilenetv3
from tensorflow.keras.applications.efficientnet import preprocess_input as preprocess_efficientnet
from tensorflow.keras.applications.resnet50 import preprocess_input as preprocess_resnet50
import time
import psutil
import json
from datetime import datetime

class MultiModelBenchmark:
    def __init__(self):
        self.models = {}
        self.results = {}
        
    def generate_dummy_image(self, seed=42):
        """Generate a dummy image"""
        np.random.seed(seed)
        image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        image = np.expand_dims(image, axis=0)
        return image.astype(np.float32)
    
    def load_model(self, model_name):
        """Load a specific model"""
        print(f"\nLoading {model_name}...")
        start_time = time.time()
        
        if model_name == "MobileNetV2":
            model = MobileNetV2(weights='imagenet', include_top=True)
            preprocess_fn = preprocess_mobilenetv2
        elif model_name == "MobileNetV3-Small":
            model = MobileNetV3Small(weights='imagenet', include_top=True)
            preprocess_fn = preprocess_mobilenetv3
        elif model_name == "MobileNetV3-Large":
            model = MobileNetV3Large(weights='imagenet', include_top=True)
            preprocess_fn = preprocess_mobilenetv3
        elif model_name == "EfficientNetB0":
            model = EfficientNetB0(weights='imagenet', include_top=True)
            preprocess_fn = preprocess_efficientnet
        elif model_name == "EfficientNetB1":
            model = EfficientNetB1(weights='imagenet', include_top=True, input_shape=(240, 240, 3))
            preprocess_fn = preprocess_efficientnet
        elif model_name == "ResNet50":
            model = ResNet50(weights='imagenet', include_top=True)
            preprocess_fn = preprocess_resnet50
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        load_time = time.time() - start_time
        
        # Warm-up
        dummy = self.generate_dummy_image()
        dummy = preprocess_fn(dummy)
        _ = model.predict(dummy, verbose=0)
        
        print(f"✓ {model_name} loaded in {load_time:.2f}s")
        
        return model, preprocess_fn, load_time
    
    def benchmark_model(self, model_name, num_images=100):
        """Benchmark a specific model"""
        print(f"\n{'='*60}")
        print(f"Benchmarking {model_name}")
        print(f"{'='*60}")
        
        model, preprocess_fn, load_time = self.load_model(model_name)
        
        # Get model info
        param_count = model.count_params()
        
        # Generate test images
        print(f"Generating {num_images} test images...")
        images = []
        for i in range(num_images):
            img = self.generate_dummy_image(seed=i)
            img = preprocess_fn(img)
            images.append(img)
        
        # Benchmark inference
        print("Running inference...")
        start_time = time.time()
        cpu_before = psutil.cpu_percent(interval=0.1)
        mem_before = psutil.virtual_memory().percent
        
        for img in images:
            _ = model.predict(img, verbose=0)
        
        end_time = time.time()
        cpu_after = psutil.cpu_percent(interval=0.1)
        mem_after = psutil.virtual_memory().percent
        
        total_time = end_time - start_time
        avg_time = total_time / num_images
        throughput = num_images / total_time
        
        # Results
        results = {
            'model_name': model_name,
            'parameters': int(param_count),
            'parameters_millions': round(param_count / 1e6, 2),
            'load_time_seconds': round(load_time, 3),
            'num_images': num_images,
            'total_inference_time_seconds': round(total_time, 3),
            'avg_time_per_image_ms': round(avg_time * 1000, 2),
            'throughput_images_per_sec': round(throughput, 2),
            'cpu_usage_percent': round((cpu_before + cpu_after) / 2, 2),
            'memory_usage_percent': round((mem_before + mem_after) / 2, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        # Print results
        print(f"\n{'-'*60}")
        print("RESULTS:")
        print(f"  Parameters: {results['parameters_millions']}M")
        print(f"  Load Time: {results['load_time_seconds']}s")
        print(f"  Inference Time: {results['total_inference_time_seconds']}s")
        print(f"  Avg Latency: {results['avg_time_per_image_ms']}ms")
        print(f"  Throughput: {results['throughput_images_per_sec']} images/sec")
        print(f"  CPU Usage: {results['cpu_usage_percent']}%")
        print(f"  Memory Usage: {results['memory_usage_percent']}%")
        print(f"{'-'*60}")
        
        self.results[model_name] = results
        
        # Clean up
        del model
        tf.keras.backend.clear_session()
        
        return results
    
    def run_all_benchmarks(self, num_images=100):
        """Run benchmarks for all models"""
        models_to_test = [
            "MobileNetV2",
            "MobileNetV3-Small",
            "MobileNetV3-Large",
            "EfficientNetB0",
            "ResNet50"
        ]
        
        print("\n" + "="*60)
        print("MULTI-MODEL EDGE COMPUTING BENCHMARK")
        print("="*60)
        print(f"Number of images per model: {num_images}")
        
        for model_name in models_to_test:
            try:
                self.benchmark_model(model_name, num_images)
                time.sleep(2)  # Cool-down between models
            except Exception as e:
                print(f"✗ Error benchmarking {model_name}: {e}")
        
        # Print comparison
        self.print_comparison()
        
        # Save results
        self.save_results()
    
    def print_comparison(self):
        """Print model comparison table"""
        if not self.results:
            return
        
        print("\n" + "="*100)
        print("MODEL COMPARISON TABLE")
        print("="*100)
        
        print(f"\n{'Model':<20} {'Params (M)':<12} {'Load (s)':<10} {'Latency (ms)':<15} "
              f"{'Throughput':<15} {'CPU %':<10}")
        print("-"*100)
        
        # Sort by throughput
        sorted_models = sorted(self.results.items(), 
                             key=lambda x: x[1]['throughput_images_per_sec'], 
                             reverse=True)
        
        for model_name, result in sorted_models:
            print(f"{model_name:<20} {result['parameters_millions']:<12.2f} "
                  f"{result['load_time_seconds']:<10.3f} "
                  f"{result['avg_time_per_image_ms']:<15.2f} "
                  f"{result['throughput_images_per_sec']:<15.2f} "
                  f"{result['cpu_usage_percent']:<10.2f}")
        
        print("\n" + "="*100)
        
        # Analysis
        print("\nKEY INSIGHTS:")
        
        fastest = sorted_models[0]
        slowest = sorted_models[-1]
        
        print(f"\n1. FASTEST MODEL: {fastest[0]}")
        print(f"   - Throughput: {fastest[1]['throughput_images_per_sec']:.2f} images/sec")
        print(f"   - Latency: {fastest[1]['avg_time_per_image_ms']:.2f}ms")
        
        print(f"\n2. SLOWEST MODEL: {slowest[0]}")
        print(f"   - Throughput: {slowest[1]['throughput_images_per_sec']:.2f} images/sec")
        print(f"   - Latency: {slowest[1]['avg_time_per_image_ms']:.2f}ms")
        
        speedup = fastest[1]['throughput_images_per_sec'] / slowest[1]['throughput_images_per_sec']
        print(f"\n3. SPEED DIFFERENCE: {speedup:.2f}x faster")
        
        print("\n4. MODEL RECOMMENDATIONS:")
        print("   - Real-time video (30 fps, <33ms): ", end="")
        suitable_models = [name for name, result in self.results.items() 
                          if result['avg_time_per_image_ms'] < 33]
        if suitable_models:
            print(", ".join(suitable_models))
        else:
            print("None (consider GPU acceleration)")
        
        print("   - Battery-constrained devices: MobileNetV3-Small or MobileNetV2")
        print("   - Best accuracy-speed trade-off: EfficientNetB0")
        print("   - Cloud/desktop with GPU: ResNet50 or larger models")
        
        print("\n" + "="*100)
    
    def save_results(self):
        """Save results to JSON"""
        filename = f"multi_model_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"/home/claude/{filename}"
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'ram_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'tensorflow_version': tf.__version__
            },
            'results': self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results saved to: {filepath}")
        return filepath


def main():
    """Main function"""
    benchmark = MultiModelBenchmark()
    
    # Run benchmarks
    benchmark.run_all_benchmarks(num_images=100)
    
    print("\n" + "="*60)
    print("BENCHMARK COMPLETE!")
    print("="*60)
    print("\nUse these results to:")
    print("1. Choose the best model for your edge device")
    print("2. Understand speed vs accuracy trade-offs")
    print("3. Determine if GPU acceleration is needed")
    print("4. Plan your AIoT application architecture")
    print()


if __name__ == "__main__":
    main()
