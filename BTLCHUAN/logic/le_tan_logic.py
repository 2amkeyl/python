"""
logic/le_tan_logic.py
"""
from database import db


class LeTanLogic:

    @staticmethod
    def get_all(keyword: str = "") -> list[dict]:
        return db.execute_query("""
            SELECT lt.ma_lt, lt.ho_ten, tk.ten_dang_nhap,
                   lt.so_dien_thoai, lt.email, lt.ca_lam_viec,
                   CASE lt.trang_thai WHEN 1 THEN 'Hoạt động' ELSE 'Ngừng' END AS trang_thai
            FROM LeTan lt
            JOIN TaiKhoan tk ON lt.ma_tk=tk.ma_tk
            WHERE lt.ho_ten LIKE %s OR lt.so_dien_thoai LIKE %s
            ORDER BY lt.ma_lt
        """, (f"%{keyword}%", f"%{keyword}%"), fetch=True) or []

    @staticmethod
    def get_full(ma_lt) -> dict | None:
        rows = db.execute_query(
            "SELECT lt.*, tk.ten_dang_nhap, tk.mat_khau FROM LeTan lt "
            "JOIN TaiKhoan tk ON lt.ma_tk=tk.ma_tk WHERE lt.ma_lt=%s",
            (ma_lt,), fetch=True,
        )
        return rows[0] if rows else None

    @staticmethod
    def insert(ten_dn, mat_khau, ho_ten, sdt, email,
               ca_lam_viec, trang_thai) -> tuple[bool, str]:
        ma_tk = db.execute_query(
            "INSERT INTO TaiKhoan (ten_dang_nhap,mat_khau,vai_tro) "
            "VALUES (%s,%s,'le_tan')",
            (ten_dn, mat_khau),
        )
        if not ma_tk:
            return False, "Tên đăng nhập đã tồn tại!"
        db.execute_query(
            "INSERT INTO LeTan (ma_tk,ho_ten,so_dien_thoai,email,ca_lam_viec,trang_thai) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (ma_tk, ho_ten, sdt, email, ca_lam_viec, trang_thai),
        )
        return True, ""

    @staticmethod
    def update(ma_lt, ma_tk, ho_ten, sdt, email,
               ca_lam_viec, trang_thai, mat_khau_moi: str = "") -> bool:
        db.execute_query(
            "UPDATE LeTan SET ho_ten=%s,so_dien_thoai=%s,email=%s,"
            "ca_lam_viec=%s,trang_thai=%s WHERE ma_lt=%s",
            (ho_ten, sdt, email, ca_lam_viec, trang_thai, ma_lt),
        )
        if mat_khau_moi:
            db.execute_query(
                "UPDATE TaiKhoan SET mat_khau=%s WHERE ma_tk=%s",
                (mat_khau_moi, ma_tk),
            )
        return True

    @staticmethod
    def delete(ma_lt) -> bool:
        r = db.execute_query("DELETE FROM LeTan WHERE ma_lt=%s", (ma_lt,))
        return r is not None
