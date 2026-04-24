from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QComboBox,
                             QDateEdit, QGroupBox, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
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


class FormBaoCao(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bao cao thong ke")
        self.resize(960, 600)
        self._build_ui()
        self._load_dich_vu()
        self.xem_bao_cao()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0);
        root.setSpacing(0)

        hdr = QLabel("BAO CAO & THONG KE")
        hdr.setFixedHeight(44)
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setStyleSheet(
            "background:#185FA5;color:white;"
            "font-size:14px;font-weight:bold;")
        root.addWidget(hdr)

        grp = QGroupBox("Bo loc")
        grp.setStyleSheet(
            "QGroupBox{margin:8px 10px;padding:8px;"
            "border:1px solid #ddd;border-radius:6px;}")
        grid = QGridLayout(grp);
        grid.setSpacing(8)

        INP = ("border:1px solid #ccc;border-radius:4px;"
               "padding:4px 8px;font-size:12px;")

        grid.addWidget(QLabel("Tu ngay:"), 0, 0)
        self.date_tu = QDateEdit()
        self.date_tu.setCalendarPopup(True)
        self.date_tu.setDisplayFormat("dd/MM/yyyy")
        self.date_tu.setDate(QDate.currentDate().addDays(-30))
        self.date_tu.setFixedHeight(30)
        self.date_tu.setStyleSheet(INP)
        grid.addWidget(self.date_tu, 0, 1)

        grid.addWidget(QLabel("Den ngay:"), 0, 2)
        self.date_den = QDateEdit()
        self.date_den.setCalendarPopup(True)
        self.date_den.setDisplayFormat("dd/MM/yyyy")
        self.date_den.setDate(QDate.currentDate())
        self.date_den.setFixedHeight(30)
        self.date_den.setStyleSheet(INP)
        grid.addWidget(self.date_den, 0, 3)

        grid.addWidget(QLabel("Trang thai:"), 1, 0)
        self.cmb_tt = QComboBox()
        self.cmb_tt.setFixedHeight(30)
        self.cmb_tt.setStyleSheet(INP)
        self.cmb_tt.addItems(
            ["Tat ca", "Cho kham", "Dang kham", "Da xong", "Da huy"])
        grid.addWidget(self.cmb_tt, 1, 1)

        grid.addWidget(QLabel("Dich vu:"), 1, 2)
        self.cmb_dv = QComboBox()
        self.cmb_dv.setFixedHeight(30)
        self.cmb_dv.setStyleSheet(INP)
        grid.addWidget(self.cmb_dv, 1, 3)

        self.btn_loc = QPushButton("Xem bao cao")
        self.btn_loc.setFixedHeight(34)
        self.btn_loc.setStyleSheet(
            "background:#185FA5;color:white;"
            "border-radius:5px;font-size:12px;padding:0 14px;")
        grid.addWidget(self.btn_loc, 0, 4, 2, 1)
        root.addWidget(grp)

        # 4 o thong ke
        sb = QHBoxLayout()
        sb.setContentsMargins(10, 6, 10, 6);
        sb.setSpacing(10)
        for ten, name, bg, fg, brd in [
            ("Tong lich kham", "lbl_tong_lk",
             "#f0f0f0", "#333", "#ccc"),
            ("Doanh thu (VND)", "lbl_doanh_thu",
             "#D1E7DD", "#0A3622", "#198754"),
            ("Luot da xong", "lbl_da_xong",
             "#CFE2FF", "#084298", "#3D8BFD"),
            ("Luot da huy", "lbl_da_huy",
             "#F8D7DA", "#842029", "#F1AEB5"),
        ]:
            col = QVBoxLayout();
            col.setSpacing(2)
            num = QLabel("0")
            num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fn = QFont();
            fn.setPointSize(18);
            fn.setBold(True)
            num.setFont(fn);
            num.setFixedHeight(50)
            num.setStyleSheet(
                f"color:{fg};background:{bg};"
                f"border:2px solid {brd};"
                f"border-radius:8px;padding:4px 12px;")
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

        # Bang chi tiet
        self.tableWidget = QTableWidget()
        headers = ["Ma lich", "Ho ten", "Dich vu",
                   "Goi kham", "Phi kham", "Ngay kham",
                   "Gio kham", "Trang thai"]
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

        br = QHBoxLayout()
        br.setContentsMargins(10, 8, 10, 8);
        br.addStretch()
        btn_dong = QPushButton("Dong")
        btn_dong.setFixedSize(100, 32)
        btn_dong.setStyleSheet(
            "background:#888780;color:white;border-radius:5px;")
        br.addWidget(btn_dong)
        brw = QWidget();
        brw.setLayout(br)
        brw.setStyleSheet(
            "border-top:1px solid #e0e0e0;background:#f9f9f9;")
        root.addWidget(brw)

        self.btn_loc.clicked.connect(self.xem_bao_cao)
        btn_dong.clicked.connect(self.close)

    def _load_dich_vu(self):
        self.cmb_dv.addItem("Tat ca dich vu")
        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute("SELECT ten FROM dich_vu")
            for row in cur.fetchall():
                self.cmb_dv.addItem(row[0])
            conn.close()
        except:
            pass

    def xem_bao_cao(self):
        tu = self.date_tu.date().toString("yyyy-MM-dd")
        den = self.date_den.date().toString("yyyy-MM-dd")
        tt = self.cmb_tt.currentText()
        dv = self.cmb_dv.currentText()

        where = ["lk.ngay_kham BETWEEN %s AND %s"]
        params = [tu, den]
        if tt != "Tat ca":
            where.append("lk.trang_thai = %s");
            params.append(tt)
        if dv != "Tat ca dich vu":
            where.append("dv.ten = %s");
            params.append(dv)
        ws = " AND ".join(where)

        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute(f"""
                SELECT COUNT(*), COALESCE(SUM(lk.phi_kham),0)
                FROM lich_kham lk
                LEFT JOIN dich_vu dv ON lk.dich_vu_id=dv.id
                WHERE {ws}""", params)
            tong, dt = cur.fetchone()
            self.lbl_tong_lk.setText(str(tong))
            self.lbl_doanh_thu.setText(f"{int(dt):,}")

            for lbl, extra in [
                (self.lbl_da_xong, "Da xong"),
                (self.lbl_da_huy, "Da huy"),
            ]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM lich_kham lk
                    LEFT JOIN dich_vu dv ON lk.dich_vu_id=dv.id
                    WHERE {ws} AND lk.trang_thai=%s""",
                            params + [extra])
                lbl.setText(str(cur.fetchone()[0]))

            # Bang chi tiet — lay ca ten BN
            cur.execute(f"""
                SELECT lk.ma_lich, bn.ho_ten, dv.ten,
                       lk.goi_kham, lk.phi_kham,
                       lk.ngay_kham, lk.gio_kham, lk.trang_thai
                FROM lich_kham lk
                JOIN benh_nhan bn ON lk.benh_nhan_id = bn.id
                LEFT JOIN dich_vu dv ON lk.dich_vu_id=dv.id
                WHERE {ws}
                ORDER BY lk.ngay_kham, lk.gio_kham""", params)

            self.tableWidget.setRowCount(0)
            for row in cur.fetchall():
                r = self.tableWidget.rowCount()
                self.tableWidget.insertRow(r)
                for c, val in enumerate(row):
                    self.tableWidget.setItem(
                        r, c, QTableWidgetItem(str(val or "")))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))