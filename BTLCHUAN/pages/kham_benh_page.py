"""
pages/kham_benh_page.py
───────────────────────
Bác sĩ ghi kết quả khám và kê đơn thuốc.
DB calls sử dụng KhamBenhLogic thay vì gọi db trực tiếp.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QDialog, QFormLayout, QTextEdit, QMessageBox, QFrame,
    QComboBox, QSpinBox, QGroupBox, QAbstractItemView, QSplitter,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from datetime import date

from ui.styles import TABLE_STYLE_DEFAULT, TABLE_STYLE_PURPLE, INPUT_STYLE
from logic import KhamBenhLogic

_BTN = ("QPushButton{{background:{bg};color:white;border:none;"
        "border-radius:6px;padding:7px 16px;font-size:12px;font-weight:bold;}}"
        "QPushButton:hover{{background:{hv};}}"
        "QPushButton:disabled{{background:#bdc3c7;}}")
_INPUT = INPUT_STYLE


def _btn(text, bg, hv, h=34):
    b = QPushButton(text)
    b.setMinimumHeight(h)
    b.setStyleSheet(_BTN.format(bg=bg, hv=hv))
    return b


# ── Dialog chọn thuốc ────────────────────────────────────────────────────
class _AddMedicineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_item = None
        self.setWindowTitle("Thêm thuốc vào đơn")
        self.setFixedSize(500, 310)
        self.setStyleSheet("QDialog{background:white;}")
        self._all = []
        self._ids = []
        self._rows = []
        self._build()
        self._load()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)
        lay.addWidget(QLabel("<b style='font-size:14px;color:#1a5276'>💊 Chọn thuốc và liều dùng</b>"))

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.eSearch = QLineEdit()
        self.eSearch.setPlaceholderText("Gõ tên thuốc để lọc...")
        self.eSearch.setMinimumHeight(34)
        self.eSearch.setStyleSheet(_INPUT)
        self.eSearch.textChanged.connect(self._filter)
        form.addRow("Tìm:", self.eSearch)

        self.cbThuoc = QComboBox()
        self.cbThuoc.setMinimumHeight(34)
        self.cbThuoc.setStyleSheet(_INPUT)
        self.cbThuoc.currentIndexChanged.connect(self._on_sel)
        form.addRow("Thuốc *:", self.cbThuoc)

        self.lblInfo = QLabel("")
        self.lblInfo.setStyleSheet("color:#2980b9;font-size:12px;font-style:italic;")
        form.addRow("", self.lblInfo)

        self.spSL = QSpinBox()
        self.spSL.setRange(1, 9999)
        self.spSL.setValue(1)
        self.spSL.setMinimumHeight(34)
        self.spSL.setStyleSheet(_INPUT)
        form.addRow("Số lượng *:", self.spSL)

        self.eLieu = QLineEdit()
        self.eLieu.setPlaceholderText("VD: Uống 2 viên/lần × 3 lần/ngày sau ăn")
        self.eLieu.setMinimumHeight(34)
        self.eLieu.setStyleSheet(_INPUT)
        form.addRow("Liều dùng *:", self.eLieu)

        lay.addLayout(form)
        brow = QHBoxLayout()
        brow.addStretch()
        bc = _btn("Hủy", "#95a5a6", "#7f8c8d")
        bc.clicked.connect(self.reject)
        ba = _btn("✅  Thêm vào đơn", "#27ae60", "#1e8449")
        ba.clicked.connect(self._accept)
        brow.addWidget(bc); brow.addWidget(ba)
        lay.addLayout(brow)

    def _load(self):
        self._all = KhamBenhLogic.get_thuoc_available()
        self._refresh(self._all)

    def _refresh(self, items):
        self.cbThuoc.blockSignals(True)
        self.cbThuoc.clear()
        self._ids = []; self._rows = []
        for r in items:
            self.cbThuoc.addItem(f"{r['ten_thuoc']}  ({r.get('don_vi','') or ''})")
            self._ids.append(r["ma_thuoc"]); self._rows.append(r)
        self.cbThuoc.blockSignals(False)
        self._on_sel(0)

    def _filter(self, txt):
        txt = txt.strip().lower()
        self._refresh([r for r in self._all if txt in r["ten_thuoc"].lower()] if txt else self._all)

    def _on_sel(self, idx):
        if not self._rows or idx < 0 or idx >= len(self._rows):
            self.lblInfo.setText(""); return
        r = self._rows[idx]
        self.lblInfo.setText(
            f"Đơn giá: {int(r.get('gia',0) or 0):,} đ  |  "
            f"Tồn kho: {int(r.get('so_luong_ton',0) or 0)} {r.get('don_vi','')}")

    def _accept(self):
        if not self._ids:
            QMessageBox.warning(self, "Lỗi", "Không có thuốc!"); return
        if not self.eLieu.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập liều dùng!"); return
        idx = self.cbThuoc.currentIndex()
        r = self._rows[idx]
        self.result_item = {
            "ma_thuoc":  self._ids[idx], "ten_thuoc": r["ten_thuoc"],
            "don_vi":    r.get("don_vi", "") or "",
            "gia":       int(r.get("gia", 0) or 0),
            "so_luong":  self.spSL.value(),
            "lieu_dung": self.eLieu.text().strip(),
        }
        self.accept()


# ── Dialog khám bệnh ─────────────────────────────────────────────────────
class KhamBenhDialog(QDialog):
    def __init__(self, parent, lich_data: dict):
        super().__init__(parent)
        self.lich = lich_data
        self._items = []
        self._ma_ba = None
        self._ma_don = None
        self.setWindowTitle(f"Khám bệnh  –  {lich_data.get('ten_bn','')}")
        self.setMinimumSize(920, 700)
        self.setStyleSheet("QDialog{background:#f4f6f7;}")
        self._build_ui()
        self._load_existing()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(self._make_header())

        body = QFrame(); body.setStyleSheet("background:#f4f6f7;")
        bl = QHBoxLayout(body); bl.setContentsMargins(14, 14, 14, 14)
        sp = QSplitter(Qt.Orientation.Horizontal)
        sp.setHandleWidth(6)
        sp.setStyleSheet("QSplitter::handle{background:#d5d8dc;}")
        sp.addWidget(self._make_left()); sp.addWidget(self._make_right())
        sp.setSizes([480, 420])
        bl.addWidget(sp)
        root.addWidget(body, 1)
        root.addWidget(self._make_footer())

    def _make_header(self):
        f = QFrame(); f.setStyleSheet("background:#1a5276;"); f.setFixedHeight(64)
        hl = QHBoxLayout(f); hl.setContentsMargins(22, 0, 22, 0)
        title = QLabel("🩺  PHIẾU KHÁM BỆNH")
        title.setStyleSheet("color:white;font-size:16px;font-weight:bold;background:transparent;")
        info = QLabel(
            f"BN: <b>{self.lich.get('ten_bn','')}</b>  |  "
            f"BS: <b>{self.lich.get('ten_bs','')}</b>  |  "
            f"Ngày: <b>{self.lich.get('ngay_kham','')}</b>")
        info.setStyleSheet("color:#aed6f1;font-size:12px;background:transparent;")
        self._lbl_status = QLabel("")
        self._lbl_status.setStyleSheet("color:#f9e79f;font-size:12px;background:transparent;")
        hl.addWidget(title); hl.addStretch(); hl.addWidget(info)
        hl.addSpacing(20); hl.addWidget(self._lbl_status)
        return f

    def _make_left(self):
        f = QFrame()
        f.setStyleSheet("background:white;border-radius:10px;border:1px solid #e8ecef;")
        lay = QVBoxLayout(f); lay.setContentsMargins(18, 16, 18, 16); lay.setSpacing(10)
        lay.addWidget(QLabel("<b style='font-size:13px;color:#1a5276'>📋  KẾT QUẢ KHÁM BỆNH</b>"))

        def grp(title, ph, h=85):
            g = QGroupBox(title)
            g.setStyleSheet(
                "QGroupBox{font-weight:bold;color:#2c3e50;border:1.5px solid #d5d8dc;"
                "border-radius:7px;margin-top:8px;padding-top:4px;}"
                "QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 4px;}")
            gl = QVBoxLayout(g)
            te = QTextEdit()
            te.setPlaceholderText(ph); te.setMinimumHeight(h)
            te.setStyleSheet("border:none;background:#fdfefe;font-size:13px;")
            gl.addWidget(te)
            return g, te

        g1, self.eTrieu    = grp("Triệu chứng",          "Mô tả triệu chứng...")
        g2, self.eChanDoan = grp("Chẩn đoán *",          "Nhập chẩn đoán bệnh...")
        g3, self.eDieuTri  = grp("Phương pháp điều trị", "Phương pháp điều trị...")
        g4, self.eKetQua   = grp("Kết quả / Lời dặn",   "Kết quả, lời dặn...", 70)
        lay.addWidget(g1); lay.addWidget(g2); lay.addWidget(g3); lay.addWidget(g4)
        lay.addStretch()
        return f

    def _make_right(self):
        f = QFrame()
        f.setStyleSheet("background:white;border-radius:10px;border:1px solid #e8ecef;")
        lay = QVBoxLayout(f); lay.setContentsMargins(18, 16, 18, 16); lay.setSpacing(10)

        hr = QHBoxLayout()
        hr.addWidget(QLabel("<b style='font-size:13px;color:#1a5276'>💊  ĐƠN THUỐC</b>"))
        hr.addStretch()
        bAdd = _btn("➕ Thêm thuốc", "#27ae60", "#1e8449")
        bAdd.clicked.connect(self._add_medicine)
        hr.addWidget(bAdd)
        lay.addLayout(hr)

        self.eGhiChu = QLineEdit()
        self.eGhiChu.setPlaceholderText("Ghi chú đơn thuốc (nếu có)...")
        self.eGhiChu.setMinimumHeight(32); self.eGhiChu.setStyleSheet(_INPUT)
        lay.addWidget(self.eGhiChu)

        self.tblThuoc = QTableWidget()
        self.tblThuoc.setColumnCount(6)
        self.tblThuoc.setHorizontalHeaderLabels(["#","Tên thuốc","ĐV","SL","Liều dùng","Xóa"])
        hh = self.tblThuoc.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for c in (0, 2, 3, 5):
            hh.setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        self.tblThuoc.setAlternatingRowColors(True)
        self.tblThuoc.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblThuoc.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblThuoc.verticalHeader().setVisible(False)
        self.tblThuoc.setStyleSheet(TABLE_STYLE_PURPLE)
        self.tblThuoc.setMinimumHeight(240)
        lay.addWidget(self.tblThuoc)

        self.lblTotal = QLabel("Tổng tiền:  0 đ")
        self.lblTotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lblTotal.setStyleSheet(
            "font-size:13px;font-weight:bold;color:#e74c3c;"
            "background:#fef9f9;border-radius:6px;padding:6px 12px;"
            "border:1px solid #f5b7b1;")
        lay.addWidget(self.lblTotal)
        lay.addStretch()
        return f

    def _make_footer(self):
        f = QFrame(); f.setStyleSheet("background:white;border-top:1px solid #eaecee;")
        fl = QHBoxLayout(f); fl.setContentsMargins(20, 10, 20, 10)
        self.lblSaved = QLabel("")
        self.lblSaved.setStyleSheet("color:#27ae60;font-size:12px;")
        fl.addWidget(self.lblSaved); fl.addStretch()
        bc = _btn("Đóng",            "#95a5a6", "#7f8c8d", 40)
        bs = _btn("💾  Lưu kết quả", "#1a5276", "#2471a3", 40)
        bp = _btn("🖨️  In phiếu",    "#e67e22", "#d35400", 40)
        bc.clicked.connect(self.reject); bs.clicked.connect(self._save)
        bp.clicked.connect(self._print)
        fl.addWidget(bc); fl.addWidget(bs); fl.addWidget(bp)
        return f

    def _load_existing(self):
        ma_lich = self.lich.get("ma_lich")
        ba = KhamBenhLogic.get_benh_an_by_lich(ma_lich)
        if ba:
            self._ma_ba = ba["ma_ba"]
            self.eTrieu.setText(ba.get("trieu_chung") or "")
            self.eChanDoan.setText(ba.get("chuan_doan") or "")
            self.eDieuTri.setText(ba.get("phuong_phap_dieu_tri") or "")
            self.eKetQua.setText(ba.get("ket_qua") or "")
            self._lbl_status.setText("✏️ Chỉnh sửa bệnh án đã có")

            don = KhamBenhLogic.get_don_thuoc(self._ma_ba)
            if don:
                self._ma_don = don["ma_don"]
                self.eGhiChu.setText(don.get("ghi_chu") or "")
                items = KhamBenhLogic.get_chi_tiet_don_thuoc(self._ma_don)
                for it in items:
                    self._items.append({
                        "ma_thuoc":  it["ma_thuoc"], "ten_thuoc": it["ten_thuoc"],
                        "don_vi":    it.get("don_vi", "") or "",
                        "gia":       int(it.get("gia", 0) or 0),
                        "so_luong":  it["so_luong"],
                        "lieu_dung": it.get("lieu_dung", "") or "",
                    })
                self._refresh_table()
        else:
            self._lbl_status.setText("🆕 Tạo bệnh án mới")

    def _add_medicine(self):
        dlg = _AddMedicineDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_item:
            for it in self._items:
                if it["ma_thuoc"] == dlg.result_item["ma_thuoc"]:
                    it["so_luong"] += dlg.result_item["so_luong"]
                    it["lieu_dung"] = dlg.result_item["lieu_dung"]
                    self._refresh_table(); return
            self._items.append(dlg.result_item)
            self._refresh_table()

    def _remove_medicine(self, idx):
        if 0 <= idx < len(self._items):
            self._items.pop(idx); self._refresh_table()

    def _refresh_table(self):
        self.tblThuoc.setRowCount(0)
        total = 0
        for i, it in enumerate(self._items):
            self.tblThuoc.insertRow(i)
            tt = it["gia"] * it["so_luong"]; total += tt
            for j, v in enumerate([str(i+1), it["ten_thuoc"], it["don_vi"],
                                    str(it["so_luong"]), it["lieu_dung"]]):
                cell = QTableWidgetItem(v)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tblThuoc.setItem(i, j, cell)
            bd = QPushButton("🗑️"); bd.setFixedSize(28, 26)
            bd.setStyleSheet("background:#e74c3c;color:white;border-radius:4px;font-size:13px;")
            bd.clicked.connect(lambda _, x=i: self._remove_medicine(x))
            self.tblThuoc.setCellWidget(i, 5, bd)
        self.lblTotal.setText(f"Tổng tiền thuốc:  {total:,} đ")
        self.tblThuoc.resizeRowsToContents()

    def _save(self):
        tc = self.eTrieu.toPlainText().strip()
        cd = self.eChanDoan.toPlainText().strip()
        dt = self.eDieuTri.toPlainText().strip()
        kq = self.eKetQua.toPlainText().strip()
        if not cd:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập chẩn đoán!")
            self.eChanDoan.setFocus(); return

        self._ma_ba = KhamBenhLogic.save_benh_an(
            self._ma_ba, self.lich["ma_lich"], tc, cd, dt, kq)
        self._lbl_status.setText("✏️ Chỉnh sửa bệnh án đã có")

        if self._items:
            items = [{"ma_thuoc": it["ma_thuoc"], "so_luong": it["so_luong"],
                      "lieu_dung": it["lieu_dung"]} for it in self._items]
            self._ma_don = KhamBenhLogic.save_don_thuoc(
                self._ma_don, self._ma_ba, self.eGhiChu.text().strip(), items)

        self.lblSaved.setText("✅ Đã lưu thành công!")
        QMessageBox.information(self, "Thành công", "Đã lưu kết quả khám và đơn thuốc!")

    def _print(self):
        tc  = self.eTrieu.toPlainText().strip() or "—"
        cd  = self.eChanDoan.toPlainText().strip() or "—"
        dt  = self.eDieuTri.toPlainText().strip() or "—"
        kq  = self.eKetQua.toPlainText().strip() or "—"
        gc  = self.eGhiChu.text().strip() or "—"
        bn  = self.lich.get("ten_bn", ""); bs = self.lich.get("ten_bs", "")
        ngay = self.lich.get("ngay_kham", "")

        rows_html = ""; total = 0
        for i, it in enumerate(self._items):
            tt = it["gia"] * it["so_luong"]; total += tt
            rows_html += (f"<tr><td align='center'>{i+1}</td>"
                          f"<td><b>{it['ten_thuoc']}</b></td>"
                          f"<td align='center'>{it['so_luong']} {it['don_vi']}</td>"
                          f"<td>{it['lieu_dung']}</td>"
                          f"<td align='right'>{tt:,} đ</td></tr>")
        if not rows_html:
            rows_html = "<tr><td colspan='5' align='center' style='color:#999'>Không có đơn thuốc</td></tr>"

        html = f"""<html><head><meta charset='utf-8'>
