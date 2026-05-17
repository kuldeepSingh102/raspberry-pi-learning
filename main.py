import cv2
import time
import threading
from ultralytics import YOLO

# ==========================================
# GLOBAL VARIABLES
# ==========================================

latest_frame = None
running = True


# ==========================================
# CAMERA THREAD
# ==========================================

def camera_capture(cap):

    global latest_frame, running

    while running:

        ret, frame = cap.read()

        if ret:
            latest_frame = frame


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    global latest_frame, running

    # ==========================================
    # LOAD YOLO MODEL
    # ==========================================

    model = YOLO("best.pt")

    # ==========================================
    # OPEN CAMERA
    # ==========================================

    print("Opening webcam...")

    # Try camera index 0
    cap = cv2.VideoCapture(0)

    # Fallback to camera index 1
    if not cap.isOpened():

        print("Trying camera index 1...")
        cap = cv2.VideoCapture(1)

    # If still failed
    if not cap.isOpened():

        print("Cannot open webcam")
        return

    print("Webcam opened successfully")

    # ==========================================
    # LOW LATENCY CAMERA SETTINGS
    # ==========================================

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # MJPEG mode for lower latency
    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*'MJPG')
    )

    # ==========================================
    # START CAMERA THREAD
    # ==========================================

    thread = threading.Thread(
        target=camera_capture,
        args=(cap,)
    )

    thread.daemon = True
    thread.start()

    print("====================================")
    print("YOLO Detection Started")
    print("Press 'q' to quit")
    print("====================================")

    prev_time = time.time()

    # ==========================================
    # MAIN LOOP
    # ==========================================

    while True:

        # Wait until frame available
        if latest_frame is None:
            continue

        # Copy latest frame
        frame = latest_frame.copy()

        # ==========================================
        # YOLO INFERENCE
        # ==========================================

        results = model(
            frame,
            imgsz=320,
            conf=0.5,
            half=True,
            verbose=False
        )

        # Get annotated frame
        annotated_frame = results[0].plot()

        # ==========================================
        # FPS CALCULATION
        # ==========================================

        current_time = time.time()

        fps = 1 / (current_time - prev_time)

        prev_time = current_time

        # Draw FPS
        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # ==========================================
        # SHOW FRAME
        # ==========================================

        cv2.imshow(
            "Raspberry Pi 5 - YOLO Detection",
            annotated_frame
        )

        # ==========================================
        # EXIT CONDITION
        # ==========================================

        if cv2.waitKey(1) & 0xFF == ord('q'):

            running = False
            break

    # ==========================================
    # CLEANUP
    # ==========================================

    cap.release()

    cv2.destroyAllWindows()

    print("Program stopped")


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()
