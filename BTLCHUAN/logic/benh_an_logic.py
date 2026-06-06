"""
logic/benh_an_logic.py
──────────────────────
CRUD bệnh án.
"""
from database import db


class BenhAnLogic:

    @staticmethod
    def get_all(keyword: str = "") -> list[dict]:
        sql = """
            SELECT ba.ma_ba, bn.ho_ten AS ten_bn, bs.ho_ten AS ten_bs,
                   lk.ngay_kham, ba.chuan_doan, ba.trieu_chung,
                   ba.phuong_phap_dieu_tri, ba.ket_qua, ba.ma_lich
            FROM BenhAn ba
            JOIN LichKham lk ON ba.ma_lich = lk.ma_lich
            JOIN BenhNhan bn ON lk.ma_bn   = bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs   = bs.ma_bs
            WHERE 1=1
        """
        params = []
        if keyword:
            sql += " AND bn.ho_ten LIKE %s"
            params.append(f"%{keyword}%")
        sql += " ORDER BY ba.ngay_tao DESC"
        return db.execute_query(sql, params or None, fetch=True) or []

    @staticmethod
    def get_lich_chua_co_benh_an() -> list[dict]:
        """Lịch khám đã xác nhận/đang khám nhưng chưa tạo bệnh án."""
        return db.execute_query("""
            SELECT lk.ma_lich, bn.ho_ten, lk.ngay_kham
            FROM LichKham lk
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            WHERE lk.trang_thai IN ('da_xac_nhan','dang_kham')
              AND lk.ma_lich NOT IN (SELECT ma_lich FROM BenhAn)
            ORDER BY lk.ngay_kham DESC
        """, fetch=True) or []

    @staticmethod
    def insert(ma_lich, trieu_chung, chuan_doan,
               phuong_phap, ket_qua) -> bool:
        result = db.execute_query(
            "INSERT INTO BenhAn "
            "(ma_lich,trieu_chung,chuan_doan,phuong_phap_dieu_tri,ket_qua) "
            "VALUES (%s,%s,%s,%s,%s)",
            (ma_lich, trieu_chung, chuan_doan, phuong_phap, ket_qua),
        )
        if result:
            db.execute_query(
                "UPDATE LichKham SET trang_thai='hoan_thanh' WHERE ma_lich=%s",
                (ma_lich,),
            )
        return bool(result)

    @staticmethod
    def update(ma_ba, trieu_chung, chuan_doan,
               phuong_phap, ket_qua) -> bool:
        result = db.execute_query(
            "UPDATE BenhAn SET trieu_chung=%s,chuan_doan=%s,"
            "phuong_phap_dieu_tri=%s,ket_qua=%s WHERE ma_ba=%s",
            (trieu_chung, chuan_doan, phuong_phap, ket_qua, ma_ba),
        )
        return result is not None
