"""Tests for gesture.stabilizer — no hardware needed."""

import time
import unittest
from unittest.mock import patch

from gesture.stabilizer import GestureStabilizer


class TestGestureStabilizer(unittest.TestCase):

    def test_accepts_after_required_frames(self):
        stab = GestureStabilizer(required_frames=5, cooldown_seconds=0)
        for _ in range(4):
            result = stab.update(3)
            self.assertIsNone(result)
        result = stab.update(3)
        self.assertEqual(result, 3)

    def test_resets_on_different_value(self):
        stab = GestureStabilizer(required_frames=5, cooldown_seconds=0)
        for _ in range(3):
            stab.update(2)
        # Switch value — should reset counter
        stab.update(4)  # frame 1 of value 4
        for _ in range(3):
            result = stab.update(4)  # frames 2, 3, 4
            self.assertIsNone(result)
        # 5th frame of value 4 should trigger acceptance
        result = stab.update(4)
        self.assertEqual(result, 4)

    def test_ignores_zero(self):
        stab = GestureStabilizer(required_frames=3, cooldown_seconds=0)
        for _ in range(10):
            result = stab.update(0)
            self.assertIsNone(result)
        self.assertEqual(stab.pending_progress, 0.0)

    def test_ignores_out_of_range(self):
        stab = GestureStabilizer(required_frames=3, cooldown_seconds=0)
        self.assertIsNone(stab.update(6))
        self.assertIsNone(stab.update(-1))

    def test_cooldown_blocks_second_rating(self):
        stab = GestureStabilizer(required_frames=2, cooldown_seconds=10.0)
        stab.update(1)
        stab.update(1)  # accepted
        # Immediately try another rating — should be blocked by cooldown
        for _ in range(5):
            result = stab.update(2)
            self.assertIsNone(result)

    def test_cooldown_allows_after_expiry(self):
        stab = GestureStabilizer(required_frames=2, cooldown_seconds=0.1)
        stab.update(1)
        stab.update(1)  # accepted
        time.sleep(0.15)
        stab.update(3)
        result = stab.update(3)
        self.assertEqual(result, 3)

    def test_progress_increases(self):
        stab = GestureStabilizer(required_frames=4, cooldown_seconds=0)
        self.assertEqual(stab.pending_progress, 0.0)
        stab.update(2)
        self.assertAlmostEqual(stab.pending_progress, 0.25)
        stab.update(2)
        self.assertAlmostEqual(stab.pending_progress, 0.5)

    def test_pending_value(self):
        stab = GestureStabilizer(required_frames=5, cooldown_seconds=0)
        self.assertIsNone(stab.pending_value)
        stab.update(4)
        self.assertEqual(stab.pending_value, 4)

    def test_boundary_values(self):
        stab = GestureStabilizer(required_frames=1, cooldown_seconds=0)
        self.assertEqual(stab.update(1), 1)
        stab2 = GestureStabilizer(required_frames=1, cooldown_seconds=0)
        self.assertEqual(stab2.update(5), 5)


if __name__ == "__main__":
    unittest.main()
