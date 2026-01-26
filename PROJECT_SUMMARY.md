# Edge Computing Performance Evaluation - Project Summary

## 📁 Project Files

This package contains everything you need to evaluate edge computing performance for AI inference:

### Core Scripts

1. **edge_performance_benchmark.py** (Main Script)
   - Comprehensive benchmark for MobileNetV2
   - Tests both same and different image scenarios
   - Records resource usage (CPU, memory)
   - Generates detailed JSON results
   - ~400 lines of well-documented code

2. **multi_model_benchmark.py** (Model Comparison)
   - Tests multiple models: MobileNetV2, MobileNetV3, EfficientNet, ResNet50
   - Compares speed, accuracy trade-offs
   - Helps you choose the best model for your use case
   - ~300 lines of code

3. **compare_results.py** (Result Analysis)
   - Compares results from multiple laptops
   - Generates comparison tables
   - Creates visualizations (requires matplotlib)
   - Exports to CSV for further analysis
   - ~250 lines of code

4. **run_benchmark.sh** (Quick Start Script)
   - Interactive menu system
   - Automatic dependency checking
   - Easy-to-use interface for running benchmarks
   - Works on Linux/Mac

### Documentation

5. **README.md**
   - Complete guide with instructions
   - Detailed explanations of all features
   - Analysis questions and guidance
   - Troubleshooting section
   - ~300 lines of documentation

6. **requirements.txt**
   - Python dependencies
   - Easy installation with pip

7. **PROJECT_SUMMARY.md** (This file)
   - Overview of the project
   - Quick reference guide

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Benchmark (Interactive)
```bash
./run_benchmark.sh
# or
bash run_benchmark.sh
```

### Step 3: Run Benchmark (Direct)
```bash
python edge_performance_benchmark.py
```

### Step 4: Compare Results
```bash
python compare_results.py result1.json result2.json result3.json
```

## 📊 What Gets Measured

### Performance Metrics
- **Total Inference Time**: Complete time to process all images
- **Average Latency**: Time per image (milliseconds)
- **Throughput**: Images processed per second
- **CPU Usage**: Percentage during inference
- **Memory Usage**: Percentage and absolute values

### Test Scenarios
1. **Same Images**: All predictions use identical image (tests caching)
2. **Different Images**: Each prediction uses unique image (real-world)

### System Information
- Platform and OS details
- Processor specifications
- CPU core count
- Total RAM
- GPU availability

## 🎯 Assignment Requirements Coverage

### ✅ Task 1: Initialize MobileNetV2
- Loads model from `tensorflow.keras.applications`
- Automatic download of pre-trained weights
- Includes warm-up prediction for accurate timing

### ✅ Task 2: Generate Dummy Images
- Function: `generate_dummy_image()`
- Creates 224x224x3 NumPy arrays
- Proper preprocessing for MobileNetV2
- Configurable seed for reproducibility

### ✅ Task 3: Predict 100 Images
- Loop through 100 iterations
- Tests both same and different images
- Progress tracking during execution
- Efficient batch processing

### ✅ Task 4: Record Resources and Timing
- Uses `psutil` for resource monitoring
- Records start/end times with high precision
- Samples resources during execution
- Saves comprehensive results to JSON

### ✅ Additional: Power Mode Testing
- Instructions for both Power Saver and High Performance
- Scripts work on Windows, macOS, and Linux
- Clear guidance on changing power settings

## 📈 Expected Results

### Typical Performance (CPU, Modern Laptop)

**Power Saver Mode:**
- Throughput: ~2-3 images/second
- Latency: ~300-500ms per image
- CPU Usage: 60-80%

**High Performance Mode:**
- Throughput: ~3-5 images/second
- Latency: ~200-400ms per image
- CPU Usage: 80-100%

**With GPU Acceleration:**
- Throughput: ~20-100+ images/second
- Latency: ~10-50ms per image
- Significant speedup (10-50x)

### Performance Differences

**Same vs Different Images:**
- Usually 2-10% difference
- Same images may benefit from caching
- Difference varies by system

**Power Mode Impact:**
- 20-50% performance improvement in High Performance
- Higher power consumption
- Better thermal management needed

## 🔍 Analysis Framework

### 1. Vertical Scaling Analysis

**Hardware Factors:**
- CPU cores → Affects potential parallelism
- CPU frequency → Directly impacts latency
- RAM → Prevents swap, maintains consistency
- GPU → 10-100x speedup potential

**Questions to Answer:**
- How do different laptops compare?
- What's the performance variation?
- Is the difference justified by hardware specs?
- Where is the bottleneck?

### 2. Power Mode Implications

**Battery vs Performance Trade-off:**
- Power Saver: Extended battery, reduced performance
- High Performance: Maximum speed, high power draw
- Dynamic adjustment possible in real applications

