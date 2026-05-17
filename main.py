import cv2
import time
import threading
from ultralytics import YOLO
from servo_controller import ServoController

# ==========================================
# GLOBAL VARIABLES
# ==========================================

latest_frame = None
running = True
servo = None
selected_drop_angle = 90  # Default drop angle


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
# SERVO CONTROL THREAD
# ==========================================

def servo_control_worker():
    """
    Runs servo operations in background thread
    Prevents blocking the main YOLO detection loop
    """
    global servo, selected_drop_angle
    
    servo = ServoController(gpio_pin=17)
    servo.move_to_angle(90)  # Home position


# ==========================================
# DRAW PICKUP ZONE
# ==========================================

def draw_pickup_zone(frame, width=640, height=480):
    """
    Draw the pickup zone (15° position indicator) on the frame
    Objects should be aligned to this zone before pickup
    """
    # Define pickup zone (center region)
    zone_width = 150
    zone_height = 150
    
    x_start = (width - zone_width) // 2
    y_start = (height - zone_height) // 2
    x_end = x_start + zone_width
    y_end = y_start + zone_height
    
    # Draw green rectangle for pickup zone
    cv2.rectangle(
        frame,
        (x_start, y_start),
        (x_end, y_end),
        (0, 255, 0),  # Green
        2
    )
    
    # Draw center crosshair
    center_x = width // 2
    center_y = height // 2
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 2)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 2)
    
    # Label
    cv2.putText(
        frame,
        "PICKUP ZONE (15 deg)",
        (x_start, y_start - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )
    
    return frame


# ==========================================
# DRAW STATUS INFO
# ==========================================

def draw_status(frame, fps, drop_angle, servo_state="Ready"):
    """
    Draw status information on the frame
    """
    # FPS
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )
    
    # Drop angle
    cv2.putText(
        frame,
        f"Drop Angle: {drop_angle}deg",
        (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 165, 0),
        2
    )
    
    # Servo state
    cv2.putText(
        frame,
        f"Servo: {servo_state}",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 165, 255),
        2
    )
    
    # Instructions
    cv2.putText(
        frame,
        "Press: 1(45) 2(90) 3(135) 4(180) | P=Pickup | Q=Quit",
        (10, frame.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (200, 200, 200),
        1
    )
    
    return frame


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    global latest_frame, running, servo, selected_drop_angle

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

    camera_thread = threading.Thread(
        target=camera_capture,
        args=(cap,)
    )

    camera_thread.daemon = True
    camera_thread.start()

    # ==========================================
    # INITIALIZE SERVO
    # ==========================================

    print("Initializing servo controller...")
    servo_thread = threading.Thread(target=servo_control_worker)
    servo_thread.daemon = True
    servo_thread.start()
    time.sleep(2)  # Wait for servo initialization

    print("====================================")
    print("PICK & PLACE SYSTEM STARTED")
    print("====================================")
    print("Controls:")
    print("  1 = Drop angle 45°")
    print("  2 = Drop angle 90°")
    print("  3 = Drop angle 135°")
    print("  4 = Drop angle 180°")
    print("  P = Execute pick & place")
    print("  Q = Quit")
    print("====================================\n")

    prev_time = time.time()
    servo_busy = False

    # ==========================================
    # MAIN LOOP
    # ==========================================

    while True:

        # Wait until frame available
        if latest_frame is None:
            continue

        # Copy latest frame
        frame = latest_frame.copy()
        height, width = frame.shape[:2]

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
        # DRAW PICKUP ZONE
        # ==========================================

        annotated_frame = draw_pickup_zone(annotated_frame, width, height)

        # ==========================================
        # FPS CALCULATION
        # ==========================================

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # ==========================================
        # DRAW STATUS
        # ==========================================

        servo_state = "Busy" if servo_busy else "Ready"
        annotated_frame = draw_status(annotated_frame, fps, selected_drop_angle, servo_state)

        # ==========================================
        # SHOW FRAME
        # ==========================================

        cv2.imshow(
            "Raspberry Pi - Pick & Place System",
            annotated_frame
        )

        # ==========================================
        # KEYBOARD INPUT HANDLING
        # ==========================================

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            # Quit
            running = False
            break

        elif key == ord('p') or key == ord('P'):
            # Pick and place
            if servo and not servo_busy:
                print(f"\n>>> Executing pick & place to {selected_drop_angle}°...")
                servo_busy = True
                
                # Execute in background thread
                pick_thread = threading.Thread(
                    target=servo.execute_pick_and_place,
                    args=(selected_drop_angle,)
                )
                pick_thread.daemon = True
                pick_thread.start()
                
                servo_busy = False

        elif key == ord('1'):
            # Set drop angle to 45°
            selected_drop_angle = 45
            print(f">>> Drop angle set to {selected_drop_angle}°")

        elif key == ord('2'):
            # Set drop angle to 90°
            selected_drop_angle = 90
            print(f">>> Drop angle set to {selected_drop_angle}°")

        elif key == ord('3'):
            # Set drop angle to 135°
            selected_drop_angle = 135
            print(f">>> Drop angle set to {selected_drop_angle}°")

        elif key == ord('4'):
            # Set drop angle to 180°
            selected_drop_angle = 180
            print(f">>> Drop angle set to {selected_drop_angle}°")

    # ==========================================
    # CLEANUP
    # ==========================================

    running = False
    
    if servo:
        servo.cleanup()

    cap.release()
    cv2.destroyAllWindows()

    print("\nProgram stopped")


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()
