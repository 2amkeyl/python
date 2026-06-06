"""
logic/thuoc_logic.py
"""
from database import db


class ThuocLogic:

    @staticmethod
    def get_all(keyword: str = "") -> list[dict]:
        sql = "SELECT * FROM Thuoc WHERE 1=1"
        params = []
        if keyword:
            sql += " AND ten_thuoc LIKE %s"
            params.append(f"%{keyword}%")
        sql += " ORDER BY ten_thuoc"
        return db.execute_query(sql, params or None, fetch=True) or []

    @staticmethod
    def get_available() -> list[dict]:
        return db.execute_query(
            "SELECT ma_thuoc AS ma, ten_thuoc AS ten, gia AS don_gia "
            "FROM Thuoc WHERE so_luong_ton>0 ORDER BY ten_thuoc",
            fetch=True,
        ) or []

    @staticmethod
    def insert(ten, don_vi, mo_ta, gia, so_luong) -> bool:
        r = db.execute_query(
            "INSERT INTO Thuoc (ten_thuoc,don_vi,mo_ta,gia,so_luong_ton) "
            "VALUES (%s,%s,%s,%s,%s)",
            (ten, don_vi, mo_ta, gia, so_luong),
        )
        return bool(r)

    @staticmethod
    def update(ma_thuoc, ten, don_vi, mo_ta, gia, so_luong) -> bool:
        r = db.execute_query(
            "UPDATE Thuoc SET ten_thuoc=%s,don_vi=%s,mo_ta=%s,"
            "gia=%s,so_luong_ton=%s WHERE ma_thuoc=%s",
            (ten, don_vi, mo_ta, gia, so_luong, ma_thuoc),
        )
        return r is not None

    @staticmethod
    def delete(ma_thuoc) -> bool:
        r = db.execute_query(
            "DELETE FROM Thuoc WHERE ma_thuoc=%s", (ma_thuoc,))
        return r is not None
