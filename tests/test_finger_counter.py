"""Tests for gesture.finger_counter — no camera or MediaPipe runtime needed."""

import unittest
from types import SimpleNamespace

from gesture.finger_counter import count_fingers


def _make_landmarks(positions):
    """Create a mock hand_landmarks object from a dict of {index: (x, y, z)}."""
    landmarks = [SimpleNamespace(x=0.5, y=0.5, z=0.0) for _ in range(21)]
    for idx, (x, y, z) in positions.items():
        landmarks[idx] = SimpleNamespace(x=x, y=y, z=z)
    lm = SimpleNamespace(landmark=landmarks)
    return lm


class TestFingerCounter(unittest.TestCase):

    def test_closed_fist_returns_zero(self):
        # All tips below their PIP joints (higher y = lower in frame)
        lm = _make_landmarks({
            4: (0.5, 0.6, 0), 3: (0.5, 0.5, 0),   # thumb tip below IP
            8: (0.5, 0.7, 0), 6: (0.5, 0.5, 0),    # index tip below PIP
            12: (0.5, 0.7, 0), 10: (0.5, 0.5, 0),   # middle
            16: (0.5, 0.7, 0), 14: (0.5, 0.5, 0),   # ring
            20: (0.5, 0.7, 0), 18: (0.5, 0.5, 0),   # pinky
        })
        self.assertEqual(count_fingers(lm, "Right"), 0)

    def test_one_finger_index(self):
        lm = _make_landmarks({
            4: (0.5, 0.6, 0), 3: (0.5, 0.5, 0),
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),     # index extended
            12: (0.5, 0.7, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.7, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.7, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Right"), 1)

    def test_two_fingers(self):
        lm = _make_landmarks({
            4: (0.5, 0.6, 0), 3: (0.5, 0.5, 0),
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.2, 0), 10: (0.5, 0.5, 0),   # middle extended
            16: (0.5, 0.7, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.7, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Right"), 2)

    def test_three_fingers(self):
        lm = _make_landmarks({
            4: (0.5, 0.6, 0), 3: (0.5, 0.5, 0),
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.2, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.2, 0), 14: (0.5, 0.5, 0),   # ring extended
            20: (0.5, 0.7, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Right"), 3)

    def test_four_fingers(self):
        lm = _make_landmarks({
            4: (0.5, 0.6, 0), 3: (0.5, 0.5, 0),
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.2, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.2, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.2, 0), 18: (0.5, 0.5, 0),   # pinky extended
        })
        self.assertEqual(count_fingers(lm, "Right"), 4)

    def test_five_fingers_right_hand(self):
        # All extended including thumb (Right label → tip.x < IP.x)
        lm = _make_landmarks({
            4: (0.3, 0.5, 0), 3: (0.5, 0.5, 0),     # thumb tip left of IP
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.2, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.2, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.2, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Right"), 5)

    def test_five_fingers_left_hand(self):
        # Left label → thumb tip.x > IP.x
        lm = _make_landmarks({
            4: (0.7, 0.5, 0), 3: (0.5, 0.5, 0),     # thumb tip right of IP
            8: (0.5, 0.2, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.2, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.2, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.2, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Left"), 5)

    def test_thumb_only_right(self):
        lm = _make_landmarks({
            4: (0.3, 0.5, 0), 3: (0.5, 0.5, 0),
            8: (0.5, 0.7, 0), 6: (0.5, 0.5, 0),
            12: (0.5, 0.7, 0), 10: (0.5, 0.5, 0),
            16: (0.5, 0.7, 0), 14: (0.5, 0.5, 0),
            20: (0.5, 0.7, 0), 18: (0.5, 0.5, 0),
        })
        self.assertEqual(count_fingers(lm, "Right"), 1)


if __name__ == "__main__":
    unittest.main()
