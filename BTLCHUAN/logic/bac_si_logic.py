"""
logic/bac_si_logic.py
─────────────────────
CRUD bác sĩ + tài khoản liên kết.
"""
from database import db


class BacSiLogic:

    @staticmethod
    def get_all(keyword: str = "", ma_khoa=None) -> list[dict]:
        sql = """
            SELECT bs.ma_bs, bs.ho_ten, k.ten_khoa, bs.chuyen_khoa,
                   bs.so_dien_thoai, bs.hoc_ham, bs.trang_thai,
                   bs.ma_tk, tk.ten_dang_nhap,
                   bs.ma_khoa, bs.email, bs.lich_lam_viec
            FROM BacSi bs
            LEFT JOIN Khoa     k  ON bs.ma_khoa = k.ma_khoa
            LEFT JOIN TaiKhoan tk ON bs.ma_tk   = tk.ma_tk
            WHERE (bs.ho_ten LIKE %s OR bs.chuyen_khoa LIKE %s)
        """
        params = [f"%{keyword}%", f"%{keyword}%"]
        if ma_khoa:
            sql += " AND bs.ma_khoa=%s"
            params.append(ma_khoa)
        sql += " ORDER BY bs.ho_ten"
        return db.execute_query(sql, params, fetch=True) or []

    @staticmethod
    def get_active() -> list[dict]:
        """Danh sách bác sĩ đang làm việc (dùng cho combobox)."""
        return db.execute_query(
            "SELECT ma_bs, ho_ten, chuyen_khoa FROM BacSi "
            "WHERE trang_thai=1 ORDER BY ho_ten",
            fetch=True,
        ) or []

    @staticmethod
    def get_khoa_list() -> list[dict]:
        return db.execute_query(
            "SELECT ma_khoa, ten_khoa FROM Khoa WHERE trang_thai=1",
            fetch=True,
        ) or []

    @staticmethod
    def insert(ten_dn, mat_khau, ho_ten, ma_khoa, chuyen_khoa,
               sdt, email, hoc_ham, lich, trang_thai) -> tuple[bool, str]:
        """Tạo TaiKhoan rồi tạo BacSi. Trả về (ok, msg)."""
        ma_tk = db.execute_query(
            "INSERT INTO TaiKhoan (ten_dang_nhap,mat_khau,vai_tro) "
            "VALUES (%s,%s,'bac_si')",
            (ten_dn, mat_khau),
        )
        if not ma_tk:
            return False, f"Tên đăng nhập '{ten_dn}' đã tồn tại!"
        db.execute_query(
            "INSERT INTO BacSi "
            "(ma_tk,ho_ten,ma_khoa,chuyen_khoa,so_dien_thoai,email,"
            "hoc_ham,lich_lam_viec,trang_thai) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (ma_tk, ho_ten, ma_khoa, chuyen_khoa, sdt, email, hoc_ham, lich, trang_thai),
        )
        return True, f"Đã thêm bác sĩ {ho_ten}!\nTài khoản: {ten_dn}"

    @staticmethod
    def update(ma_bs, ho_ten, ma_khoa, chuyen_khoa,
               sdt, email, hoc_ham, lich, trang_thai) -> bool:
        result = db.execute_query(
            "UPDATE BacSi SET ho_ten=%s,ma_khoa=%s,chuyen_khoa=%s,"
            "so_dien_thoai=%s,email=%s,hoc_ham=%s,lich_lam_viec=%s,trang_thai=%s "
            "WHERE ma_bs=%s",
            (ho_ten, ma_khoa, chuyen_khoa, sdt, email, hoc_ham, lich, trang_thai, ma_bs),
        )
        return result is not None

    @staticmethod
    def update_password(ma_tk, mat_khau_moi) -> bool:
        result = db.execute_query(
            "UPDATE TaiKhoan SET mat_khau=%s WHERE ma_tk=%s",
            (mat_khau_moi, ma_tk),
        )
        return result is not None

    @staticmethod
    def create_account_for_bs(ma_bs, ten_dn, mat_khau) -> tuple[bool, str]:
        """Tạo TaiKhoan cho bác sĩ cũ chưa có tài khoản."""
        ma_tk = db.execute_query(
            "INSERT INTO TaiKhoan (ten_dang_nhap,mat_khau,vai_tro) "
            "VALUES (%s,%s,'bac_si')",
            (ten_dn, mat_khau),
        )
        if not ma_tk:
            return False, f"Tên đăng nhập '{ten_dn}' đã tồn tại!"
        db.execute_query(
            "UPDATE BacSi SET ma_tk=%s WHERE ma_bs=%s", (ma_tk, ma_bs))
        return True, ""

    @staticmethod
    def delete(ma_bs) -> bool:
        rows = db.execute_query(
            "SELECT ma_tk FROM BacSi WHERE ma_bs=%s", (ma_bs,), fetch=True)
        db.execute_query("DELETE FROM BacSi WHERE ma_bs=%s", (ma_bs,))
        if rows and rows[0]["ma_tk"]:
            db.execute_query(
                "DELETE FROM TaiKhoan WHERE ma_tk=%s", (rows[0]["ma_tk"],))
        return True
