"""
logic/dashboard_logic.py
────────────────────────
Thống kê Dashboard.
Tất cả doanh thu CHỈ tính hóa đơn trang_thai = 'da_thanh_toan'.
Tên bảng/cột khớp với CSDL thực tế (xem ERD).
"""
from database import db


class DashboardLogic:

    # ── Thẻ số liệu ────────────────────────────────────────────────────
    @staticmethod
    def count_lich_hom_nay(date_str: str) -> int:
        r = db.execute_query(
            "SELECT COUNT(*) AS c FROM lichkham WHERE ngay_kham = %s",
            (date_str,), fetch=True,
        )
        return int(r[0]["c"]) if r else 0

    @staticmethod
    def count_benh_nhan() -> int:
        r = db.execute_query(
            "SELECT COUNT(*) AS c FROM benhnhan", fetch=True)
        return int(r[0]["c"]) if r else 0

    @staticmethod
    def doanh_thu_ngay(date_str: str) -> float:
        """Tổng thanh_tien của hóa đơn ĐÃ THANH TOÁN trong ngày."""
        r = db.execute_query(
            "SELECT COALESCE(SUM(thanh_tien), 0) AS s "
            "FROM   hoadon "
            "WHERE  DATE(ngay_lap) = %s "
            "  AND  trang_thai = 'da_thanh_toan'",
            (date_str,), fetch=True,
        )
        return float(r[0]["s"]) if r else 0.0

    @staticmethod
    def count_cho_xac_nhan() -> int:
        r = db.execute_query(
            "SELECT COUNT(*) AS c FROM lichkham "
            "WHERE trang_thai = 'cho_xac_nhan'",
            fetch=True,
        )
        return int(r[0]["c"]) if r else 0

    # ── Biểu đồ tròn ───────────────────────────────────────────────────
    @staticmethod
    def thong_ke_trang_thai() -> list[dict]:
        return db.execute_query(
            "SELECT trang_thai, COUNT(*) AS cnt "
            "FROM   lichkham "
            "GROUP  BY trang_thai",
            fetch=True,
        ) or []

    # ── Biểu đồ cột – doanh thu CHỈ hóa đơn đã thanh toán ─────────────
    @staticmethod
    def doanh_thu_ngay(date_str: str) -> float:           # noqa: F811
        r = db.execute_query(
            "SELECT COALESCE(SUM(thanh_tien), 0) AS s "
            "FROM   hoadon "
            "WHERE  DATE(ngay_lap) = %s "
            "  AND  trang_thai = 'da_thanh_toan'",
            (date_str,), fetch=True,
        )
        return float(r[0]["s"]) if r else 0.0

    @staticmethod
    def doanh_thu_theo_thang(year_month_list: list[tuple]) -> list[float]:
        """Trả về list doanh thu theo từng (year, month) — CHỈ đã thanh toán."""
        result = []
        for year, month in year_month_list:
            r = db.execute_query(
                "SELECT COALESCE(SUM(thanh_tien), 0) AS s "
                "FROM   hoadon "
                "WHERE  YEAR(ngay_lap)  = %s "
                "  AND  MONTH(ngay_lap) = %s "
                "  AND  trang_thai = 'da_thanh_toan'",
                (year, month), fetch=True,
            )
            result.append(float(r[0]["s"]) if r else 0.0)
        return result

    @staticmethod
    def doanh_thu_theo_nam(year_list: list[int]) -> list[float]:
        """Trả về list doanh thu theo từng năm — CHỈ đã thanh toán."""
        result = []
        for y in year_list:
            r = db.execute_query(
                "SELECT COALESCE(SUM(thanh_tien), 0) AS s "
                "FROM   hoadon "
                "WHERE  YEAR(ngay_lap) = %s "
                "  AND  trang_thai = 'da_thanh_toan'",
                (y,), fetch=True,
            )
            result.append(float(r[0]["s"]) if r else 0.0)
        return result

    @staticmethod
    def doanh_thu_theo_ngay(date_list: list[str]) -> list[float]:
        """Trả về list doanh thu theo từng ngày — CHỈ đã thanh toán."""
        result = []
        for d in date_list:
            r = db.execute_query(
                "SELECT COALESCE(SUM(thanh_tien), 0) AS s "
                "FROM   hoadon "
                "WHERE  DATE(ngay_lap) = %s "
                "  AND  trang_thai = 'da_thanh_toan'",
                (d,), fetch=True,
            )
            result.append(float(r[0]["s"]) if r else 0.0)
        return result
