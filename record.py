import os
import time
from datetime import datetime

import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

capture_duration = 10  # seconds
fps = 20.0
width = 640
height = 480

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError('Could not open webcam.')

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, fps)

output_name = datetime.now().strftime('recording_%Y-%m-%d_%H-%M-%S.mp4')
output_path = os.path.join(VIDEO_DIR, output_name)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

if not out.isOpened():
    cap.release()
    raise RuntimeError('Could not create video writer.')

start_time = time.time()

while time.time() - start_time < capture_duration:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (width, height))
    out.write(frame)

    cv2.imshow('Recording...', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()
cap.release()
cv2.destroyAllWindows()
print(f'Video saved: {output_path}')