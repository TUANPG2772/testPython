import cv2
import numpy as np
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk

class FlashDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash Decoder")
        
        self.video_label = Label(root)
        self.video_label.pack()
        
        self.result_label = Label(root, text="", font=("Helvetica", 16))
        self.result_label.pack()
        
        self.cap = cv2.VideoCapture(0)
        
        self.flash_detected = []
        self.flash_times = []
        self.bit_duration = 0.5  # 500ms
        self.frame_rate = 16.6  # FPS
        self.frame_duration = 1.0 / self.frame_rate
        self.total_bits = 0
        
        self.decode_completed = False
        self.update_video()

    def detect_flash(self, frame, threshold=200):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return brightness > threshold

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            is_flash = self.detect_flash(frame)
            self.flash_detected.append(is_flash)
            
            if len(self.flash_detected) >= 2:
                if self.flash_detected[-1] and not self.flash_detected[-2]:
                    self.flash_times.append(len(self.flash_detected) * self.frame_duration)
                    self.total_bits += 1

            if self.total_bits >= (len(self.flash_times) + 3 * 2) and not self.decode_completed:
                self.decode_flash_data()
                self.decode_completed = True
            else:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                
                self.video_label.configure(image=image)
                self.video_label.image = image

        self.root.after(1, self.update_video)

    def decode_flash_data(self):
        data_bits = self.flash_detected[3 * 2:]  # Skip the initial 3 blinks
        binary_data = ''.join(['1' if bit else '0' for bit in data_bits])
        
        # Split the binary string into bytes
        byte_data = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]

        # Convert binary bytes to characters
        decoded_data = ''.join([chr(int(byte, 2)) for byte in byte_data if len(byte) == 8])
        
        self.result_label.configure(text=f"Decoded Data: {decoded_data}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashDecoderApp(root)
    root.mainloop()
