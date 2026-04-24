from PyQt6.QtWidgets import (QMainWindow, QTableWidgetItem,
                             QMessageBox, QDialog)
from PyQt6.QtGui import QColor
from ui_py.mainwindow_ui import Ui_MainWindow
from database import ket_noi


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.load_du_lieu()
        self.cap_nhat_thong_ke()

        self.ui.btn_datlich.clicked.connect(self.mo_dat_lich)
        self.ui.btn_dsbn.clicked.connect(self.mo_ds_benh_nhan)
        self.ui.btn_dichvu.clicked.connect(self.mo_dich_vu)
        self.ui.btn_baocao.clicked.connect(self.mo_bao_cao)
        self.ui.btn_sua.clicked.connect(self.mo_sua_lich)
        self.ui.btn_huy.clicked.connect(self.huy_lich)
        self.ui.btn_tim.clicked.connect(self.tim_kiem)
        self.ui.btn_dangxuat.clicked.connect(self.dang_xuat)
        self.ui.txt_tim.returnPressed.connect(self.tim_kiem)

    def load_du_lieu(self, tu_khoa=""):
        self.ui.tableWidget.setRowCount(0)
        try:
            conn = ket_noi()
            cur = conn.cursor()
            kw = f"%{tu_khoa}%"
            cur.execute("""
                        SELECT lk.ma_lich,
                               bn.ho_ten,
                               bn.sdt,
                               dv.ten,
                               lk.goi_kham,
                               lk.phi_kham,
                               lk.ngay_kham,
                               lk.gio_kham,
                               lk.trang_thai
                        FROM lich_kham lk
                                 JOIN benh_nhan bn ON lk.benh_nhan_id = bn.id
                                 LEFT JOIN dich_vu dv ON lk.dich_vu_id = dv.id
                        WHERE bn.ho_ten LIKE %s
                           OR bn.sdt LIKE %s
                        ORDER BY lk.ngay_kham DESC, lk.gio_kham
                        """, (kw, kw))
            for row in cur.fetchall():
                r = self.ui.tableWidget.rowCount()
                self.ui.tableWidget.insertRow(r)
                for c, val in enumerate(row):
                    item = QTableWidgetItem(str(val or ""))
                    if row[8] == "Da huy":
                        item.setForeground(QColor("#aaaaaa"))
                    self.ui.tableWidget.setItem(r, c, item)
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Loi", f"Loi tai du lieu:\n{e}")

    def cap_nhat_thong_ke(self):
        try:
            conn = ket_noi()
            cur = conn.cursor()
            for tt, lbl in [
                ("Cho kham", self.ui.lbl_cho),
                ("Dang kham", self.ui.lbl_dang),
                ("Da xong", self.ui.lbl_xong),
            ]:
                cur.execute(
                    "SELECT COUNT(*) FROM lich_kham "
                    "WHERE trang_thai=%s", (tt,))
                lbl.setText(str(cur.fetchone()[0]))
            cur.execute("SELECT COUNT(*) FROM lich_kham")
            self.ui.lbl_tong.setText(str(cur.fetchone()[0]))
            conn.close()
        except:
            pass

    def tim_kiem(self):
        self.load_du_lieu(self.ui.txt_tim.text().strip())

    def mo_dat_lich(self):
        from form_datlich import FormDatLich
        f = FormDatLich()
        if f.exec() == QDialog.DialogCode.Accepted:
            self.load_du_lieu()
            self.cap_nhat_thong_ke()

    def mo_sua_lich(self):
        row = self.ui.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Loi", "Vui long chon lich can sua!")
            return
        ma = self.ui.tableWidget.item(row, 0).text()
        from form_sualich import FormSuaLich
        f = FormSuaLich(ma)
        if f.exec() == QDialog.DialogCode.Accepted:
            self.load_du_lieu()
            self.cap_nhat_thong_ke()

    def huy_lich(self):
        row = self.ui.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Loi", "Vui long chon lich can huy!")
            return
        tt = self.ui.tableWidget.item(row, 8).text()
        if tt == "Da huy":
            QMessageBox.information(
                self, "Thong bao", "Lich nay da duoc huy!")
            return
        if tt == "Da xong":
            QMessageBox.warning(
                self, "Loi", "Khong the huy lich da kham xong!")
            return
        ma = self.ui.tableWidget.item(row, 0).text()
        ten = self.ui.tableWidget.item(row, 1).text()
        xn = QMessageBox.question(
            self, "Xac nhan huy lich",
            f"Huy lich {ma} — {ten}?\n"
            f"Trang thai se doi thanh 'Da huy'.",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No)
        if xn != QMessageBox.StandardButton.Yes: return
        conn = ket_noi();
        cur = conn.cursor()
        cur.execute(
            "UPDATE lich_kham SET trang_thai='Da huy' "
            "WHERE ma_lich=%s", (ma,))
        conn.commit();
        conn.close()
        self.load_du_lieu()
        self.cap_nhat_thong_ke()
        QMessageBox.information(
            self, "Thanh cong", "Da huy lich thanh cong!")

    def mo_dich_vu(self):
        from form_dichvu import FormDichVu
        FormDichVu().exec()

    def mo_ds_benh_nhan(self):
        from form_dsbenhnhan import FormDsBenhNhan
        FormDsBenhNhan().exec()

    def mo_bao_cao(self):
        from form_baocao import FormBaoCao
        FormBaoCao().exec()

    def dang_xuat(self):
        xn = QMessageBox.question(
            self, "Xac nhan", "Ban co muon dang xuat?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No)
        if xn == QMessageBox.StandardButton.Yes:
            self.close()
