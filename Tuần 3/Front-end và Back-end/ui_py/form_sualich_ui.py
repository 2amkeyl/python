from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox,
                             QDateEdit, QTimeEdit, QWidget)
from PyQt6.QtCore import Qt, QDate, QTime


class Ui_FormSuaLich:
    def setupUi(self, dialog):
        dialog.setWindowTitle("Sua lich kham")
        dialog.setFixedWidth(500)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0);
        root.setSpacing(0)

        self.lbl_title = QLabel("Sua lich kham")
        self.lbl_title.setFixedHeight(42)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_title.setStyleSheet(
            "background:#185FA5;color:white;"
            "font-size:14px;font-weight:bold;padding-left:14px;")
        root.addWidget(self.lbl_title)

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 12);
        body.setSpacing(10)

        INP = ("border:1px solid #ccc;border-radius:4px;"
               "padding:4px 8px;font-size:12px;")
        INP_DIS = ("border:1px solid #e0e0e0;border-radius:4px;"
                   "padding:4px 8px;font-size:12px;"
                   "background:#f5f5f5;color:#aaa;")

        note = QLabel("* Ma lich khong duoc chinh sua")
        note.setStyleSheet("font-size:10px;color:#999;")
        body.addWidget(note)

        f1 = QFormLayout()
        f1.setSpacing(8)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.txt_ma = QLineEdit()
        self.txt_ma.setEnabled(False)
        self.txt_ma.setFixedHeight(32)
        self.txt_ma.setStyleSheet(INP_DIS)

        self.txt_hoten = QLineEdit()
        self.txt_hoten.setFixedHeight(32)
        self.txt_hoten.setStyleSheet(INP)

        self.txt_sdt = QLineEdit()
        self.txt_sdt.setFixedHeight(32)
        self.txt_sdt.setStyleSheet(INP)

        self.date_ngaysinh = QDateEdit()
        self.date_ngaysinh.setCalendarPopup(True)
        self.date_ngaysinh.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaysinh.setFixedHeight(32)
        self.date_ngaysinh.setStyleSheet(INP)

        self.txt_diachi = QLineEdit()
        self.txt_diachi.setFixedHeight(32)
        self.txt_diachi.setStyleSheet(INP)

        f1.addRow("Ma lich:", self.txt_ma)
        f1.addRow("Ho ten:", self.txt_hoten)
        f1.addRow("So dien thoai:", self.txt_sdt)
        f1.addRow("Ngay sinh:", self.date_ngaysinh)
        f1.addRow("Dia chi:", self.txt_diachi)
        body.addLayout(f1)

        # Dich vu
        dv_row = QHBoxLayout()
        lbl_dv = QLabel("Dich vu:")
        lbl_dv.setFixedWidth(110)
        lbl_dv.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cmb_dichvu = QComboBox()
        self.cmb_dichvu.setFixedHeight(32)
        self.cmb_dichvu.setStyleSheet(INP)
        dv_row.addWidget(lbl_dv);
        dv_row.addWidget(self.cmb_dichvu)
        body.addLayout(dv_row)

        # 3 nut goi
        self.btn_goi_bs = QPushButton("Bac si\n0d")
        self.btn_goi_ths = QPushButton("Thac si\n0d")
        self.btn_goi_ts = QPushButton("Tien si\n0d")
        self._goi_btns = [self.btn_goi_bs,
                          self.btn_goi_ths,
                          self.btn_goi_ts]
        self._BTN_ACT = ("border:2px solid #185FA5;border-radius:6px;"
                         "padding:6px;font-size:11px;"
                         "background:#E6F1FB;font-weight:bold;")
        self._BTN_INACT = ("border:1px solid #ccc;border-radius:6px;"
                           "padding:6px;font-size:11px;background:white;")
        goi_row = QHBoxLayout();
        goi_row.setSpacing(6)
        for b in self._goi_btns:
            b.setFixedHeight(50);
            b.setStyleSheet(self._BTN_INACT)
            goi_row.addWidget(b)
        body.addLayout(goi_row)

        self.lbl_gia = QLabel("Phi kham          0 VND")
        self.lbl_gia.setFixedHeight(34)
        self.lbl_gia.setStyleSheet(
            "background:#E6F1FB;border:1px solid #85B7EB;"
            "border-radius:6px;padding:0 12px;"
            "font-size:12px;font-weight:bold;color:#0C447C;")
        body.addWidget(self.lbl_gia)

        f2 = QFormLayout();
        f2.setSpacing(8)
        f2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.date_ngaykham = QDateEdit()
        self.date_ngaykham.setCalendarPopup(True)
        self.date_ngaykham.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaykham.setFixedHeight(32)
        self.date_ngaykham.setStyleSheet(INP)

        self.time_giokham = QTimeEdit()
        self.time_giokham.setDisplayFormat("HH:mm")
        self.time_giokham.setFixedHeight(32)
        self.time_giokham.setStyleSheet(INP)

        self.cmb_trangthai = QComboBox()
        self.cmb_trangthai.setFixedHeight(32)
        self.cmb_trangthai.setStyleSheet(INP)
        self.cmb_trangthai.addItems(
            ["Cho kham", "Dang kham", "Da xong", "Da huy"])

        f2.addRow("Ngay kham:", self.date_ngaykham)
        f2.addRow("Gio kham:", self.time_giokham)
        f2.addRow("Trang thai:", self.cmb_trangthai)
        body.addLayout(f2)

        btn_row = QHBoxLayout();
        btn_row.addStretch()
        self.btn_huy = QPushButton("Huy bo")
        self.btn_huy.setFixedSize(90, 34)
        self.btn_huy.setStyleSheet(
            "border:1px solid #ccc;border-radius:5px;font-size:12px;")
        self.btn_luu = QPushButton("Luu thay doi")
        self.btn_luu.setFixedSize(120, 34)
        self.btn_luu.setDefault(True)
        self.btn_luu.setStyleSheet(
            "background:#185FA5;color:white;"
            "border-radius:5px;font-size:12px;font-weight:bold;")
        btn_row.addWidget(self.btn_huy)
        btn_row.addWidget(self.btn_luu)
        body.addLayout(btn_row)
        root.addLayout(body)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QDialog

    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_FormSuaLich()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())