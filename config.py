# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# YOLO11 Pose settings
YOLO_MODEL_PATH = 'yolo11n-pose.pt'  # nano model (faster on RPi), use yolo11s-pose.pt for better accuracy
YOLO_CONFIDENCE = 0.7  # Minimum detection confidence
YOLO_IOU = 0.5  # IoU threshold for NMS

# Stabilization settings
STABILIZE_FRAMES = 10        # Consecutive identical readings required
COOLDOWN_SECONDS = 3.0       # Minimum time between accepted ratings

# Database
DB_PATH = "ratings.db"

# Flask API
API_HOST = "0.0.0.0"
API_PORT = 5000
