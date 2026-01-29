"""Count extended fingers from MediaPipe hand landmarks."""

# Landmark indices
THUMB_TIP = 4
THUMB_IP = 3
INDEX_TIP = 8
INDEX_PIP = 6
MIDDLE_TIP = 12
MIDDLE_PIP = 10
RING_TIP = 16
RING_PIP = 14
PINKY_TIP = 20
PINKY_PIP = 18


def count_fingers(hand_landmarks, handedness_label):
    """Count extended fingers (0-5) given landmarks and handedness ("Left"/"Right").

    Args:
        hand_landmarks: MediaPipe NormalizedLandmarkList with 21 landmarks.
        handedness_label: "Left" or "Right" as reported by MediaPipe
            (note: MediaPipe mirrors, so "Right" means the viewer's right).

    Returns:
        int: Number of extended fingers (0-5).
    """
    lm = hand_landmarks.landmark
    count = 0

    # Thumb: compare tip x vs IP joint x.
    # MediaPipe reports handedness from the camera's perspective (mirrored).
    # For a "Right" hand label (user's left), thumb extends toward lower x.
    # For a "Left" hand label (user's right), thumb extends toward higher x.
    if handedness_label == "Right":
        if lm[THUMB_TIP].x < lm[THUMB_IP].x:
            count += 1
    else:
        if lm[THUMB_TIP].x > lm[THUMB_IP].x:
            count += 1

    # Other four fingers: tip above PIP means extended (lower y = higher in frame).
    for tip, pip_ in [(INDEX_TIP, INDEX_PIP),
                      (MIDDLE_TIP, MIDDLE_PIP),
                      (RING_TIP, RING_PIP),
                      (PINKY_TIP, PINKY_PIP)]:
        if lm[tip].y < lm[pip_].y:
            count += 1

    return count
