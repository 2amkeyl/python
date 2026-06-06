"""
ui/login_ui.py
──────────────
Cửa sổ đăng nhập – thuần UI.
Logic xác thực uỷ thác cho AuthLogic.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt
from logic import AuthLogic


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.current_user: dict | None = None
        self.setWindowTitle("Đăng nhập – Quản Lý Phòng Khám")
        self.setFixedSize(400, 340)
        self._build_ui()

    # ── UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet("QDialog { background: #1c2833; }")
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 30, 40, 30)
        root.setSpacing(16)

        # Logo + tiêu đề
        lbl_icon = QLabel("🏥")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 36px;")
        root.addWidget(lbl_icon)

        lbl_title = QLabel("PHÒNG KHÁM ĐA KHOA")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet(
            "color: white; font-size: 15px; font-weight: bold;")
        root.addWidget(lbl_title)

        # Form đăng nhập
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: white; border-radius: 10px; }"
            "QLineEdit { border: 1.5px solid #d5d8dc; border-radius: 6px; "
            "padding: 8px; font-size: 13px; }"
        )
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(12)

        self.usernameInput = QLineEdit()
        self.usernameInput.setPlaceholderText("Tên đăng nhập")
        self.usernameInput.setMinimumHeight(38)
        self.usernameInput.returnPressed.connect(
            lambda: self.passwordInput.setFocus())

        self.passwordInput = QLineEdit()
        self.passwordInput.setPlaceholderText("Mật khẩu")
        self.passwordInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordInput.setMinimumHeight(38)
        self.passwordInput.returnPressed.connect(self._login)

        self.errorLabel = QLabel("")
        self.errorLabel.setStyleSheet(
            "color: #e74c3c; font-size: 12px;")
        self.errorLabel.setWordWrap(True)
        self.errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.loginButton = QPushButton("🔐  Đăng nhập")
        self.loginButton.setMinimumHeight(40)
        self.loginButton.setStyleSheet("""
            QPushButton {
                background: #1a5276; color: white; border: none;
                border-radius: 6px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #2471a3; }
        """)
        self.loginButton.clicked.connect(self._login)

        cl.addWidget(self.usernameInput)
        cl.addWidget(self.passwordInput)
        cl.addWidget(self.errorLabel)
        cl.addWidget(self.loginButton)
        root.addWidget(card)

        lbl_ver = QLabel("v2.0  –  PyQt6 + MySQL")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ver.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        root.addWidget(lbl_ver)

    # ── Logic ──────────────────────────────────────────────────────────
    def _login(self):
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().strip()
        user, error = AuthLogic.login(username, password)
        if error:
            self.errorLabel.setText(error)
            self.passwordInput.clear()
            self.passwordInput.setFocus()
            return
        self.current_user = user
        self.accept()
