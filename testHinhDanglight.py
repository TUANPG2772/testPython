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

# Hàm nhận diện bóng đèn
def detect_lights(image):
    # Chuyển đổi ảnh sang ảnh xám
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Áp dụng ngưỡng để phát hiện các vùng sáng
    _, bright_areas = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)

    # Tìm contours trong các vùng sáng
    contours, _ = cv2.findContours(bright_areas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    light_objects = []

    # Duyệt qua từng contour để xác định các vùng sáng có hình dạng đặc biệt
    for contour in contours:
        # Xác định đường viền của contour
        peri = cv2.arcLength(contour, True)
        # Xấp xỉ contour bằng các đoạn thẳng
        approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

        # Xác định hình dạng
        if len(approx) in [3, 4, 5] or len(approx) > 5:
            light_objects.append(contour)

    return light_objects

# Mở video capture từ camera với giao thức CAP_V4L2
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open video capture")
else:
    # Điều chỉnh các tham số như độ phân giải, FPS, và codec
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 680)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 680)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    # Tạo cửa sổ
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)

    while True:
        # Đọc frame từ video capture
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        # Nhận diện bóng đèn trên frame
        lights = detect_lights(frame)

        # Vẽ đường contour và ghi nhãn lên frame
        for idx, contour in enumerate(lights):
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, f"light {idx+1}", (contour[0][0][0], contour[0][0][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Hiển thị frame
        cv2.imshow("Frame", frame)

        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng video capture và đóng cửa sổ hiển thị
    cap.release()
    cv2.destroyAllWindows()
