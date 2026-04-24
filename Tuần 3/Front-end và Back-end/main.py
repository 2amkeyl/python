import sys
from PyQt6.QtWidgets import QApplication, QDialog
from form_dangnhap import FormDangNhap
from mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    while True:
        login = FormDangNhap()
        if login.exec() == QDialog.DialogCode.Accepted:
            win = MainWindow()
            win.show()
            app.exec()
        else:
            break


if __name__ == "__main__":
    main()