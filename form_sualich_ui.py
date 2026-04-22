from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTimeEdit, QGroupBox, QRadioButton
)
from PyQt6.QtCore import Qt, QDate, QTime
import sys


class Ui_FormSuaLich:
    def setupUi(self, dialog):
        dialog.setWindowTitle("Sửa lịch khám")
        dialog.setFixedWidth(500)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(8)

        # ── TIÊU ĐỀ ───────────────────────────────
        self.lbl_title = QLabel("SỬA LỊCH KHÁM")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)   # ✅ PyQt6
        self.lbl_title.setStyleSheet(
            "font-size:14px;font-weight:bold;color:white;"
            "background:#185FA5;padding:8px;border-radius:6px;"
        )
        root.addWidget(self.lbl_title)

        # ── MÃ LỊCH (chỉ đọc) ─────────────────────
        row_ma = QHBoxLayout()
        row_ma.addWidget(QLabel("Mã lịch:"))
        self.txt_ma = QLineEdit()
        self.txt_ma.setEnabled(False)
        self.txt_ma.setFixedHeight(30)
        self.txt_ma.setStyleSheet("background:#f0f0f0;color:#888;")
        row_ma.addWidget(self.txt_ma)
        root.addLayout(row_ma)

        # ── THÔNG TIN BỆNH NHÂN ───────────────────
        grp1 = QGroupBox("Thông tin bệnh nhân")
        form1 = QFormLayout(grp1)
        form1.setSpacing(8)

        self.txt_hoten = QLineEdit(); self.txt_hoten.setFixedHeight(30)
        self.txt_sdt = QLineEdit(); self.txt_sdt.setFixedHeight(30)

        self.date_ngaysinh = QDateEdit()
        self.date_ngaysinh.setCalendarPopup(True)
        self.date_ngaysinh.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaysinh.setDate(QDate.currentDate())
        self.date_ngaysinh.setFixedHeight(30)

        self.txt_diachi = QLineEdit(); self.txt_diachi.setFixedHeight(30)

        form1.addRow("Họ tên (*):", self.txt_hoten)
        form1.addRow("Số điện thoại:", self.txt_sdt)
        form1.addRow("Ngày sinh:", self.date_ngaysinh)
        form1.addRow("Địa chỉ:", self.txt_diachi)
        root.addWidget(grp1)

        # ── DỊCH VỤ & GÓI KHÁM ────────────────────
        grp2 = QGroupBox("Dịch vụ & Gói khám")
        v2 = QVBoxLayout(grp2)
        v2.setSpacing(8)

        row_dv = QHBoxLayout()
        row_dv.addWidget(QLabel("Dịch vụ:"))
        self.cmb_dichvu = QComboBox()
        self.cmb_dichvu.setFixedHeight(30)
        row_dv.addWidget(self.cmb_dichvu)
        v2.addLayout(row_dv)

        grp_goi = QGroupBox("Gói khám")
        row_goi = QHBoxLayout(grp_goi)
        self.radio_bs = QRadioButton("Bác sĩ")
        self.radio_ths = QRadioButton("Thạc sĩ")
        self.radio_ts = QRadioButton("Tiến sĩ")
        row_goi.addWidget(self.radio_bs)
        row_goi.addWidget(self.radio_ths)
        row_goi.addWidget(self.radio_ts)
        v2.addWidget(grp_goi)

        self.lbl_gia = QLabel("0 VND")
        self.lbl_gia.setAlignment(Qt.AlignmentFlag.AlignCenter)   # ✅ PyQt6
        self.lbl_gia.setStyleSheet(
            "font-size:16px;font-weight:bold;color:#185FA5;"
            "background:#E6F1FB;border-radius:6px;padding:8px;"
        )
        v2.addWidget(self.lbl_gia)
        root.addWidget(grp2)

        # ── NGÀY GIỜ & TRẠNG THÁI ─────────────────
        grp3 = QGroupBox("Lịch khám")
        form3 = QFormLayout(grp3)
        form3.setSpacing(8)

        self.date_ngaykham = QDateEdit()
        self.date_ngaykham.setCalendarPopup(True)
        self.date_ngaykham.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaykham.setDate(QDate.currentDate())
        self.date_ngaykham.setFixedHeight(30)

        self.time_giokham = QTimeEdit()
        self.time_giokham.setDisplayFormat("HH:mm")
        self.time_giokham.setTime(QTime(8, 0))
        self.time_giokham.setFixedHeight(30)

        self.cmb_trangthai = QComboBox()
        self.cmb_trangthai.setFixedHeight(30)
        self.cmb_trangthai.addItems(["Chờ khám", "Đang khám", "Đã xong", "Đã hủy"])

        form3.addRow("Ngày khám:", self.date_ngaykham)
        form3.addRow("Giờ khám:", self.time_giokham)
        form3.addRow("Trạng thái:", self.cmb_trangthai)
        root.addWidget(grp3)

        # ── NÚT BẤM ───────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_huy = QPushButton("Hủy bỏ")
        self.btn_huy.setFixedSize(100, 34)

        self.btn_luu = QPushButton("Lưu thay đổi")
        self.btn_luu.setFixedSize(130, 34)
        self.btn_luu.setDefault(True)
        self.btn_luu.setStyleSheet(
            "QPushButton{background:#185FA5;color:white;"
            "border-radius:6px;font-weight:bold;}"
            "QPushButton:hover{background:#0C447C;}"
        )

        btn_row.addWidget(self.btn_huy)
        btn_row.addWidget(self.btn_luu)
        root.addLayout(btn_row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_FormSuaLich()
    ui.setupUi(dialog)
    dialog.show()   # hoặc dialog.exec() nếu muốn modal
    sys.exit(app.exec())