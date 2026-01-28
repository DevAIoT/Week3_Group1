# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# MediaPipe Hands settings
MP_MODEL_COMPLEXITY = 0  # 0=lite (faster on RPi), 1=full
MP_MAX_NUM_HANDS = 1
MP_MIN_DETECTION_CONFIDENCE = 0.7
MP_MIN_TRACKING_CONFIDENCE = 0.5

# Stabilization settings
STABILIZE_FRAMES = 10        # Consecutive identical readings required
COOLDOWN_SECONDS = 3.0       # Minimum time between accepted ratings

# Database
DB_PATH = "ratings.db"

# Flask API
API_HOST = "0.0.0.0"
API_PORT = 5000