<style>
  body{{font-family:Arial,sans-serif;font-size:13px;margin:28px;}}
  h2{{text-align:center;color:#1a5276;}} hr{{border:1px solid #d5d8dc;}}
  .block{{background:#f4f6f7;padding:9px 13px;border-left:4px solid #1a5276;margin:7px 0;border-radius:4px;}}
  table{{width:100%;border-collapse:collapse;margin-top:8px;}}
  th{{background:#1a5276;color:white;padding:8px;text-align:left;}}
  td{{padding:7px 8px;border-bottom:1px solid #eee;}}
  .total{{text-align:right;font-weight:bold;color:#e74c3c;font-size:14px;margin-top:6px;}}
</style></head><body>
<h2>🏥 PHÒNG KHÁM ĐA KHOA</h2><hr>
<p><b>Bệnh nhân:</b> {bn}&nbsp;&nbsp;<b>Ngày:</b> {ngay}&nbsp;&nbsp;<b>Bác sĩ:</b> {bs}</p>
<div class='block'><b>Triệu chứng:</b><br>{tc}</div>
<div class='block'><b>Chẩn đoán:</b><br>{cd}</div>
<div class='block'><b>Điều trị:</b><br>{dt}</div>
<div class='block'><b>Kết quả:</b><br>{kq}</div>
<h3 style='color:#8e44ad'>💊 ĐƠN THUỐC</h3>
<table>
  <tr><th>#</th><th>Tên thuốc</th><th>Số lượng</th><th>Liều dùng</th><th>Thành tiền</th></tr>
  {rows_html}
</table>
<p class='total'>Tổng tiền: {total:,} đ</p>
<p style='color:#999;font-size:11px'>Ghi chú: {gc}</p>
<div style='text-align:right;margin-top:30px'><p><b>Bác sĩ điều trị</b><br><br><br>BS. {bs}</p></div>
</body></html>"""

        from PyQt6.QtWidgets import QTextEdit as QTE
        dlg = QDialog(self)
        dlg.setWindowTitle("Xem trước phiếu khám")
        dlg.setMinimumSize(680, 600); dlg.setStyleSheet("QDialog{background:white;}")
        vl = QVBoxLayout(dlg)
        te = QTE(); te.setReadOnly(True); te.setHtml(html)
        vl.addWidget(te)
        bc = _btn("Đóng", "#1a5276", "#2471a3", 38)
        bc.clicked.connect(dlg.accept)
        vl.addWidget(bc, alignment=Qt.AlignmentFlag.AlignRight)
        dlg.exec()


# ── Trang chính ──────────────────────────────────────────────────────────
class KhamBenhPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self._build()
        self.load_data()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.load_data)
        self._timer.start(60_000)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(25, 20, 25, 20); lay.setSpacing(14)

        hr = QHBoxLayout()
        title = QLabel("🩺  PHÒNG KHÁM – GHI KẾT QUẢ & KÊ ĐƠN THUỐC")
        title.setStyleSheet("font-size:18px;font-weight:bold;color:#1c2833;")
        hr.addWidget(title); hr.addStretch()
        bRef = _btn("🔄 Làm mới", "#2980b9", "#2471a3")
        bRef.clicked.connect(self.load_data); hr.addWidget(bRef)
        lay.addLayout(hr)

        ff = QFrame(); ff.setStyleSheet("background:white;border-radius:8px;padding:10px 16px;")
        fl = QHBoxLayout(ff); fl.setSpacing(10)

        self.eSearch = QLineEdit()
        self.eSearch.setPlaceholderText("🔍 Tìm tên bệnh nhân...")
        self.eSearch.setMinimumHeight(34); self.eSearch.setStyleSheet(_INPUT)
        self.eSearch.textChanged.connect(self.load_data)

        self.cbDate = QComboBox()
        self.cbDate.addItems(["Hôm nay", "Tất cả ngày"])
        self.cbDate.setMinimumHeight(34); self.cbDate.setStyleSheet(_INPUT)
        self.cbDate.currentIndexChanged.connect(self.load_data)

        self.cbStatus = QComboBox()
        self.cbStatus.addItems(["Tất cả trạng thái","Chờ xác nhận","Đã xác nhận",
                                 "Đang khám","Hoàn thành","Đã hủy"])
        self.cbStatus.setMinimumHeight(34); self.cbStatus.setStyleSheet(_INPUT)
        self.cbStatus.currentIndexChanged.connect(self.load_data)

        fl.addWidget(QLabel("Tìm:")); fl.addWidget(self.eSearch, 2)
        fl.addWidget(QLabel("Ngày:")); fl.addWidget(self.cbDate)
        fl.addWidget(QLabel("Trạng thái:")); fl.addWidget(self.cbStatus)
        lay.addWidget(ff)

        self.tbl = QTableWidget()
        self.tbl.setColumnCount(8)
        self.tbl.setHorizontalHeaderLabels(
            ["Mã","Bệnh nhân","Bác sĩ","Ngày khám","Giờ","Lý do","Trạng thái","Thao tác"])
        hh = self.tbl.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(7, 200)
        self.tbl.setAlternatingRowColors(True)
        self.tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl.setStyleSheet(TABLE_STYLE_DEFAULT)
        self.tbl.verticalHeader().setVisible(False)
        lay.addWidget(self.tbl)

        self.lblStat = QLabel("")
        self.lblStat.setStyleSheet("color:#7f8c8d;font-size:12px;")
        lay.addWidget(self.lblStat)

    def load_data(self):
        search = self.eSearch.text().strip()
        sv = [None,"cho_xac_nhan","da_xac_nhan","dang_kham","hoan_thanh","huy"]
        status = sv[self.cbStatus.currentIndex()]
        today_only = self.cbDate.currentIndex() == 0

        rows = KhamBenhLogic.get_lich_kham_list(search, today_only, status)

        ST = {
            "cho_xac_nhan": ("⏳ Chờ xác nhận","#e67e22"),
            "da_xac_nhan":  ("✅ Đã xác nhận", "#27ae60"),
            "dang_kham":    ("🔵 Đang khám",   "#2980b9"),
            "hoan_thanh":   ("✔️ Hoàn thành",  "#7f8c8d"),
            "huy":          ("❌ Đã hủy",       "#e74c3c"),
        }
        self.tbl.setRowCount(0)
        for i, r in enumerate(rows):
            self.tbl.insertRow(i)
            st, sc = ST.get(r["trang_thai"], (r["trang_thai"],"#000"))
            ngay = str(r["ngay_kham"])
            try:
                from datetime import datetime as _dt
                ngay = _dt.strptime(ngay, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                pass
            for j, v in enumerate([str(r["ma_lich"]), r["ten_bn"], r["ten_bs"],
                                    ngay, str(r["gio_kham"]),
                                    r.get("ly_do_kham","") or "", st]):
                cell = QTableWidgetItem(v)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if j == 6:
                    cell.setForeground(QColor(sc))
                self.tbl.setItem(i, j, cell)

            fw = QWidget()
            fl2 = QHBoxLayout(fw); fl2.setContentsMargins(4,2,4,2); fl2.setSpacing(5)
            can_start = r["trang_thai"] in ("cho_xac_nhan","da_xac_nhan")
            bStart = _btn("▶ Bắt đầu",
                          "#27ae60" if can_start else "#bdc3c7",
                          "#1e8449" if can_start else "#bdc3c7", 28)
            bStart.setEnabled(can_start)
            bStart.clicked.connect(lambda _, row=r: self._start(row))
            bKham = _btn("🩺 Ghi kết quả", "#1a5276", "#2471a3", 28)
            bKham.clicked.connect(lambda _, row=r: self._open_exam(row))
            fl2.addWidget(bStart); fl2.addWidget(bKham)
            self.tbl.setCellWidget(i, 7, fw)

        self.tbl.resizeRowsToContents()
        today_str = date.today().strftime("%Y-%m-%d")
        hom_nay = sum(1 for r in rows if str(r["ngay_kham"]) == today_str)
        ht = sum(1 for r in rows if r["trang_thai"] == "hoan_thanh")
        self.lblStat.setText(f"Hiển thị {len(rows)} lịch  •  Hôm nay: {hom_nay}  •  Hoàn thành: {ht}")

    def _start(self, row):
        from logic import LichKhamLogic
        LichKhamLogic.update_trang_thai(row["ma_lich"], "dang_kham")
        self.load_data()

    def _open_exam(self, row):
        dlg = KhamBenhDialog(self, row)
        dlg.exec()
        self.load_data()
