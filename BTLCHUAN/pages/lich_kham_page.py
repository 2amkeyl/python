"""
pages/lich_kham_page.py
───────────────────────
UI quản lý lịch khám.  Logic → LichKhamLogic, BenhNhanLogic, BacSiLogic.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDialog, QDateEdit, QTimeEdit, QTextEdit,
    QMessageBox, QFrame, QGroupBox, QScrollArea,
    QCheckBox, QSpinBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor
from datetime import date, timedelta

from ui.styles import BTN_STYLE, TABLE_STYLE_DEFAULT, INPUT_STYLE, GRP_STYLE
from logic import LichKhamLogic, BacSiLogic, BenhNhanLogic, DichVuLogic

_GRP_BLUE   = GRP_STYLE.format(c="#1a5276", b="#2980b9")
_GRP_GRAY   = GRP_STYLE.format(c="#1a5276", b="#d5d8dc")
_GRP_PURPLE = GRP_STYLE.format(c="#6c3483", b="#d2b4de")


# ── Helpers ─────────────────────────────────────────────────────────────
def _parse_time(v):
    if v is None:
        return QTime(8, 0)
    if isinstance(v, __import__("datetime").timedelta):
        s = int(v.total_seconds())
        return QTime(s // 3600, (s % 3600) // 60)
    try:
        p = str(v).split(":")
        return QTime(int(p[0]), int(p[1]))
    except Exception:
        return QTime(8, 0)


def _parse_date(v):
    if v is None:
        return QDate.currentDate()
    if isinstance(v, date):
        return QDate(v.year, v.month, v.day)
    try:
        return QDate.fromString(str(v), "yyyy-MM-dd")
    except Exception:
        return QDate.currentDate()


def _fmt_date(v):
    if not v:
        return ""
    try:
        if isinstance(v, date):
            return v.strftime("%d/%m/%Y")
        from datetime import datetime as _dt
        return _dt.strptime(str(v), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return str(v)


# ════════════════════════════════════════════════════════════════════════
#  Dialog thêm / sửa lịch khám
# ════════════════════════════════════════════════════════════════════════
class LichKhamDialog(QDialog):
    def __init__(self, parent=None, lich_data=None):
        super().__init__(parent)
        self.lich_data = lich_data
        self._ma_bn_selected = None
        self._is_new_bn = False
        self._dv_widgets = []

        self.setWindowTitle("Thêm lịch khám" if not lich_data else "Sửa lịch khám")
        self.setMinimumWidth(640)
        self.setMinimumHeight(580)
        self._bs_list  = BacSiLogic.get_active()
        self._dv_list  = DichVuLogic.get_active()
        self._build_ui()
        if lich_data:
            self._fill_data()

    # ── Build UI ─────────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(22, 18, 22, 18)

        title = QLabel("📅 " + ("Thêm Lịch Khám Mới" if not self.lich_data else "Sửa Lịch Khám"))
        title.setStyleSheet("font-size:17px;font-weight:bold;color:#1a5276;")
        layout.addWidget(title)

        if not self.lich_data:
            layout.addWidget(self._build_bn_section())

        layout.addWidget(self._build_lich_section())
        layout.addWidget(self._build_dv_section())

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setStyleSheet(BTN_STYLE.format(bg="#95a5a6", hover="#7f8c8d"))
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Lưu lịch khám")
        bs.setStyleSheet(BTN_STYLE.format(bg="#1a5276", hover="#2471a3"))
        bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        layout.addLayout(btn_row)

        self.setStyleSheet(
            "QDialog{background:white;}"
            "QLineEdit,QComboBox,QDateEdit,QTimeEdit,QTextEdit,QSpinBox"
            "{border:1.5px solid #d5d8dc;border-radius:6px;padding:5px;font-size:13px;}")

    def _build_bn_section(self):
        grp = QGroupBox("👤 Bệnh nhân")
        grp.setStyleSheet(_GRP_BLUE)
        vbox = QVBoxLayout(grp)
        vbox.setSpacing(8); vbox.setContentsMargins(14, 14, 14, 14)

        row_s = QHBoxLayout()
        lbl = QLabel("Mã bệnh nhân:")
        lbl.setStyleSheet("font-weight:bold;min-width:120px;")
        self.inpSearch = QLineEdit()
        self.inpSearch.setMinimumHeight(36)
        self.inpSearch.setPlaceholderText("Nhập mã bệnh nhân rồi nhấn Tìm hoặc Enter...")
        self.inpSearch.setStyleSheet(
            "border:1.5px solid #2980b9;border-radius:6px;padding:5px 10px;font-size:13px;")
        self.inpSearch.returnPressed.connect(self._search_bn)
        btn_search = QPushButton("🔍 Tìm")
        btn_search.setMinimumHeight(36); btn_search.setFixedWidth(90)
        btn_search.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_search.clicked.connect(self._search_bn)
        row_s.addWidget(lbl); row_s.addWidget(self.inpSearch, 1); row_s.addWidget(btn_search)
        vbox.addLayout(row_s)

        self.lblBNStatus = QLabel("⚠️  Nhập mã bệnh nhân và nhấn Tìm")
        self.lblBNStatus.setWordWrap(True)
        self.lblBNStatus.setStyleSheet(
            "color:#7f8c8d;font-weight:bold;padding:8px;background:#f2f3f4;border-radius:6px;")
        vbox.addWidget(self.lblBNStatus)

        # Panel BN tìm thấy
        self.frmBNFound = QFrame()
        self.frmBNFound.setStyleSheet(
            "QFrame{background:#eafaf1;border:1.5px solid #27ae60;border-radius:8px;}"
            "QLabel{color:#1e8449;font-size:12px;border:none;}")
        fl = QVBoxLayout(self.frmBNFound); fl.setContentsMargins(12, 8, 12, 8); fl.setSpacing(3)
        self.lblBNInfo = QLabel(); self.lblBNInfo.setWordWrap(True)
        self.lblBNHistory = QLabel(); self.lblBNHistory.setWordWrap(True)
        self.lblBNHistory.setStyleSheet("color:#2471a3;font-style:italic;border:none;")
        fl.addWidget(self.lblBNInfo); fl.addWidget(self.lblBNHistory)
        self.frmBNFound.hide()
        vbox.addWidget(self.frmBNFound)

        # Form BN mới
        self.frmNewBN = QFrame()
        self.frmNewBN.setStyleSheet(
            "QFrame{background:#fff8e1;border:1.5px dashed #f39c12;border-radius:8px;}"
            "QLineEdit,QComboBox,QDateEdit{border:1.5px solid #f0c040;border-radius:5px;padding:4px;}")
        nb = QVBoxLayout(self.frmNewBN); nb.setContentsMargins(14,10,14,10); nb.setSpacing(8)
        lbl_title = QLabel("➕  Bệnh nhân chưa có hồ sơ – nhập thông tin để tạo mới")
        lbl_title.setStyleSheet("color:#b7770d;font-weight:bold;font-size:13px;border:none;")
        nb.addWidget(lbl_title)
        nf = QFormLayout = __import__("PyQt6.QtWidgets", fromlist=["QFormLayout"]).QFormLayout
        nf = nf(); nf.setSpacing(7)
        self.inpNewMaBN  = QLineEdit(); self.inpNewMaBN.setMinimumHeight(33)
        self.inpNewHoTen = QLineEdit(); self.inpNewHoTen.setMinimumHeight(33)
        self.inpNewHoTen.setPlaceholderText("Họ và tên đầy đủ...")
        self.dateNewNS   = QDateEdit(); self.dateNewNS.setMinimumHeight(33)
        self.dateNewNS.setCalendarPopup(True); self.dateNewNS.setDisplayFormat("dd/MM/yyyy")
        self.dateNewNS.setDate(QDate(1990,1,1))
        self.cmbNewGT = QComboBox(); self.cmbNewGT.setMinimumHeight(33)
        self.cmbNewGT.addItems(["Nam","Nữ","Khác"])
        self.inpNewSDT   = QLineEdit(); self.inpNewSDT.setMinimumHeight(33)
        self.inpNewSDT.setPlaceholderText("Số điện thoại...")
        self.inpNewEmail = QLineEdit(); self.inpNewEmail.setMinimumHeight(33)
        self.inpNewEmail.setPlaceholderText("Email (không bắt buộc)...")
        self.inpNewBH    = QLineEdit(); self.inpNewBH.setMinimumHeight(33)
        self.inpNewBH.setPlaceholderText("Số thẻ bảo hiểm y tế (nếu có)...")
        row_gt = QHBoxLayout()
        row_gt.addWidget(self.dateNewNS, 2)
        row_gt.addWidget(QLabel("  Giới tính:")); row_gt.addWidget(self.cmbNewGT, 1)
        nf.addRow("Mã BN *:",  self.inpNewMaBN)
        nf.addRow("Họ tên *:", self.inpNewHoTen)
        nf.addRow("Ngày sinh:", row_gt)
        nf.addRow("SĐT:",      self.inpNewSDT)
        nf.addRow("Email:",    self.inpNewEmail)
        nf.addRow("Bảo hiểm:", self.inpNewBH)
        nb.addLayout(nf)
        self.frmNewBN.hide()
        vbox.addWidget(self.frmNewBN)
        return grp

    def _build_lich_section(self):
        grp = QGroupBox("📋 Thông tin lịch khám")
        grp.setStyleSheet(_GRP_GRAY)
        form_cls = __import__("PyQt6.QtWidgets", fromlist=["QFormLayout"]).QFormLayout
        form = form_cls(grp); form.setSpacing(10); form.setContentsMargins(14,14,14,14)

        self.bs_combo = QComboBox(); self.bs_combo.setMinimumHeight(35)
        for r in self._bs_list:
            self.bs_combo.addItem(f"{r['ho_ten']}  –  {r.get('chuyen_khoa') or ''}", r["ma_bs"])

        self.ngay_edit = QDateEdit(); self.ngay_edit.setMinimumHeight(35)
        self.ngay_edit.setDate(QDate.currentDate()); self.ngay_edit.setCalendarPopup(True)
        self.ngay_edit.setDisplayFormat("dd/MM/yyyy")

        self.gio_edit = QTimeEdit(); self.gio_edit.setMinimumHeight(35)
        self.gio_edit.setTime(QTime(8,0)); self.gio_edit.setDisplayFormat("HH:mm")

        self.lydo_edit = QTextEdit(); self.lydo_edit.setMaximumHeight(70)
        self.lydo_edit.setPlaceholderText("Nhập lý do khám...")

        self.status_combo = QComboBox(); self.status_combo.setMinimumHeight(35)
        self.status_combo.addItems(["Chờ xác nhận","Đã xác nhận","Đang khám","Hoàn thành","Đã hủy"])

        self.ghichu_edit = QTextEdit(); self.ghichu_edit.setMaximumHeight(50)
        self.ghichu_edit.setPlaceholderText("Ghi chú thêm...")

        form.addRow("Bác sĩ *:",     self.bs_combo)
        form.addRow("Ngày khám *:",  self.ngay_edit)
        form.addRow("Giờ khám *:",   self.gio_edit)
        form.addRow("Lý do khám:",   self.lydo_edit)
        form.addRow("Trạng thái:",   self.status_combo)
        form.addRow("Ghi chú:",      self.ghichu_edit)
        return grp

    def _build_dv_section(self):
        grp = QGroupBox("🏷️ Dịch vụ đăng ký kèm theo")
        grp.setStyleSheet(_GRP_PURPLE)
        vbox = QVBoxLayout(grp); vbox.setContentsMargins(14,14,14,14); vbox.setSpacing(6)

        if not self._dv_list:
            vbox.addWidget(QLabel("Không có dịch vụ nào đang hoạt động."))
            return grp

        hdr = QHBoxLayout()
        for text, w in [("✓",30),("Tên dịch vụ",0),("Đơn giá",120),("Số lượng",80),("Thành tiền",120)]:
            lh = QLabel(text)
            lh.setStyleSheet("font-weight:bold;color:#6c3483;font-size:12px;")
            lh.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if w: lh.setFixedWidth(w)
            hdr.addWidget(lh, 0 if w else 1)
        vbox.addLayout(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#d2b4de;"); vbox.addWidget(sep)

        self._dv_widgets = []
        for dv in self._dv_list:
            row_h = QHBoxLayout(); row_h.setSpacing(8)
            chk = QCheckBox(); chk.setFixedWidth(30)
            lbl_name = QLabel(dv["ten"]); lbl_name.setWordWrap(True)
            lbl_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            don_gia = float(dv.get("don_gia") or 0)
            lbl_gia = QLabel(f"{int(don_gia):,} đ"); lbl_gia.setFixedWidth(120)
            lbl_gia.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_gia.setStyleSheet("color:#1a5276;")
            spn = QSpinBox(); spn.setRange(1,999); spn.setValue(1)
            spn.setFixedWidth(80); spn.setEnabled(False)
            lbl_tt = QLabel(f"{int(don_gia):,} đ"); lbl_tt.setFixedWidth(120)
            lbl_tt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_tt.setStyleSheet("color:#27ae60;font-weight:bold;")

            def _on_chk(state, s=spn, g=don_gia, lt=lbl_tt):
                s.setEnabled(bool(state))
                lt.setText(f"{int(g*s.value()):,} đ")
                self._update_dv_total()

            def _on_spn(val, g=don_gia, lt=lbl_tt, c=chk):
                if c.isChecked():
                    lt.setText(f"{int(g*val):,} đ"); self._update_dv_total()

            chk.stateChanged.connect(_on_chk)
            spn.valueChanged.connect(_on_spn)
            row_h.addWidget(chk); row_h.addWidget(lbl_name,1)
            row_h.addWidget(lbl_gia); row_h.addWidget(spn); row_h.addWidget(lbl_tt)
            vbox.addLayout(row_h)
            self._dv_widgets.append((chk, spn, dv))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background:#d2b4de;"); vbox.addWidget(sep2)

        tot_row = QHBoxLayout(); tot_row.addStretch()
        lbl_tit = QLabel("Tổng tiền dịch vụ:")
        lbl_tit.setStyleSheet("font-weight:bold;color:#6c3483;font-size:13px;")
        self.lblDVTotal = QLabel("0 đ")
        self.lblDVTotal.setStyleSheet(
            "font-weight:bold;color:#27ae60;font-size:14px;"
            "padding:4px 14px;background:#eafaf1;border-radius:6px;")
        tot_row.addWidget(lbl_tit); tot_row.addWidget(self.lblDVTotal)
        vbox.addLayout(tot_row)
        return grp

    def _update_dv_total(self):
        total = sum(float(dv.get("don_gia") or 0) * spn.value()
                    for chk, spn, dv in self._dv_widgets if chk.isChecked())
        self.lblDVTotal.setText(f"{int(total):,} đ")

    # ── Tìm bệnh nhân ────────────────────────────────────────────────────
    def _search_bn(self):
        kw = self.inpSearch.text().strip()
        if not kw:
            QMessageBox.warning(self, "Chú ý", "Vui lòng nhập mã bệnh nhân!"); return

        self.frmBNFound.hide(); self.frmNewBN.hide()
        self._ma_bn_selected = None; self._is_new_bn = False

        rows = BenhNhanLogic.search_by_ma(kw)
        if not rows:
            self.lblBNStatus.setText(
                f"❌  Không tìm thấy «{kw}»\n➕  Điền thông tin bên dưới để tạo hồ sơ mới.")
            self.lblBNStatus.setStyleSheet(
                "color:#c0392b;font-weight:bold;padding:8px;background:#fdecea;border-radius:6px;")
            self.inpNewMaBN.setText(kw); self.inpNewHoTen.clear()
            self.inpNewSDT.clear(); self.inpNewEmail.clear(); self.inpNewBH.clear()
            self.frmNewBN.show(); self.inpNewHoTen.setFocus()
            self._is_new_bn = True
        else:
            self._apply_bn(rows[0])

    def _apply_bn(self, bn):
        self._ma_bn_selected = bn["ma_bn"]; self._is_new_bn = False
        self.frmNewBN.hide()
        ns = _fmt_date(bn.get("ngay_sinh"))
        lich_cu = BenhNhanLogic.get_lich_su(bn["ma_bn"])
        self.lblBNInfo.setText(
            f"<b>Mã:</b> {bn['ma_bn']}  │  <b>Họ tên:</b> {bn['ho_ten']}  │  "
            f"<b>Sinh:</b> {ns}  │  <b>Giới tính:</b> {bn.get('gioi_tinh') or '—'}  │  "
            f"<b>SĐT:</b> {bn.get('so_dien_thoai') or '—'}")
        _st_vi = {
            "cho_xac_nhan":"Chờ xác nhận","da_xac_nhan":"Đã xác nhận",
            "dang_kham":"Đang khám","hoan_thanh":"Hoàn thành","huy":"Đã hủy"
        }
        if lich_cu:
            lines = [f"📅 {_fmt_date(lc['ngay_kham'])}  "
                     f"{_parse_time(lc['gio_kham']).toString('HH:mm')}  –  "
                     f"BS. {lc['ten_bs']}  [{_st_vi.get(lc.get('trang_thai',''),'') }]"
                     for lc in lich_cu]
            self.lblBNHistory.setText("<b>📋 Lịch sử gần đây:</b><br>" + "<br>".join(lines))
            if not self.lydo_edit.toPlainText().strip():
                last = lich_cu[0].get("ly_do_kham") or ""
                if last: self.lydo_edit.setPlainText(last)
            self.lblBNStatus.setText(
                f"✅  Tìm thấy – {len(lich_cu)} lịch khám gần đây (lý do đã tự điền)")
            self.lblBNStatus.setStyleSheet(
                "color:#1e8449;font-weight:bold;padding:8px;background:#d4efdf;border-radius:6px;")
        else:
            self.lblBNHistory.setText("<i>📋 Chưa có lịch sử khám</i>")
            self.lblBNStatus.setText("✅  Tìm thấy – bệnh nhân chưa khám lần nào")
            self.lblBNStatus.setStyleSheet(
                "color:#1a5276;font-weight:bold;padding:8px;background:#d6eaf8;border-radius:6px;")
        self.frmBNFound.show()

    # ── Fill khi sửa ─────────────────────────────────────────────────────
    def _fill_data(self):
        d = self.lich_data
        for i in range(self.bs_combo.count()):
            if self.bs_combo.itemData(i) == d.get("ma_bs"):
                self.bs_combo.setCurrentIndex(i); break
        self.ngay_edit.setDate(_parse_date(d.get("ngay_kham")))
        self.gio_edit.setTime(_parse_time(d.get("gio_kham")))
        self.lydo_edit.setPlainText(d.get("ly_do_kham") or "")
        self.ghichu_edit.setPlainText(d.get("ghi_chu") or "")
        st_map = ["cho_xac_nhan","da_xac_nhan","dang_kham","hoan_thanh","huy"]
        tt = d.get("trang_thai","cho_xac_nhan")
        if tt in st_map: self.status_combo.setCurrentIndex(st_map.index(tt))
        if self._dv_widgets:
            dv_rows = LichKhamLogic.get_dich_vu_by_lich(d.get("ma_lich"))
            dv_map  = {r["ma_dv"]: r["so_luong"] for r in dv_rows}
            for chk, spn, dv in self._dv_widgets:
                if dv["ma"] in dv_map:
                    chk.setChecked(True); spn.setValue(dv_map[dv["ma"]])

    # ── Lưu ──────────────────────────────────────────────────────────────
    def _save(self):
        # 1. Xác định ma_bn
        if not self.lich_data:
            if self._is_new_bn:
                ma_bn  = self.inpNewMaBN.text().strip()
                ho_ten = self.inpNewHoTen.text().strip()
                if not ma_bn or not ho_ten:
                    QMessageBox.warning(self, "Thiếu thông tin","Vui lòng nhập Mã BN và Họ tên!"); return
                if BenhNhanLogic.ma_exists(ma_bn):
                    QMessageBox.warning(self, "Trùng mã", f"Mã «{ma_bn}» đã tồn tại!"); return
                BenhNhanLogic.insert(
                    ma_bn, ho_ten,
                    self.dateNewNS.date().toString("yyyy-MM-dd"),
                    self.cmbNewGT.currentText(),
                    self.inpNewSDT.text().strip(),
                    self.inpNewEmail.text().strip(),
                    self.inpNewBH.text().strip(), "")
                self._ma_bn_selected = ma_bn
            if not self._ma_bn_selected:
                QMessageBox.warning(self, "Chưa chọn bệnh nhân",
                    "Vui lòng nhập mã bệnh nhân và nhấn Tìm!"); return
            ma_bn = self._ma_bn_selected
        else:
            ma_bn = self.lich_data["ma_bn"]

        # 2. Lịch khám
        ma_bs = self.bs_combo.currentData()
        if not ma_bs:
            QMessageBox.warning(self, "Lỗi","Vui lòng chọn bác sĩ!"); return

        ngay       = self.ngay_edit.date().toString("yyyy-MM-dd")
        gio        = self.gio_edit.time().toString("HH:mm:ss")
        lydo       = self.lydo_edit.toPlainText().strip()
        ghichu     = self.ghichu_edit.toPlainText().strip()
        st_vals    = ["cho_xac_nhan","da_xac_nhan","dang_kham","hoan_thanh","huy"]
        trang_thai = st_vals[self.status_combo.currentIndex()]

        if not self.lich_data:
            ma_lich = LichKhamLogic.insert(ma_bn, ma_bs, ngay, gio, lydo, trang_thai, ghichu)
        else:
            LichKhamLogic.update(self.lich_data["ma_lich"], ma_bn, ma_bs,
                                  ngay, gio, lydo, trang_thai, ghichu)
            ma_lich = self.lich_data["ma_lich"]

        # 3. Dịch vụ kèm theo
        if ma_lich and self._dv_widgets:
            dv_list = [
                {"ma_dv": dv["ma"], "so_luong": spn.value(),
                 "don_gia": float(dv.get("don_gia") or 0)}
                for chk, spn, dv in self._dv_widgets if chk.isChecked()
            ]
            LichKhamLogic.save_dich_vu(ma_lich, dv_list)

        self.accept()


# ════════════════════════════════════════════════════════════════════════
#  Trang danh sách lịch khám
# ════════════════════════════════════════════════════════════════════════
class LichKhamPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20); layout.setSpacing(15)

        hr = QHBoxLayout()
        title = QLabel("📅 QUẢN LÝ LỊCH KHÁM")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title); hr.addStretch()
        btn_add = QPushButton("➕ Thêm lịch khám")
        btn_add.setStyleSheet(BTN_STYLE.format(bg="#27ae60", hover="#1e8449"))
        btn_add.clicked.connect(self._add)
        hr.addWidget(btn_add)
        layout.addLayout(hr)

        ff = QFrame(); ff.setStyleSheet("background:white;border-radius:8px;padding:10px;")
        fl = QHBoxLayout(ff); fl.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm tên bệnh nhân, bác sĩ, mã BN...")
        self.search_input.setMinimumHeight(36); self.search_input.setStyleSheet(INPUT_STYLE)
        self.search_input.textChanged.connect(self.load_data)

        self.status_filter = QComboBox()
        self.status_filter.setMinimumHeight(36)
        self.status_filter.addItems([
            "Tất cả trạng thái","Chờ xác nhận","Đã xác nhận",
            "Đang khám","Hoàn thành","Đã hủy"])
        self.status_filter.setStyleSheet(INPUT_STYLE)
        self.status_filter.currentIndexChanged.connect(self.load_data)

        btn_ref = QPushButton("🔄 Làm mới")
        btn_ref.setStyleSheet(BTN_STYLE.format(bg="#2980b9", hover="#2471a3"))
        btn_ref.clicked.connect(self.load_data)

        fl.addWidget(QLabel("Tìm:")); fl.addWidget(self.search_input, 2)
        fl.addWidget(QLabel("Trạng thái:")); fl.addWidget(self.status_filter)
        fl.addWidget(btn_ref)
        layout.addWidget(ff)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã","Bệnh nhân","Bác sĩ","Ngày khám","Giờ","Lý do","Trạng thái","Thao tác"])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def load_data(self):
        kw  = self.search_input.text().strip()
        sv  = [None,"cho_xac_nhan","da_xac_nhan","dang_kham","hoan_thanh","huy"]
        tts = sv[self.status_filter.currentIndex()]
        rows = LichKhamLogic.get_all(kw, tts)

        status_map = {
            "cho_xac_nhan": ("⏳ Chờ xác nhận","#e67e22"),
            "da_xac_nhan":  ("✅ Đã xác nhận", "#27ae60"),
            "dang_kham":    ("🔵 Đang khám",   "#2980b9"),
            "hoan_thanh":   ("✔️ Hoàn thành",  "#7f8c8d"),
            "huy":          ("❌ Đã hủy",       "#e74c3c"),
        }
        self.table.setRowCount(0)
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            qt = _parse_time(row["gio_kham"])
            st_text, st_color = status_map.get(row["trang_thai"], (row["trang_thai"],"#000"))
            vals = [str(row["ma_lich"]), row["ten_bn"], row["ten_bs"],
                    _fmt_date(row["ngay_kham"]), qt.toString("HH:mm"),
                    row.get("ly_do_kham") or "", st_text]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 6: item.setForeground(QColor(st_color))
                self.table.setItem(i, j, item)

            rc = dict(row)
            bf = QWidget(); bl = QHBoxLayout(bf)
            bl.setContentsMargins(4,2,4,2); bl.setSpacing(4)
            btn_e = QPushButton("✏️"); btn_e.setFixedSize(32,28)
            btn_e.setStyleSheet("background:#2980b9;color:white;border-radius:4px;font-size:14px;")
            btn_e.clicked.connect(lambda _, r=rc: self._edit(r))
            btn_d = QPushButton("🗑️"); btn_d.setFixedSize(32,28)
            btn_d.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;font-size:14px;")
            btn_d.clicked.connect(lambda _, mid=row["ma_lich"]: self._delete(mid))
            bl.addWidget(btn_e); bl.addWidget(btn_d)
            self.table.setCellWidget(i, 7, bf)
        self.table.resizeRowsToContents()

    def _add(self):
        dlg = LichKhamDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _edit(self, row_data):
        dlg = LichKhamDialog(self, lich_data=row_data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def _delete(self, ma_lich):
        r = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa lịch khám này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            LichKhamLogic.delete(ma_lich)
            self.load_data()
