from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QHeaderView, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

TBL = """
    QTableWidget{gridline-color:#e0e0e0;font-size:12px;background:#fff;}
    QHeaderView::section{background:#1D9E75;color:white;font-weight:bold;
        padding:7px;border:none;
        border-right:1px solid rgba(255,255,255,0.3);}
    QTableWidget::item{background:#fff;color:#222;padding:4px;}
    QTableWidget::item:alternate{background:#f8fffe;color:#222;}
    QTableWidget::item:hover{background:#e8f4fd;color:#222;}
    QTableWidget::item:selected{background:#cce5ff;color:#222;}
    QTableWidget::item:selected:hover{background:#b8d9ff;color:#222;}
"""


class Ui_MainWindow:
    def setupUi(self, win):
        win.setWindowTitle("Quan ly dich vu kham benh")
        win.resize(1100, 680)

        central = QWidget()
        win.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Tieu de
        self.lbl_title = QLabel("PHAN MEM QUAN LY KHAM BENH")
        f = QFont();
        f.setPointSize(16);
        f.setBold(True)
        self.lbl_title.setFont(f)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setFixedHeight(60)
        self.lbl_title.setStyleSheet(
            "color:white;background:#1D9E75;padding:10px;")
        root.addWidget(self.lbl_title)

        # 2. Menu 4 nut
        mb = QHBoxLayout()
        mb.setSpacing(0);
        mb.setContentsMargins(0, 0, 0, 0)

        def mk_menu(text, bg, fg="white", br=True):
            b = QPushButton(text)
            b.setFixedHeight(42)
            b.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed)
            brd = "border-right:1px solid rgba(255,255,255,0.3);" if br else ""
            b.setStyleSheet(
                f"QPushButton{{background:{bg};color:{fg};"
                f"font-size:13px;border:none;{brd}}}"
                f"QPushButton:hover{{background:rgba(0,0,0,0.08);}}")
            return b

        self.btn_datlich = mk_menu("+ Dat lich moi", "#1D9E75")
        self.btn_dsbn = mk_menu("Danh sach benh nhan", "#e8e8e8", "#333")
        self.btn_dichvu = mk_menu("Quan ly dich vu", "#e8e8e8", "#333")
        self.btn_baocao = mk_menu("Bao cao", "#185FA5", br=False)
        for b in [self.btn_datlich, self.btn_dsbn,
                  self.btn_dichvu, self.btn_baocao]:
            mb.addWidget(b)
        mw = QWidget();
        mw.setLayout(mb)
        mw.setStyleSheet("border-bottom:1px solid #ccc;")
        root.addWidget(mw)

        # 3. Thanh tim kiem + nut
        ab = QHBoxLayout()
        ab.setContentsMargins(10, 6, 10, 6);
        ab.setSpacing(6)
        lbl_t = QLabel("Tim kiem:")
        lbl_t.setFixedWidth(70)
        self.txt_tim = QLineEdit()
        self.txt_tim.setPlaceholderText(
            "Nhap ten hoac so dien thoai...")
        self.txt_tim.setFixedHeight(30)
        self.txt_tim.setMinimumWidth(220)
        self.btn_tim = QPushButton("Tim")
        self.btn_tim.setFixedSize(70, 30)
        self.btn_tim.setStyleSheet(
            "border:1px solid #ccc;border-radius:4px;")

        def mk_act(text, bg):
            b = QPushButton(text)
            b.setFixedHeight(30)
            b.setStyleSheet(
                f"QPushButton{{background:{bg};color:white;"
                f"border-radius:4px;padding:0 14px;font-size:12px;}}"
                f"QPushButton:hover{{opacity:0.85;}}")
            return b

        self.btn_sua = mk_act("Sua lich", "#185FA5")
        self.btn_huy = mk_act("Huy lich", "#E24B4A")
        self.btn_dangxuat = mk_act("Dang xuat", "#888780")
        ab.addWidget(lbl_t);
        ab.addWidget(self.txt_tim)
        ab.addWidget(self.btn_tim);
        ab.addStretch()
        ab.addWidget(self.btn_sua)
        ab.addWidget(self.btn_huy)
        ab.addWidget(self.btn_dangxuat)
        aw = QWidget();
        aw.setLayout(ab)
        aw.setStyleSheet(
            "background:#f9f9f9;border-bottom:1px solid #e0e0e0;")
        root.addWidget(aw)

        # 4. Thong ke
        sb = QHBoxLayout()
        sb.setContentsMargins(10, 8, 10, 8);
        sb.setSpacing(10)
        for ten, name, bg, fg, brd in [
            ("Tong lich", "lbl_tong", "#f0f0f0", "#333", "#ccc"),
            ("Cho kham", "lbl_cho", "#FFF3CD", "#856404", "#FFCA2C"),
            ("Dang kham", "lbl_dang", "#CFE2FF", "#084298", "#3D8BFD"),
            ("Da xong", "lbl_xong", "#D1E7DD", "#0A3622", "#198754"),
        ]:
            col = QVBoxLayout();
            col.setSpacing(2)
            num = QLabel("0")
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fn = QFont();
            fn.setPointSize(22);
            fn.setBold(True)
            num.setFont(fn);
            num.setFixedHeight(55)
            num.setStyleSheet(
                f"color:{fg};background:{bg};"
                f"border:2px solid {brd};"
                f"border-radius:8px;padding:4px 16px;")
            setattr(self, name, num)
            lbl = QLabel(ten)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                "font-size:11px;color:#555;font-weight:500;")
            col.addWidget(num);
            col.addWidget(lbl)
            sb.addLayout(col)
        sw = QWidget();
        sw.setLayout(sb)
        sw.setStyleSheet(
            "background:white;border-bottom:1px solid #e0e0e0;")
        root.addWidget(sw)

        # 5. Bang du lieu
        self.tableWidget = QTableWidget()
        headers = ["Ma lich", "Ten benh nhan", "SDT",
                   "Dich vu", "Goi kham", "Phi kham (VND)",
                   "Ngay kham", "Gio kham", "Trang thai"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setShowGrid(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.setStyleSheet(TBL)
        root.addWidget(self.tableWidget)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)
    win = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(win)
    win.show()
    sys.exit(app.exec())