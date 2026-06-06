"""
pages/benh_an_page.py
─────────────────────
UI quản lý bệnh án.  Logic → BenhAnLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QFormLayout, QTextEdit, QMessageBox,
    QFrame, QHBoxLayout,
)
from PyQt6.QtCore import Qt
from datetime import datetime

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, FORM_STYLE
from logic import BenhAnLogic


class BenhAnPage(QWidget):
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
        title = QLabel("📋 QUẢN LÝ BỆNH ÁN")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()
        btn_add = QPushButton("➕ Tạo bệnh án")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        lay.addLayout(hr)

        ff = QFrame()
        ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff)
        self.searchInput = QLineEdit()
        self.searchInput.setPlaceholderText("🔍 Tìm kiếm tên bệnh nhân...")
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
            "Mã BA", "Bệnh nhân", "Bác sĩ", "Ngày khám",
            "Chẩn đoán", "Kết quả", "Thao tác",
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
        rows = BenhAnLogic.get_all(kw)
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            ngay_str = str(row.get("ngay_kham", ""))
            try:
                ngay_str = datetime.strptime(ngay_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                pass
            vals = [
                str(row["ma_ba"]), row["ten_bn"], row["ten_bs"], ngay_str,
                (row.get("chuan_doan") or "")[:60],
                (row.get("ket_qua") or "")[:50],
            ]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

            bf = QWidget()
            bl = QHBoxLayout(bf)
            bl.setContentsMargins(4, 2, 4, 2)
            bl.setSpacing(4)
            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(32, 28)
            btn_view.setStyleSheet("background:#27ae60;color:white;border-radius:4px;font-size:14px;")
            btn_view.setToolTip("Xem chi tiết")
            btn_view.clicked.connect(lambda _, r=row: self._view(r))
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.setStyleSheet("background:#2980b9;color:white;border-radius:4px;font-size:14px;")
            btn_edit.clicked.connect(lambda _, r=row: self._edit(r))
            bl.addWidget(btn_view)
            bl.addWidget(btn_edit)
            self.table.setCellWidget(i, 6, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = BenhAnDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, data):
        dlg = BenhAnDialog(self, data=data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _view(self, row):
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Chi tiết bệnh án #{row['ma_ba']}")
        dlg.setMinimumWidth(500)
        dlg.setStyleSheet("QDialog{background:white;}")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(25, 20, 25, 20)
        lay.setSpacing(12)

        def info_row(label, value):
            frame = QFrame()
            frame.setStyleSheet("background:#f8f9fa;border-radius:6px;padding:8px;")
            fl = QHBoxLayout(frame)
            lbl = QLabel(f"<b>{label}</b>")
            lbl.setMinimumWidth(160)
            val_lbl = QLabel(value or "—")
            val_lbl.setWordWrap(True)
            fl.addWidget(lbl)
            fl.addWidget(val_lbl, 1)
            return frame

        lay.addWidget(QLabel(f"<h3>🏥 Bệnh án #{row['ma_ba']}</h3>"))
        lay.addWidget(info_row("Bệnh nhân:", row.get("ten_bn", "")))
        lay.addWidget(info_row("Bác sĩ:", row.get("ten_bs", "")))
        lay.addWidget(info_row("Ngày khám:", str(row.get("ngay_kham", ""))))
        lay.addWidget(info_row("Triệu chứng:", row.get("trieu_chung", "")))
        lay.addWidget(info_row("Chẩn đoán:", row.get("chuan_doan", "")))
        lay.addWidget(info_row("Phương pháp điều trị:", row.get("phuong_phap_dieu_tri", "")))
        lay.addWidget(info_row("Kết quả:", row.get("ket_qua", "")))

        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        btn_close.clicked.connect(dlg.accept)
        lay.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()


class BenhAnDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Tạo bệnh án" if not data else "Sửa bệnh án")
        self.setMinimumWidth(540)
        self._build_ui()
        if data:
            self._fill(data)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(25, 20, 25, 20)

        title = QLabel("📋 " + ("Tạo Bệnh Án Mới" if not self.data else "Sửa Bệnh Án"))
        title.setStyleSheet("font-size:16px;font-weight:bold;color:#1a5276;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        if not self.data:
            self.lich_combo = QComboBox()
            self.lich_combo.setMinimumHeight(36)
            self.lich_combo.setStyleSheet(INPUT_STYLE)
            self._lich_ids = []
            for r in BenhAnLogic.get_lich_chua_co_benh_an():
                self.lich_combo.addItem(f"{r['ho_ten']} - {r['ngay_kham']}")
                self._lich_ids.append(r["ma_lich"])
            form.addRow("Lịch khám *:", self.lich_combo)

        def make_text(ph):
            t = QTextEdit()
            t.setPlaceholderText(ph)
            t.setMaximumHeight(90)
            t.setStyleSheet(INPUT_STYLE)
            return t

        self.trieu_chung  = make_text("Mô tả triệu chứng...")
        self.chuan_doan   = make_text("Chẩn đoán bệnh...")
        self.phuong_phap  = make_text("Phương pháp điều trị...")
        self.ket_qua      = make_text("Kết quả điều trị...")
        self.ket_qua.setMaximumHeight(70)

        form.addRow("Triệu chứng:", self.trieu_chung)
        form.addRow("Chẩn đoán:",   self.chuan_doan)
        form.addRow("Điều trị:",    self.phuong_phap)
        form.addRow("Kết quả:",     self.ket_qua)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Lưu bệnh án")
        bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(bs)
        lay.addLayout(btn_row)
        self.setStyleSheet(FORM_STYLE)

    def _fill(self, d):
        self.trieu_chung.setText(d.get("trieu_chung", "") or "")
        self.chuan_doan.setText(d.get("chuan_doan", "") or "")
        self.phuong_phap.setText(d.get("phuong_phap_dieu_tri", "") or "")
        self.ket_qua.setText(d.get("ket_qua", "") or "")

    def _save(self):
        tc = self.trieu_chung.toPlainText().strip()
        cd = self.chuan_doan.toPlainText().strip()
        pp = self.phuong_phap.toPlainText().strip()
        kq = self.ket_qua.toPlainText().strip()

        if not self.data:
            if not self._lich_ids:
                QMessageBox.warning(self, "Lỗi", "Không có lịch khám phù hợp!")
                return
            ma_lich = self._lich_ids[self.lich_combo.currentIndex()]
            BenhAnLogic.insert(ma_lich, tc, cd, pp, kq)
        else:
            BenhAnLogic.update(self.data["ma_ba"], tc, cd, pp, kq)
        self.accept()
