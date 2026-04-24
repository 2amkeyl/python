from PyQt6.QtWidgets import (QDialog, QTableWidgetItem, QMessageBox)
from ui_py.form_dichvu_ui import Ui_FormDichVu
from database import ket_noi


class FormDichVu(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FormDichVu()
        self.ui.setupUi(self)
        self.load_du_lieu()
        self.ui.btn_them.clicked.connect(self.them)
        self.ui.btn_sua.clicked.connect(self.sua)
        self.ui.btn_xoa.clicked.connect(self.xoa)
        self.ui.btn_lammoi.clicked.connect(self.lam_moi)
        self.ui.btn_dong.clicked.connect(self.close)
        self.ui.tableWidget.clicked.connect(self.chon_dong)

    def load_du_lieu(self):
        self.ui.tableWidget.setRowCount(0)
        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute(
                "SELECT id,ten,gia_bs,gia_ths,gia_ts,mo_ta "
                "FROM dich_vu")
            for row in cur.fetchall():
                r = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(r)
                for c, val in enumerate(row):
                    self.ui.tableWidget.setItem(
                        r, c, QTableWidgetItem(str(val or "")))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    def lay_id(self):
        row = self.ui.tableWidget.currentRow()
        if row < 0: return None
        return self.ui.tableWidget.item(row, 0).text()

    def chon_dong(self):
        row = self.ui.tableWidget.currentRow()
        if row < 0: return
        cols = [self.ui.txt_ten, self.ui.txt_gia_bs,
                self.ui.txt_gia_ths, self.ui.txt_gia_ts,
                self.ui.txt_mota]
        for c, w in enumerate(cols):
            item = self.ui.tableWidget.item(row, c + 1)
            w.setText(item.text() if item else "")

    def them(self):
        ten = self.ui.txt_ten.text().strip()
        bs = self.ui.txt_gia_bs.text().strip()
        ths = self.ui.txt_gia_ths.text().strip()
        ts = self.ui.txt_gia_ts.text().strip()
        if not ten or not bs or not ths or not ts:
            QMessageBox.warning(self, "Loi",
                                "Nhap du: Ten, Gia BS, Gia ThS, Gia TS!")
            return
        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO dich_vu"
                "(ten,gia_bs,gia_ths,gia_ts,mo_ta)"
                " VALUES(%s,%s,%s,%s,%s)",
                (ten, int(bs), int(ths), int(ts),
                 self.ui.txt_mota.text().strip()))
            conn.commit();
            conn.close()
            self.load_du_lieu();
            self.lam_moi()
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    def sua(self):
        id_dv = self.lay_id()
        if not id_dv:
            QMessageBox.warning(self, "Loi", "Chon dong can sua!")
            return
        ten = self.ui.txt_ten.text().strip()
        bs = self.ui.txt_gia_bs.text().strip()
        ths = self.ui.txt_gia_ths.text().strip()
        ts = self.ui.txt_gia_ts.text().strip()
        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute(
                "UPDATE dich_vu SET "
                "ten=%s,gia_bs=%s,gia_ths=%s,gia_ts=%s,mo_ta=%s "
                "WHERE id=%s",
                (ten, int(bs), int(ths), int(ts),
                 self.ui.txt_mota.text().strip(), id_dv))
            conn.commit();
            conn.close()
            self.load_du_lieu();
            self.lam_moi()
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    def xoa(self):
        id_dv = self.lay_id()
        if not id_dv:
            QMessageBox.warning(self, "Loi", "Chon dong can xoa!")
            return
        xn = QMessageBox.question(
            self, "Xac nhan", "Chac chan muon xoa?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No)
        if xn != QMessageBox.StandardButton.Yes: return
        try:
            conn = ket_noi();
            cur = conn.cursor()
            cur.execute("DELETE FROM dich_vu WHERE id=%s", (id_dv,))
            conn.commit();
            conn.close()
            self.load_du_lieu();
            self.lam_moi()
        except Exception as e:
            QMessageBox.critical(self, "Loi", str(e))

    def lam_moi(self):
        for w in [self.ui.txt_ten, self.ui.txt_gia_bs,
                  self.ui.txt_gia_ths, self.ui.txt_gia_ts,
                  self.ui.txt_mota]:
            w.clear()
        self.ui.tableWidget.clearSelection()