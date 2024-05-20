import cv2
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

def detect_shapes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_shapes = []

    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * perimeter, True)
        num_sides = len(approx)

        shape = "unidentified"

        if num_sides == 3:
            shape = "triangle"
        elif num_sides == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            shape = "square" if aspect_ratio >= 0.95 and aspect_ratio <= 1.05 else "rectangle"
        elif num_sides == 5:
            shape = "pentagon"
        else:
            shape = "circle"

        detected_shapes.append((shape, contour))

    return detected_shapes

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    with pyvirtualcam.Camera(width=640, height=480, fps=30, device='/dev/video1', fmt=PixelFormat.BGR) as cam:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            shapes = detect_shapes(frame)

            for shape, contour in shapes:
                cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                cv2.putText(frame, shape, (contour[0][0][0], contour[0][0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cam.send(frame)
            cam.sleep_until_next_frame()

if __name__ == "__main__":
    main()
