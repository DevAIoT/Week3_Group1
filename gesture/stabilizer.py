"""Stabilize finger count readings to avoid jittery/accidental ratings."""

import time


class GestureStabilizer:
    """Require N consecutive identical readings (1-5) before accepting a rating.

    Enforces a cooldown period between accepted ratings.
    """

    def __init__(self, required_frames=10, cooldown_seconds=3.0):
        self.required_frames = required_frames
        self.cooldown_seconds = cooldown_seconds

        self._candidate = None
        self._consecutive = 0
        self._last_accepted_time = 0.0

    def update(self, finger_count):
        """Feed a new finger count reading.

        Args:
            finger_count: int 0-5 from the finger counter.

        Returns:
            int or None: The accepted rating (1-5) if stabilization threshold
            was just reached, otherwise None.
        """
        # Ignore 0 (no gesture / closed fist)
        if finger_count < 1 or finger_count > 5:
            self._candidate = None
            self._consecutive = 0
            return None

        # Check cooldown
        now = time.monotonic()
        if now - self._last_accepted_time < self.cooldown_seconds:
            return None

        # Track consecutive identical readings
        if finger_count == self._candidate:
            self._consecutive += 1
        else:
            self._candidate = finger_count
            self._consecutive = 1

        # Accept if threshold reached
        if self._consecutive >= self.required_frames:
            self._last_accepted_time = now
            accepted = self._candidate
            self._candidate = None
            self._consecutive = 0
            return accepted

        return None

    @property
    def pending_progress(self):
        """Progress toward acceptance (0.0 to 1.0). Useful for UI display."""
        if self._candidate is None:
            return 0.0
        return min(self._consecutive / self.required_frames, 1.0)

    @property
    def pending_value(self):
        """The current candidate value, or None if no candidate."""
        return self._candidate
