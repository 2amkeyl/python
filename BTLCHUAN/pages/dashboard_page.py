"""
pages/dashboard_page.py
───────────────────────
Dashboard thống kê - KHÔNG dùng matplotlib (tránh OpenBLAS crash).
Vẽ biểu đồ thuần bằng QPainter / QWidget.
Logic → DashboardLogic.
"""
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QButtonGroup, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QPainterPath,
)

from logic import DashboardLogic
from database import db

# ── Màu sắc ────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "cho_xac_nhan": QColor("#F39C12"),
    "da_xac_nhan":  QColor("#3498DB"),
    "dang_kham":    QColor("#9B59B6"),
    "hoan_thanh":   QColor("#2ECC71"),
    "huy":          QColor("#E74C3C"),
}
STATUS_LABELS = {
    "cho_xac_nhan": "Chờ xác nhận",
    "da_xac_nhan":  "Đã xác nhận",
    "dang_kham":    "Đang khám",
    "hoan_thanh":   "Hoàn thành",
    "huy":          "Đã hủy",
}
BAR_COLOR   = QColor("#1ABC9C")
BAR_COLOR2  = QColor("#148F77")
CARD_INFO   = [
    ("#EBF5FB", "#2E86C1", "📅", "Lịch hôm nay"),
    ("#EAFAF1", "#1E8449", "👤", "Bệnh nhân"),
    ("#FEF9E7", "#B7950B", "💳", "Doanh thu hôm nay"),
    ("#FDEDEC", "#C0392B", "⏳", "Chờ xác nhận"),
]


def _fmt_money(val: float) -> str:
    try:
        v = float(val or 0)
        if v >= 1_000_000_000:
            return f"{v/1_000_000_000:.1f}B đ"
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f}M đ"
        if v >= 1_000:
            return f"{v/1_000:.0f}K đ"
        return f"{v:.0f} đ"
    except Exception:
        return "0 đ"


