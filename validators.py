"""validators.py
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
REGEX_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$")

# Mã câu hỏi hệ thống sinh: tiền tố q_ kèm đúng 8 ký tự thập lục phân (hex)
REGEX_QUESTION_ID = re.compile(r"^q_[0-9a-fA-F]{8}$")

# Mã thực thể tổng quát: <prefix>_<8 ký tự hex>
REGEX_ENTITY_ID = re.compile(r"^[a-zA-Z]{1,10}_[0-9a-fA-F]{8}$")

# Ngày tháng: hỗ trợ định dạng ISO YYYY-MM-DD hoặc chuẩn VN DD/MM/YYYY
REGEX_DATE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REGEX_DATE_VN = re.compile(r"^\d{2}/\d{2}/\d{4}$")


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
    - Mẫu chuẩn: q_ + 8 ký tự hex (ví dụ: q_3f8c3123).
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
