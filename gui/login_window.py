import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from auth import AuthManager, get_auth_manager
from config import ROLE_ADMIN, ROLE_USER


class LoginWindow(tk.Tk):

    def __init__(self, auth_manager: Optional[AuthManager] = None):
        super().__init__()
        self.title("Đăng nhập hệ thống")
        self.geometry("420x280")
        self.resizable(False, False)
        self.logged_in_user = None
        self.auth_mgr = auth_manager or get_auth_manager()
        self.registration_window = None
        self.registration_button = None

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="ĐĂNG NHẬP", font=("Segoe UI", 14, "bold")).pack(
            pady=12
        )

        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        username_group = ttk.LabelFrame(
            frame, text="Tên đăng nhập", padding=(6, 2)
        )
        username_group.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        self.ent_user = ttk.Entry(username_group, width=32)
        self.ent_user.pack(fill=tk.X)

        password_group = ttk.LabelFrame(
            frame, text="Mật khẩu", padding=(6, 2)
        )
        password_group.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        self.ent_pass = ttk.Entry(password_group, show="*", width=32)
        self.ent_pass.pack(fill=tk.X)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=2, pady=12)
        ttk.Button(
            buttons, text="Đăng nhập", command=self.on_login
        ).pack(side=tk.LEFT, padx=5)
        self.registration_button = ttk.Button(
            buttons, text="Đăng kí", command=self.open_registration
        )
        self.registration_button.pack(side=tk.LEFT, padx=5)

        self.ent_user.focus_set()
        self.ent_pass.bind("<Return>", lambda _event: self.on_login())

    def open_registration(self):
        if self.registration_window is not None:
            if self.registration_window.winfo_exists():
                self.registration_window.lift()
                self.registration_window.focus_force()
                return

        dialog = tk.Toplevel(self)
        self.registration_window = dialog
        dialog.title("Đăng kí tài khoản")
        dialog.geometry("460x430")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", self.close_registration)

        ttk.Label(
            dialog, text="TẠO TÀI KHOẢN", font=("Segoe UI", 14, "bold")
        ).pack(pady=(14, 8))

        form = ttk.Frame(dialog, padding=12)
        form.pack(fill=tk.BOTH, expand=True)
        form.columnconfigure(1, weight=1)

        def add_entry(label, row, show=None):
            field = ttk.LabelFrame(form, text=label, padding=(6, 2))
            field.grid(row=row, column=0, columnspan=2, sticky="ew", pady=4)
            entry = ttk.Entry(field, show=show or "", width=36)
            entry.pack(fill=tk.X)
            return entry

        self.reg_username = add_entry("Tên đăng nhập", 0)
        self.reg_email = add_entry("Email (không bắt buộc)", 1)
        self.reg_password = add_entry("Mật khẩu", 2, show="*")
        self.reg_confirm_password = add_entry("Xác nhận mật khẩu", 3, show="*")

        role_group = ttk.LabelFrame(
            form, text="Loại tài khoản", padding=(6, 2)
        )
        role_group.grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)
        self.reg_role = ttk.Combobox(
            role_group,
            state="readonly",
            values=(
                "Học sinh",
                "Quản trị viên (ra đề, chỉnh sửa đề)",
            ),
        )
        self.reg_role.pack(fill=tk.X)
        self.reg_role.current(0)

        ttk.Label(
            form,
            text="Vai trò được lưu cố định cho tài khoản và không thể tự đổi sau này.",
            wraplength=420,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 4))

        actions = ttk.Frame(form)
        actions.grid(row=6, column=0, columnspan=2, pady=12)
        ttk.Button(
            actions, text="Tạo tài khoản", command=self.on_register
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            actions, text="Hủy", command=self.close_registration
        ).pack(side=tk.LEFT, padx=5)

        self.reg_username.focus_set()
        self.reg_confirm_password.bind(
            "<Return>", lambda _event: self.on_register()
        )

    def close_registration(self):
        dialog = self.registration_window
        self.registration_window = None
        if dialog is not None and dialog.winfo_exists():
            dialog.grab_release()
            dialog.destroy()
        if self.registration_button is not None:
            self.registration_button.focus_set()

    def on_register(self):
        role_by_label = {
            "Học sinh": ROLE_USER,
            "Quản trị viên (ra đề, chỉnh sửa đề)": ROLE_ADMIN,
        }
        role = role_by_label.get(self.reg_role.get())
        if role is None:
            messagebox.showerror(
                "Đăng kí thất bại",
                "Vui lòng chọn loại tài khoản hợp lệ.",
                parent=self.registration_window,
            )
            return

        username = self.reg_username.get().strip()
        if self.reg_password.get() != self.reg_confirm_password.get():
            messagebox.showerror(
                "Đăng kí thất bại",
                "Mật khẩu xác nhận không trùng khớp. Vui lòng kiểm tra lại!",
                parent=self.registration_window,
            )
            return

        try:
            self.auth_mgr.register(
                username=username,
                password=self.reg_password.get(),
                confirm_password=self.reg_confirm_password.get(),
                email=self.reg_email.get(),
                role=role,
            )
        except ValueError as error:
            messagebox.showerror(
                "Đăng kí thất bại",
                str(error),
                parent=self.registration_window,
            )
            return

        self.ent_user.delete(0, tk.END)
        self.ent_user.insert(0, username)
        self.ent_pass.delete(0, tk.END)
        dialog = self.registration_window
        self.registration_window = None
        if dialog is not None and dialog.winfo_exists():
            dialog.grab_release()
            dialog.destroy()
        self.ent_pass.focus_set()
        messagebox.showinfo(
            "Đăng kí thành công",
            "Tài khoản đã được tạo. Vui lòng đăng nhập.",
            parent=self,
        )

    def on_login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get()
        try:
            user = self.auth_mgr.login(username, password)
            self.logged_in_user = user
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Lỗi đăng nhập", str(e), parent=self)