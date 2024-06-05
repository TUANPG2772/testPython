import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QTextCursor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flash Signal Receiver")

        # Initialize labels to display camera image and decoded signal
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(10, 10, 640, 480)
        self.signal_label = QLabel("Binary Signal: ", self)
        self.signal_label.setGeometry(10, 500, 640, 30)
        self.source_label = QLabel("Searching for flash signal source...", self)
        self.source_label.setGeometry(10, 550, 640, 30)

        # Initialize text edit to display history
        self.history_edit = QTextEdit(self)
        self.history_edit.setGeometry(10, 580, 640, 100)
        self.history_edit.setReadOnly(True)

        # Initialize timer to update the camera image
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # Frame update frequency in ms

        # Initialize camera
        self.cap = cv2.VideoCapture(0)

        # Variables for flash signal detection
        self.prev_avg_intensity = None
        self.threshold = 20  # Adjusted intensity change threshold for better sensitivity
        self.binary_signal = ""
        self.blink_count = 0
        self.blink_detected = False
        self.ready_for_signal = False
        self.frames_after_blink = 0
        self.history = ""
        self.waiting_for_signal = False
        self.signal_start_time = None

        # For tracking multiple flash sources
        self.flash_sources = {}

    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            # Display the frame from the camera
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(q_img))

            # Detect flashes in the whole frame
            self.detect_flash_sources(frame)

    def detect_flash_sources(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 2)  # Increase kernel size to reduce noise
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                   param1=100, param2=30, minRadius=10, maxRadius=100)

        current_sources = {}

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # Extract the region of interest (ROI)
                roi = frame[y-r:y+r, x-r:x+r]

                # Calculate the average intensity of the ROI
                avg_intensity = np.mean(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))

                # Check if the average intensity is above a certain threshold
                if avg_intensity > 240:  # Threshold for high intensity
                    source_id = self.get_source_id(x, y, r)
                    if source_id not in current_sources:
                        current_sources[source_id] = {"position": (x, y, r), "binary_signal": "", "prev_avg_intensity": None}
                    else:
                        current_sources[source_id]["position"] = (x, y, r)

                    # Detect flash signal
                    is_flash_detected = self.detect_flash_signal(roi, source_id)

                    if is_flash_detected:
                        current_sources[source_id]["binary_signal"] += "1"
                    else:
                        current_sources[source_id]["binary_signal"] += "0"

                    # Draw bounding box and number each source
                    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                    cv2.putText(frame, f"Light {source_id}", (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Update the signal label if we have at least 8 bits
                    if len(current_sources[source_id]["binary_signal"]) >= 8:
                        binary_signal = current_sources[source_id]["binary_signal"][:8]
                        self.history += f"Light {source_id}: {binary_signal} "
                        current_sources[source_id]["binary_signal"] = current_sources[source_id]["binary_signal"][8:]

        # Update GUI
        self.signal_label.setText("Binary Signal: " + self.history)
        self.history_edit.setPlainText(self.history)
        self.history_edit.moveCursor(QTextCursor.End)

        self.flash_sources = current_sources

    def get_source_id(self, x, y, r):
        for source_id, data in self.flash_sources.items():
            sx, sy, sr = data["position"]
            if abs(x - sx) < 50 and abs(y - sy) < 50:
                return source_id
        new_id = len(self.flash_sources) + 1
        self.flash_sources[new_id] = {"position": (x, y, r), "binary_signal": "", "prev_avg_intensity": None}
        return new_id

    def detect_flash_signal(self, roi, source_id):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise and improve sensitivity
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Calculate average intensity
        current_avg_intensity = np.mean(blurred)

        if source_id not in self.flash_sources or self.flash_sources[source_id].get("prev_avg_intensity") is None:
            self.flash_sources[source_id]["prev_avg_intensity"] = current_avg_intensity
            return False

        # Check for significant intensity change
        is_flash = abs(current_avg_intensity - self.flash_sources[source_id]["prev_avg_intensity"]) > self.threshold

        # Update previous average intensity
        self.flash_sources[source_id]["prev_avg_intensity"] = current_avg_intensity

        return is_flash

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
