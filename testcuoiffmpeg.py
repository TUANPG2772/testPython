import cv2
import numpy as np

# Hàm nhận diện hình dạng vật thể
def detect_object_shape(image):
    # Chuyển đổi ảnh sang ảnh xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Làm mờ ảnh
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Phát hiện biên cạnh
    edges = cv2.Canny(blurred, 50, 150)

    # Tìm contours trong ảnh
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_objects = []

    # Duyệt qua từng contour để xác định hình dạng
    for contour in contours:
        # Xác định đường viền của contour
        peri = cv2.arcLength(contour, True)
        # Xấp xỉ contour bằng các đoạn thẳng
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        # Xác định hình dạng
        if len(approx) == 3:
            shape = "triangle"
        elif len(approx) == 4:
            shape = "rectangle"
        elif len(approx) == 5:
            shape = "pentagon"
        else:
            shape = "circle"

        # Thêm hình dạng và contour tương ứng vào danh sách
        detected_objects.append((shape, contour))

    return detected_objects

# Mở video capture từ camera với giao thức CAP_V4L2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open video capture")
else:
    # Điều chỉnh các tham số như độ phân giải, FPS, và codec
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    while True:
        # Đọc frame từ video capture
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Nhận diện hình dạng vật thể trên frame
        objects = detect_object_shape(frame)

        # Vẽ đường contour và ghi nhãn hình dáng lên frame
        for shape, contour in objects:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, shape, (contour[0][0][0], contour[0][0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Hiển thị frame
        cv2.imshow("Frame", frame)

        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng video capture và đóng cửa sổ hiển thị
    cap.release()
    cv2.destroyAllWindows()
