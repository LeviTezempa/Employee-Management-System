import os
import sys
import time
from datetime import datetime

import cv2
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

from app_utils import FACE_CASCADE_PATHS, ensure_directories, get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECOGNITION_THRESHOLD = 70
SUSPICIOUS_RECORDING_SECONDS = 10


class Monitor(QDialog):
    def __init__(self):
        super(Monitor, self).__init__()
        os.chdir(BASE_DIR)
        ensure_directories(os.path.join(BASE_DIR, 'videos'))
        self.last_logged = {}
        self.is_running = True
        self.launch_camera()

    def launch_camera(self):
        db = get_db_connection()
        cursor = db.cursor()

        model_path = os.path.join(BASE_DIR, 'trained_model', 'model.yml')
        if not os.path.isfile(model_path):
            QMessageBox.information(self, 'Setup Required', 'Please train the face model first.')
            return

        face_cascade = None
        for relative_path in FACE_CASCADE_PATHS:
            cascade_path = os.path.join(BASE_DIR, relative_path)
            cascade = cv2.CascadeClassifier(cascade_path)
            if not cascade.empty():
                face_cascade = cascade
                break

        if face_cascade is None:
            QMessageBox.information(self, 'Setup Required', 'No valid face cascade was found.')
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)

        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_date = now.strftime('%Y-%m-%d')

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            db.close()
            QMessageBox.information(self, 'Camera Error', 'The camera could not be opened.')
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)
        video_dir = os.path.join(BASE_DIR, 'videos')
        os.makedirs(video_dir, exist_ok=True)
        suspicious_video = None
        suspicious_until = 0.0
        last_recorded_frame_time = 0.0
        recording_armed = True

        while self.is_running:
            ret, img = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) == 0:
                cv2.putText(img, 'Looking for face...', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            face_found = False
            unauthorized_seen = False
            for (x, y, w, h) in faces:
                face_found = True
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                face_roi = gray[y:y + h, x:x + w]
                employee_id, confidence = recognizer.predict(face_roi)

                query = 'SELECT * FROM employees WHERE employeeID=%s'
                cursor.execute(query, (employee_id,))
                result = cursor.fetchone()

                if result and confidence <= RECOGNITION_THRESHOLD:
                    employee_name = result[1]
                    employee_email = result[4]
                    employee_phone = result[5]
                    now_ts = time.time()
                    last_seen = self.last_logged.get(employee_id)

                    if last_seen is None or (now_ts - last_seen) > 10:
                        self.last_logged[employee_id] = now_ts
                        cv2.putText(img, f'ACCESS OK: {employee_name.upper()}', (x + 2, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 255, 0), 2)

                        try:
                            cursor.execute(
                                "INSERT INTO attendance VALUES (NULL, %s, %s, 0, %s)",
                                (employee_id, current_time, current_date)
                            )
                            db.commit()
                        except Exception:
                            print(f'Attendance already taken for {employee_name.upper()}')

                        print('================')
                        print(f'Name: {employee_name}')
                        print(f'ID: {employee_id}')
                        print(f'Phone: {employee_phone}')
                        print(f'Email: {employee_email}')
                        print('================')
                    else:
                        cv2.putText(img, f'PROFILE ACTIVE: {employee_name.upper()}', (x + 2, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                else:
                    unauthorized_seen = True
                    cv2.putText(img, 'Unauthorized Employee', (x + 2, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            now_ts = time.time()
            if unauthorized_seen and suspicious_video is None and recording_armed:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                video_path = os.path.join(video_dir, f'suspicious_{timestamp}.avi')
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                suspicious_video = cv2.VideoWriter(video_path, fourcc, 10.0, size)
                suspicious_until = now_ts + SUSPICIOUS_RECORDING_SECONDS
                last_recorded_frame_time = now_ts - 0.1
                recording_armed = False

            if suspicious_video is not None and now_ts < suspicious_until:
                remaining = max(0, int(suspicious_until - now_ts))
                cv2.putText(img, f'Recording suspicious activity: {remaining}s', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if now_ts - last_recorded_frame_time >= 0.1:
                    suspicious_video.write(img)
                    last_recorded_frame_time = now_ts
            elif suspicious_video is not None:
                suspicious_video.release()
                suspicious_video = None

            if not unauthorized_seen and suspicious_video is None:
                recording_armed = True

            if not face_found:
                cv2.putText(img, 'Looking for face...', (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            cv2.imshow(f'EMPLOYEE ATTENDANCE SYSTEM FOR {current_date}', img)
            if cv2.waitKey(30) & 0xFF == 27:
                break

        cap.release()
        if suspicious_video is not None:
            suspicious_video.release()
        cv2.destroyAllWindows()
        db.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Monitor()
    widget.show()
    sys.exit(app.exec_())
