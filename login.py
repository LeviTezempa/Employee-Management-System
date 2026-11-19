import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_utils import get_db_connection, hash_password


class LoginApp(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Login")
        self.resize(460, 560)
        self.setStyleSheet(
            "QDialog { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #1e3a8a); } "
            "QLabel { color: white; } "
            "QLineEdit { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.35); border-radius: 12px; padding: 13px; color: white; selection-background-color: #34d399; } "
            "QLineEdit:focus { border: 2px solid #86efac; } "
            "QPushButton { background: #34d399; color: #052e2b; border: 2px solid #86efac; border-radius: 14px; padding: 14px; font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { background: #10b981; color: white; } "
            "QPushButton:pressed { background: #059669; }"
        )

        container = QWidget(self)
        container.setObjectName("container")
        container.setStyleSheet(
            "QWidget#container { background: rgba(15,23,42,0.72); border: 1px solid rgba(255,255,255,0.18); border-radius: 22px; }"
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(42, 38, 42, 38)
        layout.setSpacing(16)

        icon = QLabel("LOGIN")
        icon.setAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignCenter)
        icon.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 3px; color: #86efac;")
        layout.addWidget(icon)

        title = QLabel("Welcome back")
        title.setAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Sign in to access your employee account")
        subtitle.setAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #dbeafe; margin-bottom: 12px;")
        layout.addWidget(subtitle)

        self.tb1 = QLineEdit()
        self.tb1.setPlaceholderText("Enter your registration username")
        self.tb1.setMaxLength(50)

        self.tb2 = QLineEdit()
        self.tb2.setPlaceholderText("Enter password")
        self.tb2.setEchoMode(QLineEdit.Password)
        self.tb2.setMaxLength(8)

        layout.addWidget(self.tb1)
        layout.addWidget(self.tb2)

        self.show_password = QCheckBox("Show password")
        self.show_password.setStyleSheet("color: #dbeafe; padding: 2px;")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password)

        self.b1 = QPushButton("Login")
        self.b1.clicked.connect(self.login)
        layout.addWidget(self.b1)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)
        self.layout().setContentsMargins(20, 20, 20, 20)

    def toggle_password_visibility(self, checked):
        echo_mode = QLineEdit.Normal if checked else QLineEdit.Password
        self.tb2.setEchoMode(echo_mode)

    def login(self):
        username = self.tb1.text().strip()
        password = self.tb2.text().strip()

        if not username or not password:
            QMessageBox.information(self, "Error", "All fields are required")
            return

        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute(
                "SELECT employeePassword FROM employees WHERE LOWER(TRIM(employeeUsername)) = LOWER(%s)",
                (username,),
            )
            result = cursor.fetchone()

            if result and result[0] == hash_password(password):
                QMessageBox.information(self, "Login", "Login successful")
            elif result:
                QMessageBox.information(self, "Login", "Incorrect password")
            else:
                QMessageBox.information(self, "Login", "No account was found for that username")
        except Exception as error:
            QMessageBox.information(self, "Database Error", f"Could not check login: {error}")
        finally:
            if 'db' in locals() and db.is_connected():
                db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = LoginApp()
    widget.show()
    sys.exit(app.exec_())
