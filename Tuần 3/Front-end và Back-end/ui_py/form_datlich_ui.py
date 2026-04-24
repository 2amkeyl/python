from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox,
                             QDateEdit, QTimeEdit, QGroupBox, QWidget)
from PyQt6.QtCore import Qt, QDate, QTime


class Ui_FormDatLich:
    def setupUi(self, dialog):
        dialog.setWindowTitle("Đặt lịch khám mới")
        dialog.setFixedWidth(500)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QLabel("Đặt lịch khám mới")
        hdr.setFixedHeight(42)
        hdr.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        hdr.setStyleSheet(
            "background:#0F6E56;color:white;"
            "font-size:14px;font-weight:bold;padding-left:14px;")
        root.addWidget(hdr)

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 12)
        body.setSpacing(10)

        INP = ("border:1px solid #ccc;border-radius:4px;"
               "padding:4px 8px;font-size:12px;")

        # --- Tìm kiếm BN theo mã BN ---
        grp0 = QGroupBox("Tìm kiếm bệnh nhân (nhập mã BN)")
        f0 = QFormLayout(grp0)
        f0.setSpacing(8)
        f0.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        ma_row = QHBoxLayout()
        self.txt_sdt = QLineEdit()   # vẫn giữ tên biến để không ảnh hưởng code cũ
        self.txt_sdt.setPlaceholderText("Nhập mã BN rồi bấm Tìm...")
        self.txt_sdt.setFixedHeight(32)
        self.txt_sdt.setStyleSheet(INP)
        self.btn_tim_bn = QPushButton("Tìm BN")
        self.btn_tim_bn.setFixedSize(80, 32)
        self.btn_tim_bn.setStyleSheet(
            "QPushButton{background:#185FA5;color:white;"
            "border-radius:4px;font-size:11px;}"
            "QPushButton:hover{background:#0C447C;}")
        ma_row.addWidget(self.txt_sdt)
        ma_row.addWidget(self.btn_tim_bn)
        f0.addRow("Mã bệnh nhân:", ma_row)

        # Hiển thị trạng thái BN
        self.lbl_trang_thai_bn = QLabel("Chưa tìm kiếm")
        self.lbl_trang_thai_bn.setFixedHeight(24)
        self.lbl_trang_thai_bn.setStyleSheet(
            "font-size:11px;color:#888;font-style:italic;")
        f0.addRow("", self.lbl_trang_thai_bn)
        body.addWidget(grp0)

        # --- Thông tin BN ---
        grp1 = QGroupBox("Thông tin bệnh nhân")
        f1 = QFormLayout(grp1)
        f1.setSpacing(8)
        f1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.txt_hoten = QLineEdit()
        self.txt_hoten.setPlaceholderText("Họ tên bệnh nhân *")
        self.txt_hoten.setFixedHeight(32)
        self.txt_hoten.setStyleSheet(INP)

        self.date_ngaysinh = QDateEdit()
        self.date_ngaysinh.setCalendarPopup(True)
        self.date_ngaysinh.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaysinh.setFixedHeight(32)
        self.date_ngaysinh.setStyleSheet(INP)

        self.txt_diachi = QLineEdit()
        self.txt_diachi.setPlaceholderText("Địa chỉ (tùy chọn)")
        self.txt_diachi.setFixedHeight(32)
        self.txt_diachi.setStyleSheet(INP)

        # THÊM MỚI: SĐT bệnh nhân - NGAY DƯỚI địa chỉ
        self.txt_sdt_bn = QLineEdit()
        self.txt_sdt_bn.setPlaceholderText("Số điện thoại bệnh nhân")
        self.txt_sdt_bn.setFixedHeight(32)
        self.txt_sdt_bn.setStyleSheet(INP)

        f1.addRow("Họ tên (*):", self.txt_hoten)
        f1.addRow("Ngày sinh:", self.date_ngaysinh)
        f1.addRow("Địa chỉ:", self.txt_diachi)
        f1.addRow("SĐT:", self.txt_sdt_bn)  # THÊM MỚI
        body.addWidget(grp1)

        # --- Dịch vụ & Gói khám ---
        grp2 = QGroupBox("Dịch vụ & Gói khám")
        v2 = QVBoxLayout(grp2)
        v2.setSpacing(8)

        dv_row = QHBoxLayout()
        lbl_dv = QLabel("Dịch vụ:")
        lbl_dv.setFixedWidth(90)
        lbl_dv.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.cmb_dichvu = QComboBox()
        self.cmb_dichvu.setFixedHeight(32)
        self.cmb_dichvu.setStyleSheet(INP)
        dv_row.addWidget(lbl_dv)
        dv_row.addWidget(self.cmb_dichvu)
        v2.addLayout(dv_row)

        # 3 nút gói khám
        self.btn_goi_bs = QPushButton("Bác sĩ\n0đ")
        self.btn_goi_ths = QPushButton("Thạc sĩ\n0đ")
        self.btn_goi_ts = QPushButton("Tiến sĩ\n0đ")
        self._goi_btns = [self.btn_goi_bs,
                          self.btn_goi_ths,
                          self.btn_goi_ts]
        self._BTN_ACT = ("border:2px solid #0F6E56;border-radius:6px;"
                         "padding:6px;font-size:11px;"
                         "background:#E1F5EE;font-weight:bold;")
        self._BTN_INACT = ("border:1px solid #ccc;border-radius:6px;"
                           "padding:6px;font-size:11px;background:white;")
        goi_row = QHBoxLayout()
        goi_row.setSpacing(6)
        for b in self._goi_btns:
            b.setFixedHeight(50)
            b.setStyleSheet(self._BTN_INACT)
            goi_row.addWidget(b)
        self.btn_goi_bs.setStyleSheet(self._BTN_ACT)
        v2.addLayout(goi_row)

        self.lbl_gia = QLabel("Phí khám          0 VND")
        self.lbl_gia.setFixedHeight(34)
        self.lbl_gia.setStyleSheet(
            "background:#E1F5EE;border:1px solid #5DCAA5;"
            "border-radius:6px;padding:0 12px;"
            "font-size:12px;font-weight:bold;color:#085041;")
        v2.addWidget(self.lbl_gia)
        body.addWidget(grp2)

        # --- Lịch khám ---
        grp3 = QGroupBox("Lịch khám")
        f3 = QFormLayout(grp3)
        f3.setSpacing(8)
        f3.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.date_ngaykham = QDateEdit()
        self.date_ngaykham.setCalendarPopup(True)
        self.date_ngaykham.setDisplayFormat("dd/MM/yyyy")
        self.date_ngaykham.setDate(QDate.currentDate())
        self.date_ngaykham.setFixedHeight(32)
        self.date_ngaykham.setStyleSheet(INP)

        self.time_giokham = QTimeEdit()
        self.time_giokham.setDisplayFormat("HH:mm")
        self.time_giokham.setTime(QTime(8, 0))
        self.time_giokham.setFixedHeight(32)
        self.time_giokham.setStyleSheet(INP)

        self.lbl_ma = QLabel("LK001")
        self.lbl_ma.setStyleSheet(
            "color:#0F6E56;font-weight:bold;"
            "background:#E1F5EE;border-radius:4px;padding:3px 8px;")

        f3.addRow("Ngày khám:", self.date_ngaykham)
        f3.addRow("Giờ khám:", self.time_giokham)
        f3.addRow("Mã lịch:", self.lbl_ma)
        body.addWidget(grp3)

        # Nút
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_huy = QPushButton("Hủy bỏ")
        self.btn_huy.setFixedSize(90, 34)
        self.btn_huy.setStyleSheet(
            "border:1px solid #ccc;border-radius:5px;font-size:12px;")
        self.btn_datlich = QPushButton("Đặt lịch")
        self.btn_datlich.setFixedSize(110, 34)
        self.btn_datlich.setDefault(True)
        self.btn_datlich.setStyleSheet(
            "background:#0F6E56;color:white;"
            "border-radius:5px;font-size:12px;font-weight:bold;")
        btn_row.addWidget(self.btn_huy)
        btn_row.addWidget(self.btn_datlich)
        body.addLayout(btn_row)
        root.addLayout(body)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QDialog

    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_FormDatLich()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())