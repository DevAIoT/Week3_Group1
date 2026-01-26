# Task 4: Three-Tier Smart Routing - Setup Guide

## Overview

This guide provides step-by-step instructions for setting up and running the three-tier smart routing system across three separate laptops.

## System Architecture

```
Edge Client (Laptop 1 - Standard)
  |
  | Routes based on complexity threshold (2000)
  ↓
Fog Server/Client (Laptop 2 - Medium)
  |
  | Routes based on complexity threshold (5000)
  ↓
Cloud Server (Laptop 3 - Advanced)
```

## Files Created

1. **Shared Utilities:**
   - `router_utils.py` - Image complexity calculation and routing logic
   - `config_routing.py` - Configuration constants and thresholds

2. **Server Components:**
   - `server_cloud.py` - Cloud server (port 8001, Laptop 3)
   - `server_fog.py` - Fog server with routing (port 8000, Laptop 2)

3. **Client Component:**
   - `client_edge_smart.py` - Smart edge client (Laptop 1)

4. **Analysis:**
   - `analyze_task4_results.py` - Results analysis script

## Prerequisites

All three laptops must have:
- Python 3.x
- TensorFlow 2.x
- Required packages: `numpy`, `requests`, `fastapi`, `uvicorn`, `psutil`

```bash
pip install tensorflow numpy requests fastapi uvicorn psutil
```

## Setup Instructions

### Step 1: Network Configuration

1. **Connect all laptops to the same network** (WiFi or LAN)

2. **Find IP addresses on each laptop:**
   - Windows: `ipconfig` (look for IPv4 Address)
   - Linux/Mac: `ifconfig` or `ip addr` (look for inet)

3. **Note down the IP addresses:**
   - Laptop 1 (Edge): Not needed, client only
   - Laptop 2 (Fog): Example: `192.168.1.100`
   - Laptop 3 (Cloud): Example: `192.168.1.101`

4. **Update `config_routing.py` with actual IPs:**

```python
# Replace with your actual IP addresses
FOG_SERVER_URL = "http://192.168.1.100:8000/predict"
CLOUD_SERVER_URL = "http://192.168.1.101:8001/predict"
```

5. **Ensure firewall allows connections:**
   - Windows: Allow Python through Windows Firewall
   - Linux: `sudo ufw allow 8000` and `sudo ufw allow 8001`
   - Mac: System Preferences → Security & Privacy → Firewall

6. **Test connectivity:**
   - From Laptop 1, ping Laptop 2 and Laptop 3
   - From Laptop 2, ping Laptop 3

### Step 2: Copy Files to Each Laptop

**All laptops need:**
- `router_utils.py`
- `config_routing.py`

**Laptop 3 (Cloud) needs:**
- `server_cloud.py`

**Laptop 2 (Fog) needs:**
- `server_fog.py`

**Laptop 1 (Edge) needs:**
- `client_edge_smart.py`
- `analyze_task4_results.py` (for later analysis)

## Execution Instructions

### Phase 1: Start Servers (In Order)

**IMPORTANT: Start in reverse order - Cloud first, then Fog**

#### 1. Start Cloud Server (Laptop 3)

```bash
python server_cloud.py
```

Expected output:
```
============================================================
Cloud MobileNetV2 Inference Server
Three-Tier Smart Routing - Cloud Tier
============================================================
Initializing MobileNetV2 model on Cloud Server...
Model loaded in X.XX seconds
Performing warm-up inference...
Warm-up complete

Cloud Server ready and waiting for requests...
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Verification:** Open browser on Laptop 3 and visit `http://localhost:8001/health`

#### 2. Start Fog Server (Laptop 2)

```bash
python server_fog.py
```

Expected output:
```
============================================================
Fog MobileNetV2 Inference Server
Three-Tier Smart Routing - Fog Tier
============================================================
Initializing MobileNetV2 model on Fog Server...
Model loaded in X.XX seconds
Performing warm-up inference...
Warm-up complete

Fog Server ready and waiting for requests...
Complexity Threshold: 5000.0
Cloud Server URL: http://192.168.1.101:8001/predict

INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verification:**
1. Open browser on Laptop 2 and visit `http://localhost:8000/health`
2. Check that Cloud Server URL is correct in output

### Phase 2: Run Edge Client (Laptop 1)

```bash
python client_edge_smart.py
```

Expected output:
```
============================================================
Smart Edge Client - Three-Tier Routing Test
============================================================
Edge Threshold: 2000.0
Fog Server: http://192.168.1.100:8000/predict

Initializing local model for edge processing...
Model loaded in X.XX seconds
Performing warm-up inference...
Warm-up complete

[OK] Fog server is healthy and ready

Initial Resources:
  CPU: XX.X%
  Memory: X.XX GB (XX.X%)

Generating 50 test images...
Generated 50 images

Running smart routing test...
[Request 0] Complexity: 4123.45 → LOCAL (85.2ms)
[Request 1] Complexity: 5678.90 → FOG (456.8ms)
[Request 2] Complexity: 8901.23 → CLOUD (892.1ms)
...
```

