"""
pages/dich_vu_page.py
─────────────────────
UI quản lý danh mục dịch vụ.  Logic → DichVuLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QMessageBox, QDoubleSpinBox, QTextEdit,
)
from PyQt6.QtCore import Qt

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import DichVuLogic


class DichVuPage(QWidget):
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
        title = QLabel("🏷️ DANH MỤC DỊCH VỤ")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        btn_add = QPushButton("➕ Thêm dịch vụ")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        lay.addLayout(hr)

        fl_h = QHBoxLayout()
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm tên dịch vụ...")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Tên dịch vụ", "Khoa", "Đơn giá",
            "Đơn vị", "Trạng thái", "Thao tác",
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

    def load_data(self):
        kw = self.searchInput.text().strip()
        rows = DichVuLogic.get_all(kw)
        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            vals = [
                str(r["ma_dv"]), r["ten_dv"],
                r.get("ten_khoa") or "—",
                f"{r['don_gia']:,.0f} đ",
                r.get("don_vi") or "",
                r["tt"],
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2); bl.setSpacing(4)
            btn_e = QPushButton("✏️")
            btn_e.setFixedSize(32, 28)
            btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;")
            btn_e.clicked.connect(lambda _, mid=r["ma_dv"]: self._edit(mid))
            btn_d = QPushButton("🗑️")
            btn_d.setFixedSize(32, 28)
            btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;")
            btn_d.clicked.connect(lambda _, mid=r["ma_dv"]: self._delete(mid))
            bl.addWidget(btn_e); bl.addWidget(btn_d)
            self.table.setCellWidget(i, 6, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = DichVuDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, ma_dv):
        data = DichVuLogic.get_by_id(ma_dv)
        if not data:
            return
        dlg = DichVuDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_dv):
        r = QMessageBox.question(self, "Xác nhận", "Ẩn dịch vụ này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            DichVuLogic.deactivate(ma_dv)
            self.load_data()


class DichVuDialog(QDialog):
    def __init__(self, parent, data=None):
        super().__init__(parent)
        self.data = data
        self._khoa_list = DichVuLogic.get_khoa_list()
        self.setWindowTitle("Thêm dịch vụ" if not data else "Sửa dịch vụ")
        self.setMinimumWidth(420)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        form = QFormLayout()
        self.inpTen    = QLineEdit(); self.inpTen.setMinimumHeight(34)
        self.cmbKhoa   = QComboBox(); self.cmbKhoa.setMinimumHeight(34)
        self.cmbKhoa.addItem("— Không thuộc khoa —", None)
        for k in self._khoa_list:
            self.cmbKhoa.addItem(k["ten_khoa"], k["ma_khoa"])
        self.spDonGia  = QDoubleSpinBox()
        self.spDonGia.setRange(0, 99_999_999)
        self.spDonGia.setSuffix(" đ")
        self.spDonGia.setGroupSeparatorShown(True)
        self.inpDonVi  = QLineEdit()
        self.inpDonVi.setPlaceholderText("lần / ca / giờ ...")
        self.txtMoTa   = QTextEdit(); self.txtMoTa.setMaximumHeight(80)
        self.cmbTT     = QComboBox()
        self.cmbTT.addItems(["Hoạt động", "Ngừng"])

        form.addRow("Tên dịch vụ *:", self.inpTen)
        form.addRow("Khoa:",          self.cmbKhoa)
        form.addRow("Đơn giá *:",     self.spDonGia)
        form.addRow("Đơn vị:",        self.inpDonVi)
        form.addRow("Mô tả:",         self.txtMoTa)
        form.addRow("Trạng thái:",    self.cmbTT)
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
        self.inpTen.setText(d.get("ten_dv", ""))
        self.spDonGia.setValue(float(d.get("don_gia", 0)))
        self.inpDonVi.setText(d.get("don_vi", "") or "")
        self.txtMoTa.setPlainText(d.get("mo_ta", "") or "")
        self.cmbTT.setCurrentIndex(0 if d.get("trang_thai", 1) == 1 else 1)
        ma_khoa = d.get("ma_khoa")
        for i in range(self.cmbKhoa.count()):
            if self.cmbKhoa.itemData(i) == ma_khoa:
                self.cmbKhoa.setCurrentIndex(i); break

    def _save(self):
        ten = self.inpTen.text().strip()
        if not ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên dịch vụ!")
            return
        ma_khoa    = self.cmbKhoa.currentData()
        don_gia    = self.spDonGia.value()
        don_vi     = self.inpDonVi.text().strip() or "lần"
        mo_ta      = self.txtMoTa.toPlainText().strip()
        trang_thai = 1 if self.cmbTT.currentIndex() == 0 else 0

        if not self.data:
            DichVuLogic.insert(ma_khoa, ten, mo_ta, don_gia, don_vi, trang_thai)
        else:
            DichVuLogic.update(self.data["ma_dv"], ma_khoa, ten,
                                mo_ta, don_gia, don_vi, trang_thai)
        self.accept()
