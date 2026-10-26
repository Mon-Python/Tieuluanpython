/**
 * Python Source Code repository definitions for Member B
 * Allows in-browser syntax viewing, copying, and 1-click zip export.
 */

export interface PythonFileMeta {
  path: string;
  name: string;
  description: string;
  author: string;
  category: 'core' | 'gui' | 'test' | 'sample' | 'config';
  code: string;
}

export const PYTHON_FILES: PythonFileMeta[] = [
  {
    path: 'validators.py',
    name: 'validators.py',
    description: 'Kiểm tra dữ liệu nhập bằng Regular Expression (username, email, q_id, date) và kiểm tra câu hỏi',
    author: 'Thành viên B',
    category: 'core',
    code: `"""validators.py
==============
[B sở hữu] Tập trung toàn bộ kiểm tra dữ liệu nhập cho hệ thống:
- Regular Expression: Email, Tên đăng nhập (Username), Mã thực thể/câu hỏi, Ngày tháng.
- Kiểm tra số không âm, kiểm tra chuỗi không rỗng.
- Kiểm tra tính hợp lệ của câu hỏi và đáp án dựa trên Question.is_valid().

Mọi hàm đều trả về tuple (is_valid: bool, error_message: str).
Khi không hợp lệ, error_message cung cấp hướng dẫn cụ thể cách sửa cho người dùng.
"""

import re
from datetime import datetime
from typing import Optional, Tuple
from base_models import Question, Option, DifficultyLevel

# ============================================================
# CÁC MẪU REGULAR EXPRESSION (Regex)
# ============================================================

# Username: 3-20 ký tự gồm chữ cái, chữ số và dấu gạch dưới, không bắt đầu bằng số
REGEX_USERNAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{2,19}$")

# Email: định dạng chuẩn username@domain.ext
REGEX_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\\.[a-zA-Z0-9-]+)+$")

# Mã câu hỏi hệ thống sinh: tiền tố q_ kèm đúng 8 ký tự thập lục phân (hex)
REGEX_QUESTION_ID = re.compile(r"^q_[0-9a-fA-F]{8}$")

# Mã thực thể tổng quát: <prefix>_<8 ký tự hex>
REGEX_ENTITY_ID = re.compile(r"^[a-zA-Z]{1,10}_[0-9a-fA-F]{8}$")

# Ngày tháng: hỗ trợ định dạng ISO YYYY-MM-DD hoặc chuẩn VN DD/MM/YYYY
REGEX_DATE_ISO = re.compile(r"^\\d{4}-\\d{2}-\\d{2}$")
REGEX_DATE_VN = re.compile(r"^\\d{2}/\\d{2}/\\d{4}$")


# ============================================================
# CÁC HÀM VALIDATE
# ============================================================

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Kiểm tra tên đăng nhập:
    - Không được để trống.
    - Độ dài từ 3 đến 20 ký tự.
    - Bắt đầu bằng chữ cái hoặc dấu gạch dưới.
    - Chỉ chứa chữ cái không dấu, chữ số (0-9) và dấu gạch dưới (_).
    """
    if not username or not username.strip():
        return False, "Tên đăng nhập không được để trống. Vui lòng nhập từ 3 đến 20 ký tự."
    
    val = username.strip()
    if len(val) < 3:
        return False, f"Tên đăng nhập '{val}' quá ngắn ({len(val)} ký tự). Vui lòng nhập tối thiểu 3 ký tự."
    if len(val) > 20:
        return False, f"Tên đăng nhập '{val}' quá dài ({len(val)} ký tự). Vui lòng nhập tối đa 20 ký tự."
    
    if not REGEX_USERNAME.match(val):
        if val[0].isdigit():
            return False, "Tên đăng nhập không được bắt đầu bằng chữ số. Hãy bắt đầu bằng chữ cái hoặc dấu _."
        return False, "Tên đăng nhập chỉ được chứa chữ cái không dấu (a-z, A-Z), số (0-9) và dấu gạch dưới (_)."
    
    return True, "OK"


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Kiểm tra địa chỉ email:
    - Đúng cấu trúc <tên_người_dùng>@<tên_miền>.<phần_mở_rộng>.
    - Không chứa khoảng trắng hoặc ký tự đặc biệt không hợp lệ.
    """
    if not email or not email.strip():
        return False, "Email không được để trống. Vui lòng nhập email dạng ví dụ: nguoidung@example.com."
    
    val = email.strip()
    if "@" not in val:
        return False, f"Email '{val}' thiếu ký tự '@'. Định dạng chuẩn phải có dạng: ten@domain.com."
    
    parts = val.split("@")
    if len(parts) != 2:
        return False, "Email chỉ được chứa đúng một ký tự '@'."
    
    if not parts[1] or "." not in parts[1]:
        return False, f"Phần tên miền sau '@' ({parts[1]}) chưa hợp lệ. Cần có phần mở rộng như .com, .edu.vn."
    
    if not REGEX_EMAIL.match(val):
        return False, f"Email '{val}' không đúng định dạng. Hãy kiểm tra lại, không chứa dấu cách hoặc ký tự đặc biệt."
    
    return True, "OK"


def validate_question_id(q_id: str) -> Tuple[bool, str]:
    """
    Kiểm tra mã câu hỏi do hệ thống sinh:
    - Mẫu chuẩn: q_ + 8 ký tự hex (ví dụ: q_a1b2c3d4).
    """
    if not q_id or not q_id.strip():
        return False, "Mã câu hỏi không được để trống."
    
    val = q_id.strip()
    if not REGEX_QUESTION_ID.match(val):
        return False, f"Mã câu hỏi '{val}' không hợp lệ. Mã chuẩn có định dạng 'q_' kèm đúng 8 ký tự hex (ví dụ: q_a1b2c3d4)."
    
    return True, "OK"


def validate_date_string(date_str: str) -> Tuple[bool, str]:
    """
    Kiểm tra chuỗi ngày tháng:
    - Khớp định dạng YYYY-MM-DD hoặc DD/MM/YYYY.
    - Kiểm tra tính hợp lệ thực tế (không có ngày 31 tháng 2, tháng 1-12, năm hợp lệ).
    """
    if not date_str or not date_str.strip():
        return False, "Ngày tháng không được để trống. Vui lòng nhập theo định dạng YYYY-MM-DD hoặc DD/MM/YYYY."
    
    val = date_str.strip()
    dt = None
    if REGEX_DATE_ISO.match(val):
        try:
            dt = datetime.strptime(val, "%Y-%m-%d")
        except ValueError:
            return False, f"Ngày '{val}' không tồn tại trong lịch thực tế. Hãy kiểm tra lại ngày và tháng."
    elif REGEX_DATE_VN.match(val):
        try:
            dt = datetime.strptime(val, "%d/%m/%Y")
        except ValueError:
            return False, f"Ngày '{val}' không tồn tại trong lịch thực tế. Hãy kiểm tra lại ngày và tháng."
    else:
        return False, f"Định dạng ngày '{val}' không đúng. Vui lòng nhập theo dạng YYYY-MM-DD (VD: 2026-10-21) hoặc DD/MM/YYYY."
    
    if dt.year < 1900 or dt.year > 2100:
        return False, f"Năm {dt.year} nằm ngoài phạm vi hợp lệ (1900 - 2100)."
    
    return True, "OK"


def validate_non_negative_number(value: any, field_name: str = "Giá trị") -> Tuple[bool, str]:
    """
    Kiểm tra số không âm (số nguyên hoặc số thực >= 0).
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} phải là một số hợp lệ."
    
    if num < 0:
        return False, f"{field_name} không được là số âm (nhận được: {value}). Vui lòng nhập số >= 0."
    
    return True, "OK"


def validate_question(question: Question) -> Tuple[bool, str]:
    """
    Kiểm tra toàn diện một câu hỏi ngân hàng đề:
    - Tận dụng triệt để phương thức Question.is_valid() của base_models.
    - Bổ sung kiểm tra topic_id không rỗng.
    """
    if not question.topic_id or not question.topic_id.strip():
        return False, "Câu hỏi phải thuộc về một chủ đề cụ thể (topic_id không được để trống)."
    
    ok, msg = question.is_valid()
    if not ok:
        return False, f"Dữ liệu câu hỏi chưa hợp lệ: {msg}"
    
    return True, "OK"


def validate_question_data(content: str, options: list[str], correct_index: int,
                           difficulty: str = "de") -> Tuple[bool, str]:
    """
    Kiểm tra nhanh dữ liệu form câu hỏi trước khi tạo object Question:
    - Nội dung câu hỏi không rỗng.
    - Đủ 4 phương án, không phương án nào rỗng.
    - Không có phương án trùng nhau (không phân biệt hoa/thường).
    - correct_index nằm trong khoảng 0 đến 3.
    """
    if not content or not content.strip():
        return False, "Nội dung câu hỏi không được rỗng. Hãy nhập câu hỏi."
    
    if not options or len(options) != 4:
        return False, "Câu hỏi bắt buộc phải có đúng 4 phương án trả lời (A, B, C, D)."
    
    for i, opt in enumerate(options):
        if not opt or not str(opt).strip():
            label = chr(ord('A') + i)
            return False, f"Phương án {label} không được để trống. Hãy điền nội dung phương án."
    
    normalized = [str(opt).strip().lower() for opt in options]
    if len(set(normalized)) != len(normalized):
        return False, "Các phương án trả lời không được trùng lặp nội dung với nhau."
    
    if correct_index < 0 or correct_index >= 4:
        return False, "Vui lòng chọn chính xác 1 phương án đúng trong 4 phương án (A, B, C, D)."
    
    if difficulty not in ("de", "kho", DifficultyLevel.DE, DifficultyLevel.KHO):
        return False, "Mức độ câu hỏi không hợp lệ. Chỉ chấp nhận 'de' (Dễ) hoặc 'kho' (Khó)."
    
    return True, "OK"
`
  },
  {
    path: 'auth.py',
    name: 'auth.py',
    description: 'Xác thực tài khoản, đăng ký, đăng nhập, đổi mật khẩu, băm mật khẩu PBKDF2 với salt',
    author: 'Thành viên B',
    category: 'core',
    code: `"""auth.py
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
    """Băm mật khẩu kết hợp salt bằng chuẩn an toàn PBKDF2-HMAC-SHA256 (100,000 rounds)."""
    if not password:
        raise ValueError("Mật khẩu không được để trống")
    if not salt:
        raise ValueError("Salt không được để trống")
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return dk.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """So sánh mật khẩu nhập vào với mã băm đã lưu (chống timing attack)."""
    computed = hash_password(password, salt)
    return secrets.compare_digest(computed, expected_hash)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    if not password or len(password) < 6:
        return False, "Mật khẩu phải có độ dài tối thiểu 6 ký tự để đảm bảo an toàn."
    return True, "OK"


class AuthManager:
    def __init__(self, users_file: Optional[Union[str, Path]] = None,
                 file_handler: Optional[JsonFileHandler] = None):
        self.users_file = Path(users_file) if users_file else Path(USERS_FILE)
        self.file_handler = file_handler or JsonFileHandler()

    def _load_users_data(self) -> List[dict]:
        data = self.file_handler.read(self.users_file, default=[])
        return data if isinstance(data, list) else []

    def _save_users_data(self, users_data: List[dict]) -> None:
        self.file_handler.write(self.users_file, users_data)

    def list_users(self) -> List[User]:
        return [User.from_dict(u) for u in self._load_users_data()]

    def get_user_by_username(self, username: str) -> Optional[User]:
        target = username.strip().lower()
        for u in self.list_users():
            if u.username.lower() == target:
                return u
        return None

    def register(self, username: str, password: str, email: str = "",
                 role: str = ROLE_USER) -> User:
        ok_u, msg_u = validate_username(username)
        if not ok_u:
            raise ValueError(msg_u)
        clean_username = username.strip()

        clean_email = email.strip()
        if clean_email:
            ok_e, msg_e = validate_email(clean_email)
            if not ok_e:
                raise ValueError(msg_e)

        ok_p, msg_p = validate_password_strength(password)
        if not ok_p:
            raise ValueError(msg_p)

        if role not in (ROLE_ADMIN, ROLE_USER):
            raise ValueError(f"Vai trò '{role}' không hợp lệ.")

        users_raw = self._load_users_data()
        for u in users_raw:
            if u.get("username", "").strip().lower() == clean_username.lower():
                raise ValueError(f"Tên đăng nhập '{clean_username}' đã tồn tại.")
            if clean_email and u.get("email", "").strip().lower() == clean_email.lower():
                raise ValueError(f"Email '{clean_email}' đã được đăng ký.")

        salt = secrets.token_hex(16)
        pw_hash = hash_password(password, salt)

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
        for u in users_raw:
            if u.get("id") == user.id or u.get("username", "").lower() == username.lower():
                u["salt"] = new_salt
                u["password_hash"] = new_hash
                self._save_users_data(users_raw)
                return True
        return False
`
  },
  {
    path: 'import_questions.py',
    name: 'import_questions.py',
    description: 'Nhập hàng loạt câu hỏi từ file văn bản (.txt) với xử lý lỗi dòng và báo cáo chi tiết',
    author: 'Thành viên B',
    category: 'core',
    code: `"""import_questions.py
===================
[B sở hữu] Đọc và nhập hàng loạt câu hỏi từ file văn bản (.txt) vào ngân hàng câu hỏi:
- Xử lý các trường hợp: file không tồn tại, file rỗng, dòng sai định dạng.
- Bỏ qua các dòng lỗi nhưng tiếp tục nạp các câu hợp lệ.
- Báo cáo chi tiết số lượng câu nạp thành công và danh sách dòng/câu bị lỗi.
- Lưu dữ liệu thông qua JsonDataRepository.add_questions.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

from base_models import DifficultyLevel, Option, Question
from data_repository import JsonDataRepository
from validators import validate_question


def parse_question_line(line: str, line_no: int,
                        default_topic_id: str = "") -> Tuple[Optional[Question], Optional[str]]:
    clean_line = line.strip()
    if not clean_line or clean_line.startswith("#"):
        return None, None

    parts = [p.strip() for p in clean_line.split("|")]
    if len(parts) == 8:
        topic_id, content, diff_str, opt_a, opt_b, opt_c, opt_d, correct_raw = parts
    elif len(parts) == 7:
        if not default_topic_id:
            return None, f"Dòng {line_no}: Thiếu mã chủ đề (topic_id) và chưa chọn chủ đề mặc định."
        topic_id = default_topic_id
        content, diff_str, opt_a, opt_b, opt_c, opt_d, correct_raw = parts
    else:
        return None, f"Dòng {line_no}: Sai định dạng ({len(parts)} trường). Yêu cầu 7 hoặc 8 trường cách nhau bởi ký tự '|'."

    if not topic_id:
        return None, f"Dòng {line_no}: Mã chủ đề bị rỗng."
    if not content:
        return None, f"Dòng {line_no}: Nội dung câu hỏi bị rỗng."

    diff_norm = diff_str.lower()
    if diff_norm in ("de", "dễ", "easy"):
        diff = DifficultyLevel.DE
    elif diff_norm in ("kho", "khó", "hard"):
        diff = DifficultyLevel.KHO
    else:
        return None, f"Dòng {line_no}: Mức độ '{diff_str}' không hợp lệ (chỉ de/kho)."

    option_texts = [opt_a, opt_b, opt_c, opt_d]
    for i, t in enumerate(option_texts):
        if not t:
            label = chr(ord('A') + i)
            return None, f"Dòng {line_no}: Phương án {label} bị để trống."

    normalized_opts = [t.lower() for t in option_texts]
    if len(set(normalized_opts)) != 4:
        return None, f"Dòng {line_no}: Các phương án câu hỏi bị trùng lặp nội dung."

    correct_clean = correct_raw.strip().upper()
    valid_keys = {"A": 0, "B": 1, "C": 2, "D": 3, "1": 0, "2": 1, "3": 2, "4": 3}
    if correct_clean not in valid_keys:
        return None, f"Dòng {line_no}: Đáp án đúng '{correct_raw}' không hợp lệ. Hãy nhập A, B, C hoặc D."
    correct_idx = valid_keys[correct_clean]

    options = [Option.create(t, i == correct_idx) for i, t in enumerate(option_texts)]
    question = Question.create(topic_id, content, diff, options)
    ok, val_err = validate_question(question)
    if not ok:
        return None, f"Dòng {line_no}: {val_err}"

    return question, None


def import_questions_from_file(file_path: Union[str, Path],
                               repository: JsonDataRepository,
                               default_topic_id: str = "") -> Tuple[int, List[str]]:
    p = Path(file_path)
    if not p.exists():
        return 0, [f"Lỗi: Không tìm thấy file dữ liệu tại đường dẫn '{file_path}'."]

    try:
        text = p.read_text(encoding="utf-8-sig")
    except Exception as e:
        return 0, [f"Lỗi khi đọc file '{p.name}': {e}"]

    lines = text.splitlines()
    non_empty = [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not non_empty:
        return 0, [f"Lỗi: File '{p.name}' rỗng hoặc không chứa dữ liệu câu hỏi nào."]

    questions_to_add: List[Question] = []
    parse_errors: List[str] = []

    for line_no, line in enumerate(lines, start=1):
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        q, err = parse_question_line(clean, line_no, default_topic_id)
        if err:
            parse_errors.append(err)
        elif q:
            questions_to_add.append(q)

    if not questions_to_add:
        return 0, parse_errors

    added_count, repo_errors = repository.add_questions(questions_to_add)
    return added_count, parse_errors + repo_errors
`
  },
  {
    path: 'api_import.py',
    name: 'api_import.py',
    description: 'Thu thập và làm sạch câu hỏi tự động từ Open Trivia DB Web API',
    author: 'Thành viên B',
    category: 'core',
    code: `"""api_import.py
=============
[B sở hữu] Lấy câu hỏi từ Web API bên ngoài (Open Trivia DB hoặc API tương đương):
- Sử dụng urllib.request với timeout an toàn từ config.py.
- Làm sạch dữ liệu HTML entities (&quot;, &#039;, &amp;).
- Chuyển đổi về 4 phương án (1 đúng, 3 sai, xáo trộn).
- Lưu kết quả thô vào API_QUESTIONS_FILE và lưu vào JsonDataRepository.
"""

import html
import json
import random
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from base_models import DifficultyLevel, Option, Question
from config import API_QUESTIONS_FILE, API_TIMEOUT_SECONDS, API_URL
from data_repository import JsonDataRepository
from json_file_handler import JsonFileHandler
from validators import validate_question


def clean_html_text(text: str) -> str:
    if not text:
        return ""
    return html.unescape(html.unescape(str(text))).strip()


def fetch_questions_from_api(url: Optional[str] = None,
                             amount: int = 10,
                             category: Optional[int] = None,
                             difficulty: Optional[str] = None,
                             timeout: int = API_TIMEOUT_SECONDS) -> Tuple[List[dict], Optional[str]]:
    target_url = url or API_URL

    if "opentdb.com" in target_url:
        parsed = urllib.parse.urlparse(target_url)
        params = urllib.parse.parse_qs(parsed.query)
        params["amount"] = [str(amount)]
        params["type"] = ["multiple"]
        if category:
            params["category"] = [str(category)]
        if difficulty and difficulty in ("easy", "medium", "hard"):
            params["difficulty"] = [difficulty]
        new_query = urllib.parse.urlencode(params, doseq=True)
        target_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

    req = urllib.request.Request(
        target_url,
        headers={"User-Agent": "QuestionBankManager/1.0 (Student Python Project)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.getcode() != 200:
                return [], f"Máy chủ API trả về mã lỗi HTTP {response.getcode()}."
            raw_data = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return [], f"Lỗi HTTP từ máy chủ API: {e.code} - {e.reason}."
    except urllib.error.URLError as e:
        return [], f"Không thể kết nối đến máy chủ API: {e.reason}."
    except TimeoutError:
        return [], f"Kết nối đến API bị quá thời gian (timeout {timeout}s)."
    except Exception as e:
        return [], f"Lỗi không xác định khi gọi API: {e}"

    try:
        payload = json.loads(raw_data)
    except json.JSONDecodeError as e:
        return [], f"Dữ liệu nhận từ API không phải JSON hợp lệ: {e}"

    if isinstance(payload, dict) and "results" in payload:
        return payload["results"], None

    if isinstance(payload, list):
        return payload, None

    return [], "Cấu trúc phản hồi API không tương thích."
`
  },
  {
    path: 'gui/question_editor.py',
    name: 'gui/question_editor.py',
    description: 'Custom Widget QuestionEditor kế thừa tk.Frame nhập/sửa câu hỏi và 4 phương án',
    author: 'Thành viên B',
    category: 'gui',
    code: `"""gui/question_editor.py
======================
[B sở hữu] Custom Widget QuestionEditor kế thừa ttk.Frame:
- Cho phép nhập/sửa nội dung câu hỏi, 4 phương án (A, B, C, D).
- Radiobutton chọn phương án đúng duy nhất.
- Combobox chọn mức độ khó (Dễ / Khó).
- Tích hợp kiểm tra tính hợp lệ tức thì qua validators.py.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from base_models import DifficultyLevel, Option, Question
from validators import validate_question_data


class QuestionEditor(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.editing_question_id: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1)

        # Mức độ khó
        lbl_diff = ttk.Label(self, text="Mức độ khó:", font=("Segoe UI", 9, "bold"))
        lbl_diff.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.var_diff = tk.StringVar(value="de")
        self.cbo_diff = ttk.Combobox(self, textvariable=self.var_diff, values=["Dễ (de)", "Khó (kho)"], state="readonly", width=20)
        self.cbo_diff.current(0)
        self.cbo_diff.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Nội dung
        lbl_content = ttk.Label(self, text="Nội dung câu hỏi:", font=("Segoe UI", 9, "bold"))
        lbl_content.grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.txt_content = tk.Text(self, height=4, width=50, wrap="word", font=("Segoe UI", 10))
        self.txt_content.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 4 Phương án
        grp_options = ttk.LabelFrame(self, text="Các phương án trả lời (chọn nút tròn để đánh dấu ĐÁP ÁN ĐÚNG)")
        grp_options.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        grp_options.columnconfigure(2, weight=1)

        self.correct_var = tk.IntVar(value=0)
        self.option_entries: List[ttk.Entry] = []
        labels = ["A", "B", "C", "D"]

        for i, lbl in enumerate(labels):
            rb = ttk.Radiobutton(grp_options, text=f"Đáp án {lbl}", value=i, variable=self.correct_var)
            rb.grid(row=i, column=0, sticky="w", padx=8, pady=4)
            lbl_opt = ttk.Label(grp_options, text=f"{lbl}:", font=("Segoe UI", 9, "bold"))
            lbl_opt.grid(row=i, column=1, sticky="e", padx=(5, 2), pady=4)
            entry = ttk.Entry(grp_options, font=("Segoe UI", 9))
            entry.grid(row=i, column=2, sticky="ew", padx=8, pady=4)
            self.option_entries.append(entry)

    def set_question(self, question: Optional[Question]):
        self.clear()
        if not question:
            return
        self.editing_question_id = question.id
        self.cbo_diff.current(1 if question.difficulty == "kho" else 0)
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert("1.0", question.content)
        for i, opt in enumerate(question.options[:4]):
            self.option_entries[i].delete(0, tk.END)
            self.option_entries[i].insert(0, opt.content)
            if opt.is_correct:
                self.correct_var.set(i)

    def get_question(self, topic_id: str) -> Optional[Question]:
        content = self.txt_content.get("1.0", tk.END).strip()
        diff_choice = "kho" if "kho" in self.cbo_diff.get().lower() else "de"
        diff_level = DifficultyLevel.KHO if diff_choice == "kho" else DifficultyLevel.DE
        options_text = [entry.get().strip() for entry in self.option_entries]
        correct_idx = self.correct_var.get()

        ok, msg = validate_question_data(content, options_text, correct_idx, diff_choice)
        if not ok:
            messagebox.showerror("Dữ liệu câu hỏi chưa hợp lệ", msg, parent=self)
            return None

        opts = [Option.create(content=txt, is_correct=(i == correct_idx)) for i, txt in enumerate(options_text)]
        if self.editing_question_id:
            return Question(id=self.editing_question_id, topic_id=topic_id, content=content, difficulty=diff_level, options=opts)
        return Question.create(topic_id=topic_id, content=content, difficulty=diff_level, options=opts)

    def clear(self):
        self.editing_question_id = None
        self.txt_content.delete("1.0", tk.END)
        self.cbo_diff.current(0)
        self.correct_var.set(0)
        for entry in self.option_entries:
            entry.delete(0, tk.END)
`
  },
  {
    path: 'gui/question_tab.py',
    name: 'gui/question_tab.py',
    description: 'Giao diện Quản lý ngân hàng câu hỏi (Treeview, tìm kiếm đa tiêu chí, CRUD, Nhập file/API)',
    author: 'Thành viên B',
    category: 'gui',
    code: `"""gui/question_tab.py
===================
[B sở hữu] Tab Quản lý ngân hàng câu hỏi:
- Treeview câu hỏi (Mã, Môn, Chủ đề, Mức độ, Nội dung, Đáp án đúng).
- Tìm kiếm kết hợp đa tiêu chí: Từ khóa, Môn học, Chủ đề, Mức độ.
- CRUD câu hỏi có xác nhận; bắt lỗi ràng buộc câu hỏi đã nằm trong đề.
- Nhập từ file mẫu .txt và Web API OpenTDB.
"""
# Xem mã nguồn hoàn chỉnh tại file /python_project/gui/question_tab.py
`
  },
  {
    path: 'gui/subject_topic_tab.py',
    name: 'gui/subject_topic_tab.py',
    description: 'Giao diện Quản lý Môn học và Chủ đề (2 Treeview, CRUD, ràng buộc cha-con)',
    author: 'Thành viên B',
    category: 'gui',
    code: `"""gui/subject_topic_tab.py
========================
[B sở hữu] Tab Quản lý Môn học và Chủ đề:
- 2 Bảng Treeview: Môn học và Chủ đề con.
- Đầy đủ CRUD Môn học và Chủ đề.
- Ràng buộc cha-con: Không thể xóa môn còn chủ đề hoặc chủ đề còn câu hỏi.
"""
# Xem mã nguồn hoàn chỉnh tại file /python_project/gui/subject_topic_tab.py
`
  },
  {
    path: 'tests/test_validators.py',
    name: 'test_validators.py',
    description: 'Bộ 30 test case kiểm thử Regex username, email, question ID, date, number và question structure',
    author: 'Thành viên B',
    category: 'test',
    code: `# Xem toàn bộ 30 test case trong /python_project/tests/test_validators.py`
  },
  {
    path: 'tests/test_auth.py',
    name: 'test_auth.py',
    description: 'Bộ 13 test case kiểm thử đăng ký, đăng nhập, đổi mật khẩu, băm có salt và phân quyền',
    author: 'Thành viên B',
    category: 'test',
    code: `# Xem toàn bộ 13 test case trong /python_project/tests/test_auth.py`
  },
  {
    path: 'tests/test_import.py',
    name: 'test_import.py',
    description: 'Bộ 9 test case kiểm thử nhập câu hỏi từ file thiếu, file rỗng, dòng sai định dạng, câu hỏi trùng',
    author: 'Thành viên B',
    category: 'test',
    code: `# Xem toàn bộ 9 test case trong /python_project/tests/test_import.py`
  },
  {
    path: 'data/sample/mau_cau_hoi.txt',
    name: 'mau_cau_hoi.txt',
    description: 'File mẫu câu hỏi trắc nghiệm định dạng chuẩn pipe-delimited cho hệ thống',
    author: 'Thành viên B',
    category: 'sample',
    code: `# FILE MẪU CÂU HỎI TRẮC NGHIỆM (mau_cau_hoi.txt)
# Định dạng: topic_id|Nội dung câu hỏi|Mức độ (de/kho)|Phương án A|Phương án B|Phương án C|Phương án D|Đáp án đúng (A/B/C/D)

topic_01|Từ khóa nào dùng để định nghĩa hàm trong Python?|de|def|function|fun|define|A
topic_01|Cấu trúc dữ liệu nào trong Python là bất biến (immutable)?|de|list|tuple|dict|set|B
topic_01|Toán tử nào dùng để tính lũy thừa trong Python?|de|^|**|pow|exp|B
topic_01|Phương thức nào dùng để thêm một phần tử vào cuối danh sách (list)?|de|insert|push|append|extend|C
topic_01|Kết quả của biểu thức bool([]) trong Python là gì?|de|True|False|None|Lỗi TypeError|B
topic_02|Độ phức tạp thời gian trung bình khi tìm kiếm trong dict là gì?|kho|O(1)|O(n)|O(log n)|O(n log n)|A
topic_02|Decorators trong Python hoạt động dựa trên cơ chế nào?|kho|Higher-order functions|Multiple inheritance|Metaclass|Garbage collection|A
topic_02|Biểu thức generator khác list comprehension ở điểm mấu chốt nào?|kho|Dùng ít bộ nhớ hơn nhờ tính toán lazy|Luôn chạy nhanh hơn|Có thể lập chỉ mục index|Cho phép thay đổi kích thước|A
`
  }
];
