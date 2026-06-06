# 🏥 PHẦN MỀM QUẢN LÝ PHÒNG KHÁM  –  v2.0 (Refactored)

## 📐 Kiến trúc 3 tầng

```
clinic_app/
│
├── main.py                        # Entry point
│
├── database/                      # ── TẦNG KẾT NỐI ──
│   ├── __init__.py
│   └── connection.py              # Singleton DatabaseConnection + DB_CONFIG
│
├── logic/                         # ── TẦNG NGHIỆP VỤ ──
│   ├── __init__.py
│   ├── auth_logic.py              # Xác thực đăng nhập
│   ├── role_logic.py              # Phân quyền toàn hệ thống
│   ├── bac_si_logic.py            # CRUD bác sĩ
│   ├── benh_an_logic.py           # CRUD bệnh án
│   ├── benh_nhan_logic.py         # CRUD bệnh nhân
│   ├── dashboard_logic.py         # Thống kê dashboard
│   ├── dich_vu_logic.py           # CRUD dịch vụ
│   ├── hoa_don_logic.py           # CRUD hóa đơn
│   ├── kham_benh_logic.py         # Khám bệnh + kê đơn thuốc
│   ├── le_tan_logic.py            # CRUD lễ tân
│   ├── lich_kham_logic.py         # CRUD lịch khám + dịch vụ kèm
│   ├── tai_khoan_logic.py         # CRUD tài khoản
│   └── thuoc_logic.py             # CRUD thuốc
│
├── ui/                            # ── TẦNG GIAO DIỆN DÙNG CHUNG ──
│   ├── __init__.py
│   ├── styles.py                  # Hằng số CSS toàn ứng dụng
│   ├── login_ui.py                # Cửa sổ đăng nhập
│   └── main_window_ui.py          # Cửa sổ chính + sidebar
│
├── pages/                         # ── TẦNG TRANG (UI trang) ──
│   ├── __init__.py
│   ├── dashboard_page.py
│   ├── lich_kham_page.py
│   ├── kham_benh_page.py
│   ├── benh_nhan_page.py
│   ├── bac_si_page.py
│   ├── benh_an_page.py
│   ├── thuoc_page.py
│   ├── tai_khoan_page.py
│   ├── le_tan_page.py
│   ├── dich_vu_page.py
│   └── hoa_don_page.py
│
├── database.sql                   # Script tạo CSDL
└── requirements.txt
```

---

## 🔑 Nguyên tắc phân tầng

| Tầng | Trách nhiệm | KHÔNG được làm |
|------|-------------|----------------|
| `database/` | Kết nối MySQL, thực thi SQL | Import PyQt6 |
| `logic/` | Truy vấn + xử lý nghiệp vụ | Import PyQt6 |
| `ui/` | Widget dùng chung, styles | Gọi DB trực tiếp |
| `pages/` | Hiển thị + tương tác người dùng | Gọi DB trực tiếp |

---

## ⚙️ Cài đặt

```bash
pip install PyQt6 mysql-connector-python matplotlib
```

Tạo CSDL:
```bash
mysql -u root -p < database.sql
```

Chỉnh mật khẩu MySQL trong `database/connection.py`:
```python
DB_CONFIG = {
    "password": "your_password",   # ← sửa tại đây
    "database": "clinic_db",
    ...
}
```

Chạy ứng dụng:
```bash
python main.py
```

---

## 👤 Tài khoản mặc định

| Tên đăng nhập | Mật khẩu | Vai trò |
|---------------|----------|---------|
| admin | admin123 | Quản trị viên |
| bs_hung | bs123 | Bác sĩ |
| bs_lan | bs123 | Bác sĩ |
| le_tan1 | lt123 | Lễ tân |
