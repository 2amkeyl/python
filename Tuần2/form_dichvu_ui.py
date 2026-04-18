from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLabel, QLineEdit, QPushButton,
                             QTableWidget, QHeaderView)
from PyQt6.QtCore import Qt

TBL_DV = """
    QTableWidget{gridline-color:#e0e0e0;font-size:12px;background:#fff;}
    QHeaderView::section{background:#534AB7;color:white;font-weight:bold;
        padding:6px;border:none;
        border-right:1px solid rgba(255,255,255,0.3);}
    QTableWidget::item{background:#fff;color:#222;padding:4px;}
    QTableWidget::item:alternate{background:#fafaf8;color:#222;}
    QTableWidget::item:hover{background:#f0eeff;color:#222;}
    QTableWidget::item:selected{background:#e8e5ff;color:#222;}
    QTableWidget::item:selected:hover{background:#d8d5ff;color:#222;}
"""


class Ui_FormDichVu:
    def setupUi(self, dialog):
        dialog.setWindowTitle("Quan ly dich vu kham")
        dialog.resize(640, 480)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(0, 0, 0, 0);
        root.setSpacing(0)

        hdr = QLabel("Quan ly dich vu kham")
        hdr.setFixedHeight(42)
        hdr.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        hdr.setStyleSheet(
            "background:#534AB7;color:white;"
            "font-size:14px;font-weight:bold;padding-left:14px;")
        root.addWidget(hdr)

        body = QVBoxLayout()
        body.setContentsMargins(16, 12, 16, 8);
        body.setSpacing(8)

        INP = ("border:1px solid #ccc;border-radius:4px;"
               "padding:4px 8px;font-size:12px;")

        form = QFormLayout();
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.txt_ten = QLineEdit()
        self.txt_ten.setPlaceholderText("Ten dich vu *")
        self.txt_ten.setFixedHeight(32)
        self.txt_ten.setStyleSheet(INP)

        self.txt_gia_bs = QLineEdit()
        self.txt_gia_bs.setPlaceholderText("VD: 200000")
        self.txt_gia_bs.setFixedHeight(32)
        self.txt_gia_bs.setStyleSheet(INP)

        self.txt_gia_ths = QLineEdit()
        self.txt_gia_ths.setPlaceholderText("VD: 300000")
        self.txt_gia_ths.setFixedHeight(32)
        self.txt_gia_ths.setStyleSheet(INP)

        self.txt_gia_ts = QLineEdit()
        self.txt_gia_ts.setPlaceholderText("VD: 400000")
        self.txt_gia_ts.setFixedHeight(32)
        self.txt_gia_ts.setStyleSheet(INP)

        self.txt_mota = QLineEdit()
        self.txt_mota.setPlaceholderText("Mo ta ngan (tuy chon)")
        self.txt_mota.setFixedHeight(32)
        self.txt_mota.setStyleSheet(INP)

        form.addRow("Ten dich vu (*):", self.txt_ten)
        form.addRow("Gia Bac si (*):", self.txt_gia_bs)
        form.addRow("Gia Thac si (*):", self.txt_gia_ths)
        form.addRow("Gia Tien si (*):", self.txt_gia_ts)
        form.addRow("Mo ta:", self.txt_mota)
        body.addLayout(form)

        btn_row = QHBoxLayout();
        btn_row.setSpacing(6)

        def mk(text, bg, fg="white"):
            b = QPushButton(text);
            b.setFixedHeight(34)
            b.setStyleSheet(
                f"QPushButton{{background:{bg};color:{fg};"
                f"border-radius:5px;padding:0 16px;font-size:12px;}}"
                f"QPushButton:hover{{opacity:0.85;}}")
            return b

        self.btn_them = mk("Them", "#1D9E75")
        self.btn_sua = mk("Sua", "#185FA5")
        self.btn_xoa = mk("Xoa", "#E24B4A")
        self.btn_lammoi = mk("Lam moi", "#888780")
        self.btn_dong = mk("Dong", "#444441")
        for b in [self.btn_them, self.btn_sua,
                  self.btn_xoa, self.btn_lammoi]:
            btn_row.addWidget(b)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_dong)
        body.addLayout(btn_row)

        self.tableWidget = QTableWidget()
        headers = ["ID", "Ten dich vu",
                   "Gia BS", "Gia ThS", "Gia TS", "Mo ta"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.tableWidget.setStyleSheet(TBL_DV)
        body.addWidget(self.tableWidget)
        root.addLayout(body)
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QDialog

    app = QApplication(sys.argv)
    dialog = QDialog()
    ui = Ui_FormDichVu()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec())