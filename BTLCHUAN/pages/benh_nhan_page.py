"""
pages/benh_nhan_page.py
───────────────────────
UI quản lý bệnh nhân.  Logic → BenhNhanLogic.  Phân quyền → RoleLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QMessageBox, QFrame,
    QDateEdit, QTextEdit,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import BenhNhanLogic, RoleLogic


class BenhNhanPage(QWidget):
    def __init__(self, user_info: dict):
        super().__init__()
        self.user_info = user_info
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 20, 25, 20)
        lay.setSpacing(15)

        # Header
        hr = QHBoxLayout()
        title = QLabel("👤 QUẢN LÝ BỆNH NHÂN")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        if RoleLogic.can_edit(self.user_info, "benh_nhan"):
            btn_add = QPushButton("➕ Thêm bệnh nhân")
            btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
            btn_add.clicked.connect(self._add)
            hr.addWidget(btn_add)
        lay.addLayout(hr)

        # Filter
        ff = QFrame()
        ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm tên, SĐT, email...")
        self.searchInput.setMinimumHeight(36)
        self.searchInput.setStyleSheet(INPUT_STYLE)
        self.searchInput.textChanged.connect(self.load_data)
        self.cmbGioiTinh = QComboBox()
        self.cmbGioiTinh.setMinimumHeight(36)
        self.cmbGioiTinh.addItems(["Tất cả", "Nam", "Nữ", "Khác"])
        self.cmbGioiTinh.currentIndexChanged.connect(self.load_data)
        btn_ref = QPushButton("🔄")
        btn_ref.setFixedSize(36, 36)
        btn_ref.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_ref.clicked.connect(self.load_data)
        fl.addWidget(QLabel("Tìm:"))
        fl.addWidget(self.searchInput, 2)
        fl.addWidget(QLabel("Giới tính:"))
        fl.addWidget(self.cmbGioiTinh)
        fl.addWidget(btn_ref)
        lay.addWidget(ff)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Họ tên", "Ngày sinh", "Giới tính",
            "SĐT", "Email", "Bảo hiểm", "Số lần khám", "Thao tác",
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

    def load_data(self):
        kw = self.searchInput.text().strip()
        gt = self.cmbGioiTinh.currentText()
        rows = BenhNhanLogic.get_all(kw, gt)

        self.table.setRowCount(0)
        for i, r in enumerate(rows):
            self.table.insertRow(i)
            ns = ""
            if r["ngay_sinh"]:
                try:
                    ns = r["ngay_sinh"].strftime("%d/%m/%Y")
                except Exception:
                    ns = str(r["ngay_sinh"])
            so_lan = int(r.get("so_lan_kham") or 0)
            vals = [
                str(r["ma_bn"]), r["ho_ten"], ns,
                r.get("gioi_tinh") or "—",
                r.get("so_dien_thoai") or "—",
                r.get("email") or "—",
                r.get("so_bao_hiem") or "—",
                str(so_lan),
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 7:
                    if so_lan == 0:
                        item.setForeground(QColor("#95a5a6"))
                    elif so_lan >= 5:
                        item.setForeground(QColor("#1a5276"))
                        item.setFont(QFont("", -1, 75))
                    else:
                        item.setForeground(QColor("#27ae60"))
                self.table.setItem(i, j, item)

            row_copy = dict(r)
            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            if RoleLogic.can_edit(self.user_info, "benh_nhan"):
                btn_e = QPushButton("✏️")
                btn_e.setFixedSize(32, 28)
                btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;")
                btn_e.clicked.connect(lambda _, d=row_copy: self._edit(d))
                btn_d = QPushButton("🗑️")
                btn_d.setFixedSize(32, 28)
                btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;")
                btn_d.clicked.connect(lambda _, mid=r["ma_bn"]: self._delete(mid))
                bl.addWidget(btn_e)
                bl.addWidget(btn_d)
            else:
                btn_v = QPushButton("👁")
                btn_v.setFixedSize(32, 28)
                btn_v.setStyleSheet("background:#7f8c8d;color:white;border-radius:4px;")
                btn_v.clicked.connect(lambda _, d=row_copy: self._view(d))
                bl.addWidget(btn_v)
            self.table.setCellWidget(i, 8, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = BenhNhanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, data):
        dlg = BenhNhanDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _view(self, data):
        dlg = BenhNhanDialog(self, data, readonly=True)
        dlg.exec()

    def _delete(self, ma_bn):
        r = QMessageBox.question(self, "Xác nhận", "Xóa bệnh nhân này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            BenhNhanLogic.delete(ma_bn)
            self.load_data()


class BenhNhanDialog(QDialog):
    def __init__(self, parent, data=None, readonly=False):
        super().__init__(parent)
        self.data = data
        self.readonly = readonly
        self.setWindowTitle(
            "Thông tin bệnh nhân" if readonly
            else ("Thêm bệnh nhân" if not data else "Sửa thông tin bệnh nhân")
        )
        self.setMinimumWidth(460)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        title = QLabel("👤 " + ("Thêm Bệnh Nhân Mới" if not self.data
                                else "Sửa Thông Tin Bệnh Nhân"))
        title.setStyleSheet("font-size:15px;font-weight:bold;color:#1a5276;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        if not self.data and not self.readonly:
            self.inpMaBN = QLineEdit()
            self.inpMaBN.setMinimumHeight(34)
            self.inpMaBN.setPlaceholderText("Nhập mã bệnh nhân...")
            form.addRow("Mã bệnh nhân *:", self.inpMaBN)

        self.inpHoTen   = QLineEdit(); self.inpHoTen.setMinimumHeight(34)
        self.dateSinh   = QDateEdit()
        self.dateSinh.setMinimumHeight(34)
        self.dateSinh.setCalendarPopup(True)
        self.dateSinh.setDisplayFormat("dd/MM/yyyy")
        self.dateSinh.setDate(QDate(1990, 1, 1))
        self.cmbGT      = QComboBox(); self.cmbGT.setMinimumHeight(34)
        self.cmbGT.addItems(["Nam", "Nữ", "Khác"])
        self.inpSDT     = QLineEdit(); self.inpSDT.setMinimumHeight(34)
        self.inpEmail   = QLineEdit(); self.inpEmail.setMinimumHeight(34)
        self.inpBH      = QLineEdit(); self.inpBH.setMinimumHeight(34)
        self.inpBH.setPlaceholderText("Số thẻ bảo hiểm y tế")
        self.txtDiaChi  = QTextEdit(); self.txtDiaChi.setMaximumHeight(70)

        form.addRow("Họ tên *:",  self.inpHoTen)
        form.addRow("Ngày sinh:", self.dateSinh)
        form.addRow("Giới tính:", self.cmbGT)
        form.addRow("SĐT:",       self.inpSDT)
        form.addRow("Email:",     self.inpEmail)
        form.addRow("Bảo hiểm:", self.inpBH)
        form.addRow("Địa chỉ:",   self.txtDiaChi)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Đóng" if self.readonly else "Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        btn_row.addWidget(bc)
        if not self.readonly:
            bs = QPushButton("💾 Lưu")
            bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
            bs.clicked.connect(self._save)
            btn_row.addWidget(bs)
        lay.addLayout(btn_row)

        if self.readonly:
            for w in [self.inpHoTen, self.inpSDT, self.inpEmail,
                      self.inpBH, self.txtDiaChi]:
                w.setReadOnly(True)
            self.dateSinh.setReadOnly(True)
            self.cmbGT.setEnabled(False)

        self.setStyleSheet(FORM_STYLE)

    def _fill(self, d):
        self.inpHoTen.setText(d.get("ho_ten", ""))
        if d.get("ngay_sinh"):
            try:
                ns = d["ngay_sinh"]
                self.dateSinh.setDate(QDate(ns.year, ns.month, ns.day))
            except Exception:
                pass
        gt_map = {"Nam": 0, "Nữ": 1, "Khác": 2}
        self.cmbGT.setCurrentIndex(gt_map.get(d.get("gioi_tinh", "Nam"), 0))
        self.inpSDT.setText(d.get("so_dien_thoai", "") or "")
        self.inpEmail.setText(d.get("email", "") or "")
        self.inpBH.setText(d.get("so_bao_hiem", "") or "")
        self.txtDiaChi.setPlainText(d.get("dia_chi", "") or "")

    def _save(self):
        ho_ten = self.inpHoTen.text().strip()
        if not ho_ten:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ tên!")
            return
        ngay_sinh = self.dateSinh.date().toString("yyyy-MM-dd")
        gioi_tinh = self.cmbGT.currentText()
        sdt    = self.inpSDT.text().strip()
        email  = self.inpEmail.text().strip()
        bh     = self.inpBH.text().strip()
        diachi = self.txtDiaChi.toPlainText().strip()

        if not self.data:
            ma_bn = self.inpMaBN.text().strip()
            if not ma_bn:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã bệnh nhân!")
                return
            if BenhNhanLogic.ma_exists(ma_bn):
                QMessageBox.warning(self, "Lỗi", f"Mã «{ma_bn}» đã tồn tại!")
                return
            BenhNhanLogic.insert(ma_bn, ho_ten, ngay_sinh, gioi_tinh,
                                 sdt, email, bh, diachi)
        else:
            BenhNhanLogic.update(self.data["ma_bn"], ho_ten, ngay_sinh,
                                 gioi_tinh, sdt, email, bh, diachi)
        self.accept()
