"""auth.py
=======
[B sở hữu] Quản lý xác thực người dùng và phân quyền:
- Đăng ký tài khoản (register)
- Đăng nhập (login)
- Đổi mật khẩu (change_password)
- Băm mật khẩu an toàn với salt (PBKDF2-HMAC-SHA256)
- Phân biệt vai trò Quản trị viên (ROLE_ADMIN) và Người dùng thường (ROLE_USER)
- Đọc/ghi dữ liệu an toàn qua JsonFileHandler và USERS_FILE
"""

import hashlib
import secrets
from pathlib import Path
from typing import List, Optional, Tuple, Union

from base_models import Admin, User, _dt_to_str, _str_to_dt
from config import ROLE_ADMIN, ROLE_USER, USERS_FILE
from json_file_handler import JsonFileHandler
from validators import validate_email, validate_username


def hash_password(password: str, salt: str) -> str:
    """
    Băm mật khẩu kết hợp salt bằng thuật toán chuẩn an toàn PBKDF2-HMAC-SHA256
    với 100,000 vòng lặp (iteration).
    """
    if not password:
        raise ValueError("Mật khẩu không được để trống")
    if not salt:
        raise ValueError("Salt không được để trống")
    
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return dk.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """
    So sánh mật khẩu nhập vào với mã băm đã lưu (chống tấn công timing attack).
    """
    computed = hash_password(password, salt)
    return secrets.compare_digest(computed, expected_hash)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Kiểm tra độ an toàn của mật khẩu:
    - Không được rỗng.
    - Độ dài tối thiểu 6 ký tự.
    """
    if not password or len(password) < 6:
        return False, "Mật khẩu phải có độ dài tối thiểu 6 ký tự để đảm bảo an toàn."
    return True, "OK"


class AuthManager:
    """
    Lớp quản lý xác thực và lưu trữ tài khoản người dùng trong users.json.
    """
    def __init__(self, users_file: Optional[Union[str, Path]] = None,
                 file_handler: Optional[JsonFileHandler] = None):
        self.users_file = Path(users_file) if users_file else Path(USERS_FILE)
        self.file_handler = file_handler or JsonFileHandler()

    def _load_users_data(self) -> List[dict]:
        """Tải danh sách dict người dùng từ users.json (file thiếu -> trả [])."""
        data = self.file_handler.read(self.users_file, default=[])
        if not isinstance(data, list):
            return []
        return data

    def _save_users_data(self, users_data: List[dict]) -> None:
        """Lưu danh sách người dùng vào users.json."""
        self.file_handler.write(self.users_file, users_data)

    def list_users(self) -> List[User]:
        """Trả về danh sách tất cả User/Admin objects."""
        raw = self._load_users_data()
        return [User.from_dict(u) for u in raw]

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Tìm người dùng theo username (không phân biệt hoa/thường)."""
        target = username.strip().lower()
        for u in self.list_users():
            if u.username.lower() == target:
                return u
        return None

    def register(self, username: str, password: str, confirm_password: str = "",  email: str = "",
                 role: str = ROLE_USER) -> User:
        """
        Đăng ký tài khoản mới:
        - Kiểm tra tính hợp lệ của username, email, password.
        - Chặn trùng lặp username.
        - Sinh salt ngẫu nhiên bằng secrets.token_hex(16).
        - Băm mật khẩu và lưu vào file users.json.
        - Trả về đối tượng User hoặc Admin theo vai trò.
        """
        # 1. Validate username
        ok_u, msg_u = validate_username(username)
        if not ok_u:
            raise ValueError(msg_u)
        clean_username = username.strip()

        # 2. Validate email (nếu có cung cấp)
        clean_email = email.strip()
        if clean_email:
            ok_e, msg_e = validate_email(clean_email)
            if not ok_e:
                raise ValueError(msg_e)
        if confirm_password and password != confirm_password:
            raise ValueError("Mật khẩu xác nhận không trùng khớp. Vui lòng kiểm tra lại!")
        # 3. Validate password
        ok_p, msg_p = validate_password_strength(password)
        if not ok_p:
            raise ValueError(msg_p)

        # 4. Kiểm tra vai trò
        if role not in (ROLE_ADMIN, ROLE_USER):
            raise ValueError(f"Vai trò '{role}' không hợp lệ. Chỉ chấp nhận '{ROLE_ADMIN}' hoặc '{ROLE_USER}'.")

        # 5. Kiểm tra trùng lặp
        users_raw = self._load_users_data()
        for u in users_raw:
            if u.get("username", "").strip().lower() == clean_username.lower():
                raise ValueError(f"Tên đăng nhập '{clean_username}' đã tồn tại trong hệ thống. Vui lòng chọn tên khác.")
            if clean_email and u.get("email", "").strip().lower() == clean_email.lower():
                raise ValueError(f"Email '{clean_email}' đã được đăng ký cho tài khoản khác.")

        # 6. Sinh salt và băm mật khẩu
        salt = secrets.token_hex(16)
        pw_hash = hash_password(password, salt)

        # 7. Tạo đối tượng và lưu
        new_user = User.create(
            username=clean_username,
            password_hash=pw_hash,
            salt=salt,
            email=clean_email,
            role=role
        )
        users_raw.append(new_user.to_dict())
        self._save_users_data(users_raw)

        return new_user

    def login(self, username: str, password: str) -> User:
        """
        Đăng nhập người dùng:
        - Tìm kiếm tài khoản theo username.
        - Kiểm tra mật khẩu bằng salt và hàm băm an toàn.
        - Trả về đối tượng User hoặc Admin tương ứng.
        - Ném ValueError có giải thích rõ ràng nếu không tìm thấy hoặc sai mật khẩu.
        """
        if not username or not username.strip():
            raise ValueError("Vui lòng nhập tên đăng nhập.")
        if not password:
            raise ValueError("Vui lòng nhập mật khẩu.")

        user = self.get_user_by_username(username)
        if not user:
            raise ValueError(f"Tài khoản '{username.strip()}' không tồn tại trong hệ thống.")

        if not verify_password(password, user.salt, user.password_hash):
            raise ValueError("Mật khẩu không chính xác. Vui lòng kiểm tra lại.")

        return user

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Đổi mật khẩu:
        - Xác minh mật khẩu cũ.
        - Kiểm tra độ an toàn của mật khẩu mới.
        - Sinh salt mới, băm mật khẩu mới và cập nhật file users.json.
        """
        if not username:
            raise ValueError("Tên người dùng không được để trống.")
        
        user = self.get_user_by_username(username)
        if not user:
            raise ValueError(f"Tài khoản '{username}' không tồn tại.")

        if not verify_password(old_password, user.salt, user.password_hash):
            raise ValueError("Mật khẩu cũ không chính xác. Không thể đổi mật khẩu.")

        ok_p, msg_p = validate_password_strength(new_password)
        if not ok_p:
            raise ValueError(msg_p)

        if old_password == new_password:
            raise ValueError("Mật khẩu mới không được trùng với mật khẩu cũ.")

        new_salt = secrets.token_hex(16)
        new_hash = hash_password(new_password, new_salt)

        users_raw = self._load_users_data()
        updated = False
        for u in users_raw:
            if u.get("id") == user.id or u.get("username", "").lower() == username.lower():
                u["salt"] = new_salt
                u["password_hash"] = new_hash
                updated = True
                break

        if updated:
            self._save_users_data(users_raw)
            return True
        return False


# ============================================================
# CÁC HÀM CẤP MODULE TIỆN LỢI CHO D (login_window.py) VÀ A (app.py)
# ============================================================

_default_auth_manager = None

def get_auth_manager(users_file: Optional[Union[str, Path]] = None) -> AuthManager:
    global _default_auth_manager
    if users_file:
        return AuthManager(users_file)
    if _default_auth_manager is None:
        _default_auth_manager = AuthManager()
    return _default_auth_manager

def register(username: str, password: str, email: str = "", role: str = ROLE_USER) -> User:
    return get_auth_manager().register(username, password, email=email, role=role)

def login(username: str, password: str) -> User:
    return get_auth_manager().login(username, password)

def change_password(username: str, old_password: str, new_password: str) -> bool:
    return get_auth_manager().change_password(username, old_password, new_password)
