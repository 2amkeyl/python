from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QWidget, QMessageBox)
from PyQt6.QtCore import Qt
from database import ket_noi

TBL = """
    QTableWidget{gridline-color:#e0e0e0;font-size:12px;background:#fff;}
    QHeaderView::section{background:#185FA5;color:white;font-weight:bold;
        padding:7px;border:none;
        border-right:1px solid rgba(255,255,255,0.3);}
    QTableWidget::item{background:#fff;color:#222;padding:4px;}
    QTableWidget::item:alternate{background:#f5f9ff;color:#222;}
    QTableWidget::item:hover{background:#e8f4fd;color:#222;}
    QTableWidget::item:selected{background:#cce5ff;color:#222;}
    QTableWidget::item:selected:hover{background:#b8d9ff;color:#222;}
"""


class FormDsBenhNhan(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Danh sach benh nhan")
        self.resize(900, 540)
        self._build_ui()
        self.load_du_lieu()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QLabel("DANH SACH BENH NHAN")
        hdr.setFixedHeight(44)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setStyleSheet(
            "background:#185FA5;color:white;"
            "font-size:14px;font-weight:bold;")
        root.addWidget(hdr)

        # Thanh tim kiem
        bar = QHBoxLayout()
        bar.setContentsMargins(10, 6, 10, 6);
        bar.setSpacing(6)
        bar.addWidget(QLabel("Tim kiem:"))
        self.txt_tim = QLineEdit()
        self.txt_tim.setPlaceholderText(
            "Ten hoac so dien thoai...")
        self.txt_tim.setFixedHeight(30)
        self.txt_tim.setMinimumWidth(220)
        self.btn_tim = QPushButton("Tim")
        self.btn_tim.setFixedSize(70, 30)
        self.btn_xoa_loc = QPushButton("Xoa bo loc")
        self.btn_xoa_loc.setFixedHeight(30)
        self.lbl_tong = QLabel("Tong: 0 benh nhan")
        self.lbl_tong.setStyleSheet(
            "color:#555;font-size:12px;font-weight:bold;")
        bar.addWidget(self.txt_tim)
        bar.addWidget(self.btn_tim)
        bar.addWidget(self.btn_xoa_loc)
        bar.addStretch()
        bar.addWidget(self.lbl_tong)
        bw = QWidget();
        bw.setLayout(bar)
        bw.setStyleSheet(
            "background:#f9f9f9;border-bottom:1px solid #e0e0e0;")
        root.addWidget(bw)

        # Bang — them cot Ma BN, So lan kham, Lan kham gan nhat
        self.tableWidget = QTableWidget()
        headers = ["Ma BN", "Ho ten", "So dien thoai",
                   "Ngay sinh", "Dia chi",
                   "So lan kham", "Lan kham gan nhat"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.setStyleSheet(TBL)
        root.addWidget(self.tableWidget)

        # Nut dong
        br = QHBoxLayout()
        br.setContentsMargins(10, 8, 10, 8);
        br.addStretch()
        self.btn_dong = QPushButton("Dong")
        self.btn_dong.setFixedSize(100, 32)
        self.btn_dong.setStyleSheet(
            "background:#888780;color:white;border-radius:5px;")
        br.addWidget(self.btn_dong)
        brw = QWidget();
        brw.setLayout(br)
        brw.setStyleSheet(
            "border-top:1px solid #e0e0e0;background:#f9f9f9;")
        root.addWidget(brw)

        self.btn_tim.clicked.connect(self.tim_kiem)
        self.txt_tim.returnPressed.connect(self.tim_kiem)
        self.btn_xoa_loc.clicked.connect(
            lambda: (self.txt_tim.clear(), self.load_du_lieu()))
        self.btn_dong.clicked.connect(self.close)

    def load_du_lieu(self, kw=""):
        self.tableWidget.setRowCount(0)
        try:
            conn = ket_noi();
            cur = conn.cursor()
            q = f"%{kw}%"
            # Lay BN tu bang benh_nhan, dem so lan kham tu lich_kham
            cur.execute("""
                        SELECT bn.ma_bn,
                               bn.ho_ten,
                               bn.sdt,
                               bn.ngay_sinh,
                               bn.dia_chi,
                               COUNT(lk.id)      AS so_lan_kham,
                               MAX(lk.ngay_kham) AS lan_gan_nhat
                        FROM benh_nhan bn
                                 LEFT JOIN lich_kham lk ON bn.id = lk.benh_nhan_id
                        WHERE bn.ho_ten LIKE %s
                           OR bn.sdt LIKE %s
                        GROUP BY bn.id, bn.ma_bn, bn.ho_ten,
                                 bn.sdt, bn.ngay_sinh, bn.dia_chi
                        ORDER BY bn.ho_ten
                        """, (q, q))
            rows = cur.fetchall()
            conn.close()
            self.lbl_tong.setText(
                f"Tong: {len(rows)} benh nhan")
            for row in rows:
                r = self.tableWidget.rowCount()
                self.tableWidget.insertRow(r)
                for c, val in enumerate(row):
                    self.tableWidget.setItem(
                        r, c, QTableWidgetItem(str(val or "")))
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    def tim_kiem(self):
        self.load_du_lieu(self.txt_tim.text().strip())
