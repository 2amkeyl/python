from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QDate
from ui_py.form_datlich_ui import Ui_FormDatLich
from database import ket_noi


class FormDatLich(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FormDatLich()
        self.ui.setupUi(self)
        self._dv_data = []
        self.gia_hien_tai = 0
        self.goi_hien_tai = "Bác sĩ"
        self._bn_id_hien_tai = None  # ID bệnh nhân đã tìm thấy

        self.load_dich_vu()
        self.cap_nhat_ma()

        # Nút tìm BN theo mã BN
        self.ui.btn_tim_bn.clicked.connect(self.tim_benh_nhan)
        self.ui.txt_sdt.returnPressed.connect(self.tim_benh_nhan)

        # Nút chọn gói khám
        self.ui.btn_goi_bs.clicked.connect(lambda: self.chon_goi("Bác sĩ"))
        self.ui.btn_goi_ths.clicked.connect(lambda: self.chon_goi("Thạc sĩ"))
        self.ui.btn_goi_ts.clicked.connect(lambda: self.chon_goi("Tiến sĩ"))

        self.ui.cmb_dichvu.currentIndexChanged.connect(self.tinh_gia)
        self.ui.btn_datlich.clicked.connect(self.luu)
        self.ui.btn_huy.clicked.connect(self.close)

        # Mặc định chọn Bác sĩ
        self.chon_goi("Bác sĩ")

    # ── TÌM BỆNH NHÂN THEO MÃ BN ────────────────────────────
    def tim_benh_nhan(self):
        ma_bn = self.ui.txt_sdt.text().strip()
        if not ma_bn:
            QMessageBox.warning(self, "Lỗi", "Nhập mã bệnh nhân!")
            return
        try:
            conn = ket_noi()
            cur = conn.cursor()
            cur.execute("""
                SELECT bn.id,
                       bn.ho_ten,
                       bn.ngay_sinh,
                       bn.dia_chi,
                       bn.sdt,
                       COUNT(lk.id) as so_lan_kham
                FROM benh_nhan bn
                         LEFT JOIN lich_kham lk ON bn.id = lk.benh_nhan_id
                WHERE bn.ma_bn = %s
                GROUP BY bn.id, bn.ho_ten, bn.ngay_sinh, bn.dia_chi, bn.sdt
            """, (ma_bn,))
            row = cur.fetchone()
            conn.close()

            if row:
                self._bn_id_hien_tai = row[0]
                self.ui.txt_hoten.setText(row[1])
                if row[2]:
                    self.ui.date_ngaysinh.setDate(
                        QDate.fromString(str(row[2]), "yyyy-MM-dd"))
                self.ui.txt_diachi.setText(row[3] or "")
                self.ui.txt_sdt_bn.setText(row[4] or "")  # ✅ THÊM: điền SĐT
                so_lan = row[5]
                self.ui.lbl_trang_thai_bn.setText(
                    f"Đã khám {so_lan} lần trước — thông tin tự động điền")
                self.ui.lbl_trang_thai_bn.setStyleSheet(
                    "font-size:11px;color:#185FA5;"
                    "font-weight:bold;font-style:normal;")
                for w in [self.ui.txt_hoten, self.ui.txt_diachi, self.ui.txt_sdt_bn]:  # ✅ THÊM txt_sdt_bn
                    w.setReadOnly(True)
                    w.setStyleSheet(
                        "border:1px solid #e0e0e0;border-radius:4px;"
                        "padding:4px 8px;font-size:12px;"
                        "background:#f0f8ff;color:#333;")
            else:
                self._bn_id_hien_tai = None
                self.ui.txt_hoten.clear()
                self.ui.txt_diachi.clear()
                self.ui.txt_sdt_bn.clear()  # ✅ THÊM: clear SĐT
                self.ui.lbl_trang_thai_bn.setText(
                    "Bệnh nhân mới — vui lòng nhập thông tin")
                self.ui.lbl_trang_thai_bn.setStyleSheet(
                    "font-size:11px;color:#0A3622;"
                    "font-weight:bold;font-style:normal;")
                INP = ("border:1px solid #ccc;border-radius:4px;"
                       "padding:4px 8px;font-size:12px;")
                for w in [self.ui.txt_hoten, self.ui.txt_diachi, self.ui.txt_sdt_bn]:  # ✅ THÊM txt_sdt_bn
                    w.setReadOnly(False)
                    w.setStyleSheet(INP)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    # ── LOAD DỊCH VỤ ────────────────────────────────────────
    def load_dich_vu(self):
        self.ui.cmb_dichvu.clear()
        try:
            conn = ket_noi()
            cur = conn.cursor()
            cur.execute("SELECT id,ten,gia_bs,gia_ths,gia_ts FROM dich_vu")
            self._dv_data = cur.fetchall()
            conn.close()
            for row in self._dv_data:
                self.ui.cmb_dichvu.addItem(row[1])
            self.tinh_gia()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi load dịch vụ:\n{e}")

    # ── TÍNH GIÁ ────────────────────────────────────────────
    def tinh_gia(self):
        idx = self.ui.cmb_dichvu.currentIndex()
        if idx < 0 or idx >= len(self._dv_data):
            return
        _, _, g_bs, g_ths, g_ts = self._dv_data[idx]
        gia_map = {"Bác sĩ": g_bs, "Thạc sĩ": g_ths, "Tiến sĩ": g_ts}
        self.gia_hien_tai = gia_map[self.goi_hien_tai]
        labels = ["Bác sĩ", "Thạc sĩ", "Tiến sĩ"]
        gias = [g_bs, g_ths, g_ts]
        for b, lbl, g in zip(self.ui._goi_btns, labels, gias):
            b.setText(f"{lbl}\n{g:,}đ")
        self.ui.lbl_gia.setText(f"Phí khám          {self.gia_hien_tai:,} VND")

    # ── CHỌN GÓI KHÁM ──────────────────────────────────────
    def chon_goi(self, goi):
        self.goi_hien_tai = goi
        m = {"Bác sĩ": self.ui.btn_goi_bs,
             "Thạc sĩ": self.ui.btn_goi_ths,
             "Tiến sĩ": self.ui.btn_goi_ts}
        for g, b in m.items():
            b.setStyleSheet(
                self.ui._BTN_ACT if g == goi else self.ui._BTN_INACT)
        self.tinh_gia()

    # ── TẠO MÃ LỊCH ────────────────────────────────────────
    def cap_nhat_ma(self):
        try:
            conn = ket_noi()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM lich_kham")
            n = cur.fetchone()[0]
            conn.close()
            self.ui.lbl_ma.setText(f"LK{n + 1:03d}")
        except:
            self.ui.lbl_ma.setText("LK001")

    # ── LƯU LỊCH ───────────────────────────────────────────
    def luu(self):
        ma_bn = self.ui.txt_sdt.text().strip()
        hoten = self.ui.txt_hoten.text().strip()
        if not ma_bn:
            QMessageBox.warning(self, "Lỗi", "Chưa nhập mã bệnh nhân!")
            return
        if not hoten:
            QMessageBox.warning(self, "Lỗi", "Chưa nhập họ tên!")
            return
        if self.ui.date_ngaykham.date() < QDate.currentDate():
            QMessageBox.warning(self, "Lỗi", "Ngày khám không được ở quá khứ!")
            return
        idx = self.ui.cmb_dichvu.currentIndex()
        if idx < 0 or not self._dv_data:
            QMessageBox.warning(self, "Lỗi", "Chưa chọn dịch vụ!")
            return
        id_dv = self._dv_data[idx][0]

        try:
            conn = ket_noi()
            cur = conn.cursor()

            # Nếu BN mới → tạo mới trong bảng benh_nhan
            if self._bn_id_hien_tai is None:
                cur.execute("SELECT COUNT(*) FROM benh_nhan")
                n_bn = cur.fetchone()[0]
                ma_bn_new = f"BN{n_bn + 1:03d}"

                cur.execute("""
                    INSERT INTO benh_nhan
                        (ma_bn, ho_ten, sdt, ngay_sinh, dia_chi)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    ma_bn_new, hoten,
                    self.ui.txt_sdt_bn.text().strip() or None,  # ✅ THÊM: lưu SĐT
                    self.ui.date_ngaysinh.date().toString("yyyy-MM-dd"),
                    self.ui.txt_diachi.text().strip()
                ))
                conn.commit()
                self._bn_id_hien_tai = cur.lastrowid

            # Lưu lịch khám
            cur.execute("""
                INSERT INTO lich_kham
                (ma_lich, benh_nhan_id, dich_vu_id,
                 goi_kham, phi_kham, ngay_kham, gio_kham, trang_thai)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.ui.lbl_ma.text(),
                self._bn_id_hien_tai,
                id_dv,
                self.goi_hien_tai,
                self.gia_hien_tai,
                self.ui.date_ngaykham.date().toString("yyyy-MM-dd"),
                self.ui.time_giokham.time().toString("HH:mm:ss"),
                "Chờ khám"
            ))
            conn.commit()
            conn.close()

            QMessageBox.information(
                self, "Thành công",
                f"Đã đặt lịch!\nMã: {self.ui.lbl_ma.text()}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi lưu:\n{e}")