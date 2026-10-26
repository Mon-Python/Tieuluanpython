"""test_auth.py
=============
[B] Kiểm thử toàn diện module xác thực auth.py:
- Đăng ký tài khoản thành công (User và Admin)
- Kiểm tra băm mật khẩu có salt, không lưu mật khẩu thô
- Đăng nhập đúng trả về User/Admin
- Đăng nhập sai tên người dùng -> ném ValueError
- Đăng nhập sai mật khẩu -> ném ValueError
- Đăng ký trùng tên đăng nhập -> ném ValueError
- Đăng ký tên đăng nhập / email / mật khẩu sai định dạng -> ném ValueError
- Đổi mật khẩu thành công (mật khẩu cũ không còn đăng nhập được, mật khẩu mới đăng nhập được)
- Đổi mật khẩu sai mật khẩu cũ -> ném ValueError
- Phân quyền: User.can() và Admin.can()
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auth import AuthManager, hash_password, verify_password
from base_models import Admin, User
from config import ROLE_ADMIN, ROLE_USER
from json_file_handler import JsonFileHandler


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.users_file = self.temp_dir / "users.json"
        self.handler = JsonFileHandler(backup_dir=self.temp_dir / "backup")
        self.auth = AuthManager(users_file=self.users_file, file_handler=self.handler)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_hash_and_verify_password(self):
        pw = "MySecret123!"
        salt = "random_salt_hex"
        hashed = hash_password(pw, salt)
        self.assertNotEqual(pw, hashed)
        self.assertTrue(verify_password(pw, salt, hashed))
        self.assertFalse(verify_password("wrong_password", salt, hashed))
        self.assertFalse(verify_password(pw, "other_salt", hashed))

    def test_register_user_success(self):
        user = self.auth.register("nguyenvana", "MatKhau123", email="vana@example.com", role=ROLE_USER)
        self.assertIsInstance(user, User)
        self.assertNotIsInstance(user, Admin)
        self.assertEqual(user.username, "nguyenvana")
        self.assertEqual(user.role, ROLE_USER)
        self.assertEqual(user.email, "vana@example.com")
        self.assertTrue(user.password_hash)
        self.assertTrue(user.salt)
        self.assertNotEqual(user.password_hash, "MatKhau123")

        # Kiểm tra file users.json được ghi
        users_in_file = self.auth.list_users()
        self.assertEqual(len(users_in_file), 1)
        self.assertEqual(users_in_file[0].username, "nguyenvana")

    def test_register_admin_success(self):
        admin = self.auth.register("quantrivien", "AdminPass2026", email="admin@school.edu.vn", role=ROLE_ADMIN)
        self.assertIsInstance(admin, Admin)
        self.assertTrue(admin.is_admin)
        self.assertEqual(admin.role, ROLE_ADMIN)
        self.assertTrue(admin.can("manage_question"))
        self.assertTrue(admin.can("manage_subject_topic"))

    def test_register_duplicate_username_raises(self):
        self.auth.register("student1", "Pass123456")
        with self.assertRaises(ValueError) as ctx:
            self.auth.register("STUDENT1", "PassDifferent")
        self.assertIn("đã tồn tại", str(ctx.exception))

    def test_register_invalid_username_raises(self):
        with self.assertRaises(ValueError):
            self.auth.register("ab", "Pass123456")  # quá ngắn
        with self.assertRaises(ValueError):
            self.auth.register("1user", "Pass123456")  # bắt đầu bằng số

    def test_register_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self.auth.register("user_valid", "Pass123456", email="invalid_email")

    def test_register_weak_password_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.auth.register("user_valid", "123")
        self.assertIn("tối thiểu 6 ký tự", str(ctx.exception))

    def test_login_success(self):
        self.auth.register("teacher_linh", "PasswordLinh#1")
        logged_in = self.auth.login("teacher_linh", "PasswordLinh#1")
        self.assertIsNotNone(logged_in)
        self.assertEqual(logged_in.username, "teacher_linh")

    def test_login_nonexistent_user_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.auth.login("user_chua_dang_ky", "Password123")
        self.assertIn("không tồn tại", str(ctx.exception))

    def test_login_wrong_password_raises(self):
        self.auth.register("student_hai", "MatKhauChuan")
        with self.assertRaises(ValueError) as ctx:
            self.auth.login("student_hai", "MatKhauSai")
        self.assertIn("Mật khẩu không chính xác", str(ctx.exception))

    def test_change_password_success(self):
        self.auth.register("user_change", "OldPassword123")
        ok = self.auth.change_password("user_change", "OldPassword123", "NewSecurePassword456")
        self.assertTrue(ok)

        # Mật khẩu cũ không đăng nhập được nữa
        with self.assertRaises(ValueError):
            self.auth.login("user_change", "OldPassword123")

        # Mật khẩu mới đăng nhập thành công
        user = self.auth.login("user_change", "NewSecurePassword456")
        self.assertEqual(user.username, "user_change")

    def test_change_password_wrong_old_password_raises(self):
        self.auth.register("user_change_err", "OriginalPass")
        with self.assertRaises(ValueError) as ctx:
            self.auth.change_password("user_change_err", "SaiPass", "NewPassword")
        self.assertIn("Mật khẩu cũ không chính xác", str(ctx.exception))

    def test_user_permissions(self):
        user = self.auth.register("regular_user", "UserPass123", role=ROLE_USER)
        admin = self.auth.register("super_admin", "AdminPass123", role=ROLE_ADMIN)

        # User thường: không được quản lý câu hỏi hay chủ đề
        self.assertFalse(user.can("manage_question"))
        self.assertFalse(user.can("manage_subject_topic"))
        self.assertTrue(user.can("take_exam"))
        self.assertTrue(user.can("change_password"))

        # Admin: có đầy đủ quyền
        self.assertTrue(admin.can("manage_question"))
        self.assertTrue(admin.can("manage_subject_topic"))
        self.assertTrue(admin.can("import_question"))
        self.assertTrue(admin.can("create_exam"))
        self.assertTrue(admin.can("take_exam"))


if __name__ == "__main__":
    unittest.main()
