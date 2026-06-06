"""
logic/role_logic.py
───────────────────
Tất cả quy tắc phân quyền của hệ thống.
Không phụ thuộc database hay UI.
"""


class RoleLogic:
    # ma trận quyền sửa: (admin, bac_si, le_tan)
    _QUYEN_SUA = {
        "lich_kham":  (True,  False, True),
        "benh_nhan":  (True,  False, True),
        "bac_si":     (True,  False, False),
        "benh_an":    (True,  True,  False),
        "ket_qua":    (True,  True,  False),
        "thuoc":      (True,  False, False),
        "hoa_don":    (True,  False, True),
        "dich_vu":    (True,  False, False),
        "le_tan":     (True,  False, False),
        "tai_khoan":  (True,  False, False),
    }

    # ma trận quyền xem (chỉ các module có giới hạn)
    _QUYEN_XEM = {
        "kham_benh":  (True,  True,  False),
        "hoa_don":    (True,  False, True),
        "le_tan":     (True,  False, False),
        "tai_khoan":  (True,  False, False),
    }

    # Quyền hiển thị menu sidebar
    _QUYEN_MENU = {
        "btnDashboard": (True,  False, False),
        "btnLichKham":  (True,  False, True),
        "btnKhamBenh":  (True,  True,  False),
        "btnBenhNhan":  (True,  True,  True),
        "btnBacSi":     (True,  False, True),
        "btnBenhAn":    (True,  True,  True),
        "btnThuoc":     (True,  True,  True),
        "btnHoaDon":    (True,  False, True),
        "btnDichVu":    (True,  True,  True),
        "btnLeTan":     (True,  False, False),
        "btnTaiKhoan":  (True,  False, False),
    }

    _ROLE_IDX = {"admin": 0, "bac_si": 1, "le_tan": 2}

    @classmethod
    def _idx(cls, user_info: dict) -> int:
        return cls._ROLE_IDX.get(user_info.get("vai_tro", "le_tan"), 2)

    @classmethod
    def is_admin(cls, user_info: dict) -> bool:
        return user_info.get("vai_tro") == "admin"

    @classmethod
    def is_bac_si(cls, user_info: dict) -> bool:
        return user_info.get("vai_tro") == "bac_si"

    @classmethod
    def is_le_tan(cls, user_info: dict) -> bool:
        return user_info.get("vai_tro") == "le_tan"

    @classmethod
    def can_edit(cls, user_info: dict, module: str) -> bool:
        """Kiểm tra quyền thêm/sửa/xóa trên module."""
        perms = cls._QUYEN_SUA.get(module, (False, False, False))
        return perms[cls._idx(user_info)]

    @classmethod
    def can_view(cls, user_info: dict, module: str) -> bool:
        """Kiểm tra quyền xem module. Mặc định True nếu không khai báo."""
        if module not in cls._QUYEN_XEM:
            return True
        perms = cls._QUYEN_XEM[module]
        return perms[cls._idx(user_info)]

    @classmethod
    def menu_visibility(cls, user_info: dict) -> dict[str, bool]:
        """Trả về dict {tên_btn: hiện/ẩn} cho sidebar."""
        idx = cls._idx(user_info)
        return {btn: perms[idx] for btn, perms in cls._QUYEN_MENU.items()}

    @classmethod
    def get_ma_bs(cls, user_info: dict):
        """Trả về ma_bs nếu user là bác sĩ, ngược lại None."""
        if cls.is_bac_si(user_info):
            return user_info.get("ma_bs")
        return None

    @classmethod
    def get_ma_lt(cls, user_info: dict):
        """Trả về ma_lt nếu user là lễ tân, ngược lại None."""
        if cls.is_le_tan(user_info):
            return user_info.get("ma_lt")
        return None

    @classmethod
    def display_role(cls, user_info: dict) -> str:
        """Nhãn hiển thị vai trò."""
        return {
            "admin":  "👑 Quản trị viên",
            "bac_si": "👨‍⚕️ Bác sĩ",
            "le_tan": "🏥 Lễ tân",
        }.get(user_info.get("vai_tro", ""), "")

    @classmethod
    def default_page(cls, user_info: dict) -> tuple[str, int]:
        """Trả về (tên_btn, page_index) mặc định theo vai trò."""
        return {
            "admin":  ("btnDashboard", 0),
            "bac_si": ("btnKhamBenh",  2),
            "le_tan": ("btnLichKham",  1),
        }.get(user_info.get("vai_tro", "le_tan"), ("btnDashboard", 0))
