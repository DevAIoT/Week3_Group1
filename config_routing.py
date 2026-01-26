"""
Configuration for Three-Tier Smart Routing System
Defines thresholds, URLs, and system parameters
"""

# Complexity Thresholds
EDGE_COMPLEXITY_THRESHOLD = 2000.0  # Edge processes only simplest images
FOG_COMPLEXITY_THRESHOLD = 5000.0   # Fog handles moderately complex images

# Server URLs (Update these with actual IP addresses from your laptops)
# To find IP address on each laptop:
#   Windows: ipconfig
#   Linux/Mac: ifconfig
FOG_SERVER_URL = "http://172.20.10.4:8000/predict"    # Laptop 2 IP
CLOUD_SERVER_URL = "http://172.20.10.5:8001/predict"  # Laptop 3 IP

# Server Ports
FOG_SERVER_PORT = 8000
CLOUD_SERVER_PORT = 8001

# Request Settings
REQUEST_TIMEOUT = 30  # seconds

# Test Parameters
NUM_TEST_IMAGES = 50
