"""
ui/styles.py
────────────
Hằng số style CSS dùng chung cho toàn bộ ứng dụng.
Thay đổi tại đây là thay đổi toàn bộ giao diện.
"""

# ── Nút bấm ────────────────────────────────────────────────────────────────
BTN_STYLE = """
QPushButton {{
    background: {bg}; color: white; border: none;
    border-radius: 6px; padding: 8px 16px; font-size: 13px; font-weight: bold;
}}
QPushButton:hover {{ background: {hover}; }}
QPushButton:disabled {{ background: #bdc3c7; }}
"""

# Nút icon nhỏ trong bảng (✏️ 🗑️ 👁️)
ICON_BTN_STYLE = "background:{bg};color:white;border-radius:4px;font-size:14px;"

# ── Bảng dữ liệu ───────────────────────────────────────────────────────────
TABLE_STYLE = """
QTableWidget {{
    background: white; border-radius: 8px; border: none;
    gridline-color: #ecf0f1;
}}
QHeaderView::section {{
    background: {header_bg}; color: white; padding: 10px;
    font-weight: bold; border: none;
}}
QTableWidget::item {{ padding: 8px; }}
QTableWidget::item:selected {{ background: #d6eaf8; color: #1c2833; }}
"""

TABLE_STYLE_DEFAULT = TABLE_STYLE.format(header_bg="#1a5276")
TABLE_STYLE_PURPLE  = TABLE_STYLE.format(header_bg="#8e44ad")

# ── Input / Form ───────────────────────────────────────────────────────────
INPUT_STYLE = (
    "border: 1.5px solid #d5d8dc; border-radius: 6px; "
    "padding: 6px 10px; font-size: 13px; background: white;"
)

FORM_STYLE = (
    "QDialog { background: white; } "
    "QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit, QSpinBox, QDoubleSpinBox "
    "{ border: 1.5px solid #d5d8dc; border-radius: 6px; padding: 5px; font-size: 13px; }"
)

# ── GroupBox ───────────────────────────────────────────────────────────────
GRP_STYLE = (
    "QGroupBox {{ font-weight: bold; color: {c}; border: 1.5px solid {b}; "
    "border-radius: 8px; margin-top: 8px; padding-top: 12px; }} "
    "QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}"
)

# ── Sidebar (main window) ──────────────────────────────────────────────────
SIDEBAR_BTN_STYLE = (
    "QPushButton { background: transparent; color: #bdc3c7; text-align: left; "
    "padding-left: 18px; border: none; font-size: 13px; } "
    "QPushButton:hover { background: #2c3e50; color: white; } "
    "QPushButton:checked { background: #1a5276; color: white; "
    "border-left: 4px solid #3498db; }"
)

SIDEBAR_LOGOUT_STYLE = (
    "QPushButton { background: transparent; color: #e74c3c; text-align: left; "
    "padding-left: 18px; border: none; font-size: 13px; } "
    "QPushButton:hover { background: #2c3e50; }"
)
