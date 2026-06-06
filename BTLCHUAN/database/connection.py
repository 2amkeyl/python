"""
database/connection.py
──────────────────────
Kết nối MySQL dùng Singleton.
Chỉnh sửa DB_CONFIG ở đây để thay đổi thông tin kết nối.
Không import bất kỳ thứ gì từ PyQt6 hay UI.
"""
import mysql.connector
from mysql.connector import Error

# ══════════════════════════════════════════
#  CẤU HÌNH KẾT NỐI  –  sửa tại đây
# ══════════════════════════════════════════
DB_CONFIG = {
    "host":       "localhost",
    "port":       3306,
    "user":       "root",
    "password":   "123456",       # ← sửa mật khẩu MySQL của bạn
    "database":   "qlbenhvien",
    "charset":    "utf8mb4",
    "use_unicode": True,
}
# ══════════════════════════════════════════


class DatabaseConnection:
    """Singleton – đảm bảo toàn ứng dụng chỉ dùng 1 kết nối."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
        return cls._instance

    # ── Public API ─────────────────────────────────────────────────────
    def connect(self) -> bool:
        """Kết nối tới MySQL. Trả về True nếu thành công."""
        try:
            self._conn = mysql.connector.connect(**DB_CONFIG)
            if self._conn.is_connected():
                print("[DB] Kết nối MySQL thành công!")
                return True
        except Error as e:
            print(f"[DB] Lỗi kết nối: {e}")
            self._conn = None
        return False

    def disconnect(self):
        """Đóng kết nối."""
        try:
            if self._conn and self._conn.is_connected():
                self._conn.close()
                print("[DB] Đã đóng kết nối MySQL.")
        except Exception:
            pass

    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối."""
        try:
            return bool(self._conn and self._conn.is_connected())
        except Exception:
            return False

    def execute_query(self, query: str, params=None, fetch: bool = False):
        """
        Thực thi câu SQL.

        Parameters
        ----------
        query  : Câu SQL, dùng %s cho placeholder.
        params : Tuple / list tham số (tuỳ chọn).
        fetch  : True  → trả về list[dict] (SELECT).
                 False → trả về lastrowid (INSERT/UPDATE/DELETE).

        Returns
        -------
        list[dict] | int | None
        """
        if not self._ensure_connected():
            return [] if fetch else None
        try:
            cur = self._conn.cursor(dictionary=True)
            cur.execute(query, params or ())
            if fetch:
                result = cur.fetchall()
                cur.close()
                return result
            else:
                self._conn.commit()
                last_id = cur.lastrowid
                cur.close()
                return last_id
        except Error as e:
            print(f"[DB] Query error: {e}\nSQL: {query}\nParams: {params}")
            try:
                self._conn.rollback()
            except Exception:
                pass
            return [] if fetch else None

    # ── Private helper ─────────────────────────────────────────────────
    def _ensure_connected(self) -> bool:
        """Tự kết nối lại nếu mất kết nối."""
        try:
            if self._conn and self._conn.is_connected():
                return True
        except Exception:
            pass
        return self.connect()


# Module-level singleton – import `db` từ đây
db = DatabaseConnection()
