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
        backend = cv2.CAP_V4L2 if sys.platform == "linux" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(self.index, backend)
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
