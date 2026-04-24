from PyQt6.QtWidgets import QDialog
from ui_py.form_dangnhap_ui import Ui_FormDangNhap
from database import ket_noi


class FormDangNhap(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FormDangNhap()
        self.ui.setupUi(self)
        self.ui.btn_dangnhap.clicked.connect(self.dang_nhap)
        self.ui.txt_matkhau.returnPressed.connect(self.dang_nhap)
        self.ui.txt_ten.returnPressed.connect(self.dang_nhap)

    def dang_nhap(self):
        ten = self.ui.txt_ten.text().strip()
        mk = self.ui.txt_matkhau.text().strip()
        if not ten or not mk:
            self.ui.lbl_loi.setText("* Vui long nhap du thong tin!")
            return
        try:
            conn = ket_noi()
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM tai_khoan "
                "WHERE ten=%s AND mat_khau=%s", (ten, mk))
            result = cur.fetchone()
            conn.close()
            if result:
                self.accept()
            else:
                self.ui.lbl_loi.setText("* Sai ten hoac mat khau!")
                self.ui.txt_matkhau.clear()
                self.ui.txt_matkhau.setFocus()
        except Exception as e:
            self.ui.lbl_loi.setText(f"Loi ket noi CSDL!")