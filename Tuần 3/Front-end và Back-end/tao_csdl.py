import mysql.connector

conn = mysql.connector.connect(
    host="localhost", user="root", password="123456"
)
cur = conn.cursor()

cur.execute(
    "CREATE DATABASE IF NOT EXISTS quanlykham "
    "DEFAULT CHARACTER SET utf8mb4"
)
cur.execute("USE quanlykham")

# Bang tai khoan
cur.execute("""
            CREATE TABLE IF NOT EXISTS tai_khoan
            (
                id
                INT
                AUTO_INCREMENT
                PRIMARY
                KEY,
                ten
                VARCHAR
            (
                50
            ) NOT NULL UNIQUE,
                mat_khau VARCHAR
            (
                50
            ) NOT NULL
                )""")

# Bang dich vu — 3 muc gia
cur.execute("""
            CREATE TABLE IF NOT EXISTS dich_vu
            (
                id
                INT
                AUTO_INCREMENT
                PRIMARY
                KEY,
                ten
                VARCHAR
            (
                100
            ) NOT NULL,
                gia_bs INT NOT NULL COMMENT 'Gia Bac si',
                gia_ths INT NOT NULL COMMENT 'Gia Thac si',
                gia_ts INT NOT NULL COMMENT 'Gia Tien si',
                mo_ta VARCHAR
            (
                200
            )
                )""")

# Bang benh nhan — luu thong tin 1 lan, tai su dung nhieu lich
cur.execute("""
            CREATE TABLE IF NOT EXISTS benh_nhan
            (
                id
                INT
                AUTO_INCREMENT
                PRIMARY
                KEY,
                ma_bn
                VARCHAR
            (
                10
            ) NOT NULL UNIQUE,
                ho_ten VARCHAR
            (
                100
            ) NOT NULL,
                sdt VARCHAR
            (
                15
            ) NOT NULL UNIQUE,
                ngay_sinh DATE,
                dia_chi VARCHAR
            (
                200
            ),
                ngay_tao DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")

# Bang lich kham — lien ket voi benh_nhan va dich_vu
cur.execute("""
            CREATE TABLE IF NOT EXISTS lich_kham
            (
                id
                INT
                AUTO_INCREMENT
                PRIMARY
                KEY,
                ma_lich
                VARCHAR
            (
                10
            ) NOT NULL UNIQUE,
                benh_nhan_id INT NOT NULL,
                dich_vu_id INT,
                goi_kham VARCHAR
            (
                20
            ) COMMENT 'Bac si/Thac si/Tien si',
                phi_kham INT,
                ngay_kham DATE,
                gio_kham TIME,
                trang_thai VARCHAR
            (
                20
            ) DEFAULT 'Cho kham',
                FOREIGN KEY
            (
                benh_nhan_id
            )
                REFERENCES benh_nhan
            (
                id
            ) ON DELETE CASCADE,
                FOREIGN KEY
            (
                dich_vu_id
            )
                REFERENCES dich_vu
            (
                id
            )
              ON DELETE SET NULL
                )""")

# Du lieu mac dinh
cur.execute(
    "INSERT IGNORE INTO tai_khoan(ten,mat_khau) VALUES('admin','123456')"
)
cur.execute("""
            INSERT
            IGNORE INTO dich_vu(id,ten,gia_bs,gia_ths,gia_ts,mo_ta) VALUES
    (1,'Kham tong quat',200000,300000,400000,'Kham suc khoe dinh ky'),
    (2,'Kham tim mach', 350000,500000,700000,'Do dien tam do, sieu am'),
    (3,'Kham mat',      250000,375000,500000,'Do thi luc, ap suat mat'),
    (4,'Kham xuong khop',300000,450000,600000,'Chup X-quang, sieu am')
            """)

conn.commit()
conn.close()
print("Tao CSDL thanh cong!")
print("Tai khoan: admin / 123456")
