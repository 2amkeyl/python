"""
logic/auth_logic.py
───────────────────
Xử lý đăng nhập: xác thực TaiKhoan,
load thêm thông tin BacSi / LeTan tương ứng.
"""
from database import db


class AuthLogic:

    @staticmethod
    def login(username: str, password: str) -> tuple[dict | None, str]:
        """
        Xác thực đăng nhập.

        Returns
        -------
        (user_dict, error_msg)
            user_dict: dict đầy đủ thông tin nếu thành công, None nếu thất bại.
            error_msg: chuỗi lỗi (rỗng khi thành công).
        """
        if not username or not password:
            return None, "Vui lòng nhập đầy đủ thông tin!"

        rows = db.execute_query(
            "SELECT * FROM TaiKhoan "
            "WHERE ten_dang_nhap=%s AND mat_khau=%s AND trang_thai=1",
            (username, password), fetch=True,
        )
        if not rows:
            return None, "Tên đăng nhập hoặc mật khẩu không đúng!"

        user = dict(rows[0])
        vai_tro = user.get("vai_tro")
        ma_tk   = user.get("ma_tk")

        if vai_tro == "bac_si":
            bs = db.execute_query(
                "SELECT * FROM BacSi WHERE ma_tk=%s AND trang_thai=1",
                (ma_tk,), fetch=True,
            )
            if not bs:
                return None, (
                    "Tài khoản chưa được liên kết với hồ sơ bác sĩ!\n"
                    "Liên hệ admin để được hỗ trợ."
                )
            user.update(bs[0])
            user["ma_tk"] = ma_tk       # giữ nguyên, tránh bị ghi đè

        elif vai_tro == "le_tan":
            lt = db.execute_query(
                "SELECT * FROM LeTan WHERE ma_tk=%s AND trang_thai=1",
                (ma_tk,), fetch=True,
            )
            if not lt:
                return None, (
                    "Tài khoản chưa được liên kết với hồ sơ lễ tân!\n"
                    "Liên hệ admin để được hỗ trợ."
                )
            user.update(lt[0])
            user["ma_tk"] = ma_tk

        # admin: không cần load thêm
        return user, ""
