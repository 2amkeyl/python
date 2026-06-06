"""
pages/tai_khoan_page.py
───────────────────────
UI quản lý tài khoản.  Logic → TaiKhoanLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QMessageBox, QFrame, QCheckBox,
)
from PyQt6.QtCore import Qt

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import TaiKhoanLogic


class TaiKhoanPage(QWidget):
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
        title = QLabel("🔑 QUẢN LÝ TÀI KHOẢN")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        if self.user_info.get("vai_tro") == "admin":
            btn_add = QPushButton("➕ Thêm tài khoản")
            btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
            btn_add.clicked.connect(self._add)
            hr.addWidget(btn_add)
        lay.addLayout(hr)

        ff = QFrame()
        ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm kiếm tên đăng nhập...")
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
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Tên đăng nhập", "Vai trò", "Trạng thái", "Thao tác",
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        lay.addWidget(self.table)

    def load_data(self):
        kw = self.searchInput.text().strip()
        rows = TaiKhoanLogic.get_all(kw)
        vt_display = {
            "admin":  "👑 Quản trị viên",
            "bac_si": "👨‍⚕️ Bác sĩ",
            "le_tan": "🏥 Lễ tân",
        }
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            trang_thai = "✅ Hoạt động" if row.get("trang_thai") else "❌ Khóa"
            vals = [
                str(row["ma_tk"]), row["ten_dang_nhap"],
                vt_display.get(row.get("vai_tro", ""), row.get("vai_tro", "")),
                trang_thai,
            ]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            if self.user_info.get("vai_tro") == "admin":
                btn_e = QPushButton("✏️")
                btn_e.setFixedSize(32, 28)
                btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;font-size:14px;")
                btn_e.clicked.connect(lambda _, r=row: self._edit(r))
                btn_d = QPushButton("🗑️")
                btn_d.setFixedSize(32, 28)
                btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;font-size:14px;")
                btn_d.clicked.connect(lambda _, rid=row["ma_tk"]: self._delete(rid))
                bl.addWidget(btn_e)
                bl.addWidget(btn_d)
            self.table.setCellWidget(i, 4, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = TaiKhoanDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, data):
        dlg = TaiKhoanDialog(self, data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_tk):
        if ma_tk == self.user_info.get("ma_tk"):
            QMessageBox.warning(self, "Lỗi", "Không thể xóa tài khoản đang đăng nhập!")
            return
        r = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa tài khoản này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            TaiKhoanLogic.delete(ma_tk)
            self.load_data()


class TaiKhoanDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm tài khoản" if not data else "Sửa tài khoản")
        self.setMinimumWidth(400)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(25, 20, 25, 20)

        title = QLabel("🔑 " + ("Thêm Tài Khoản Mới" if not self.data else "Sửa Tài Khoản"))
        title.setStyleSheet("font-size:16px;font-weight:bold;color:#1a5276;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.inpUsername = QLineEdit()
        self.inpUsername.setPlaceholderText("Tên đăng nhập...")
        self.inpUsername.setMinimumHeight(36)
        self.inpUsername.setStyleSheet(INPUT_STYLE)

        self.inpPassword = QLineEdit()
        self.inpPassword.setPlaceholderText(
            "Mật khẩu..." + (" (bỏ trống = giữ nguyên)" if self.data else ""))
        self.inpPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.inpPassword.setMinimumHeight(36)
        self.inpPassword.setStyleSheet(INPUT_STYLE)

        self.cmbVaiTro = QComboBox()
        self.cmbVaiTro.addItems(["Lễ tân", "Bác sĩ", "Quản trị viên"])
        self.cmbVaiTro.setMinimumHeight(36)
        self.cmbVaiTro.setStyleSheet(INPUT_STYLE)

        self.chkActive = QCheckBox("Tài khoản đang hoạt động")
        self.chkActive.setChecked(True)

        form.addRow("Tên đăng nhập *:", self.inpUsername)
        form.addRow("Mật khẩu *:",      self.inpPassword)
        form.addRow("Vai trò:",          self.cmbVaiTro)
        form.addRow("Trạng thái:",       self.chkActive)
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
        self.inpUsername.setText(d.get("ten_dang_nhap", ""))
        vt_map = {"le_tan": 0, "bac_si": 1, "admin": 2}
        self.cmbVaiTro.setCurrentIndex(vt_map.get(d.get("vai_tro", "le_tan"), 0))
        self.chkActive.setChecked(bool(d.get("trang_thai", 1)))

    def _save(self):
        username = self.inpUsername.text().strip()
        password = self.inpPassword.text().strip()
        if not username:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        if not self.data and not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu!")
            return
        vt_vals    = ["le_tan", "bac_si", "admin"]
        vai_tro    = vt_vals[self.cmbVaiTro.currentIndex()]
        trang_thai = 1 if self.chkActive.isChecked() else 0

        if not self.data:
            TaiKhoanLogic.insert(username, password, vai_tro, trang_thai)
        else:
            TaiKhoanLogic.update(self.data["ma_tk"], username,
                                  vai_tro, trang_thai, password)
        self.accept()
