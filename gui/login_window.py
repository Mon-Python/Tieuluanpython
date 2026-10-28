"""Login and registration screens for the main application."""

import tkinter as tk
from tkinter import ttk

from config import (
    APP_TITLE,
    COLOR_ERROR,
    COLOR_PRIMARY,
    FONT_NORMAL,
    FONT_TITLE,
    PADDING,
    WINDOW_MIN_SIZE,
    WINDOW_SIZE,
)


class LoginWindow(ttk.Frame):
    """A login/register widget to be placed inside the application's root window."""

    def __init__(self, parent):
        super().__init__(parent, padding=PADDING)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.message_var = tk.StringVar()

        window = self.winfo_toplevel()
        window.title(APP_TITLE)
        window.geometry(WINDOW_SIZE)
        window.minsize(*WINDOW_MIN_SIZE)

        self.columnconfigure(0, weight=1)
        self.form_frame = ttk.Frame(self)
        self.form_frame.grid(row=0, column=0, sticky="nsew")
        self.message_label = ttk.Label(
            self,
            textvariable=self.message_var,
            foreground=COLOR_ERROR,
            font=FONT_NORMAL,
            wraplength=420,
        )
        self.message_label.grid(row=1, column=0, pady=(PADDING, 0))

        self._show_login_form()

    def _clear_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.message_var.set("")

    def _add_field(self, row, label_text, variable, show=None):
        ttk.Label(
            self.form_frame,
            text=label_text,
            font=FONT_NORMAL,
        ).grid(row=row, column=0, sticky="w", pady=4)

        entry = ttk.Entry(
            self.form_frame,
            textvariable=variable,
            font=FONT_NORMAL,
            show=show,
            width=32,
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(PADDING, 0), pady=4)
        self.form_frame.columnconfigure(1, weight=1)
        return entry

    def _show_login_form(self):
        self._clear_form()
        ttk.Label(
            self.form_frame,
            text="Đăng nhập",
            font=FONT_TITLE,
            foreground=COLOR_PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(0, PADDING))

        self.username_entry = self._add_field(
            1, "Tên đăng nhập:", self.username_var
        )
        self.password_entry = self._add_field(
            2, "Mật khẩu:", self.password_var, show="*"
        )

        ttk.Button(
            self.form_frame,
            text="Đăng nhập",
            command=self._handle_login,
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(PADDING, 4))
        ttk.Button(
            self.form_frame,
            text="Tạo tài khoản mới",
            command=self._show_register_form,
        ).grid(row=4, column=0, columnspan=2, sticky="ew")
        self.username_entry.focus_set()

    def _show_register_form(self):
        self._clear_form()
        ttk.Label(
            self.form_frame,
            text="Đăng ký tài khoản",
            font=FONT_TITLE,
            foreground=COLOR_PRIMARY,
        ).grid(row=0, column=0, columnspan=2, pady=(0, PADDING))

        self.username_entry = self._add_field(
            1, "Tên đăng nhập:", self.username_var
        )
        self.email_entry = self._add_field(
            2, "Email (nếu có):", self.email_var
        )
        self.password_entry = self._add_field(
            3, "Mật khẩu:", self.password_var, show="*"
        )

        ttk.Button(
            self.form_frame,
            text="Đăng ký",
            command=self._handle_register,
        ).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(PADDING, 4))
        ttk.Button(
            self.form_frame,
            text="Quay lại đăng nhập",
            command=self._show_login_form,
        ).grid(row=5, column=0, columnspan=2, sticky="ew")
        self.username_entry.focus_set()

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.message_var.set("Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        self.message_var.set(
            "Chưa thể đăng nhập: cần tích hợp API auth.py của thành viên B."
        )

    def _handle_register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            self.message_var.set("Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        self.message_var.set(
            "Chưa thể đăng ký: cần tích hợp API auth.py của thành viên B."
        )