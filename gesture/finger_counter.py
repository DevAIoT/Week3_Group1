"""Count extended fingers from YOLO11 hand keypoints."""

# Keypoint indices (same as MediaPipe hand landmarks)
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


def count_fingers(keypoints, handedness_label):
    """Count extended fingers (0-5) given keypoints and handedness ("Left"/"Right").

    Args:
        keypoints: Numpy array of shape [21, 3] with normalized x, y, confidence.
        handedness_label: "Left" or "Right" handedness label.

    Returns:
        int: Number of extended fingers (0-5).
    """
    if keypoints is None or len(keypoints) < 21:
        return 0

    count = 0

    # Thumb: compare tip x vs IP joint x.
    # For a "Right" hand, thumb extends toward lower x.
    # For a "Left" hand, thumb extends toward higher x.
    if handedness_label == "Right":
        if keypoints[THUMB_TIP, 0] < keypoints[THUMB_IP, 0]:
            count += 1
    else:
        if keypoints[THUMB_TIP, 0] > keypoints[THUMB_IP, 0]:
            count += 1

    # Other four fingers: tip above PIP means extended (lower y = higher in frame).
    for tip, pip_ in [(INDEX_TIP, INDEX_PIP),
                      (MIDDLE_TIP, MIDDLE_PIP),
                      (RING_TIP, RING_PIP),
                      (PINKY_TIP, PINKY_PIP)]:
        if keypoints[tip, 1] < keypoints[pip_, 1]:
            count += 1

    return count
