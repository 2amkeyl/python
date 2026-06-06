"""
logic/hoa_don_logic.py
"""
from database import db


class HoaDonLogic:

    @staticmethod
    def get_all(keyword: str = "", trang_thai: str | None = None) -> list[dict]:
        sql = """
            SELECT hd.ma_hd, bn.ho_ten AS benh_nhan, bs.ho_ten AS bac_si,
                   lk.ngay_kham, hd.tong_tien, hd.giam_gia, hd.thanh_tien, hd.trang_thai
            FROM HoaDon hd
            JOIN LichKham lk ON hd.ma_lich=lk.ma_lich
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs=bs.ma_bs
            WHERE bn.ho_ten LIKE %s
        """
        params = [f"%{keyword}%"]
        if trang_thai:
            sql += " AND hd.trang_thai=%s"
            params.append(trang_thai)
        sql += " ORDER BY hd.ma_hd DESC"
        return db.execute_query(sql, params, fetch=True) or []

    @staticmethod
    def get_detail(ma_hd) -> dict | None:
        rows = db.execute_query("""
            SELECT hd.*, bn.ho_ten AS benh_nhan, bs.ho_ten AS bac_si,
                   lk.ngay_kham, lt.ho_ten AS le_tan
            FROM HoaDon hd
            JOIN LichKham lk ON hd.ma_lich=lk.ma_lich
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs=bs.ma_bs
            LEFT JOIN LeTan lt ON hd.ma_lt=lt.ma_lt
            WHERE hd.ma_hd=%s
        """, (ma_hd,), fetch=True)
        return rows[0] if rows else None

    @staticmethod
    def get_chi_tiet(ma_hd) -> list[dict]:
        return db.execute_query(
            "SELECT loai_ct,ten_hang,don_gia,so_luong,thanh_tien "
            "FROM ChiTietHoaDon WHERE ma_hd=%s",
            (ma_hd,), fetch=True,
        ) or []

    @staticmethod
    def get_trang_thai(ma_hd) -> str | None:
        rows = db.execute_query(
            "SELECT trang_thai FROM HoaDon WHERE ma_hd=%s",
            (ma_hd,), fetch=True,
        )
        return rows[0]["trang_thai"] if rows else None

    @staticmethod
    def get_lich_chua_hoa_don() -> list[dict]:
        return db.execute_query("""
            SELECT lk.ma_lich, bn.ho_ten AS ten_bn, bs.ho_ten AS ten_bs,
                   lk.ngay_kham, lk.gio_kham, lk.ly_do_kham, lk.trang_thai,
                   lk.ma_bn, lk.ma_bs
            FROM LichKham lk
            JOIN BenhNhan bn ON lk.ma_bn=bn.ma_bn
            JOIN BacSi    bs ON lk.ma_bs=bs.ma_bs
            WHERE lk.trang_thai IN ('da_xac_nhan','dang_kham','hoan_thanh')
              AND lk.ma_lich NOT IN (
                  SELECT ma_lich FROM HoaDon WHERE trang_thai != 'huy'
              )
            ORDER BY lk.ngay_kham DESC, lk.gio_kham
        """, fetch=True) or []

    @staticmethod
    def get_dv_tu_benh_an(ma_ba) -> list[dict]:
        return db.execute_query("""
            SELECT dv.ma_dv AS ma, dv.ten_dv AS ten, dv.don_gia
            FROM KetQuaKham kq JOIN DichVu dv ON kq.ma_dv=dv.ma_dv
            WHERE kq.ma_ba=%s
        """, (ma_ba,), fetch=True) or []

    @staticmethod
    def get_thuoc_tu_don(ma_ba) -> list[dict]:
        return db.execute_query("""
            SELECT t.ma_thuoc AS ma, t.ten_thuoc AS ten,
                   t.gia AS don_gia, ct.so_luong
            FROM DonThuoc dt
            JOIN ChiTietDonThuoc ct ON dt.ma_don=ct.ma_don
            JOIN Thuoc t            ON ct.ma_thuoc=t.ma_thuoc
            WHERE dt.ma_ba=%s
        """, (ma_ba,), fetch=True) or []

    @staticmethod
    def get_dv_tu_lich(ma_lich) -> list[dict]:
        return db.execute_query("""
            SELECT dv.ma_dv AS ma, dv.ten_dv AS ten,
                   lkdv.don_gia, lkdv.so_luong
            FROM LichKhamDichVu lkdv JOIN DichVu dv ON lkdv.ma_dv=dv.ma_dv
            WHERE lkdv.ma_lich=%s
        """, (ma_lich,), fetch=True) or []

    @staticmethod
    def get_benh_an_by_lich(ma_lich) -> dict | None:
        rows = db.execute_query(
            "SELECT ma_ba FROM BenhAn WHERE ma_lich=%s",
            (ma_lich,), fetch=True,
        )
        return rows[0] if rows else None

    @staticmethod
    def get_ma_lt(ma_tk) -> int | None:
        rows = db.execute_query(
            "SELECT ma_lt FROM LeTan WHERE ma_tk=%s", (ma_tk,), fetch=True)
        return rows[0]["ma_lt"] if rows else None

    @staticmethod
    def insert(ma_lich, ma_lt, tong_tien, giam_gia,
               phuong_thuc, items: list[dict]) -> int | None:
        """Tạo HoaDon + ChiTietHoaDon. Trả về ma_hd."""
        ma_hd = db.execute_query(
            "INSERT INTO HoaDon "
            "(ma_lich,ma_lt,tong_tien,giam_gia,phuong_thuc,trang_thai) "
            "VALUES (%s,%s,%s,%s,%s,'chua_thanh_toan')",
            (ma_lich, ma_lt, tong_tien, giam_gia, phuong_thuc),
        )
        if not ma_hd:
            return None
        for it in items:
            thanh_tien = float(it["don_gia"]) * int(it["so_luong"])
            if it["loai"] == "dich_vu":
                db.execute_query(
                    "INSERT INTO ChiTietHoaDon "
                    "(ma_hd,loai_ct,ma_dv,ten_hang,don_gia,so_luong,thanh_tien) "
                    "VALUES (%s,'dich_vu',%s,%s,%s,%s,%s)",
                    (ma_hd, it["ma"], it["ten"], it["don_gia"], it["so_luong"], thanh_tien),
                )
            else:
                db.execute_query(
                    "INSERT INTO ChiTietHoaDon "
                    "(ma_hd,loai_ct,ma_thuoc,ten_hang,don_gia,so_luong,thanh_tien) "
                    "VALUES (%s,'thuoc',%s,%s,%s,%s,%s)",
                    (ma_hd, it["ma"], it["ten"], it["don_gia"], it["so_luong"], thanh_tien),
                )
        return ma_hd

    @staticmethod
    def confirm_payment(ma_hd, ma_lt) -> bool:
        r = db.execute_query(
            "UPDATE HoaDon SET trang_thai='da_thanh_toan',ma_lt=%s WHERE ma_hd=%s",
            (ma_lt, ma_hd),
        )
        return r is not None

    @staticmethod
    def cancel(ma_hd) -> bool:
        r = db.execute_query(
            "UPDATE HoaDon SET trang_thai='huy' WHERE ma_hd=%s", (ma_hd,))
        return r is not None
