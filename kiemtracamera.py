import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("Error: Could not open video capture")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
