"""
pages/thuoc_page.py
───────────────────
UI quản lý thuốc.  Logic → ThuocLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QTextEdit, QMessageBox, QFrame,
    QSpinBox, QDoubleSpinBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import ThuocLogic


class ThuocPage(QWidget):
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
        title = QLabel("💊 QUẢN LÝ THUỐC")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        btn_add = QPushButton("➕ Thêm thuốc")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        lay.addLayout(hr)

        ff = QFrame()
        ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm kiếm tên thuốc...")
        self.searchInput.setMinimumHeight(36)
        self.searchInput.setStyleSheet(INPUT_STYLE)
        self.searchInput.textChanged.connect(self.load_data)
        btn_ref = QPushButton("🔄 Làm mới")
        btn_ref.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_ref.clicked.connect(self.load_data)
        fl.addWidget(QLabel("Tìm:"))
        fl.addWidget(self.searchInput, 2)
        fl.addWidget(btn_ref)
        lay.addWidget(ff)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Tên thuốc", "Đơn vị", "Mô tả",
            "Đơn giá", "Tồn kho", "Thao tác",
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
        rows = ThuocLogic.get_all(kw)
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            gia = f"{int(row.get('gia', 0) or 0):,} đ"
            ton = int(row.get("so_luong_ton", 0) or 0)
            vals = [
                str(row["ma_thuoc"]), row["ten_thuoc"],
                row.get("don_vi", "") or "",
                (row.get("mo_ta", "") or "")[:60],
                gia, str(ton),
            ]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 5 and ton < 50:
                    item.setForeground(QColor("#e74c3c"))
                self.table.setItem(i, j, item)

            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            btn_e = QPushButton("✏️")
            btn_e.setFixedSize(32, 28)
            btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;font-size:14px;")
            btn_e.clicked.connect(lambda _, r=row: self._edit(r))
            btn_d = QPushButton("🗑️")
            btn_d.setFixedSize(32, 28)
            btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;font-size:14px;")
            btn_d.clicked.connect(lambda _, mid=row["ma_thuoc"]: self._delete(mid))
            bl.addWidget(btn_e)
            bl.addWidget(btn_d)
            self.table.setCellWidget(i, 6, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = ThuocDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, data):
        dlg = ThuocDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_thuoc):
        r = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa thuốc này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            ThuocLogic.delete(ma_thuoc)
            self.load_data()


class ThuocDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm thuốc" if not data else "Sửa thuốc")
        self.setMinimumWidth(420)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(25, 20, 25, 20)

        title = QLabel("💊 " + ("Thêm Thuốc Mới" if not self.data else "Sửa Thông Tin Thuốc"))
        title.setStyleSheet("font-size:16px;font-weight:bold;color:#1a5276;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.inpTen = QLineEdit()
        self.inpTen.setPlaceholderText("Tên thuốc...")
        self.inpTen.setMinimumHeight(36)
        self.inpTen.setStyleSheet(INPUT_STYLE)

        self.inpDonVi = QLineEdit()
        self.inpDonVi.setPlaceholderText("VD: Viên, Chai, Ống...")
        self.inpDonVi.setMinimumHeight(36)
        self.inpDonVi.setStyleSheet(INPUT_STYLE)

        self.inpMoTa = QTextEdit()
        self.inpMoTa.setPlaceholderText("Mô tả, công dụng...")
        self.inpMoTa.setMaximumHeight(80)
        self.inpMoTa.setStyleSheet(INPUT_STYLE)

        self.spGia = QDoubleSpinBox()
        self.spGia.setMinimumHeight(36)
        self.spGia.setMaximum(99_999_999)
        self.spGia.setDecimals(0)
        self.spGia.setSuffix(" đ")
        self.spGia.setStyleSheet(INPUT_STYLE)

        self.spSoLuong = QSpinBox()
        self.spSoLuong.setMinimumHeight(36)
        self.spSoLuong.setMaximum(999_999)
        self.spSoLuong.setSuffix(" (đơn vị)")
        self.spSoLuong.setStyleSheet(INPUT_STYLE)

        form.addRow("Tên thuốc *:",    self.inpTen)
        form.addRow("Đơn vị:",         self.inpDonVi)
        form.addRow("Mô tả:",          self.inpMoTa)
        form.addRow("Đơn giá:",        self.spGia)
        form.addRow("Số lượng tồn:",   self.spSoLuong)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Lưu")
        bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(bs)
        lay.addLayout(btn_row)
        self.setStyleSheet(FORM_STYLE)

    def _fill(self, d):
        self.inpTen.setText(d.get("ten_thuoc", ""))
        self.inpDonVi.setText(d.get("don_vi", "") or "")
        self.inpMoTa.setPlainText(d.get("mo_ta", "") or "")
        self.spGia.setValue(float(d.get("gia", 0) or 0))
        self.spSoLuong.setValue(int(d.get("so_luong_ton", 0) or 0))

    def _save(self):
        ten = self.inpTen.text().strip()
        if not ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên thuốc!")
            return
        don_vi   = self.inpDonVi.text().strip()
        mo_ta    = self.inpMoTa.toPlainText().strip()
        gia      = self.spGia.value()
        so_luong = self.spSoLuong.value()

        if not self.data:
            ThuocLogic.insert(ten, don_vi, mo_ta, gia, so_luong)
        else:
            ThuocLogic.update(self.data["ma_thuoc"], ten, don_vi, mo_ta, gia, so_luong)
        self.accept()
