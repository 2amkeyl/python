"""
logic/kham_benh_logic.py
────────────────────────
Ghi kết quả khám, kê đơn thuốc.
"""
from database import db


class KhamBenhLogic:

    @staticmethod
    def get_benh_an_by_lich(ma_lich) -> dict | None:
        rows = db.execute_query(
            "SELECT * FROM BenhAn WHERE ma_lich=%s", (ma_lich,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_don_thuoc(ma_ba) -> dict | None:
        rows = db.execute_query(
            "SELECT * FROM DonThuoc WHERE ma_ba=%s", (ma_ba,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_chi_tiet_don_thuoc(ma_don) -> list[dict]:
        return db.execute_query("""
            SELECT ct.*, t.ten_thuoc, t.don_vi, t.gia
            FROM ChiTietDonThuoc ct
            JOIN Thuoc t ON ct.ma_thuoc=t.ma_thuoc
            WHERE ct.ma_don=%s
        """, (ma_don,), fetch=True) or []

    @staticmethod
    def get_thuoc_available() -> list[dict]:
        return db.execute_query(
            "SELECT * FROM Thuoc WHERE so_luong_ton>0 ORDER BY ten_thuoc",
            fetch=True,
        ) or []

    @staticmethod
    def save_benh_an(ma_ba, ma_lich, trieu_chung, chuan_doan,
                     dieu_tri, ket_qua) -> int:
        """Tạo mới hoặc cập nhật bệnh án. Trả về ma_ba."""
        if ma_ba:
            db.execute_query(
                "UPDATE BenhAn SET trieu_chung=%s,chuan_doan=%s,"
                "phuong_phap_dieu_tri=%s,ket_qua=%s WHERE ma_ba=%s",
                (trieu_chung, chuan_doan, dieu_tri, ket_qua, ma_ba),
            )
            return ma_ba
        else:
            new_id = db.execute_query(
                "INSERT INTO BenhAn(ma_lich,trieu_chung,chuan_doan,"
                "phuong_phap_dieu_tri,ket_qua) VALUES(%s,%s,%s,%s,%s)",
                (ma_lich, trieu_chung, chuan_doan, dieu_tri, ket_qua),
            )
            db.execute_query(
                "UPDATE LichKham SET trang_thai='hoan_thanh' WHERE ma_lich=%s",
                (ma_lich,),
            )
            return new_id

    @staticmethod
    def save_don_thuoc(ma_don, ma_ba, ghi_chu, items: list[dict]) -> int:
        """
        Lưu đơn thuốc + chi tiết. Trả về ma_don.
        items: [{'ma_thuoc', 'so_luong', 'lieu_dung'}]
        """
        if ma_don:
            db.execute_query(
                "UPDATE DonThuoc SET ghi_chu=%s WHERE ma_don=%s",
                (ghi_chu, ma_don),
            )
            db.execute_query(
                "DELETE FROM ChiTietDonThuoc WHERE ma_don=%s", (ma_don,))
        else:
            ma_don = db.execute_query(
                "INSERT INTO DonThuoc(ma_ba,ghi_chu) VALUES(%s,%s)",
                (ma_ba, ghi_chu),
            )

        for it in items:
            db.execute_query(
                "INSERT INTO ChiTietDonThuoc(ma_don,ma_thuoc,so_luong,lieu_dung) "
                "VALUES(%s,%s,%s,%s)",
                (ma_don, it["ma_thuoc"], it["so_luong"], it["lieu_dung"]),
            )
            # Trừ tồn kho
            db.execute_query(
                "UPDATE Thuoc SET so_luong_ton=GREATEST(0,so_luong_ton-%s) "
                "WHERE ma_thuoc=%s",
                (it["so_luong"], it["ma_thuoc"]),
            )
        return ma_don

    @staticmethod
    def get_lich_kham_list(keyword: str = "", today_only: bool = True,
                           trang_thai: str | None = None) -> list[dict]:
        from datetime import date
        sql = """
            SELECT lk.ma_lich, bn.ho_ten ten_bn, bs.ho_ten ten_bs,
                   lk.ngay_kham, lk.gio_kham, lk.ly_do_kham, lk.trang_thai,
                   lk.ma_bn, lk.ma_bs
            FROM LichKham lk
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs=bs.ma_bs
            WHERE 1=1
        """
        params = []
        if today_only:
            sql += " AND lk.ngay_kham=%s"
            params.append(date.today().strftime("%Y-%m-%d"))
        if keyword:
            sql += " AND (bn.ho_ten LIKE %s OR bs.ho_ten LIKE %s)"
            params += [f"%{keyword}%", f"%{keyword}%"]
        if trang_thai:
            sql += " AND lk.trang_thai=%s"
            params.append(trang_thai)
        sql += " ORDER BY lk.ngay_kham DESC, lk.gio_kham"
        return db.execute_query(sql, params or None, fetch=True) or []
