import cv2
import mediapipe as mp


class HandDetector:
    """MediaPipe Hands wrapper for hand landmark detection."""

    def __init__(self, model_complexity=0, max_hands=1,
                 min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            model_complexity=model_complexity,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

    def process(self, frame_bgr):
        """Process a BGR frame and return (landmarks_list, handedness_list) or (None, None)."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks and results.multi_handedness:
            return results.multi_hand_landmarks, results.multi_handedness
        return None, None

    def draw_landmarks(self, frame_bgr, landmarks_list):
        """Draw hand landmarks on the frame (modifies in place)."""
        if landmarks_list:
            for hand_landmarks in landmarks_list:
                self.mp_draw.draw_landmarks(
                    frame_bgr, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def close(self):
        self.hands.close()
