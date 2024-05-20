import cv2
import numpy as np
import subprocess

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
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Try using V4L2 backend

    if not cap.isOpened():
        print("Error: Could not open video capture")
        return

    # Get the width and height of the frame
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the FFmpeg command
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{frame_width}x{frame_height}',  # Size of one frame
        '-pix_fmt', 'bgr24',
        '-r', '20',  # Frames per second
        '-i', '-',  # Input comes from a pipe
        '-an',  # No audio
        '-vcodec', 'mpeg4',
        'output.mp4'
    ]

    # Open a pipe to the FFmpeg process
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        shapes = detect_shapes(frame)

        for shape, contour in shapes:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, shape, (contour[0][0][0], contour[0][0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Write the frame to the FFmpeg process
        process.stdin.write(frame.tobytes())

        cv2.imshow("Shapes Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    process.stdin.close()
    process.wait()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