**Questions to Answer:**
- How much performance is lost in Power Saver?
- Is the trade-off acceptable for your use case?
- Can you achieve real-time requirements in both modes?

### 3. Model Selection Impact

**Model Characteristics:**

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| MobileNetV2 | Fast | Good | Small | Mobile/Edge |
| MobileNetV3 | Faster | Better | Small | Latest mobile |
| EfficientNet | Medium | Great | Medium | Balanced |
| ResNet50 | Slower | High | Large | Cloud/Server |

**Questions to Answer:**
- Which model meets your latency requirements?
- Can you accept lower accuracy for better speed?
- Does model size affect deployment?

### 4. AIoT Application Design

**Real-Time Requirements:**
- Video (30 fps): <33ms per frame
- Video (60 fps): <16ms per frame
- Interactive systems: <50ms
- Monitoring: 100-200ms acceptable

**Deployment Strategies:**
- Full Edge: All processing local
- Hybrid: Simple tasks on edge, complex in cloud
- Adaptive: Switch based on conditions

**Questions to Answer:**
- Can your hardware meet real-time requirements?
- Should you use edge, cloud, or hybrid?
- What optimizations are needed?
- How does your choice affect user experience?

## 📝 Report Recommendations

### Section 1: Methodology
- Describe test setup and conditions
- Explain why you chose specific tests
- Document hardware specifications
- Mention any limitations

### Section 2: Results
- Present data in tables and graphs
- Compare across laptops and power modes
- Show same vs different image results
- Include statistical analysis

### Section 3: Analysis
- Interpret performance differences
- Explain impact of vertical scaling
- Discuss power mode trade-offs
- Analyze model selection implications

### Section 4: AIoT Application Design
- Describe your proposed architecture
- Justify edge vs cloud decisions
- Explain how you meet requirements
- Discuss potential optimizations

### Section 5: Conclusions
- Summarize key findings
- Provide recommendations
- Suggest future work
- Reflect on learning

## 🔧 Customization Options

### Change Number of Images
```python
benchmark.run_full_benchmark(num_images=50)  # Instead of 100
```

### Test Different Models
```python
from tensorflow.keras.applications import MobileNetV3Small
self.model = MobileNetV3Small(weights='imagenet', include_top=True)
```

### Add Custom Metrics
```python
# In monitor_resources():
'gpu_usage': get_gpu_usage(),  # Add custom function
```

### Batch Processing
```python
# Process multiple images at once
batch = np.vstack([images[i] for i in range(10)])
predictions = model.predict(batch)
```

## 🐛 Troubleshooting

### TensorFlow Not Installing
```bash
# For CPU-only (lighter)
pip install tensorflow-cpu

# If that fails, try specific version
pip install tensorflow-cpu==2.10.0
```

### Out of Memory
```python
# Reduce number of images
benchmark.run_full_benchmark(num_images=50)
```

### Import Errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --upgrade
```

### Slow Performance
- Close other applications
- Ensure laptop is in correct power mode
- Check if thermal throttling is occurring
- Consider using GPU if available

## 📚 Additional Resources

### Learning Materials
- TensorFlow Tutorials: https://www.tensorflow.org/tutorials
- MobileNet Paper: https://arxiv.org/abs/1801.04381
- Edge AI Overview: https://www.edge-ai-vision.com/

### Tools and Libraries
- TensorFlow Lite: For mobile deployment
- ONNX: Model conversion between frameworks
- TensorRT: NVIDIA's inference optimization

### Related Topics
- Model quantization (INT8)
- Neural architecture search
- Hardware acceleration (TPU, NPU)
- Federated learning on edge devices

## 💡 Tips for Success

1. **Run Multiple Times**: Average 3-5 runs for reliability
2. **Control Variables**: Test one thing at a time
3. **Document Everything**: Record conditions for each test
4. **Compare Fairly**: Use same conditions across laptops
5. **Think Critically**: Don't just present data, interpret it
6. **Consider Real World**: Think about practical deployment

## 🎓 Learning Objectives

By completing this assignment, you will understand:
- How to benchmark AI models on edge devices
- Impact of hardware on inference performance
- Trade-offs between power and performance
- Model selection for different use cases
- How to design edge/cloud hybrid systems
- Resource monitoring and profiling techniques
- Performance optimization strategies

## 📞 Getting Help

If you encounter issues:
1. Check the README.md for detailed instructions
2. Review the troubleshooting section
3. Consult with group members
4. Search for TensorFlow-specific issues online
5. Ask your instructor/TA for guidance

## 🎉 Success Criteria

Your benchmarking is successful if you can:
- ✅ Run scripts without errors
- ✅ Generate complete JSON results
- ✅ Compare results across different conditions
- ✅ Interpret performance metrics
- ✅ Make informed decisions about deployment
- ✅ Present findings clearly in your report

Good luck with your edge computing evaluation! 🚀
