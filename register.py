import os
import sys
import time

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_utils import FACE_CASCADE_PATHS, ensure_directories, get_db_connection, hash_password

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, 'trained_dataset')
MODEL_DIR = os.path.join(BASE_DIR, 'trained_model')


class RegApp(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Registration")
        self.resize(460, 700)
        self.setStyleSheet(
            "QDialog { background: #eef3ff; } "
            "QLabel { color: #1f2937; } "
            "QLineEdit, QComboBox { background: #ffffff; border: 1px solid #cfd8e3; border-radius: 10px; padding: 10px; color: #111827; } "
            "QComboBox { padding-right: 34px; selection-background-color: #2563eb; } "
            "QComboBox:hover { border: 1px solid #60a5fa; background: #f8fbff; } "
            "QComboBox:focus { border: 2px solid #2563eb; } "
            "QComboBox::drop-down { width: 32px; border: none; border-left: 1px solid #dbe3ef; background: #eff6ff; border-top-right-radius: 10px; border-bottom-right-radius: 10px; } "
            "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid #2563eb; } "
            "QComboBox QAbstractItemView { background: #ffffff; border: 1px solid #bfdbfe; selection-background-color: #2563eb; selection-color: #ffffff; padding: 6px; outline: none; } "
            "QPushButton { background: #1d4ed8; color: white; border: none; border-radius: 10px; padding: 11px; font-weight: bold; } "
            "QPushButton:hover { background: #2563eb; } "
            "QPushButton#secondary { background: #e5e7eb; color: #111827; } "
            "QPushButton#secondary:hover { background: #d1d5db; } "
            "QCheckBox { color: #374151; }"
        )

        ensure_directories(DATASET_DIR, MODEL_DIR)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(14)

        title = QLabel("Create Employee Account")
        title.setStyleSheet("font-size: 24px; font-weight: bold; qproperty-alignment: AlignCenter;")
        main_layout.addWidget(title)

        subtitle = QLabel("Complete the form and train the employee face profile.")
        subtitle.setStyleSheet("font-size: 12px; color: #475569; qproperty-alignment: AlignCenter;")
        main_layout.addWidget(subtitle)

        form = QFormLayout()
        form.setLabelAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignLeft)
        form.setFormAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignTop)
        form.setSpacing(12)

        self.tb3 = QLineEdit()
        self.tb3.setPlaceholderText("Full name")
        self.tb4 = QLineEdit()
        self.tb4.setPlaceholderText("Username (use this to log in)")
        self.tb4.setMaxLength(50)

        self.tb5 = QLineEdit()
        self.tb5.setPlaceholderText("Password")
        self.tb5.setEchoMode(QLineEdit.Password)
        self.tb5.setMaxLength(8)

        self.tb_confirm = QLineEdit()
        self.tb_confirm.setPlaceholderText("Confirm password")
        self.tb_confirm.setEchoMode(QLineEdit.Password)
        self.tb_confirm.setMaxLength(8)

        self.tb6 = QLineEdit()
        self.tb6.setPlaceholderText("Email")
        self.tb7 = QLineEdit()
        self.tb7.setInputMask("000-000-0000")
        self.tb7.setPlaceholderText("416-555-0123")

        self.c1 = QComboBox()
        self.c1.addItems([
            "Computer Science",
            "Business Administration",
            "Nursing",
            "Engineering",
            "Health Sciences",
        ])

        self.c2 = QComboBox()
        self.c2.addItems(["M", "F"])

        form.addRow("Full name", self.tb3)
        form.addRow("Username", self.tb4)
        form.addRow("Password", self.tb5)
        form.addRow("Confirm password", self.tb_confirm)
        form.addRow("Email", self.tb6)
        form.addRow("Phone", self.tb7)
        form.addRow("Program", self.c1)
        form.addRow("Sex", self.c2)

        main_layout.addLayout(form)

        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        main_layout.addWidget(self.show_password)

        self.b2 = QPushButton("Register & Train Face")
        self.b2.clicked.connect(self.reg)
        main_layout.addWidget(self.b2)

        row = QHBoxLayout()
        self.label_9 = QLabel("Already registered?")
        self.b3 = QPushButton("Login")
        self.b3.setObjectName("secondary")
        self.b3.clicked.connect(self.show_login)
        row.addWidget(self.label_9)
        row.addWidget(self.b3)
        main_layout.addLayout(row)

        self.setLayout(main_layout)

    def toggle_password_visibility(self, checked):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.tb5.setEchoMode(mode)
        self.tb_confirm.setEchoMode(mode)

    def reg(self):
        full_name = self.tb3.text().strip()
        username = self.tb4.text().strip()
        password = self.tb5.text().strip()
        confirm_password = self.tb_confirm.text().strip()
        email = self.tb6.text().strip()
        phone = self.tb7.text().replace("-", "").strip()
        department = self.c1.currentText()
        sex = self.c2.currentText()

        if not all([full_name, username, password, confirm_password, email, phone, department, sex]):
            QMessageBox.information(self, "Error", "All fields are required")
            return

        if password != confirm_password:
            QMessageBox.information(self, "Error", "Passwords do not match")
            return

        if len(phone) != 10 or not phone.isdigit():
            QMessageBox.information(self, "Error", "Enter a valid 10-digit Canadian phone number")
            return

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT employeeID FROM employees ORDER BY employeeID DESC LIMIT 1")
            latest_id = cursor.fetchone()
            employee_id = (latest_id[0] + 1) if latest_id else 1

            cursor.execute(
                "SELECT employeeID FROM employees WHERE LOWER(TRIM(employeeUsername)) = LOWER(%s)",
                (username,),
            )
            if cursor.fetchone():
                QMessageBox.information(self, "Registration", "User already exists with this username")
                db.close()
                return

            cursor.execute(
                "INSERT INTO employees (employeeID, employeeFullName, employeeUsername, employeePassword, employeeEmail, employeePhone, employeeDepartment, employeeSex) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (employee_id, full_name, username, hash_password(password), email, phone, department, sex),
            )
            db.commit()
            db.close()

            QMessageBox.information(
                self,
                "Registration",
                f"Employee registered successfully.\n\nYour login username is: {username}\n\nTraining face samples now...",
            )
            training_completed = self.train_face_model(employee_id, username, full_name)
            if not training_completed:
                return

            self.tb3.clear()
            self.tb4.clear()
            self.tb5.clear()
            self.tb_confirm.clear()
            self.tb6.clear()
            self.tb7.clear()
            self.open_welcome()

        except Exception as e:
            QMessageBox.information(self, "Server Response", "Failed because: " + str(e))

    def train_face_model(self, employee_id, username, full_name):
        face_cascade = None
        for relative_path in FACE_CASCADE_PATHS:
            cascade_path = os.path.join(BASE_DIR, relative_path)
            cascade = cv2.CascadeClassifier(cascade_path)
            if not cascade.empty():
                face_cascade = cascade
                break

        if face_cascade is None:
            QMessageBox.information(self, "Face Setup", "No valid Haar cascade found.")
            return False

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            QMessageBox.information(self, "Face Setup", "The camera could not be opened.")
            return False

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        sample_num = 0
        last_sample_time = 0.0
        window_title = 'Training Model For Employee: ' + full_name

        while True:
            ret, img = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100),
            )

            if len(faces) == 1:
                x, y, w, h = faces[0]
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, f'Samples: {sample_num}/100', (x, max(y - 10, 25)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                now = time.monotonic()
                if now - last_sample_time >= 0.12:
                    face_img = gray[y:y + h, x:x + w]
                    face_img = cv2.resize(face_img, (200, 200))
                    face_img = cv2.equalizeHist(face_img)
                    sample_num += 1
                    sample_path = os.path.join(DATASET_DIR, f'{username}.{employee_id}.{sample_num}.jpg')
                    cv2.imwrite(sample_path, face_img)
                    last_sample_time = now
            elif len(faces) == 0:
                cv2.putText(img, 'Move your face into the camera', (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                cv2.putText(img, 'Only one face should be visible', (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow(window_title, img)
            if sample_num >= 100 or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        image_paths = [os.path.join(DATASET_DIR, f) for f in os.listdir(DATASET_DIR)]
        faces = []
        ids = []

        for image_path in image_paths:
            if not image_path.endswith('.jpg'):
                continue
            face_img = Image.open(image_path).convert('L')
            face_np = np.array(face_img, 'uint8')
            face_np = cv2.resize(face_np, (200, 200))
            face_np = cv2.equalizeHist(face_np)
            employee_number = int(os.path.split(image_path)[-1].split('.')[1])
            faces.append(face_np)
            ids.append(employee_number)

        if not faces:
            QMessageBox.information(self, "Training", "No face samples were captured.")
            return False

        recognizer.train(faces, np.array(ids))
        recognizer.save(os.path.join(MODEL_DIR, 'model.yml'))
        QMessageBox.information(self, "Registration Complete", "Employee trained successfully")
        return True

    def open_welcome(self):
        try:
            from welcome import welcome as WelcomeWindow

            self.welcome_window = WelcomeWindow()
            self.welcome_window.show()
            self.welcome_window.raise_()
            self.welcome_window.activateWindow()
            self.hide()
        except Exception as error:
            QMessageBox.critical(self, "Launch Error", f"Could not open the welcome page:\n{error}")

    def show_login(self):
        self.open_welcome()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RegApp()
    widget.show()
    sys.exit(app.exec_())
