import sys
import cv2
import numpy as np


class Camera:
    """Camera wrapper with context manager support.

    Automatically detects and uses:
    - Picamera2 for Raspberry Pi Camera Module
    - OpenCV for USB cameras or other platforms
    """

    def __init__(self, index=0, width=640, height=480):
        self.index = index
        self.width = width
        self.height = height
        self.cap = None
        self.picam2 = None
        self.use_picamera2 = False

    def __enter__(self):
        # Try Picamera2 first (for Raspberry Pi Camera Module)
        if sys.platform == "linux":
            try:
                from picamera2 import Picamera2
                print("Attempting to use Picamera2 for Raspberry Pi Camera Module...")
                self.picam2 = Picamera2()

                # Configure camera for video capture
                config = self.picam2.create_preview_configuration(
                    main={"size": (self.width, self.height), "format": "RGB888"}
                )
                self.picam2.configure(config)
                self.picam2.start()

                self.use_picamera2 = True
                print("Successfully initialized Picamera2")
                return self
            except (ImportError, RuntimeError) as e:
                print(f"Picamera2 not available ({e}), falling back to OpenCV...")
                self.picam2 = None
                self.use_picamera2 = False

        # Fallback to OpenCV VideoCapture
        if sys.platform == "linux":
            self.cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)
        else:
            self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print("Successfully initialized OpenCV VideoCapture")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.use_picamera2 and self.picam2:
            self.picam2.stop()
        if self.cap:
            self.cap.release()
        return False

    def read(self):
        """Read a frame. Returns (success, frame_bgr)."""
        if self.use_picamera2 and self.picam2:
            try:
                # Picamera2 returns RGB, convert to BGR for OpenCV
                frame_rgb = self.picam2.capture_array()
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                return True, frame_bgr
            except Exception as e:
                print(f"Error reading from Picamera2: {e}")
                return False, None
        else:
            return self.cap.read()
