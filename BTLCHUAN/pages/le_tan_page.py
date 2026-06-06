"""
pages/le_tan_page.py
────────────────────
UI quản lý lễ tân.  Logic → LeTanLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QMessageBox,
)
from PyQt6.QtCore import Qt

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import LeTanLogic


class LeTanPage(QWidget):
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
        title = QLabel("👩‍💼 QUẢN LÝ LỄ TÂN")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        btn_add = QPushButton("➕ Thêm lễ tân")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        lay.addLayout(hr)

        fl_h = QHBoxLayout()
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm theo tên / SĐT...")
        self.searchInput.setMinimumHeight(36)
        self.searchInput.setStyleSheet(INPUT_STYLE)
        self.searchInput.textChanged.connect(self.load_data)
        fl_h.addWidget(QLabel("Tìm:"))
        fl_h.addWidget(self.searchInput, 2)
        btn_ref = QPushButton("🔄 Làm mới")
        btn_ref.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_ref.clicked.connect(self.load_data)
        fl_h.addWidget(btn_ref)
        lay.addLayout(fl_h)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Họ tên", "Tài khoản", "SĐT",
            "Email", "Ca làm việc", "Trạng thái", "Thao tác",
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
        rows = LeTanLogic.get_all(kw)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            keys = ["ma_lt", "ho_ten", "ten_dang_nhap",
                    "so_dien_thoai", "email", "ca_lam_viec", "trang_thai"]
            for j, k in enumerate(keys):
                item = QTableWidgetItem(str(r.get(k) or ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2); bl.setSpacing(4)
            btn_e = QPushButton("✏️")
            btn_e.setFixedSize(32, 28)
            btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;")
            btn_e.clicked.connect(lambda _, mid=r["ma_lt"]: self._edit(mid))
            btn_d = QPushButton("🗑️")
            btn_d.setFixedSize(32, 28)
            btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;")
            btn_d.clicked.connect(lambda _, mid=r["ma_lt"]: self._delete(mid))
            bl.addWidget(btn_e); bl.addWidget(btn_d)
            self.table.setCellWidget(i, 7, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = LeTanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, ma_lt):
        data = LeTanLogic.get_full(ma_lt)
        if not data:
            return
        dlg = LeTanDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_lt):
        r = QMessageBox.question(self, "Xác nhận", "Xóa lễ tân này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            LeTanLogic.delete(ma_lt)
            self.load_data()


class LeTanDialog(QDialog):
    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm lễ tân" if not data else "Sửa thông tin lễ tân")
        self.setMinimumWidth(420)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        form = QFormLayout()
        self.inpHoTen    = QLineEdit(); self.inpHoTen.setMinimumHeight(34)
        self.inpSDT      = QLineEdit(); self.inpSDT.setMinimumHeight(34)
        self.inpEmail    = QLineEdit(); self.inpEmail.setMinimumHeight(34)
        self.inpCa       = QLineEdit(); self.inpCa.setMinimumHeight(34)
        self.inpCa.setPlaceholderText("vd: Ca sáng 7h-12h")
        self.cmbTT       = QComboBox(); self.cmbTT.setMinimumHeight(34)
        self.cmbTT.addItems(["Hoạt động", "Ngừng"])
        self.inpTenDN    = QLineEdit(); self.inpTenDN.setMinimumHeight(34)
        self.inpMatKhau  = QLineEdit(); self.inpMatKhau.setMinimumHeight(34)
        self.inpMatKhau.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Họ tên *:",        self.inpHoTen)
        form.addRow("SĐT:",             self.inpSDT)
        form.addRow("Email:",           self.inpEmail)
        form.addRow("Ca làm việc:",     self.inpCa)
        form.addRow("Trạng thái:",      self.cmbTT)
        form.addRow("Tên đăng nhập *:", self.inpTenDN)
        form.addRow("Mật khẩu *:",      self.inpMatKhau)

        if self.data:
            self.inpTenDN.setReadOnly(True)
            self.inpMatKhau.setPlaceholderText("(để trống = giữ nguyên)")

        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Lưu")
        bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        lay.addLayout(btn_row)
        self.setStyleSheet(FORM_STYLE)

    def _fill(self, d):
        self.inpHoTen.setText(d.get("ho_ten", ""))
        self.inpSDT.setText(d.get("so_dien_thoai", "") or "")
        self.inpEmail.setText(d.get("email", "") or "")
        self.inpCa.setText(d.get("ca_lam_viec", "") or "")
        self.cmbTT.setCurrentIndex(0 if d.get("trang_thai", 1) == 1 else 1)
        self.inpTenDN.setText(d.get("ten_dang_nhap", ""))

    def _save(self):
        ho_ten   = self.inpHoTen.text().strip()
        ten_dn   = self.inpTenDN.text().strip()
        mat_khau = self.inpMatKhau.text().strip()
        if not ho_ten or not ten_dn:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Họ tên và Tên đăng nhập!")
            return
        trang_thai = 1 if self.cmbTT.currentIndex() == 0 else 0
        sdt   = self.inpSDT.text().strip()
        email = self.inpEmail.text().strip()
        ca    = self.inpCa.text().strip()

        if not self.data:
            if not mat_khau:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
                return
            ok, msg = LeTanLogic.insert(ten_dn, mat_khau, ho_ten,
                                         sdt, email, ca, trang_thai)
            if not ok:
                QMessageBox.critical(self, "Lỗi", msg)
                return
        else:
            LeTanLogic.update(self.data["ma_lt"], self.data["ma_tk"],
                               ho_ten, sdt, email, ca, trang_thai, mat_khau)
        self.accept()
