# Edge Computing Performance Benchmark

## Overview
This script evaluates the performance capabilities of local execution ("Edge") for AI inference using MobileNetV2 on different laptop configurations.

## Requirements
- Python 3.8 or higher
- TensorFlow 2.10 or higher
- NumPy
- psutil

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Benchmark

### Quick Start
```bash
python edge_performance_benchmark.py
```

### Test Scenarios

#### 1. Power Saver Mode (Unplugged)
- Disconnect laptop from power
- Set power mode to "Power Saver" or "Battery Saver"
- Run: `python edge_performance_benchmark.py`
- Results will be saved as `edge_benchmark_results_YYYYMMDD_HHMMSS.json`

#### 2. High Performance Mode
- Connect laptop to power
- Set power mode to "High Performance" or "Best Performance"
- Run: `python edge_performance_benchmark.py`
- Results will be saved as `edge_benchmark_results_YYYYMMDD_HHMMSS.json`

### Changing Power Mode

**Windows:**
- Click battery icon in system tray
- Drag slider to "Best Performance" or "Best Battery Life"

**macOS:**
- System Preferences → Battery
- Uncheck "Optimize video streaming while on battery"
- Uncheck "Automatic graphics switching"

**Linux:**
- Use `cpupower` or power management settings
- Or use: `sudo cpupower frequency-set -g performance` / `powersave`

## What the Script Does

1. **Initializes MobileNetV2**: Loads pre-trained ImageNet model
2. **Generates Dummy Images**: Creates 224x224x3 RGB images
3. **Test 1 - Same Image**: Runs 100 predictions using the same image (tests caching)
4. **Test 2 - Different Images**: Runs 100 predictions with different images (real-world scenario)
5. **Records Metrics**:
   - Start and end times
   - CPU usage percentage
   - Memory usage percentage
   - Total inference time
   - Average time per image
   - Throughput (images/second)

## Understanding Results

### Key Metrics

- **Total Inference Time**: Time to process all 100 images
- **Average Time per Image**: Latency per image (lower is better)
- **Throughput**: Images processed per second (higher is better)
- **CPU/Memory Usage**: Resource utilization during inference

### Result File Structure
```json
{
  "system_info": {
    "platform": "...",
    "processor": "...",
    "cpu_count": 8,
    "ram_total_gb": 16.0,
    "gpu_available": false
  },
  "same_images_test": {
    "total_time_seconds": 45.2,
    "avg_time_per_image_ms": 452.0,
    "throughput_images_per_sec": 2.21
  },
  "different_images_test": {
    "total_time_seconds": 47.8,
    "avg_time_per_image_ms": 478.0,
    "throughput_images_per_sec": 2.09
  }
}
```

## Analysis Questions

### 1. Hardware Capability and Configuration (Vertical Scaling)

**Impact on Inference Performance:**
- **CPU Cores**: More cores → better batch processing
- **CPU Frequency**: Higher frequency → lower latency per image
- **RAM**: Sufficient RAM prevents swap, maintains performance
- **GPU**: 10-100x speedup possible with GPU acceleration

**Observations to Make:**
- Compare results between different laptops in your group
- Laptops with better processors should show higher throughput
- GPU-enabled systems will significantly outperform CPU-only

### 2. Power Modes

**Power Saver vs High Performance:**
- Power Saver: Reduces CPU frequency, thermal throttling
- High Performance: Maximum CPU frequency, full power
- Expected difference: 20-50% performance improvement in High Performance mode

### 3. Different Model Selection

**MobileNetV2 vs Other Models:**

| Model | Parameters | Inference Speed | Accuracy | Use Case |
|-------|-----------|----------------|----------|----------|
| MobileNetV2 | 3.4M | Fast | Good | Mobile/Edge devices |
| MobileNetV3 | 5.4M | Faster | Better | Latest mobile |
| EfficientNet-B0 | 5.3M | Medium | Better | Balanced |
| ResNet50 | 25M | Slower | High | Cloud/Desktop |
| EfficientNet-B7 | 66M | Very Slow | Very High | Cloud only |

