import sys
import cv2


class Camera:
    """OpenCV camera wrapper with context manager support."""

    def __init__(self, index=0, width=640, height=480):
        self.index = index
        self.width = width
        self.height = height
        self.cap = None

    def __enter__(self):
        # Try multiple backends for Raspberry Pi camera support
        if sys.platform == "linux":
            # First try V4L2 (for USB cameras or legacy setup)
            self.cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)

            # If V4L2 fails, try GStreamer pipeline for libcamera (Pi Camera Module)
            if not self.cap.isOpened():
                print(f"V4L2 failed, trying libcamera via GStreamer...")
                gst_pipeline = (
                    f"libcamerasrc ! "
                    f"video/x-raw,width={self.width},height={self.height},framerate=30/1 ! "
                    f"videoconvert ! appsink"
                )
                self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

            # If both fail, try ANY backend as fallback
            if not self.cap.isOpened():
                print(f"GStreamer failed, trying CAP_ANY...")
                self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)
        else:
            self.cap = cv2.VideoCapture(self.index, cv2.CAP_ANY)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cap:
            self.cap.release()
        return False

    def read(self):
        """Read a frame. Returns (success, frame_bgr)."""
        return self.cap.read()
