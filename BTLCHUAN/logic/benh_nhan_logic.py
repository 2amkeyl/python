"""
logic/benh_nhan_logic.py
────────────────────────
CRUD bệnh nhân, không phụ thuộc UI.
"""
from database import db


class BenhNhanLogic:

    @staticmethod
    def get_all(keyword: str = "", gioi_tinh: str = "Tất cả") -> list[dict]:
        sql = """
            SELECT bn.ma_bn, bn.ho_ten, bn.ngay_sinh, bn.gioi_tinh,
                   bn.so_dien_thoai, bn.email, bn.so_bao_hiem, bn.dia_chi,
                   COUNT(lk.ma_lich) AS so_lan_kham
            FROM BenhNhan bn
            LEFT JOIN LichKham lk ON bn.ma_bn = lk.ma_bn
            WHERE (bn.ho_ten LIKE %s OR bn.so_dien_thoai LIKE %s OR bn.email LIKE %s)
        """
        params = [f"%{keyword}%"] * 3
        if gioi_tinh != "Tất cả":
            sql += " AND bn.gioi_tinh=%s"
            params.append(gioi_tinh)
        sql += (" GROUP BY bn.ma_bn, bn.ho_ten, bn.ngay_sinh, bn.gioi_tinh,"
                " bn.so_dien_thoai, bn.email, bn.so_bao_hiem, bn.dia_chi"
                " ORDER BY bn.ho_ten")
        return db.execute_query(sql, params, fetch=True) or []

    @staticmethod
    def get_by_id(ma_bn) -> dict | None:
        rows = db.execute_query(
            "SELECT * FROM BenhNhan WHERE ma_bn=%s", (ma_bn,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def search_by_ma(keyword: str) -> list[dict]:
        return db.execute_query(
            "SELECT * FROM BenhNhan WHERE ma_bn=%s "
            "OR CAST(ma_bn AS CHAR) LIKE %s ORDER BY ma_bn",
            (keyword, f"{keyword}%"), fetch=True,
        ) or []

    @staticmethod
    def get_lich_su(ma_bn, limit: int = 3) -> list[dict]:
        return db.execute_query("""
            SELECT lk.ngay_kham, lk.gio_kham, lk.ly_do_kham,
                   bs.ho_ten AS ten_bs, lk.trang_thai
            FROM LichKham lk
            JOIN BacSi bs ON lk.ma_bs = bs.ma_bs
            WHERE lk.ma_bn = %s
            ORDER BY lk.ngay_kham DESC, lk.gio_kham DESC
            LIMIT %s
        """, (ma_bn, limit), fetch=True) or []

    @staticmethod
    def insert(ma_bn, ho_ten, ngay_sinh, gioi_tinh,
               sdt, email, bao_hiem, dia_chi) -> bool:
        result = db.execute_query(
            "INSERT INTO BenhNhan "
            "(ma_bn,ho_ten,ngay_sinh,gioi_tinh,so_dien_thoai,email,so_bao_hiem,dia_chi) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (ma_bn, ho_ten, ngay_sinh, gioi_tinh, sdt, email, bao_hiem, dia_chi),
        )
        return result is not None

    @staticmethod
    def update(ma_bn, ho_ten, ngay_sinh, gioi_tinh,
               sdt, email, bao_hiem, dia_chi) -> bool:
        result = db.execute_query(
            "UPDATE BenhNhan SET ho_ten=%s,ngay_sinh=%s,gioi_tinh=%s,"
            "so_dien_thoai=%s,email=%s,so_bao_hiem=%s,dia_chi=%s WHERE ma_bn=%s",
            (ho_ten, ngay_sinh, gioi_tinh, sdt, email, bao_hiem, dia_chi, ma_bn),
        )
        return result is not None

    @staticmethod
    def delete(ma_bn) -> bool:
        result = db.execute_query(
            "DELETE FROM BenhNhan WHERE ma_bn=%s", (ma_bn,))
        return result is not None

    @staticmethod
    def ma_exists(ma_bn) -> bool:
        rows = db.execute_query(
            "SELECT ma_bn FROM BenhNhan WHERE ma_bn=%s", (ma_bn,), fetch=True)
        return bool(rows)
