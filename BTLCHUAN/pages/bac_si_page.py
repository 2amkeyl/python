"""
pages/bac_si_page.py
────────────────────
UI quản lý bác sĩ.  Logic → BacSiLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QMessageBox, QFrame, QTextEdit, QTabWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import BacSiLogic


class BacSiPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 20, 25, 20)
        lay.setSpacing(15)

        hr = QHBoxLayout()
        title = QLabel("👨‍⚕️ QUẢN LÝ BÁC SĨ")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        btn_add = QPushButton("➕ Thêm bác sĩ")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        lay.addLayout(hr)

        ff = QFrame()
        ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm tên bác sĩ, chuyên khoa...")
        self.searchInput.setMinimumHeight(36)
        self.searchInput.setStyleSheet(INPUT_STYLE)
        self.searchInput.textChanged.connect(self.load_data)
        self.cmbKhoa = QComboBox()
        self.cmbKhoa.setMinimumHeight(36)
        self.cmbKhoa.setStyleSheet(INPUT_STYLE)
        self.cmbKhoa.addItem("Tất cả khoa", None)
        for k in BacSiLogic.get_khoa_list():
            self.cmbKhoa.addItem(k["ten_khoa"], k["ma_khoa"])
        self.cmbKhoa.currentIndexChanged.connect(self.load_data)
        btn_ref = QPushButton("🔄")
        btn_ref.setFixedSize(36, 36)
        btn_ref.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_ref.clicked.connect(self.load_data)
        fl.addWidget(QLabel("Tìm:"))
        fl.addWidget(self.searchInput, 2)
        fl.addWidget(QLabel("Khoa:"))
        fl.addWidget(self.cmbKhoa)
        fl.addWidget(btn_ref)
        lay.addWidget(ff)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Họ tên", "Khoa", "Chuyên khoa",
            "SĐT", "Học hàm", "Tài khoản", "Thao tác",
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

    def load_data(self):
        kw = self.searchInput.text().strip()
        ma_khoa = self.cmbKhoa.currentData()
        rows = BacSiLogic.get_all(kw, ma_khoa)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            has_tk = bool(r.get("ma_tk"))
            tk_text = r["ten_dang_nhap"] if has_tk else "❌ Chưa có"
            vals = [
                str(r["ma_bs"]), r["ho_ten"],
                r.get("ten_khoa") or "—", r.get("chuyen_khoa") or "—",
                r.get("so_dien_thoai") or "—", r.get("hoc_ham") or "—", tk_text,
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 6:
                    item.setBackground(
                        QColor("#d4edda") if has_tk else QColor("#f8d7da"))
                self.table.setItem(i, j, item)

            row_copy = dict(r)
            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2); bl.setSpacing(4)
            btn_e = QPushButton("✏️")
            btn_e.setFixedSize(32, 28)
            btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;")
            btn_e.clicked.connect(lambda _, d=row_copy: self._edit(d))
            btn_d = QPushButton("🗑️")
            btn_d.setFixedSize(32, 28)
            btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;")
            btn_d.clicked.connect(lambda _, mid=r["ma_bs"]: self._delete(mid))
            bl.addWidget(btn_e); bl.addWidget(btn_d)
            self.table.setCellWidget(i, 7, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = BacSiDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, data):
        dlg = BacSiDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_bs):
        r = QMessageBox.question(
            self, "Xác nhận",
            "Xóa bác sĩ sẽ xóa cả tài khoản liên kết. Bạn chắc chắn?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            BacSiLogic.delete(ma_bs)
            self.load_data()


class BacSiDialog(QDialog):
    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.data = data
        self._khoa_list = BacSiLogic.get_khoa_list()
        self.setWindowTitle("Sửa bác sĩ" if data else "Thêm bác sĩ mới")
        self.setMinimumWidth(500)
        self.setMinimumHeight(480)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)
        tabs = QTabWidget()

        # Tab 1: Thông tin
        tab1 = QWidget()
        f1 = QFormLayout(tab1)
        f1.setSpacing(12); f1.setContentsMargins(12, 12, 12, 12)
        self.inpHoTen      = QLineEdit(); self.inpHoTen.setMinimumHeight(34)
        self.cmbKhoa       = QComboBox(); self.cmbKhoa.setMinimumHeight(34)
        self.cmbKhoa.addItem("— Chọn khoa —", None)
        for k in self._khoa_list:
            self.cmbKhoa.addItem(k["ten_khoa"], k["ma_khoa"])
        self.inpChuyenKhoa = QLineEdit(); self.inpChuyenKhoa.setMinimumHeight(34)
        self.inpSDT        = QLineEdit(); self.inpSDT.setMinimumHeight(34)
        self.inpEmail      = QLineEdit(); self.inpEmail.setMinimumHeight(34)
        self.inpHocHam     = QLineEdit(); self.inpHocHam.setMinimumHeight(34)
        self.inpHocHam.setPlaceholderText("Tiến sĩ / Thạc sĩ...")
        self.txtLich       = QTextEdit(); self.txtLich.setMaximumHeight(70)
        self.cmbTT         = QComboBox(); self.cmbTT.setMinimumHeight(34)
        self.cmbTT.addItems(["Đang làm việc", "Ngừng"])
        f1.addRow("Họ tên *:",      self.inpHoTen)
        f1.addRow("Khoa:",          self.cmbKhoa)
        f1.addRow("Chuyên khoa:",   self.inpChuyenKhoa)
        f1.addRow("SĐT:",           self.inpSDT)
        f1.addRow("Email:",         self.inpEmail)
        f1.addRow("Học hàm:",       self.inpHocHam)
        f1.addRow("Lịch làm việc:", self.txtLich)
        f1.addRow("Trạng thái:",    self.cmbTT)
        tabs.addTab(tab1, "👨‍⚕️ Thông tin bác sĩ")

        # Tab 2: Tài khoản
        tab2 = QWidget()
        f2 = QFormLayout(tab2)
        f2.setSpacing(12); f2.setContentsMargins(12, 12, 12, 12)
        self.lblTKStatus = QLabel()
        self.lblTKStatus.setWordWrap(True)
        self.inpTenDN   = QLineEdit(); self.inpTenDN.setMinimumHeight(34)
        self.inpTenDN.setPlaceholderText("Tên đăng nhập (không dấu, không khoảng trắng)")
        self.inpMatKhau = QLineEdit(); self.inpMatKhau.setMinimumHeight(34)
        self.inpMatKhau.setEchoMode(QLineEdit.EchoMode.Password)
        self.inpXacNhan = QLineEdit(); self.inpXacNhan.setMinimumHeight(34)
        self.inpXacNhan.setEchoMode(QLineEdit.EchoMode.Password)
        hint = QLabel(
            "• Thêm mới: bắt buộc nhập tên đăng nhập và mật khẩu\n"
            "• Sửa: để trống mật khẩu = giữ nguyên\n"
            "• Tên đăng nhập không thể thay đổi sau khi tạo")
        hint.setStyleSheet("color:#7f8c8d;font-size:11px;")
        hint.setWordWrap(True)
        f2.addRow("Trạng thái:",      self.lblTKStatus)
        f2.addRow("Tên đăng nhập *:", self.inpTenDN)
        f2.addRow("Mật khẩu *:",      self.inpMatKhau)
        f2.addRow("Xác nhận MK:",     self.inpXacNhan)
        f2.addRow("", hint)
        tabs.addTab(tab2, "🔑 Tài khoản đăng nhập")

        root.addWidget(tabs)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Lưu")
        bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        root.addLayout(btn_row)
        self.setStyleSheet(FORM_STYLE)

    def _fill(self, d):
        self.inpHoTen.setText(d.get("ho_ten", ""))
        self.inpChuyenKhoa.setText(d.get("chuyen_khoa", "") or "")
        self.inpSDT.setText(d.get("so_dien_thoai", "") or "")
        self.inpEmail.setText(d.get("email", "") or "")
        self.inpHocHam.setText(d.get("hoc_ham", "") or "")
        self.txtLich.setPlainText(d.get("lich_lam_viec", "") or "")
        self.cmbTT.setCurrentIndex(0 if d.get("trang_thai", 1) == 1 else 1)
        for i in range(self.cmbKhoa.count()):
            if self.cmbKhoa.itemData(i) == d.get("ma_khoa"):
                self.cmbKhoa.setCurrentIndex(i); break
        if d.get("ma_tk"):
            ten_dn = d.get("ten_dang_nhap", "")
            self.lblTKStatus.setText(f"✅ Đã có tài khoản: <b>{ten_dn}</b>")
            self.lblTKStatus.setStyleSheet("color:#27ae60;")
            self.inpTenDN.setText(ten_dn)
            self.inpTenDN.setReadOnly(True)
            self.inpMatKhau.setPlaceholderText("Để trống = giữ nguyên mật khẩu cũ")
            self.inpXacNhan.setPlaceholderText("Để trống = giữ nguyên mật khẩu cũ")
        else:
            self.lblTKStatus.setText("❌ Chưa có tài khoản — hãy tạo ở đây")
            self.lblTKStatus.setStyleSheet("color:#e74c3c;")

    def _save(self):
        ho_ten = self.inpHoTen.text().strip()
        if not ho_ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên bác sĩ!")
            return
        ma_khoa     = self.cmbKhoa.currentData()
        chuyen_khoa = self.inpChuyenKhoa.text().strip()
        sdt         = self.inpSDT.text().strip()
        email       = self.inpEmail.text().strip()
        hoc_ham     = self.inpHocHam.text().strip()
        lich        = self.txtLich.toPlainText().strip()
        trang_thai  = 1 if self.cmbTT.currentIndex() == 0 else 0
        ten_dn      = self.inpTenDN.text().strip()
        mat_khau    = self.inpMatKhau.text().strip()
        xac_nhan    = self.inpXacNhan.text().strip()

        if not self.data:  # Thêm mới
            if not ten_dn:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập!")
                return
            if not mat_khau:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
                return
            if mat_khau != xac_nhan:
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            ok, msg = BacSiLogic.insert(ten_dn, mat_khau, ho_ten, ma_khoa,
                                         chuyen_khoa, sdt, email, hoc_ham,
                                         lich, trang_thai)
            if not ok:
                QMessageBox.critical(self, "Lỗi", msg)
                return
            QMessageBox.information(self, "Thành công", msg)
        else:  # Sửa
            if mat_khau and mat_khau != xac_nhan:
                QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            BacSiLogic.update(self.data["ma_bs"], ho_ten, ma_khoa, chuyen_khoa,
                               sdt, email, hoc_ham, lich, trang_thai)
            has_tk = self.data.get("ma_tk")
            if mat_khau and has_tk:
                BacSiLogic.update_password(has_tk, mat_khau)
            if not has_tk and ten_dn and mat_khau:
                ok, msg = BacSiLogic.create_account_for_bs(
                    self.data["ma_bs"], ten_dn, mat_khau)
                if not ok:
                    QMessageBox.warning(self, "Cảnh báo",
                        f"{msg}\nThông tin bác sĩ đã lưu nhưng chưa tạo được tài khoản.")
        self.accept()
