"""
main.py  –  Entry point
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Quản Lý Phòng Khám")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet("""
        QToolTip{background:#2c3e50;color:white;border:none;padding:4px 8px;border-radius:4px;}
        QScrollBar:vertical{background:#f0f0f0;width:8px;border-radius:4px;}
        QScrollBar::handle:vertical{background:#bdc3c7;border-radius:4px;min-height:20px;}
        QScrollBar::handle:vertical:hover{background:#95a5a6;}
        QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}
        QScrollBar:horizontal{background:#f0f0f0;height:8px;border-radius:4px;}
        QScrollBar::handle:horizontal{background:#bdc3c7;border-radius:4px;min-width:20px;}
        QScrollBar::handle:horizontal:hover{background:#95a5a6;}
        QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal{width:0px;}
    """)

    # Kết nối CSDL
    from database import db
    if not db.connect():
        QMessageBox.critical(
            None, "Lỗi kết nối CSDL",
            "Không thể kết nối MySQL!\n\n"
            "Mở file  database/connection.py  và sửa DB_CONFIG.\n\n"
            "Mặc định: host=localhost, port=3306, user=root, password=123456"
        )
        sys.exit(1)

    # Vòng lặp: đăng nhập → main window → (đăng xuất → đăng nhập lại)
    while True:
        from ui.login_ui import LoginWindow
        login = LoginWindow()
        if login.exec() != 1 or not login.current_user:
            break

        from ui.main_window_ui import MainWindow
        win = MainWindow(login.current_user)
        win._do_logout = False
        win.showMaximized()
        app.exec()

        if not getattr(win, "_do_logout", False):
            break

    db.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    main()
