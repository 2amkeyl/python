"""
logic/dich_vu_logic.py
"""
from database import db


class DichVuLogic:

    @staticmethod
    def get_all(keyword: str = "") -> list[dict]:
        return db.execute_query(
            "SELECT dv.ma_dv, dv.ten_dv, k.ten_khoa, dv.don_gia, dv.don_vi, "
            "CASE dv.trang_thai WHEN 1 THEN 'Hoạt động' ELSE 'Ngừng' END AS tt "
            "FROM DichVu dv LEFT JOIN Khoa k ON dv.ma_khoa=k.ma_khoa "
            "WHERE dv.ten_dv LIKE %s ORDER BY dv.ma_dv",
            (f"%{keyword}%",), fetch=True,
        ) or []

    @staticmethod
    def get_by_id(ma_dv) -> dict | None:
        rows = db.execute_query(
            "SELECT * FROM DichVu WHERE ma_dv=%s", (ma_dv,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_active() -> list[dict]:
        return db.execute_query(
            "SELECT ma_dv AS ma, ten_dv AS ten, don_gia "
            "FROM DichVu WHERE trang_thai=1 ORDER BY ten_dv",
            fetch=True,
        ) or []

    @staticmethod
    def get_khoa_list() -> list[dict]:
        return db.execute_query(
            "SELECT ma_khoa, ten_khoa FROM Khoa WHERE trang_thai=1",
            fetch=True,
        ) or []

    @staticmethod
    def insert(ma_khoa, ten, mo_ta, don_gia, don_vi, trang_thai) -> bool:
        r = db.execute_query(
            "INSERT INTO DichVu (ma_khoa,ten_dv,mo_ta,don_gia,don_vi,trang_thai) "
            "VALUES(%s,%s,%s,%s,%s,%s)",
            (ma_khoa, ten, mo_ta, don_gia, don_vi, trang_thai),
        )
        return bool(r)

    @staticmethod
    def update(ma_dv, ma_khoa, ten, mo_ta, don_gia, don_vi, trang_thai) -> bool:
        r = db.execute_query(
            "UPDATE DichVu SET ma_khoa=%s,ten_dv=%s,mo_ta=%s,"
            "don_gia=%s,don_vi=%s,trang_thai=%s WHERE ma_dv=%s",
            (ma_khoa, ten, mo_ta, don_gia, don_vi, trang_thai, ma_dv),
        )
        return r is not None

    @staticmethod
    def deactivate(ma_dv) -> bool:
        r = db.execute_query(
            "UPDATE DichVu SET trang_thai=0 WHERE ma_dv=%s", (ma_dv,))
        return r is not None
