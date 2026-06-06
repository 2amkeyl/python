"""
ui/main_window_ui.py
────────────────────
Cửa sổ chính: sidebar điều hướng + StackedWidget chứa các trang.
Phân quyền menu uỷ thác cho RoleLogic.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QButtonGroup, QMessageBox,
)
from PyQt6.QtCore import Qt
from ui.styles import SIDEBAR_BTN_STYLE, SIDEBAR_LOGOUT_STYLE
from logic import RoleLogic

from pages.dashboard_page  import DashboardPage
from pages.lich_kham_page  import LichKhamPage
from pages.kham_benh_page  import KhamBenhPage
from pages.benh_nhan_page  import BenhNhanPage
from pages.bac_si_page     import BacSiPage
from pages.benh_an_page    import BenhAnPage
from pages.thuoc_page      import ThuocPage
from pages.tai_khoan_page  import TaiKhoanPage
from pages.le_tan_page     import LeTanPage
from pages.dich_vu_page    import DichVuPage
from pages.hoa_don_page    import HoaDonPage


class MainWindow(QMainWindow):
    def __init__(self, user_info: dict):
        super().__init__()
        self.user_info = user_info
        self._do_logout = False
        self.setWindowTitle("Quản Lý Phòng Khám")
        self._build_ui()
        self._apply_role()
        self._set_default_page()

    # ── Build UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # Sidebar
        main_lay.addWidget(self._build_sidebar())

        # Content area
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.setStyleSheet("background: #f4f6f7;")
        self._setup_pages()
        main_lay.addWidget(self.stackedWidget)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(215)
        sidebar.setStyleSheet("QFrame { background: #1c2833; }")

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 8)
        lay.setSpacing(2)

        # Logo header
        logo = QFrame()
        logo.setMinimumHeight(110)
        logo.setStyleSheet("QFrame { background: #1a5276; }")
        ll = QVBoxLayout(logo)
        ll.setSpacing(4)

        lbl_icon = QLabel("🏥")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 28px; background: transparent;")

        lbl_name = QLabel("PHÒNG KHÁM")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setStyleSheet(
            "color: white; font-weight: bold; font-size: 13px; background: transparent;")

        ho_ten = self.user_info.get("ho_ten") or \
                 self.user_info.get("ten_dang_nhap", "")
        role_label = RoleLogic.display_role(self.user_info)
        self.userLabel = QLabel(f"{ho_ten}  |  {role_label}")
        self.userLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.userLabel.setWordWrap(True)
        self.userLabel.setStyleSheet(
            "color: #aed6f1; font-size: 11px; background: transparent;")

        ll.addWidget(lbl_icon)
        ll.addWidget(lbl_name)
        ll.addWidget(self.userLabel)
        lay.addWidget(logo)

        # Nav buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("btnDashboard", "   📊   Tổng Quan",   0),
            ("btnLichKham",  "   📅   Lịch Khám",   1),
            ("btnKhamBenh",  "   🩺   Khám Bệnh",   2),
            ("btnBenhNhan",  "   👤   Bệnh Nhân",   3),
            ("btnBacSi",     "   👨‍⚕️   Bác Sĩ",     4),
            ("btnBenhAn",    "   📋   Bệnh Án",     5),
            ("btnThuoc",     "   💊   Thuốc",       6),
            ("btnTaiKhoan",  "   🔑   Tài Khoản",   7),
            ("btnLeTan",     "   👩‍💼   Lễ Tân",     8),
            ("btnDichVu",    "   🏷️   Dịch Vụ",    9),
            ("btnHoaDon",    "   💳   Hóa Đơn",    10),
        ]
        for attr, text, idx in nav_items:
            btn = QPushButton(text)
            btn.setMinimumHeight(46)
            btn.setCheckable(True)
            btn.setStyleSheet(SIDEBAR_BTN_STYLE)
            btn.clicked.connect(lambda _, i=idx: self._go(i))
            setattr(self, attr, btn)
            self.nav_group.addButton(btn)
            lay.addWidget(btn)

        lay.addStretch()

        # Logout
        self.btnLogout = QPushButton("   🚪   Đăng Xuất")
        self.btnLogout.setMinimumHeight(46)
        self.btnLogout.setStyleSheet(SIDEBAR_LOGOUT_STYLE)
        self.btnLogout.clicked.connect(self._logout)
        lay.addWidget(self.btnLogout)

        return sidebar

    def _setup_pages(self):
        self._pages = [
            DashboardPage(self.user_info),   # 0
            LichKhamPage(self.user_info),    # 1
            KhamBenhPage(self.user_info),    # 2
            BenhNhanPage(self.user_info),    # 3
            BacSiPage(self.user_info),       # 4
            BenhAnPage(self.user_info),      # 5
            ThuocPage(self.user_info),       # 6
            TaiKhoanPage(self.user_info),    # 7
            LeTanPage(self.user_info),       # 8
            DichVuPage(self.user_info),      # 9
            HoaDonPage(self.user_info),      # 10
        ]
        for page in self._pages:
            self.stackedWidget.addWidget(page)

    # ── Navigation ─────────────────────────────────────────────────────
    def _go(self, index: int):
        self.stackedWidget.setCurrentIndex(index)
        page = self._pages[index]
        if hasattr(page, "load_data"):
            page.load_data()

    def _set_default_page(self):
        btn_name, page_idx = RoleLogic.default_page(self.user_info)
        btn = getattr(self, btn_name, None)
        if btn:
            btn.setChecked(True)
        self.stackedWidget.setCurrentIndex(page_idx)

    # ── Role-based menu visibility ─────────────────────────────────────
    def _apply_role(self):
        visibility = RoleLogic.menu_visibility(self.user_info)
        for btn_name, visible in visibility.items():
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setVisible(visible)

    # ── Logout ─────────────────────────────────────────────────────────
    def _logout(self):
        r = QMessageBox.question(
            self, "Đăng xuất", "Bạn có chắc muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r == QMessageBox.StandardButton.Yes:
            self._do_logout = True
            self.close()