# ════════════════════════════════════════════════════════════════════════
#  Widget biểu đồ tròn (Pie chart)
# ════════════════════════════════════════════════════════════════════════
class PieChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: list[tuple[str, int, QColor]] = []   # (label, value, color)
        self.setMinimumSize(320, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[tuple[str, int, QColor]]):
        self._data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        total = sum(v for _, v, _ in self._data)
        if total == 0:
            painter.setPen(QColor("#95A5A6"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Chưa có dữ liệu")
            return

        # Kích thước pie
        legend_h = 20 * len(self._data) + 10
        pie_size  = min(w - 20, h - legend_h - 20)
        pie_size  = max(pie_size, 80)
        pie_x     = (w - pie_size) // 2
        pie_y     = 10
        rect      = QRectF(pie_x, pie_y, pie_size, pie_size)

        # Vẽ từng miếng
        start_angle = 90 * 16   # Qt dùng 1/16 độ, bắt đầu từ 12h
        for label, value, color in self._data:
            span = int(round(value / total * 360 * 16))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawPie(rect, start_angle, -span)

            # % text ở giữa miếng
            mid_angle = (start_angle - span / 2) / 16
            import math
            rad       = math.radians(mid_angle)
            cx        = pie_x + pie_size / 2 + math.cos(rad) * pie_size * 0.32
            cy        = pie_y + pie_size / 2 - math.sin(rad) * pie_size * 0.32
            pct       = value / total * 100
            if pct >= 5:
                painter.setPen(QColor("white"))
                f = QFont(); f.setBold(True); f.setPointSize(8)
                painter.setFont(f)
                painter.drawText(
                    QRectF(cx - 24, cy - 10, 48, 20),
                    Qt.AlignmentFlag.AlignCenter,
                    f"{pct:.0f}%",
                )
            start_angle -= span

        # Legend bên dưới
        legend_y = int(pie_y + pie_size + 10)
        col_w    = w // min(3, len(self._data))
        f2 = QFont(); f2.setPointSize(8)
        painter.setFont(f2)
        for i, (label, value, color) in enumerate(self._data):
            col   = i % 3
            row   = i // 3
            lx    = col * col_w + 8
            ly    = legend_y + row * 20
            # Ô màu
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(lx, ly + 2, 12, 12, 3, 3)
            # Text
            painter.setPen(QColor("#2C3E50"))
            painter.drawText(lx + 16, ly, col_w - 16, 18,
                             Qt.AlignmentFlag.AlignVCenter,
                             f"{label} ({value})")


# ════════════════════════════════════════════════════════════════════════
#  Widget biểu đồ cột (Bar chart)
# ════════════════════════════════════════════════════════════════════════
class BarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._labels: list[str]  = []
        self._values: list[float] = []
        self._title  = ""
        self.setMinimumSize(380, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, labels: list[str], values: list[float], title: str = ""):
        self._labels = labels
        self._values = values
        self._title  = title
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h    = self.width(), self.height()
        pad_l   = 62
        pad_r   = 16
        pad_t   = 36
        pad_b   = 48
        plot_w  = w - pad_l - pad_r
        plot_h  = h - pad_t - pad_b

        if not self._values or plot_w <= 0 or plot_h <= 0:
            return

        max_val = max(self._values) if self._values else 1
        if max_val == 0:
            max_val = 1

        # Tiêu đề
        f_title = QFont(); f_title.setBold(True); f_title.setPointSize(9)
        painter.setFont(f_title)
        painter.setPen(QColor("#2C3E50"))
        painter.drawText(0, 0, w, pad_t,
                         Qt.AlignmentFlag.AlignCenter, self._title)

        # Grid lines (5 dòng ngang)
        f_small = QFont(); f_small.setPointSize(7)
        painter.setFont(f_small)
        grid_pen = QPen(QColor("#ECF0F1"), 1, Qt.PenStyle.SolidLine)
        for i in range(6):
            y   = pad_t + plot_h - int(plot_h * i / 5)
            val = max_val * i / 5
            # Grid line
            painter.setPen(grid_pen)
            painter.drawLine(pad_l, y, pad_l + plot_w, y)
            # Y label
            painter.setPen(QColor("#7F8C8D"))
            painter.drawText(0, y - 9, pad_l - 4, 18,
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             _fmt_money(val))

        # Trục
        axis_pen = QPen(QColor("#BDC3C7"), 1)
        painter.setPen(axis_pen)
        painter.drawLine(pad_l, pad_t, pad_l, pad_t + plot_h)
        painter.drawLine(pad_l, pad_t + plot_h, pad_l + plot_w, pad_t + plot_h)

        # Cột
        n       = len(self._values)
        bar_gap = max(4, plot_w // (n * 4))
        bar_w   = max(8, (plot_w - bar_gap * (n + 1)) // n)

        f_val = QFont(); f_val.setPointSize(7)
        painter.setFont(f_val)

        for i, (val, label) in enumerate(zip(self._values, self._labels)):
            bx  = pad_l + bar_gap + i * (bar_w + bar_gap)
            bh  = int(plot_h * val / max_val) if max_val > 0 else 0
            by  = pad_t + plot_h - bh

            # Gradient-like: 2 màu
            color = BAR_COLOR if val > 0 else QColor("#D5D8DC")
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            radius = min(4, bar_w // 3)
            path.addRoundedRect(QRectF(bx, by, bar_w, bh), radius, radius)
            painter.drawPath(path)

            # Giá trị trên cột
            if val > 0:
                painter.setPen(QColor("#1A5276"))
                painter.drawText(
                    bx - 10, by - 16, bar_w + 20, 16,
                    Qt.AlignmentFlag.AlignCenter,
                    _fmt_money(val),
                )

            # X label
            painter.setPen(QColor("#2C3E50"))
            painter.drawText(
                bx - 8, pad_t + plot_h + 4, bar_w + 16, pad_b - 4,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
                label,
            )


# ════════════════════════════════════════════════════════════════════════
#  Trang Dashboard
# ════════════════════════════════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self._build_ui()
        self.load_data()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.load_data)
        self._timer.start(30_000)

    # ── Xây giao diện ───────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # Tiêu đề
        title = QLabel("📊 Tổng Quan & Thống Kê")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#2C3E50;")
        root.addWidget(title)

        # 4 card số liệu
        card_row = QHBoxLayout()
        card_row.setSpacing(12)
        self._cards = []
        for bg, fg, icon, label in CARD_INFO:
            card = self._make_card(bg, fg, icon, label)
            card_row.addWidget(card)
            self._cards.append(card)
        root.addLayout(card_row)

        # Khu vực biểu đồ
        chart_row = QHBoxLayout()
        chart_row.setSpacing(14)

        # ── Biểu đồ tròn ──
        left_frame = QFrame()
        left_frame.setStyleSheet(
            "QFrame{background:white;border-radius:10px;"
            "border:1px solid #E8ECEF;}")
        lf = QVBoxLayout(left_frame)
        lf.setContentsMargins(12, 10, 12, 10)
        lbl_pie = QLabel("🏥 Lịch khám theo trạng thái")
        lbl_pie.setStyleSheet("font-weight:bold;font-size:13px;color:#2C3E50;")
        lf.addWidget(lbl_pie)
        self.pieChart = PieChart()
        lf.addWidget(self.pieChart)
        chart_row.addWidget(left_frame, 4)

        # ── Biểu đồ cột ──
        right_frame = QFrame()
        right_frame.setStyleSheet(
            "QFrame{background:white;border-radius:10px;"
            "border:1px solid #E8ECEF;}")
        rf = QVBoxLayout(right_frame)
        rf.setContentsMargins(12, 10, 12, 10)
        rf.setSpacing(6)

        # Header doanh thu + nút period
        hdr_rev = QHBoxLayout()
        lbl_rev = QLabel("💰 Doanh thu (hóa đơn đã thanh toán)")
        lbl_rev.setStyleSheet("font-weight:bold;font-size:13px;color:#2C3E50;")
        hdr_rev.addWidget(lbl_rev)
        hdr_rev.addStretch()

        self.btnGroup = QButtonGroup(self)
        self.btnGroup.setExclusive(True)
        for txt in ["Tuần", "Tháng", "Năm"]:
            btn = QPushButton(txt)
            btn.setCheckable(True)
            btn.setFixedWidth(60)
            btn.setFixedHeight(26)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #BDC3C7; border-radius: 4px;
                    background: white; font-size: 12px;
                }
                QPushButton:checked {
                    background: #1ABC9C; color: white;
                    border-color: #17A589;
                }
                QPushButton:hover { background: #D5F5E3; }
            """)
            self.btnGroup.addButton(btn)
            hdr_rev.addWidget(btn)

        self.btnGroup.buttons()[1].setChecked(True)   # mặc định Tháng
        self.btnGroup.buttonClicked.connect(self._on_period_changed)
        rf.addLayout(hdr_rev)

        self.barChart = BarChart()
        rf.addWidget(self.barChart)
        chart_row.addWidget(right_frame, 6)

        root.addLayout(chart_row)

        # Bảng lịch hôm nay
        lbl_today = QLabel("📅 Lịch khám hôm nay")
        lbl_today.setStyleSheet(
            "font-weight:bold;font-size:13px;color:#2C3E50;")
        root.addWidget(lbl_today)

        self.todayTable = QTableWidget()
        self.todayTable.setColumnCount(5)
        self.todayTable.setHorizontalHeaderLabels(
            ["Giờ khám", "Bệnh nhân", "Bác sĩ", "Lý do", "Trạng thái"])
        self.todayTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.todayTable.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.todayTable.setAlternatingRowColors(True)
        self.todayTable.setMaximumHeight(180)
        self.todayTable.verticalHeader().setVisible(False)
        self.todayTable.setStyleSheet("""
            QTableWidget { background: white; border-radius: 8px;
                           border: none; gridline-color: #ecf0f1; }
            QHeaderView::section { background: #1a5276; color: white;
                           padding: 8px; font-weight: bold; border: none; }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background: #d6eaf8; }
        """)
        root.addWidget(self.todayTable)

    # ── Card helper ─────────────────────────────────────────────────────
    def _make_card(self, bg, fg, icon, label):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame{{background:{bg};border-radius:10px;"
            f"border:1px solid {fg}33;}}")
        frame.setMinimumHeight(88)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)

        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:24px;")
        top.addWidget(ico)
        top.addStretch()
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size:11px;color:{fg};font-weight:bold;")
        top.addWidget(lbl)
        lay.addLayout(top)

        val = QLabel("—")
        val.setStyleSheet(
            f"font-size:22px;font-weight:bold;color:{fg};")
        val.setObjectName("cardValue")
        lay.addWidget(val)
        return frame

    def _set_card(self, idx, text):
        self._cards[idx].findChild(QLabel, "cardValue").setText(text)

    # ── Load toàn bộ ────────────────────────────────────────────────────
    def load_data(self):
        self._load_cards()
        self._load_pie()
        self._load_revenue()
        self._load_today_table()

    def _load_cards(self):
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        self._set_card(0, str(DashboardLogic.count_lich_hom_nay(today_str)))
        self._set_card(1, str(DashboardLogic.count_benh_nhan()))
        self._set_card(2, _fmt_money(
            DashboardLogic.doanh_thu_ngay(today_str)))
        self._set_card(3, str(DashboardLogic.count_cho_xac_nhan()))

    def _load_pie(self):
        rows = DashboardLogic.thong_ke_trang_thai()
        data = []
        for r in rows:
            tt    = r["trang_thai"]
            label = STATUS_LABELS.get(tt, tt)
            color = STATUS_COLORS.get(tt, QColor("#95A5A6"))
            data.append((label, int(r["cnt"]), color))
        self.pieChart.set_data(data)

    def _on_period_changed(self, _btn):
        self._load_revenue()

    def _load_revenue(self):
        checked = [b for b in self.btnGroup.buttons() if b.isChecked()]
        period  = checked[0].text() if checked else "Tháng"
        now     = datetime.now()
        labels: list[str]  = []
        values: list[float] = []

        if period == "Tuần":
            for i in range(6, -1, -1):
                d = (now - timedelta(days=i)).date()
                labels.append(d.strftime("%d/%m"))
                values.append(DashboardLogic.doanh_thu_ngay(
                    d.strftime("%Y-%m-%d")))

        elif period == "Tháng":
            for i in range(11, -1, -1):
                m = now.month - i
                y = now.year
                while m <= 0:
                    m += 12
                    y -= 1
                labels.append(f"T{m}\n{str(y)[-2:]}")
                vals = DashboardLogic.doanh_thu_theo_thang([(y, m)])
                values.append(vals[0] if vals else 0.0)

        else:  # Năm
            for i in range(4, -1, -1):
                y = now.year - i
                labels.append(str(y))
                vals = DashboardLogic.doanh_thu_theo_nam([y])
                values.append(vals[0] if vals else 0.0)

        title_map = {
            "Tuần":  "Doanh thu 7 ngày gần nhất  (chỉ HĐ đã thanh toán)",
            "Tháng": "Doanh thu 12 tháng gần nhất (chỉ HĐ đã thanh toán)",
            "Năm":   "Doanh thu 5 năm gần nhất    (chỉ HĐ đã thanh toán)",
        }
        self.barChart.set_data(labels, values, title_map[period])

    def _load_today_table(self):
        today_str = datetime.now().date().strftime("%Y-%m-%d")
        rows = db.execute_query("""
            SELECT lk.gio_kham, bn.ho_ten AS benh_nhan,
                   bs.ho_ten AS bac_si,
                   lk.ly_do_kham, lk.trang_thai
            FROM   lichkham lk
            JOIN   benhnhan bn ON lk.ma_bn = bn.ma_bn
            JOIN   bacsi    bs ON lk.ma_bs = bs.ma_bs
            WHERE  lk.ngay_kham = %s
            ORDER  BY lk.gio_kham
        """, (today_str,), fetch=True) or []

        self.todayTable.setRowCount(0)
        for r in rows:
            i = self.todayTable.rowCount()
            self.todayTable.insertRow(i)
            tt     = r.get("trang_thai", "")
            st_lbl = STATUS_LABELS.get(tt, tt)
            color  = STATUS_COLORS.get(tt, QColor("#FFFFFF"))
            bg     = QColor(color.red(), color.green(), color.blue(), 40)
            vals   = [
                str(r["gio_kham"]),
                r["benh_nhan"],
                r["bac_si"],
                r.get("ly_do_kham") or "—",
                st_lbl,
            ]
            for j, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(bg)
                self.todayTable.setItem(i, j, item)
        self.todayTable.resizeRowsToContents()