**To test different models**, modify the script:
```python
from tensorflow.keras.applications import MobileNetV3Small, EfficientNetB0

# Replace in initialize_model():
self.model = MobileNetV3Small(weights='imagenet', include_top=True)
# or
self.model = EfficientNetB0(weights='imagenet', include_top=True)
```

## AIoT Application Implications

### Real-Time Processing Requirements
- **Video (30 fps)**: Need <33ms per frame
- **Video (60 fps)**: Need <16ms per frame
- **Surveillance**: 5-10 fps acceptable (100-200ms per frame)
- **Gesture Recognition**: <50ms for responsive interaction

### Edge vs Cloud Trade-offs

**Edge Advantages:**
- Low latency (no network delay)
- Privacy (data stays local)
- Works offline
- Reduced bandwidth

**Edge Challenges:**
- Limited compute power
- Battery constraints
- Thermal management
- Model size limitations

### Deployment Strategies

1. **Full Edge**: All processing on device
   - Use lightweight models (MobileNet, EfficientNet-Lite)
   - Optimize for specific hardware
   - Consider quantization (INT8)

2. **Hybrid**: Simple processing on edge, complex in cloud
   - Edge: Object detection, tracking
   - Cloud: Recognition, classification
   - Reduces latency for time-critical tasks

3. **Adaptive**: Switch based on conditions
   - Battery high + performance needed → Edge
   - Battery low or complex task → Cloud
   - Network available → Cloud backup

## Expected Results

### Typical Performance (CPU-only, Modern Laptop)

**Power Saver Mode:**
- Throughput: 1.5-3 images/second
- Latency: 300-600ms per image
- CPU Usage: 60-80%

**High Performance Mode:**
- Throughput: 2-5 images/second
- Latency: 200-500ms per image
- CPU Usage: 80-100%

**With GPU Acceleration:**
- Throughput: 20-100+ images/second
- Latency: 10-50ms per image
- GPU Usage: 70-90%

## Troubleshooting

### TensorFlow Installation Issues
```bash
# For CPU-only (lightweight)
pip install tensorflow-cpu

# For GPU support (requires CUDA)
pip install tensorflow
```

### Memory Issues
If you encounter out-of-memory errors:
```python
# Modify in the script: reduce batch size or number of images
benchmark.run_full_benchmark(num_images=50)  # Reduce from 100 to 50
```

### psutil Not Found
```bash
pip install psutil
```

## Additional Experiments

### 1. Test with Real Images
```python
from tensorflow.keras.preprocessing import image

def load_real_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return preprocess_input(img_array)
```

### 2. Test Different Batch Sizes
Modify the predict call to process multiple images at once:
```python
# Batch of 10 images
batch = np.vstack([images[i % len(images)] for i in range(10)])
pred = self.model.predict(batch, verbose=0)
```

### 3. Enable GPU Acceleration
```python
# Add at the beginning of the script
import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Enable memory growth
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
```

## Comparison with Other Students

Collect JSON results from all group members and compare:
- Which laptop has the best edge computing capability?
- How much does power mode affect performance?
- Is the performance sufficient for real-time AIoT applications?
- What model would you choose for your specific AIoT use case?

## Report Suggestions

Your report should include:
1. **System Specifications**: CPU, RAM, GPU for each laptop
2. **Performance Tables**: Compare all test results
3. **Graphs**: 
   - Throughput comparison across laptops
   - Power mode impact
   - Same vs different images
4. **Analysis**:
   - Why do different laptops perform differently?
   - How does vertical scaling help?
   - When would you choose edge vs cloud?
   - Model selection recommendations for different scenarios
5. **AIoT Application Design**:
   - Proposed architecture for your application
   - Rationale for edge vs cloud decisions
   - Performance requirements and how they're met

## References

- TensorFlow Documentation: https://www.tensorflow.org/
- MobileNetV2 Paper: https://arxiv.org/abs/1801.04381
- Edge AI: https://www.edge-ai-vision.com/
- AIoT Applications: https://www.iotforall.com/what-is-aiot
