import cv2
import numpy as np
from ultralytics import YOLO


class HandDetector:
    """YOLO11 Hand Pose wrapper for hand landmark detection."""

    def __init__(self, model_path='yolo11n-pose.pt', confidence=0.7, iou=0.5):
        """
        Initialize YOLO11 hand pose detector.

        Args:
            model_path: Path to YOLO11 pose model (default uses pretrained nano model)
            confidence: Minimum detection confidence threshold
            iou: IoU threshold for NMS
        """
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.iou = iou

        # YOLO hand keypoints connection pairs (21 keypoints, same as MediaPipe)
        self.hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # Index
            (0, 9), (9, 10), (10, 11), (11, 12),   # Middle
            (0, 13), (13, 14), (14, 15), (15, 16), # Ring
            (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (5, 9), (9, 13), (13, 17)              # Palm connections
        ]

    def process(self, frame_bgr):
        """
        Process a BGR frame and return (keypoints_list, handedness_list) or (None, None).

        Returns:
            keypoints_list: List of normalized keypoint arrays (shape: [21, 3] with x, y, confidence)
            handedness_list: List of handedness labels ("Left" or "Right")
        """
        results = self.model.predict(
            frame_bgr,
            conf=self.confidence,
            iou=self.iou,
            verbose=False,
            show=False
        )

        if len(results) == 0 or results[0].keypoints is None:
            return None, None

        keypoints_data = results[0].keypoints

        if keypoints_data.xy is None or len(keypoints_data.xy) == 0:
            return None, None

        # Extract keypoints and normalize to 0-1 range
        h, w = frame_bgr.shape[:2]
        keypoints_list = []
        handedness_list = []

        # Process first detection only (max_hands=1)
        kpts = keypoints_data.xy[0].cpu().numpy()  # Shape: [num_keypoints, 2]
        conf = keypoints_data.conf[0].cpu().numpy() if keypoints_data.conf is not None else np.ones(len(kpts))

        # Normalize keypoints to 0-1 range
        normalized_kpts = np.zeros((len(kpts), 3))
        normalized_kpts[:, 0] = kpts[:, 0] / w  # x normalized
        normalized_kpts[:, 1] = kpts[:, 1] / h  # y normalized
        normalized_kpts[:, 2] = conf            # confidence

        keypoints_list.append(normalized_kpts)

        # Determine handedness based on wrist (0) and thumb positions (1-4)
        # If thumb is on left side of wrist, it's left hand, else right hand
        wrist_x = normalized_kpts[0, 0]
        thumb_tip_x = normalized_kpts[4, 0]
        handedness = "Left" if thumb_tip_x > wrist_x else "Right"
        handedness_list.append(handedness)

        return keypoints_list, handedness_list

    def draw_landmarks(self, frame_bgr, keypoints_list):
        """Draw hand landmarks on the frame (modifies in place)."""
        if not keypoints_list:
            return

        h, w = frame_bgr.shape[:2]

        for keypoints in keypoints_list:
            # Draw connections
            for start_idx, end_idx in self.hand_connections:
                if start_idx < len(keypoints) and end_idx < len(keypoints):
                    start_point = (int(keypoints[start_idx, 0] * w),
                                 int(keypoints[start_idx, 1] * h))
                    end_point = (int(keypoints[end_idx, 0] * w),
                               int(keypoints[end_idx, 1] * h))
                    cv2.line(frame_bgr, start_point, end_point, (0, 255, 0), 2)

            # Draw keypoints
            for kpt in keypoints:
                x, y, conf = kpt
                if conf > 0.5:  # Only draw confident keypoints
                    center = (int(x * w), int(y * h))
                    cv2.circle(frame_bgr, center, 4, (0, 0, 255), -1)

    def close(self):
        """Cleanup resources."""
        pass
