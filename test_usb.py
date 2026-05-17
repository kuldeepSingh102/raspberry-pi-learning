import cv2

for i in range(5):

    print(f"\nTesting camera index {i}")

    cap = cv2.VideoCapture(i)

    if not cap.isOpened():
        print("Cannot open")
        continue

    ret, frame = cap.read()

    if not ret:
        print("Opened but cannot read frame")
        cap.release()
        continue

    print(f"WORKING CAMERA FOUND AT INDEX {i}")

    cv2.imshow(f"Camera {i}", frame)

    cv2.waitKey(3000)

    cap.release()

cv2.destroyAllWindows()
