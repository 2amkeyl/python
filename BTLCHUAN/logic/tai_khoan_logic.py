"""
logic/tai_khoan_logic.py
"""
from database import db


class TaiKhoanLogic:

    @staticmethod
    def get_all(keyword: str = "") -> list[dict]:
        sql = "SELECT * FROM TaiKhoan WHERE 1=1"
        params = []
        if keyword:
            sql += " AND ten_dang_nhap LIKE %s"
            params.append(f"%{keyword}%")
        sql += " ORDER BY ma_tk"
        return db.execute_query(sql, params or None, fetch=True) or []

    @staticmethod
    def insert(ten_dn, mat_khau, vai_tro, trang_thai) -> bool:
        r = db.execute_query(
            "INSERT INTO TaiKhoan (ten_dang_nhap,mat_khau,vai_tro,trang_thai) "
            "VALUES (%s,%s,%s,%s)",
            (ten_dn, mat_khau, vai_tro, trang_thai),
        )
        return bool(r)

    @staticmethod
    def update(ma_tk, ten_dn, vai_tro, trang_thai,
               mat_khau_moi: str = "") -> bool:
        if mat_khau_moi:
            r = db.execute_query(
                "UPDATE TaiKhoan SET ten_dang_nhap=%s,mat_khau=%s,"
                "vai_tro=%s,trang_thai=%s WHERE ma_tk=%s",
                (ten_dn, mat_khau_moi, vai_tro, trang_thai, ma_tk),
            )
        else:
            r = db.execute_query(
                "UPDATE TaiKhoan SET ten_dang_nhap=%s,vai_tro=%s,"
                "trang_thai=%s WHERE ma_tk=%s",
                (ten_dn, vai_tro, trang_thai, ma_tk),
            )
        return r is not None

    @staticmethod
    def delete(ma_tk) -> bool:
        r = db.execute_query(
            "DELETE FROM TaiKhoan WHERE ma_tk=%s", (ma_tk,))
        return r is not None
