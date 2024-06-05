import cv2
import numpy as np
import tkinter as tk
from tkinter import Label, Text, Button
from PIL import Image, ImageTk
import time

class CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.binary_string = ""
        self.binary_label = Label(window, text="Binary String:", font=("Helvetica", 14))
        self.binary_label.pack()
        self.binary_text = Text(window, width=50, height=10, font=("Helvetica", 14))
        self.binary_text.pack()

        self.start_button = Button(window, text="Start", command=self.start_processing, font=("Helvetica", 14))
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = Button(window, text="Pause", command=self.pause_processing, font=("Helvetica", 14))
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.previous_brightness = None  # Biến để lưu mức sáng khung hình trước
        self.is_running = False

        self.fps_label = Label(window, text=f"FPS: {self.fps:.2f}", font=("Helvetica", 14))
        self.fps_label.pack()

        self.start_time = time.time()
        self.frame_count = 0

        self.update()
        self.window.mainloop()

    def start_processing(self):
        self.is_running = True

    def pause_processing(self):
        self.is_running = False

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            if self.is_running:
                self.process_frame(frame)
            
            self.frame_count += 1
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 1:
                fps = self.frame_count / elapsed_time
                self.fps_label.config(text=f"FPS: {fps:.2f}")
                self.start_time = time.time()
                self.frame_count = 0

        self.window.after(10, self.update)

    def process_frame(self, frame):
        roi = frame[100:200, 100:200]  # Định nghĩa Vùng Quan Tâm (ROI)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Ngưỡng nhị phân
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # Tính độ sáng trung bình của ROI
        current_brightness = np.mean(binary)
        
        if self.previous_brightness is None:
            self.previous_brightness = current_brightness

        # Xác định giá trị bit nhị phân dựa trên sự thay đổi mức sáng
        if abs(current_brightness - self.previous_brightness) > 50:  # Ngưỡng thay đổi
            bit_value = 1
        else:
            bit_value = 0
        
        self.binary_string += str(bit_value)
        self.binary_text.delete(1.0, tk.END)  # Xóa nội dung cũ
        self.binary_text.insert(tk.END, self.binary_string)  # Chèn nội dung mới
        
        self.previous_brightness = current_brightness
        
        # Vẽ hình chữ nhật quanh ROI để dễ hình dung
        cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), 2)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root, "Camera Flash Detection")
