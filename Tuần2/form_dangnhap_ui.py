from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Ui_FormDangNhap:
    def setupUi(self, dialog):
        dialog.setFixedSize(380, 260)
        dialog.setWindowTitle("Dang nhap")

        root = QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QLabel("Quan ly kham benh — Dang nhap")
        hdr.setFixedHeight(44)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setStyleSheet(
            "background:#333;color:white;"
            "font-size:13px;font-weight:bold;")
        root.addWidget(hdr)

        body = QVBoxLayout()
        body.setContentsMargins(30, 20, 30, 20)
        body.setSpacing(12)

        lbl_sub = QLabel("DANG NHAP HE THONG")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont();
        f.setPointSize(13);
        f.setBold(True)
        lbl_sub.setFont(f)
        body.addWidget(lbl_sub)

        INP = ("border:1px solid #ccc;border-radius:4px;"
               "padding:4px 8px;")

        row1 = QHBoxLayout()
        lbl1 = QLabel("Ten DN")
        lbl1.setFixedWidth(80)
        lbl1.setStyleSheet("color:#555;font-size:12px;")
        self.txt_ten = QLineEdit()
        self.txt_ten.setFixedHeight(32)
        self.txt_ten.setStyleSheet(INP)
        row1.addWidget(lbl1);
        row1.addWidget(self.txt_ten)
        body.addLayout(row1)

        row2 = QHBoxLayout()
        lbl2 = QLabel("Mat khau")
        lbl2.setFixedWidth(80)
        lbl2.setStyleSheet("color:#555;font-size:12px;")
        self.txt_matkhau = QLineEdit()
        self.txt_matkhau.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_matkhau.setFixedHeight(32)
        self.txt_matkhau.setStyleSheet(INP)
        row2.addWidget(lbl2);
        row2.addWidget(self.txt_matkhau)
        body.addLayout(row2)

        self.lbl_loi = QLabel("")
        self.lbl_loi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_loi.setStyleSheet("color:red;font-size:11px;")
        self.lbl_loi.setFixedHeight(18)
        body.addWidget(self.lbl_loi)

        self.btn_dangnhap = QPushButton("Dang nhap")
        self.btn_dangnhap.setFixedHeight(38)
        self.btn_dangnhap.setDefault(True)
        self.btn_dangnhap.setStyleSheet("""
            QPushButton{background:#f5f5f5;border:1px solid #ccc;
                border-radius:6px;font-size:13px;font-weight:bold;}
            QPushButton:hover{background:#e8e8e8;}
        """)
        body.addWidget(self.btn_dangnhap)
        root.addLayout(body)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QDialog

    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_FormDangNhap()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())