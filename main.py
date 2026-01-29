"""GestureRating — Hand gesture rating capture with REST API."""

import signal
import threading

import cv2
from flask_socketio import SocketIO

import config
from gesture.camera import Camera
from gesture.detector import HandDetector
from gesture.finger_counter import count_fingers
from gesture.stabilizer import GestureStabilizer
from ratings.database import RatingsDatabase
from ratings.api import create_app


def start_api(db):
    """Run Flask API with WebSocket support in a daemon thread."""
    app = create_app(db)
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    db.set_socketio(socketio)  # Allow DB to emit events
    socketio.run(app, host=config.API_HOST, port=config.API_PORT, allow_unsafe_werkzeug=True, use_reloader=False)


def draw_overlay(frame, finger_count, stabilizer, last_accepted):
    """Draw detection info, progress bar, and accepted rating on the frame."""
    h, w = frame.shape[:2]

    # Current detected count
    text = f"Fingers: {finger_count}" if finger_count is not None else "No hand"
    cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                (0, 255, 0), 2)

    # Progress bar
    progress = stabilizer.pending_progress
    if progress > 0:
        bar_w = int(w * 0.6)
        bar_x = (w - bar_w) // 2
        bar_y = h - 50
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 25),
                      (100, 100, 100), -1)
        fill_w = int(bar_w * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + 25),
                      (0, 200, 0), -1)
        cv2.putText(frame, f"Hold: {stabilizer.pending_value}",
                    (bar_x, bar_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 1)

    # Flash accepted rating
    if last_accepted is not None:
        cv2.putText(frame, f"Rating accepted: {last_accepted}",
                    (w // 2 - 150, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    (0, 0, 255), 3)


def main():
    db = RatingsDatabase(config.DB_PATH)

    # Start Flask API in background daemon thread
    api_thread = threading.Thread(target=start_api, args=(db,), daemon=True)
    api_thread.start()
    print(f"API running at http://{config.API_HOST}:{config.API_PORT}")

    detector = HandDetector(
        model_complexity=config.MP_MODEL_COMPLEXITY,
        max_hands=config.MP_MAX_NUM_HANDS,
        min_detection_confidence=config.MP_MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MP_MIN_TRACKING_CONFIDENCE,
    )
    stabilizer = GestureStabilizer(
        required_frames=config.STABILIZE_FRAMES,
        cooldown_seconds=config.COOLDOWN_SECONDS,
    )

    last_accepted = None
    accepted_frame_counter = 0

    # Allow clean shutdown with Ctrl+C
    shutdown = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: shutdown.set())

    with Camera(config.CAMERA_INDEX, config.CAMERA_WIDTH, config.CAMERA_HEIGHT) as cam:
        print("Camera opened. Press 'q' to quit.")
        while not shutdown.is_set():
            ok, frame = cam.read()
            if not ok:
                print("Failed to read frame.")
                break

            landmarks_list, handedness_list = detector.process(frame)

            finger_count = None
            if landmarks_list and handedness_list:
                hand_lm = landmarks_list[0]
                label = handedness_list[0].classification[0].label
                finger_count = count_fingers(hand_lm, label)

                accepted = stabilizer.update(finger_count)
                if accepted is not None:
                    db.insert(accepted, source="gesture")
                    print(f"Rating accepted: {accepted}")
                    last_accepted = accepted
                    accepted_frame_counter = 30  # Show for ~30 frames
            else:
                stabilizer.update(0)

            # Clear flash after display period
            if accepted_frame_counter > 0:
                accepted_frame_counter -= 1
            else:
                last_accepted = None

            detector.draw_landmarks(frame, landmarks_list)
            draw_overlay(frame, finger_count, stabilizer, last_accepted)

            cv2.imshow("GestureRating", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    detector.close()
    db.close()
    cv2.destroyAllWindows()
    print("Shutdown complete.")


if __name__ == "__main__":
    main()
