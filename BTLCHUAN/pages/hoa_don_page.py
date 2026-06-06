"""
pages/hoa_don_page.py
─────────────────────
UI quản lý hóa đơn.  Logic → HoaDonLogic.
Đã sửa lỗi crash 0xC0000409:
  1. _refresh_items_cb: bỏ đoạn HoaDonLogic.get_all.__func__ vô nghĩa
  2. _on_lich_changed: dùng QTimer.singleShot để tránh QMessageBox trong signal
  3. ChiTietHoaDon: thêm cột thanh_tien khi insert
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QDialog, QFormLayout, QMessageBox, QHeaderView,
    QDoubleSpinBox, QGroupBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE
from logic import HoaDonLogic


def _fmt(num):
    try:
        return f"{float(num):,.0f} đ"
    except Exception:
        return str(num)


# ════════════════════════════════════════════════════════════════════════
#  Trang danh sách hóa đơn
# ════════════════════════════════════════════════════════════════════════
class HoaDonPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(25, 20, 25, 20)
        root.setSpacing(15)

        hr = QHBoxLayout()
        title = QLabel("💳 QUẢN LÝ HÓA ĐƠN")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title)
        hr.addStretch()

        self.cmbFilter = QComboBox()
        self.cmbFilter.addItems(["Tất cả", "Chưa thanh toán", "Đã thanh toán", "Hủy"])
        self.cmbFilter.setMinimumHeight(34)
        self.cmbFilter.setStyleSheet(INPUT_STYLE)
        self.cmbFilter.currentIndexChanged.connect(self.load_data)
        hr.addWidget(QLabel("Lọc:"))
        hr.addWidget(self.cmbFilter)

        self.searchInput = QLineEdit(placeholderText="🔍 Tìm tên bệnh nhân...")
        self.searchInput.setFixedWidth(220)
        self.searchInput.setMinimumHeight(34)
        self.searchInput.setStyleSheet(INPUT_STYLE)
        self.searchInput.textChanged.connect(self.load_data)
        hr.addWidget(self.searchInput)

        btn_new = QPushButton("➕ Lập hóa đơn")
        btn_new.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_new.clicked.connect(self._create)
        hr.addWidget(btn_new)
        root.addLayout(hr)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã HĐ", "Bệnh nhân", "Bác sĩ", "Ngày khám",
            "Tổng tiền", "Giảm giá", "Thành tiền", "Trạng thái",
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._view)
        root.addWidget(self.table)

        bot = QHBoxLayout()
        bot.addStretch()
        btn_view   = QPushButton("🔍 Xem chi tiết")
        btn_pay    = QPushButton("✅ Xác nhận thanh toán")
        btn_cancel = QPushButton("❌ Hủy hóa đơn")
        btn_view.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_pay.setStyleSheet(BTN_STYLE.format(bg="#27ae60",  hover="#1e8449"))
        btn_cancel.setStyleSheet(BTN_STYLE.format(bg="#e74c3c", hover="#c0392b"))
        btn_view.clicked.connect(self._view)
        btn_pay.clicked.connect(self._pay)
        btn_cancel.clicked.connect(self._cancel)
        for b in [btn_view, btn_pay, btn_cancel]:
            bot.addWidget(b)
        root.addLayout(bot)

    def load_data(self):
        kw = self.searchInput.text().strip()
        state_map = {0: None, 1: "chua_thanh_toan", 2: "da_thanh_toan", 3: "huy"}
        state = state_map[self.cmbFilter.currentIndex()]
        rows  = HoaDonLogic.get_all(kw, state)

        state_label = {
            "chua_thanh_toan": "⏳ Chưa TT",
            "da_thanh_toan":   "✅ Đã TT",
            "huy":             "❌ Hủy",
        }
        state_color = {
            "chua_thanh_toan": QColor("#fff3cd"),
            "da_thanh_toan":   QColor("#d4edda"),
            "huy":             QColor("#f8d7da"),
        }
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            vals = [
                str(r["ma_hd"]), r["benh_nhan"], r["bac_si"],
                str(r["ngay_kham"]),
                _fmt(r["tong_tien"]), _fmt(r["giam_gia"]), _fmt(r["thanh_tien"]),
                state_label.get(r["trang_thai"], r["trang_thai"]),
            ]
            color = state_color.get(r["trang_thai"])
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if color:
                    item.setBackground(color)
                self.table.setItem(i, j, item)
        self.table.resizeRowsToContents()

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn một hóa đơn!")
            return None
        return int(self.table.item(row, 0).text())

    def _create(self):
        dlg = HoaDonDialog(self, self.user_info)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _view(self):
        ma = self._selected_id()
        if ma is None:
            return
        dlg = HoaDonDetailDialog(self, ma)
        dlg.exec()

    def _pay(self):
        ma = self._selected_id()
        if ma is None:
            return
        tt = HoaDonLogic.get_trang_thai(ma)
        if tt != "chua_thanh_toan":
            QMessageBox.warning(self, "Lỗi", "Hóa đơn không ở trạng thái chờ thanh toán!")
            return
        r = QMessageBox.question(
            self, "Xác nhận", "Xác nhận đã thu tiền?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r == QMessageBox.StandardButton.Yes:
            ma_lt = HoaDonLogic.get_ma_lt(self.user_info.get("ma_tk"))
            HoaDonLogic.confirm_payment(ma, ma_lt)
            self.load_data()

    def _cancel(self):
        ma = self._selected_id()
        if ma is None:
            return
        r = QMessageBox.question(
            self, "Xác nhận", "Hủy hóa đơn này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r == QMessageBox.StandardButton.Yes:
            HoaDonLogic.cancel(ma)
            self.load_data()


# ════════════════════════════════════════════════════════════════════════
#  Dialog lập hóa đơn mới
# ════════════════════════════════════════════════════════════════════════
class HoaDonDialog(QDialog):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info  = user_info
        self._items     = []
        self._lich      = {}
        self._item_data = []
        self.setWindowTitle("Lập hóa đơn mới")
        self.setMinimumWidth(700)
        self.setMinimumHeight(580)
        self._build_ui()
        self._load_lich()

    # ── Build UI ─────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # 1. Chọn lịch khám
        grp1 = QGroupBox("1. Chọn lịch khám")
        grp1.setStyleSheet("QGroupBox{font-weight:bold;color:#1a5276;}")
        g1 = QVBoxLayout(grp1)

        self.cmbLich = QComboBox()
        self.cmbLich.setMinimumHeight(34)
        # Dùng activated thay currentIndexChanged để tránh crash Windows
        self.cmbLich.activated.connect(self._on_lich_changed)
        g1.addWidget(self.cmbLich)

        lbl_hint = QLabel("ℹ️  Dịch vụ và thuốc sẽ tự động load từ bệnh án + lịch khám.")
        lbl_hint.setStyleSheet("color:#555;font-size:11px;font-weight:normal;")
        lbl_hint.setWordWrap(True)
        g1.addWidget(lbl_hint)

        self._lbl_lich_info = QLabel("")
        self._lbl_lich_info.setStyleSheet(
            "background:#eaf4fb;border:1px solid #aed6f1;border-radius:6px;"
            "padding:6px 10px;color:#1a5276;font-size:12px;")
        self._lbl_lich_info.setWordWrap(True)
        self._lbl_lich_info.hide()
        g1.addWidget(self._lbl_lich_info)
        root.addWidget(grp1)

        # 2. Thêm / chỉnh sửa dịch vụ – thuốc
        grp2 = QGroupBox("2. Thêm / chỉnh sửa dịch vụ – thuốc")
        grp2.setStyleSheet("QGroupBox{font-weight:bold;color:#1a5276;}")
        g2v = QVBoxLayout(grp2)

        row_add = QHBoxLayout()
        self.cmbLoai = QComboBox()
        self.cmbLoai.addItems(["🏥 Dịch vụ", "💊 Thuốc"])
        self.cmbLoai.setMinimumHeight(32)
        self.cmbLoai.currentIndexChanged.connect(self._refresh_items_cb)

        self.cmbItem = QComboBox()
        self.cmbItem.setMinimumWidth(240)
        self.cmbItem.setMinimumHeight(32)

        self.spQty = QDoubleSpinBox()
        self.spQty.setRange(1, 9999)
        self.spQty.setValue(1)
        self.spQty.setDecimals(0)
        self.spQty.setFixedWidth(80)
        self.spQty.setMinimumHeight(32)

        btn_add_item = QPushButton("➕ Thêm")
        btn_add_item.setMinimumHeight(32)
        btn_add_item.setStyleSheet(
            "background:#27ae60;color:white;border-radius:5px;"
            "padding:4px 12px;font-weight:bold;")
        btn_add_item.clicked.connect(self._add_item)

        row_add.addWidget(QLabel("Loại:"))
        row_add.addWidget(self.cmbLoai)
        row_add.addWidget(QLabel("Chọn:"))
        row_add.addWidget(self.cmbItem, 1)
        row_add.addWidget(QLabel("SL:"))
        row_add.addWidget(self.spQty)
        row_add.addWidget(btn_add_item)
        g2v.addLayout(row_add)

        self.tblItems = QTableWidget()
        self.tblItems.setColumnCount(5)
        self.tblItems.setHorizontalHeaderLabels(
            ["Loại", "Tên hàng", "Đơn giá", "SL", "Thành tiền"])
        hh = self.tblItems.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.tblItems.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tblItems.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setMinimumHeight(160)
        self.tblItems.setMaximumHeight(220)
        self.tblItems.verticalHeader().setVisible(False)
        g2v.addWidget(self.tblItems)

        btn_del = QPushButton("🗑️ Xóa dòng đã chọn")
        btn_del.setStyleSheet(
            "background:#e74c3c;color:white;border-radius:5px;padding:4px 10px;")
        btn_del.clicked.connect(self._del_item)
        g2v.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignRight)
        root.addWidget(grp2)

        # 3. Thanh toán
        grp3 = QGroupBox("3. Thanh toán")
        grp3.setStyleSheet("QGroupBox{font-weight:bold;color:#1a5276;}")
        g3 = QFormLayout(grp3)
        g3.setSpacing(10)

        self.spGiam = QDoubleSpinBox()
        self.spGiam.setRange(0, 999_999_999)
        self.spGiam.setSuffix(" đ")
        self.spGiam.setGroupSeparatorShown(True)
        self.spGiam.setMinimumHeight(32)
        self.spGiam.valueChanged.connect(self._update_total)

        self.cmbPhuongThuc = QComboBox()
        self.cmbPhuongThuc.addItems(["Tiền mặt", "Chuyển khoản", "Thẻ", "Bảo hiểm"])
        self.cmbPhuongThuc.setMinimumHeight(32)

        self.lblTong  = QLabel("0 đ")
        self.lblTong.setStyleSheet("font-weight:bold;font-size:13px;")
        self.lblThanh = QLabel("0 đ")
        self.lblThanh.setStyleSheet("font-weight:bold;font-size:16px;color:#27ae60;")

        g3.addRow("Giảm giá (VNĐ):", self.spGiam)
        g3.addRow("Phương thức TT:", self.cmbPhuongThuc)
        g3.addRow("Tổng cộng:",      self.lblTong)
        g3.addRow("💰 Thành tiền:",   self.lblThanh)
        root.addWidget(grp3)

        # Nút lưu / hủy
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok = QPushButton("💾 Lưu hóa đơn")
        ok.setMinimumHeight(38)
        ok.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        ok.clicked.connect(self._save)
        hl = QPushButton("Hủy")
        hl.setMinimumHeight(38)
        hl.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        hl.clicked.connect(self.reject)
        btn_row.addWidget(hl)
        btn_row.addWidget(ok)
        root.addLayout(btn_row)

        # Load combo item lần đầu
        self._refresh_items_cb()

    # ── Load dữ liệu ─────────────────────────────────────────────────────
    def _load_lich(self):
        rows = HoaDonLogic.get_lich_chua_hoa_don()
        self._lich = {r["ma_lich"]: r for r in rows}

        self.cmbLich.blockSignals(True)
        self.cmbLich.clear()
        self.cmbLich.addItem("— Chọn lịch khám —", None)

        tt_label = {
            "da_xac_nhan": "✅ Đã XN",
            "dang_kham":   "🔵 Đang khám",
            "hoan_thanh":  "✔️ Hoàn thành",
        }
        for r in rows:
            ngay = str(r["ngay_kham"])
            try:
                from datetime import datetime as _dt
                ngay = _dt.strptime(ngay, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                pass
            gio = str(r.get("gio_kham") or "")[:5]
            tt  = tt_label.get(r["trang_thai"], r["trang_thai"])
            self.cmbLich.addItem(
                f"[{ngay} {gio}]  {r['ten_bn']}  –  BS. {r['ten_bs']}  ({tt})",
                r["ma_lich"],
            )
        self.cmbLich.blockSignals(False)

    def _on_lich_changed(self, index):
        """Dùng signal activated(int) — an toàn hơn currentIndexChanged trên Windows."""
        ma_lich = self.cmbLich.itemData(index)
        self._items.clear()

        if not ma_lich:
            self._lbl_lich_info.hide()
            self._refresh_table()
            return

        # Hiển thị thông tin lịch
        lich = self._lich.get(ma_lich, {})
        ngay = str(lich.get("ngay_kham", ""))
        try:
            from datetime import datetime as _dt
            ngay = _dt.strptime(ngay, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass
        tt_vi = {
            "da_xac_nhan": "Đã xác nhận",
            "dang_kham":   "Đang khám",
            "hoan_thanh":  "Hoàn thành",
        }.get(lich.get("trang_thai", ""), "")

        self._lbl_lich_info.setText(
            f"<b>Bệnh nhân:</b> {lich.get('ten_bn', '')}  │  "
            f"<b>Bác sĩ:</b> {lich.get('ten_bs', '')}  │  "
            f"<b>Ngày:</b> {ngay} {str(lich.get('gio_kham', ''))[:5]}  │  "
            f"<b>Lý do:</b> {lich.get('ly_do_kham') or '—'}  │  "
            f"<b>Trạng thái:</b> {tt_vi}"
        )
        self._lbl_lich_info.show()

        # Load dịch vụ từ bệnh án
        n_dv = n_thuoc = 0
        ba = HoaDonLogic.get_benh_an_by_lich(ma_lich)
        if ba:
            ma_ba = ba["ma_ba"]
            for r in HoaDonLogic.get_dv_tu_benh_an(ma_ba):
                self._items.append({
                    "loai": "dich_vu", "ma": r["ma"], "ten": r["ten"],
                    "don_gia": float(r["don_gia"]), "so_luong": 1,
                })
                n_dv += 1
            for r in HoaDonLogic.get_thuoc_tu_don(ma_ba):
                self._items.append({
                    "loai": "thuoc", "ma": r["ma"], "ten": r["ten"],
                    "don_gia": float(r["don_gia"]), "so_luong": int(r["so_luong"]),
                })
                n_thuoc += 1

        # Load dịch vụ đăng ký kèm lịch (nếu chưa có)
        for r in HoaDonLogic.get_dv_tu_lich(ma_lich):
            already = any(
                it["loai"] == "dich_vu" and it["ma"] == r["ma"]
                for it in self._items
            )
            if not already:
                self._items.append({
                    "loai": "dich_vu", "ma": r["ma"], "ten": r["ten"],
                    "don_gia": float(r["don_gia"]), "so_luong": int(r["so_luong"]),
                })
                n_dv += 1

        self._refresh_table()

        # QTimer.singleShot: tránh gọi QMessageBox ngay trong signal → crash Windows
        if self._items:
            parts = []
            if n_dv:    parts.append(f"{n_dv} dịch vụ")
            if n_thuoc: parts.append(f"{n_thuoc} thuốc")
            if parts:
                msg = " và ".join(parts)
                QTimer.singleShot(
                    150,
                    lambda m=msg: QMessageBox.information(
                        self, "Tự động load",
                        f"Đã tải {m}.\nBạn có thể thêm / xóa trước khi lưu.",
                    ),
                )

    def _refresh_items_cb(self):
        """Load combo dịch vụ hoặc thuốc theo loại đang chọn."""
        self.cmbItem.clear()
        from logic import DichVuLogic, ThuocLogic
        if self.cmbLoai.currentIndex() == 0:
            rows = DichVuLogic.get_active()
        else:
            rows = ThuocLogic.get_available()
        self._item_data = rows
        for r in rows:
            self.cmbItem.addItem(f"{r['ten']}  ({_fmt(r['don_gia'])})", r)

    # ── Thao tác danh sách ───────────────────────────────────────────────
    def _add_item(self):
        d = self.cmbItem.currentData()
        if not d:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn dịch vụ hoặc thuốc!")
            return
        loai = "dich_vu" if self.cmbLoai.currentIndex() == 0 else "thuoc"
        qty  = int(self.spQty.value())
        # Nếu đã có → cộng dồn số lượng
        for it in self._items:
            if it["loai"] == loai and it["ma"] == d["ma"]:
                it["so_luong"] += qty
                self._refresh_table()
                return
        self._items.append({
            "loai":     loai,
            "ma":       d["ma"],
            "ten":      d["ten"],
            "don_gia":  float(d["don_gia"]),
            "so_luong": qty,
        })
        self._refresh_table()

    def _del_item(self):
        row = self.tblItems.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Chú ý", "Vui lòng chọn dòng muốn xóa!")
            return
        self._items.pop(row)
        self._refresh_table()

    def _refresh_table(self):
        self.tblItems.setRowCount(0)
        for it in self._items:
            i = self.tblItems.rowCount()
            self.tblItems.insertRow(i)
            vals = [
                "🏥 Dịch vụ" if it["loai"] == "dich_vu" else "💊 Thuốc",
                it["ten"],
                _fmt(it["don_gia"]),
                str(it["so_luong"]),
                _fmt(it["don_gia"] * it["so_luong"]),
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter if j != 1
                    else Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                self.tblItems.setItem(i, j, item)
        self.tblItems.resizeColumnsToContents()
        self._update_total()

    def _update_total(self):
        tong  = sum(it["don_gia"] * it["so_luong"] for it in self._items)
        giam  = self.spGiam.value()
        thanh = max(0.0, tong - giam)
        self.lblTong.setText(_fmt(tong))
        self.lblThanh.setText(_fmt(thanh))
        color = "#e74c3c" if giam > tong else "#27ae60"
        self.lblThanh.setStyleSheet(
            f"font-weight:bold;color:{color};font-size:14px;")

    # ── Lưu ─────────────────────────────────────────────────────────────
    def _save(self):
        ma_lich = self.cmbLich.currentData()
        if not ma_lich:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn lịch khám!")
            return
        if not self._items:
            QMessageBox.warning(self, "Lỗi",
                "Vui lòng thêm ít nhất 1 dịch vụ hoặc thuốc!")
            return

        tong = sum(it["don_gia"] * it["so_luong"] for it in self._items)
        giam = self.spGiam.value()
        pt_map = {
            "Tiền mặt":    "tien_mat",
            "Chuyển khoản":"chuyen_khoan",
            "Thẻ":         "the",
            "Bảo hiểm":   "bao_hiem",
        }
        pt    = pt_map.get(self.cmbPhuongThuc.currentText(), "tien_mat")
        ma_lt = HoaDonLogic.get_ma_lt(self.user_info.get("ma_tk"))
        ma_hd = HoaDonLogic.insert(ma_lich, ma_lt, tong, giam, pt, self._items)

        if not ma_hd:
            QMessageBox.critical(self, "Lỗi", "Không thể tạo hóa đơn!")
            return
        QMessageBox.information(self, "Thành công", f"Đã lập hóa đơn #{ma_hd}!")
        self.accept()


# ════════════════════════════════════════════════════════════════════════
#  Dialog xem chi tiết hóa đơn
# ════════════════════════════════════════════════════════════════════════
class HoaDonDetailDialog(QDialog):
    def __init__(self, parent, ma_hd):
        super().__init__(parent)
        self.setWindowTitle(f"Chi tiết hóa đơn #{ma_hd}")
        self.setMinimumWidth(600)
        self._build_ui(ma_hd)

    def _build_ui(self, ma_hd):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        hd = HoaDonLogic.get_detail(ma_hd)
        if not hd:
            root.addWidget(QLabel("Không tìm thấy hóa đơn!"))
            return

        info = QLabel(
            f"<b>Bệnh nhân:</b> {hd['benh_nhan']}  |  "
            f"<b>Bác sĩ:</b> {hd['bac_si']}  |  "
            f"<b>Ngày khám:</b> {hd['ngay_kham']}<br>"
            f"<b>Lễ tân:</b> {hd.get('le_tan') or '—'}  |  "
            f"<b>Ngày lập:</b> {hd.get('ngay_lap', '')}  |  "
            f"<b>Trạng thái:</b> {hd['trang_thai']}"
        )
        info.setWordWrap(True)
        root.addWidget(info)

        ct  = HoaDonLogic.get_chi_tiet(ma_hd)
        tbl = QTableWidget(len(ct), 5)
        tbl.setHorizontalHeaderLabels(["Loại", "Tên", "Đơn giá", "SL", "Thành tiền"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        for i, r in enumerate(ct):
            vals = [
                "Dịch vụ" if r["loai_ct"] == "dich_vu" else "Thuốc",
                r["ten_hang"],
                _fmt(r["don_gia"]),
                str(r["so_luong"]),
                _fmt(r["thanh_tien"]),
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tbl.setItem(i, j, item)
        root.addWidget(tbl)

        summary = QLabel(
            f"<hr><b>Tổng tiền:</b> {_fmt(hd['tong_tien'])}  |  "
            f"<b>Giảm giá:</b> {_fmt(hd['giam_gia'])}  |  "
            f"<b style='color:#e74c3c;font-size:14px;'>"
            f"Thành tiền: {_fmt(hd['thanh_tien'])}</b>"
        )
        summary.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(summary)

        ok = QPushButton("Đóng")
        ok.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        ok.clicked.connect(self.accept)
        root.addWidget(ok, alignment=Qt.AlignmentFlag.AlignRight)
