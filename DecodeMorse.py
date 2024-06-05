import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import Label, Text
from PIL import Image, ImageTk

# Hàm giải mã mã Morse
def morse_decode(signal):
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
        '----.': '9'
    }
    return morse_dict.get(signal, '')

# Khởi tạo camera
cap = cv2.VideoCapture(0)

# Các biến để theo dõi tín hiệu
prev_light = False
light_on_time = 0
light_off_time = 0
morse_signal = ''
decoded_message = ''

# Tạo giao diện GUI
root = tk.Tk()
root.title("Morse Code Decoder")

# Khung hình cho video và nhãn cho thông điệp giải mã
video_label = Label(root)
video_label.pack()

# Tạo Text widget để hiển thị thông điệp giải mã
decoded_text = Text(root, height=10, width=50, font=("Helvetica", 16))
decoded_text.pack()

def update_frame():
    global prev_light, light_on_time, light_off_time, morse_signal, decoded_message
    
    ret, frame = cap.read()
    if not ret:
        root.after(10, update_frame)
        return

    # Chuyển đổi khung hình sang grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Áp dụng threshold để phát hiện ánh sáng
    _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
    # Tính toán tỷ lệ vùng sáng
    light_ratio = np.sum(thresh == 255) / thresh.size

    current_light = light_ratio > 0.5

    if current_light and not prev_light:
        # Ánh sáng bật
        light_on_time = time.time()
        if light_off_time:
            duration = light_on_time - light_off_time
            if duration > 1.5:
                decoded_message += ' '
                decoded_text.insert(tk.END, ' ')
                print(' ', end='', flush=True)
            elif duration > 0.5:
                morse_signal += ' '
    elif not current_light and prev_light:
        # Ánh sáng tắt
        light_off_time = time.time()
        if light_on_time:
            duration = light_off_time - light_on_time
            if duration > 0.5:
                morse_signal += '-'
            else:
                morse_signal += '.'

            # Giải mã tín hiệu Morse
            if len(morse_signal) > 0 and (len(morse_signal) >= 5 or morse_signal[-1] == ' '):
                decoded_char = morse_decode(morse_signal.strip())
                decoded_message += decoded_char
                decoded_text.insert(tk.END, decoded_char)
                print(decoded_char, end='', flush=True)
                morse_signal = ''

    prev_light = current_light

    # Chuyển đổi khung hình thành ảnh cho tkinter
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(image=img)
    
    video_label.imgtk = img_tk
    video_label.configure(image=img_tk)
    
    root.after(10, update_frame)

def on_closing():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
update_frame()
root.mainloop()
