import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from unittest.mock import patch

from auth import AuthManager
from base_models import Admin, User
from config import ROLE_ADMIN, ROLE_USER
from gui.login_window import LoginWindow
from json_file_handler import JsonFileHandler


class TestLoginRegistrationWindow(unittest.TestCase):
    def setUp(self):
        try:
            self.temp_dir = tempfile.TemporaryDirectory()
            root = Path(self.temp_dir.name)
            handler = JsonFileHandler(root / "backup")
            self.auth_manager = AuthManager(root / "users.json", handler)
            self.window = LoginWindow(self.auth_manager)
        except tk.TclError as error:
            self.temp_dir.cleanup()
            self.skipTest(f"Tk display is unavailable: {error}")

    def tearDown(self):
        if hasattr(self, "window") and self.window.winfo_exists():
            self.window.destroy()
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def _fill_registration(self, username, role_label):
        self.window.open_registration()
        self.window.reg_username.insert(0, username)
        self.window.reg_email.insert(0, f"{username}@example.com")
        self.window.reg_password.insert(0, "secure-password")
        self.window.reg_confirm_password.insert(0, "secure-password")
        self.window.reg_role.set(role_label)

    def test_login_page_has_registration_button(self):
        self.assertIsInstance(self.window, LoginWindow)
        buttons = []
        pending = list(self.window.winfo_children())
        while pending:
            widget = pending.pop()
            if isinstance(widget, ttk.Button):
                buttons.append(widget.cget("text"))
            pending.extend(widget.winfo_children())
        self.assertIn("Đăng kí", buttons)

    @patch("gui.login_window.messagebox.showinfo")
    def test_student_registration_returns_to_login_and_role_is_persisted(self, show_info):
        self._fill_registration("student_one", "Học sinh")

        self.window.on_register()

        self.assertIsNone(self.window.registration_window)
        self.assertTrue(self.window.winfo_exists())
        self.assertEqual(self.window.ent_user.get(), "student_one")
        self.assertEqual(self.window.ent_pass.get(), "")
        self.assertIsInstance(
            self.auth_manager.login("student_one", "secure-password"), User
        )
        self.assertNotIsInstance(
            self.auth_manager.login("student_one", "secure-password"), Admin
        )
        self.assertEqual(
            self.auth_manager.login("student_one", "secure-password").role,
            ROLE_USER,
        )
        show_info.assert_called_once()

    @patch("gui.login_window.messagebox.showinfo")
    def test_admin_registration_persists_admin_role(self, show_info):
        self._fill_registration(
            "teacher_one", "Quản trị viên (ra đề, chỉnh sửa đề)"
        )

        self.window.on_register()

        account = self.auth_manager.login("teacher_one", "secure-password")
        self.assertIsInstance(account, Admin)
        self.assertEqual(account.role, ROLE_ADMIN)
        self.assertTrue(account.can("create_exam"))
        self.assertTrue(account.can("manage_question"))
        show_info.assert_called_once()

    @patch("gui.login_window.messagebox.showerror")
    def test_password_confirmation_must_match(self, show_error):
        self._fill_registration("student_two", "Học sinh")
        self.window.reg_confirm_password.delete(0, tk.END)
        self.window.reg_confirm_password.insert(0, "a-different-password")

        self.window.on_register()

        self.assertIsNone(self.auth_manager.get_user_by_username("student_two"))
        self.assertTrue(self.window.registration_window.winfo_exists())
        show_error.assert_called_once()

    def test_cancel_registration_restores_focus_to_registration_button(self):
        self.window.open_registration()
        self.window.update()

        self.window.close_registration()
        self.window.update()

        self.assertIsNone(self.window.registration_window)
        self.assertEqual(self.window.focus_get(), self.window.registration_button)


if __name__ == "__main__":
    unittest.main()
