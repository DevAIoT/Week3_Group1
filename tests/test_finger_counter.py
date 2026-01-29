"""Tests for gesture.finger_counter — no camera or YOLO runtime needed."""

import unittest
import numpy as np

from gesture.finger_counter import count_fingers


def _make_keypoints(positions):
    """Create a mock keypoints array from a dict of {index: (x, y, confidence)}."""
    keypoints = np.full((21, 3), [0.5, 0.5, 1.0])
    for idx, (x, y, conf) in positions.items():
        keypoints[idx] = [x, y, conf]
    return keypoints


class TestFingerCounter(unittest.TestCase):

    def test_closed_fist_returns_zero(self):
        # All tips below their PIP joints (higher y = lower in frame)
        kpts = _make_keypoints({
            4: (0.5, 0.6, 1.0), 3: (0.5, 0.5, 1.0),   # thumb tip below IP
            8: (0.5, 0.7, 1.0), 6: (0.5, 0.5, 1.0),    # index tip below PIP
            12: (0.5, 0.7, 1.0), 10: (0.5, 0.5, 1.0),   # middle
            16: (0.5, 0.7, 1.0), 14: (0.5, 0.5, 1.0),   # ring
            20: (0.5, 0.7, 1.0), 18: (0.5, 0.5, 1.0),   # pinky
        })
        self.assertEqual(count_fingers(kpts, "Right"), 0)

    def test_one_finger_index(self):
        kpts = _make_keypoints({
            4: (0.5, 0.6, 1.0), 3: (0.5, 0.5, 1.0),
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),     # index extended
            12: (0.5, 0.7, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.7, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.7, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Right"), 1)

    def test_two_fingers(self):
        kpts = _make_keypoints({
            4: (0.5, 0.6, 1.0), 3: (0.5, 0.5, 1.0),
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.2, 1.0), 10: (0.5, 0.5, 1.0),   # middle extended
            16: (0.5, 0.7, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.7, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Right"), 2)

    def test_three_fingers(self):
        kpts = _make_keypoints({
            4: (0.5, 0.6, 1.0), 3: (0.5, 0.5, 1.0),
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.2, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.2, 1.0), 14: (0.5, 0.5, 1.0),   # ring extended
            20: (0.5, 0.7, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Right"), 3)

    def test_four_fingers(self):
        kpts = _make_keypoints({
            4: (0.5, 0.6, 1.0), 3: (0.5, 0.5, 1.0),
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.2, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.2, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.2, 1.0), 18: (0.5, 0.5, 1.0),   # pinky extended
        })
        self.assertEqual(count_fingers(kpts, "Right"), 4)

    def test_five_fingers_right_hand(self):
        # All extended including thumb (Right label → tip.x < IP.x)
        kpts = _make_keypoints({
            4: (0.3, 0.5, 1.0), 3: (0.5, 0.5, 1.0),     # thumb tip left of IP
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.2, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.2, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.2, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Right"), 5)

    def test_five_fingers_left_hand(self):
        # Left label → thumb tip.x > IP.x
        kpts = _make_keypoints({
            4: (0.7, 0.5, 1.0), 3: (0.5, 0.5, 1.0),     # thumb tip right of IP
            8: (0.5, 0.2, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.2, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.2, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.2, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Left"), 5)

    def test_thumb_only_right(self):
        kpts = _make_keypoints({
            4: (0.3, 0.5, 1.0), 3: (0.5, 0.5, 1.0),
            8: (0.5, 0.7, 1.0), 6: (0.5, 0.5, 1.0),
            12: (0.5, 0.7, 1.0), 10: (0.5, 0.5, 1.0),
            16: (0.5, 0.7, 1.0), 14: (0.5, 0.5, 1.0),
            20: (0.5, 0.7, 1.0), 18: (0.5, 0.5, 1.0),
        })
        self.assertEqual(count_fingers(kpts, "Right"), 1)


if __name__ == "__main__":
    unittest.main()
