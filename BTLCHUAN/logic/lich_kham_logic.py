"""
logic/lich_kham_logic.py
────────────────────────
CRUD lịch khám + dịch vụ đăng ký kèm theo.
"""
from database import db


class LichKhamLogic:

    @staticmethod
    def get_all(keyword: str = "", trang_thai: str | None = None) -> list[dict]:
        sql = """
            SELECT lk.ma_lich, bn.ho_ten AS ten_bn, bs.ho_ten AS ten_bs,
                   lk.ngay_kham, lk.gio_kham, lk.ly_do_kham, lk.trang_thai,
                   lk.ghi_chu, lk.ma_bn, lk.ma_bs
            FROM LichKham lk
            JOIN BenhNhan bn ON lk.ma_bn = bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs = bs.ma_bs
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += (" AND (bn.ho_ten LIKE %s OR bs.ho_ten LIKE %s "
                    "OR CAST(lk.ma_bn AS CHAR) LIKE %s)")
            params += [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
        if trang_thai:
            sql += " AND lk.trang_thai=%s"
            params.append(trang_thai)
        sql += " ORDER BY lk.ngay_kham DESC, lk.gio_kham"
        return db.execute_query(sql, params or None, fetch=True) or []

    @staticmethod
    def get_today(date_str: str) -> list[dict]:
        return db.execute_query("""
            SELECT lk.gio_kham, bn.ho_ten AS benh_nhan,
                   bs.ho_ten AS bac_si, lk.ly_do_kham, lk.trang_thai
            FROM LichKham lk
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs=bs.ma_bs
            WHERE lk.ngay_kham=%s
            ORDER BY lk.gio_kham
        """, (date_str,), fetch=True) or []

    @staticmethod
    def insert(ma_bn, ma_bs, ngay, gio, ly_do, trang_thai, ghi_chu) -> int | None:
        return db.execute_query(
            "INSERT INTO LichKham "
            "(ma_bn,ma_bs,ngay_kham,gio_kham,ly_do_kham,trang_thai,ghi_chu) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (ma_bn, ma_bs, ngay, gio, ly_do, trang_thai, ghi_chu),
        )

    @staticmethod
    def update(ma_lich, ma_bn, ma_bs, ngay, gio,
               ly_do, trang_thai, ghi_chu) -> bool:
        result = db.execute_query(
            "UPDATE LichKham SET ma_bn=%s,ma_bs=%s,ngay_kham=%s,gio_kham=%s,"
            "ly_do_kham=%s,trang_thai=%s,ghi_chu=%s WHERE ma_lich=%s",
            (ma_bn, ma_bs, ngay, gio, ly_do, trang_thai, ghi_chu, ma_lich),
        )
        return result is not None

    @staticmethod
    def update_trang_thai(ma_lich, trang_thai) -> bool:
        result = db.execute_query(
            "UPDATE LichKham SET trang_thai=%s WHERE ma_lich=%s",
            (trang_thai, ma_lich),
        )
        return result is not None

    @staticmethod
    def delete(ma_lich) -> bool:
        result = db.execute_query(
            "DELETE FROM LichKham WHERE ma_lich=%s", (ma_lich,))
        return result is not None

    # ── Dịch vụ kèm theo lịch khám ────────────────────────────────────
    @staticmethod
    def ensure_lkdv_table():
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS LichKhamDichVu (
                ma_lkdv  INT AUTO_INCREMENT PRIMARY KEY,
                ma_lich  INT NOT NULL,
                ma_dv    INT NOT NULL,
                so_luong INT NOT NULL DEFAULT 1,
                don_gia  DECIMAL(15,2) NOT NULL DEFAULT 0,
                FOREIGN KEY (ma_lich) REFERENCES LichKham(ma_lich) ON DELETE CASCADE,
                FOREIGN KEY (ma_dv)   REFERENCES DichVu(ma_dv)
            )
        """)

    @staticmethod
    def get_dich_vu_by_lich(ma_lich) -> list[dict]:
        return db.execute_query(
            "SELECT ma_dv, so_luong FROM LichKhamDichVu WHERE ma_lich=%s",
            (ma_lich,), fetch=True,
        ) or []

    @staticmethod
    def save_dich_vu(ma_lich, dv_list: list[dict]):
        """dv_list: [{'ma_dv':..., 'so_luong':..., 'don_gia':...}]"""
        LichKhamLogic.ensure_lkdv_table()
        db.execute_query(
            "DELETE FROM LichKhamDichVu WHERE ma_lich=%s", (ma_lich,))
        for dv in dv_list:
            db.execute_query(
                "INSERT INTO LichKhamDichVu (ma_lich,ma_dv,so_luong,don_gia) "
                "VALUES (%s,%s,%s,%s)",
                (ma_lich, dv["ma_dv"], dv["so_luong"], dv["don_gia"]),
            )