The client will:
1. Load MobileNetV2 model locally
2. Generate 50 test images
3. Route each image based on complexity
4. Display results and save to JSON file

### Phase 3: Analyze Results

After the client completes, analyze the results:

```bash
python analyze_task4_results.py output/task4_smart_routing_results_*.json
```

This will:
1. Display comprehensive statistics
2. Show distribution across tiers
3. Calculate latency by tier
4. Analyze complexity distribution
5. Save text report to `output/task4_analysis_report.txt`

## Understanding the Output

### Client Output

- **LOCAL**: Image processed on edge client (Laptop 1)
- **FOG**: Image forwarded to fog and processed there (Laptop 2)
- **CLOUD**: Image forwarded to fog, then to cloud (Laptop 3)

### Server Output

**Fog Server will show:**
```
[FOG] Processing locally (complexity: 3456.78)
[FOG] Forwarding to cloud (complexity: 7890.12)
```

**Cloud Server will show:**
```
INFO:     127.0.0.1:XXXXX - "POST /predict HTTP/1.1" 200 OK
```

### Expected Distribution

With thresholds of 2000 and 5000:
- **Local (< 2000)**: ~30% of requests
- **Fog (2000-5000)**: ~40% of requests
- **Cloud (> 5000)**: ~30% of requests

**Note:** Random images typically have variance in range 1000-8000, so distribution may vary.

## Adjusting Thresholds

If you want to change the routing behavior, edit `config_routing.py`:

```python
# Lower thresholds = more requests forwarded
EDGE_COMPLEXITY_THRESHOLD = 1500.0  # More forwarding from edge

# Higher thresholds = more local processing
EDGE_COMPLEXITY_THRESHOLD = 3000.0  # More local processing on edge
```

After changing thresholds, restart all servers and re-run the client.

## Troubleshooting

### Problem: Client cannot connect to fog server

**Solution:**
1. Check fog server is running: `curl http://localhost:8000/health`
2. Verify IP address in `config_routing.py`
3. Check firewall settings
4. Ping fog server from edge client

### Problem: Fog cannot connect to cloud

**Solution:**
1. Check cloud server is running: `curl http://localhost:8001/health`
2. Verify cloud IP in `config_routing.py`
3. Check firewall on cloud server
4. Look at fog server logs for error messages

### Problem: All requests go to one tier

**Solution:**
1. This is expected if thresholds don't match image complexity
2. Run complexity profiling:
   ```python
   import numpy as np
   complexities = []
   for i in range(100):
       np.random.seed(i)
       img = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
       complexities.append(np.var(img))
   print(f"25th: {np.percentile(complexities, 25)}")
   print(f"50th: {np.percentile(complexities, 50)}")
   print(f"75th: {np.percentile(complexities, 75)}")
   ```
3. Adjust thresholds based on percentiles

### Problem: Model loading takes very long

**Expected:** First run downloads ImageNet weights (~14MB)
**Solution:** Wait for download to complete, subsequent runs will be faster

### Problem: High latency on fog/cloud requests

**Possible causes:**
1. Network congestion
2. Server overloaded
3. Large network distance between devices

**Check:**
- Network latency: `ping <server-ip>`
- Server CPU/memory usage
- Network bandwidth

## Performance Tips

1. **Use wired connections** instead of WiFi for lower latency
2. **Close unnecessary applications** on all laptops
3. **Run warm-up first** to ensure models are loaded
4. **Monitor resources** with `htop` or Task Manager
5. **Test with smaller batches** first (e.g., 10 images) before full test

## Testing Checklist

Before running full experiment:

- [ ] All three laptops on same network
- [ ] IP addresses confirmed and updated in `config_routing.py`
- [ ] Firewall allows ports 8000 and 8001
- [ ] Cloud server started and healthy
- [ ] Fog server started and can reach cloud
- [ ] Edge client can reach fog server
- [ ] Test with 5 images first to verify routing
- [ ] Check server logs show correct routing decisions

## Output Files

After running the test, you'll find:

1. **JSON Results:** `output/task4_smart_routing_results_YYYYMMDD_HHMMSS.json`
   - Complete test data with all requests
   - System information
   - Routing statistics

2. **Text Report:** `output/task4_analysis_report.txt`
   - Human-readable analysis
   - Statistics and insights
   - Performance comparison

## Next Steps

After successful execution:

1. Review the analysis report
2. Compare performance across tiers
3. Experiment with different thresholds
4. Test with different network conditions
5. Document observations for your report

## Additional Notes

- **Complexity Metric:** Uses pixel variance (`np.var()`) as complexity measure
- **Routing Logic:** Lower complexity → weaker device, Higher complexity → stronger device
- **Fallback:** Fog server falls back to local processing if cloud is unreachable
- **Timeout:** 30 seconds default for all requests
- **Test Size:** 50 images by default, configurable in `config_routing.py`
