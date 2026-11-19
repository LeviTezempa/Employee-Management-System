import os
import subprocess
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class welcome(QDialog):
    def __init__(self):
        super().__init__()
        self.child_process = None
        self.setWindowTitle("Welcome")
        self.resize(800, 600)
        self.setStyleSheet(
            "QDialog { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #1e3a8a); } "
            "QPushButton { border: 2px solid rgba(255,255,255,0.25); border-radius: 18px; font-size: 20px; padding: 18px; font-weight: bold; color: #0f172a; } "
            "QPushButton:hover { border: 2px solid rgba(255,255,255,0.7); } "
            "QLabel { color: white; }"
        )

        container = QWidget(self)
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(120, 80, 120, 80)
        layout.setSpacing(22)

        title = QLabel("Welcome")
        title.setAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 38px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(title)

        subtitle = QLabel("Choose a sign-in method")
        subtitle.setAlignment(__import__('PyQt5.QtCore').QtCore.Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px; color: #dbeafe;")
        layout.addWidget(subtitle)

        self.log1 = QPushButton("Login")
        self.log1.setStyleSheet(
            "background: #34d399; color: #052e2b; "
            "border: 2px solid #86efac; "
            "border-radius: 18px; "
            "padding: 18px; "
            "font-size: 20px; "
            "font-weight: bold; "
            "QPushButton:hover { background: #10b981; color: white; }"
        )
        self.log1.setCursor(__import__('PyQt5.QtGui').QtGui.QCursor(__import__('PyQt5.QtCore').QtCore.Qt.PointingHandCursor))
        self.log1.clicked.connect(self.Login)
        layout.addWidget(self.log1)

        self.log2 = QPushButton("Face Login")
        self.log2.setStyleSheet(
            "background: #60a5fa; color: #0f172a; "
            "border: 2px solid #bfdbfe; "
            "border-radius: 18px; "
            "padding: 18px; "
            "font-size: 20px; "
            "font-weight: bold; "
            "QPushButton:hover { background: #3b82f6; color: white; }"
        )
        self.log2.setCursor(__import__('PyQt5.QtGui').QtGui.QCursor(__import__('PyQt5.QtCore').QtCore.Qt.PointingHandCursor))
        self.log2.clicked.connect(self.LoginAI)
        layout.addWidget(self.log2)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)
        self.layout().setContentsMargins(0, 0, 0, 0)


    def Login(self):
        self.launch_page('login.py')

    def LoginAI(self):
        self.launch_page('loginAI.py')

    def launch_page(self, script_name):
        if self.child_process is not None and self.child_process.poll() is None:
            return

        script_path = os.path.join(BASE_DIR, script_name)
        try:
            self.child_process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=BASE_DIR,
            )
            self.log1.setEnabled(False)
            self.log2.setEnabled(False)
            self.hide()
            QTimer.singleShot(500, self.check_child_process)
        except OSError as error:
            QMessageBox.critical(self, "Launch Error", f"Could not open {script_name}: {error}")

    def check_child_process(self):
        if self.child_process is None:
            return

        if self.child_process.poll() is None:
            QTimer.singleShot(500, self.check_child_process)
            return

        exit_code = self.child_process.returncode
        self.child_process = None
        self.log1.setEnabled(True)
        self.log2.setEnabled(True)
        self.show()
        self.raise_()
        self.activateWindow()

        if exit_code != 0:
            QMessageBox.warning(
                self,
                "Page Closed",
                f"The selected page closed with error code {exit_code}. Check its terminal for details.",
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = welcome()
    widget.show()
    sys.exit(app.exec_())
