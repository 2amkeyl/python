from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QDate, QTime
from ui_py.form_sualich_ui import Ui_FormSuaLich
from database import ket_noi


class FormSuaLich(QDialog):
    def __init__(self, ma_lich):
        super().__init__()
        self.ui = Ui_FormSuaLich()
        self.ui.setupUi(self)
        self.ma_lich = ma_lich
        self._dv_data = []
        self.gia_hien_tai = 0
        self.goi_hien_tai = "Bac si"
        self._bn_id = None

        self.ui.lbl_title.setText(f"Sua lich kham — {ma_lich}")
        self.load_dich_vu()
        self.load_du_lieu()

        self.ui.btn_goi_bs.clicked.connect(
            lambda: self.chon_goi("Bac si"))
        self.ui.btn_goi_ths.clicked.connect(
            lambda: self.chon_goi("Thac si"))
        self.ui.btn_goi_ts.clicked.connect(
            lambda: self.chon_goi("Tien si"))
        self.ui.cmb_dichvu.currentIndexChanged.connect(self.tinh_gia)
        self.ui.btn_luu.clicked.connect(self.luu)
        self.ui.btn_huy.clicked.connect(self.close)

    def load_dich_vu(self):
        self.ui.cmb_dichvu.blockSignals(True)
        self.ui.cmb_dichvu.clear()
        conn = ket_noi();
        cur = conn.cursor()
        cur.execute("SELECT id,ten,gia_bs,gia_ths,gia_ts FROM dich_vu")
        self._dv_data = cur.fetchall()
        conn.close()
        for row in self._dv_data:
            self.ui.cmb_dichvu.addItem(row[1])
        self.ui.cmb_dichvu.blockSignals(False)

    def load_du_lieu(self):
        conn = ket_noi();
        cur = conn.cursor()
        cur.execute("""
                    SELECT lk.benh_nhan_id,
                           bn.ho_ten,
                           bn.sdt,
                           bn.ngay_sinh,
                           bn.dia_chi,
                           lk.dich_vu_id,
                           lk.goi_kham,
                           lk.ngay_kham,
                           lk.gio_kham,
                           lk.trang_thai
                    FROM lich_kham lk
                             JOIN benh_nhan bn ON lk.benh_nhan_id = bn.id
                    WHERE lk.ma_lich = %s
                    """, (self.ma_lich,))
        row = cur.fetchone()
        conn.close()
        if not row: return

        self._bn_id = row[0]
        self.ui.txt_ma.setText(self.ma_lich)
        self.ui.txt_hoten.setText(row[1])
        self.ui.txt_sdt.setText(row[2] or "")
        if row[3]:
            self.ui.date_ngaysinh.setDate(
                QDate.fromString(str(row[3]), "yyyy-MM-dd"))
        self.ui.txt_diachi.setText(row[4] or "")

        # Chon dich vu
        self.ui.cmb_dichvu.blockSignals(True)
        for i, dv in enumerate(self._dv_data):
            if dv[0] == row[5]:
                self.ui.cmb_dichvu.setCurrentIndex(i);
                break
        self.ui.cmb_dichvu.blockSignals(False)

        # Chon goi
        self.goi_hien_tai = row[6] or "Bac si"
        self.chon_goi(self.goi_hien_tai, update_gia=False)

        if row[7]:
            self.ui.date_ngaykham.setDate(
                QDate.fromString(str(row[7]), "yyyy-MM-dd"))
        if row[8]:
            self.ui.time_giokham.setTime(
                QTime.fromString(str(row[8]), "HH:mm:ss"))

        idx = self.ui.cmb_trangthai.findText(row[9] or "Cho kham")
        if idx >= 0:
            self.ui.cmb_trangthai.setCurrentIndex(idx)

        self.tinh_gia()

    def tinh_gia(self):
        idx = self.ui.cmb_dichvu.currentIndex()
        if idx < 0 or idx >= len(self._dv_data): return
        _, _, g_bs, g_ths, g_ts = self._dv_data[idx]
        gia_map = {
            "Bac si": g_bs,
            "Thac si": g_ths,
            "Tien si": g_ts
        }
        self.gia_hien_tai = gia_map.get(self.goi_hien_tai, g_bs)
        for b, lbl, g in zip(
                self.ui._goi_btns,
                ["Bac si", "Thac si", "Tien si"],
                [g_bs, g_ths, g_ts]):
            b.setText(f"{lbl}\n{g:,}d")
        self.ui.lbl_gia.setText(
            f"Phi kham          {self.gia_hien_tai:,} VND")

    def chon_goi(self, goi, update_gia=True):
        self.goi_hien_tai = goi
        m = {"Bac si": self.ui.btn_goi_bs,
             "Thac si": self.ui.btn_goi_ths,
             "Tien si": self.ui.btn_goi_ts}
        for g, b in m.items():
            b.setStyleSheet(
                self.ui._BTN_ACT if g == goi
                else self.ui._BTN_INACT)
        if update_gia: self.tinh_gia()

    def luu(self):
        hoten = self.ui.txt_hoten.text().strip()
        sdt = self.ui.txt_sdt.text().strip()
        if not hoten or not sdt:
            QMessageBox.warning(self, "Loi", "Nhap du thong tin!")
            return
        idx = self.ui.cmb_dichvu.currentIndex()
        id_dv = self._dv_data[idx][0]
        try:
            conn = ket_noi();
            cur = conn.cursor()
            # Cap nhat thong tin BN
            cur.execute("""
                        UPDATE benh_nhan
                        SET ho_ten=%s,
                            sdt=%s,
                            ngay_sinh=%s,
                            dia_chi=%s
                        WHERE id = %s
                        """, (
                            hoten, sdt,
                            self.ui.date_ngaysinh.date().toString("yyyy-MM-dd"),
                            self.ui.txt_diachi.text().strip(),
                            self._bn_id
                        ))
            # Cap nhat lich kham
            cur.execute("""
                        UPDATE lich_kham
                        SET dich_vu_id=%s,
                            goi_kham=%s,
                            phi_kham=%s,
                            ngay_kham=%s,
                            gio_kham=%s,
                            trang_thai=%s
                        WHERE ma_lich = %s
                        """, (
                            id_dv, self.goi_hien_tai, self.gia_hien_tai,
                            self.ui.date_ngaykham.date().toString("yyyy-MM-dd"),
                            self.ui.time_giokham.time().toString("HH:mm:ss"),
                            self.ui.cmb_trangthai.currentText(),
                            self.ma_lich
                        ))
            conn.commit();
            conn.close()
            QMessageBox.information(
                self, "Thanh cong", "Da luu thay doi!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Loi", f"Loi luu:\n{e}")