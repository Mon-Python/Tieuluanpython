"""test_validators.py
===================
[B] Kiểm thử toàn diện các hàm kiểm tra dữ liệu trong validators.py:
- Regex Username (hợp lệ, quá ngắn, quá dài, ký tự đặc biệt, bắt đầu bằng số)
- Regex Email (hợp lệ, thiếu @, thiếu domain, sai định dạng, khoảng trắng)
- Regex Question ID (mẫu chuẩn q_ + 8 ký tự hex, sai tiền tố, sai độ dài, ký tự không phải hex)
- Regex Date (ISO YYYY-MM-DD, VN DD/MM/YYYY, ngày không có trong lịch, năm ngoài biên)
- Non-negative number (số 0, số dương, số âm, chuỗi không phải số)
- Question validation & Question data (hợp lệ, rỗng, thiếu/thừa phương án, trùng phương án, không có đáp án đúng, nhiều đáp án đúng)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import Question, Option, DifficultyLevel
from validators import (
    validate_username,
    validate_email,
    validate_question_id,
    validate_date_string,
    validate_non_negative_number,
    validate_question,
    validate_question_data,
)


class TestValidators(unittest.TestCase):

    # ============================================================
    # 1. USERNAME VALIDATION (Regex)
    # ============================================================
    def test_username_valid(self):
        valid_cases = ["admin", "user_01", "teacher_python", "nv_2026", "A_long_name_19"]
        for u in valid_cases:
            ok, msg = validate_username(u)
            self.assertTrue(ok, f"Username '{u}' phải hợp lệ nhưng nhận: {msg}")

    def test_username_empty(self):
        ok, msg = validate_username("")
        self.assertFalse(ok)
        self.assertIn("không được để trống", msg)

    def test_username_too_short(self):
        ok, msg = validate_username("ab")
        self.assertFalse(ok)
        self.assertIn("quá ngắn", msg)

    def test_username_too_long(self):
        ok, msg = validate_username("a" * 21)
        self.assertFalse(ok)
        self.assertIn("quá dài", msg)

    def test_username_starts_with_digit(self):
        ok, msg = validate_username("1user")
        self.assertFalse(ok)
        self.assertIn("không được bắt đầu bằng chữ số", msg)

    def test_username_special_characters(self):
        for bad in ["user@123", "user space", "user-name", "user.name", "user#1"]:
            ok, msg = validate_username(bad)
            self.assertFalse(ok, f"'{bad}' không được hợp lệ")
            self.assertIn("chỉ được chứa", msg)

    # ============================================================
    # 2. EMAIL VALIDATION (Regex)
    # ============================================================
    def test_email_valid(self):
        valid_emails = [
            "admin@school.edu.vn",
            "teacher.python@gmail.com",
            "user_test+1@domain.org",
            "simple@example.com"
        ]
        for e in valid_emails:
            ok, msg = validate_email(e)
            self.assertTrue(ok, f"Email '{e}' phải hợp lệ nhưng nhận: {msg}")

    def test_email_empty(self):
        ok, msg = validate_email("")
        self.assertFalse(ok)
        self.assertIn("không được để trống", msg)

    def test_email_missing_at(self):
        ok, msg = validate_email("usernamedomain.com")
        self.assertFalse(ok)
        self.assertIn("thiếu ký tự '@'", msg)

    def test_email_missing_domain_extension(self):
        ok, msg = validate_email("user@localhost")
        self.assertFalse(ok)
        self.assertIn("tên miền", msg)

    def test_email_with_spaces(self):
        ok, msg = validate_email("user name@example.com")
        self.assertFalse(ok)
        self.assertIn("không đúng định dạng", msg)

    # ============================================================
    # 3. QUESTION ID VALIDATION (Regex)
    # ============================================================
    def test_question_id_valid(self):
        valid_ids = ["q_a1b2c3d4", "q_00000000", "q_abcdef12", "q_8f9e0a1b"]
        for qid in valid_ids:
            ok, msg = validate_question_id(qid)
            self.assertTrue(ok, f"ID '{qid}' phải hợp lệ nhưng nhận: {msg}")

    def test_question_id_wrong_prefix(self):
        ok, msg = validate_question_id("question_12345678")
        self.assertFalse(ok)
        self.assertIn("không hợp lệ", msg)

    def test_question_id_wrong_length(self):
        ok, msg = validate_question_id("q_1234567")  # 7 hex chars
        self.assertFalse(ok)
        ok2, msg2 = validate_question_id("q_123456789")  # 9 hex chars
        self.assertFalse(ok2)

    def test_question_id_non_hex(self):
        ok, msg = validate_question_id("q_1234567g")  # 'g' is not hex
        self.assertFalse(ok)

    # ============================================================
    # 4. DATE VALIDATION
    # ============================================================
    def test_date_valid_iso(self):
        ok, msg = validate_date_string("2026-10-21")
        self.assertTrue(ok, msg)

    def test_date_valid_vn(self):
        ok, msg = validate_date_string("21/10/2026")
        self.assertTrue(ok, msg)

    def test_date_invalid_calendar_day(self):
        # 31/02 does not exist
        ok, msg = validate_date_string("2026-02-31")
        self.assertFalse(ok)
        self.assertIn("không tồn tại", msg)

    def test_date_invalid_format(self):
        ok, msg = validate_date_string("21-10-2026")
        self.assertFalse(ok)
        self.assertIn("không đúng", msg)

    # ============================================================
    # 5. NON-NEGATIVE NUMBER VALIDATION
    # ============================================================
    def test_non_negative_number_valid(self):
        self.assertTrue(validate_non_negative_number(0)[0])
        self.assertTrue(validate_non_negative_number(10)[0])
        self.assertTrue(validate_non_negative_number(3.14)[0])
        self.assertTrue(validate_non_negative_number("100")[0])

    def test_non_negative_number_negative(self):
        ok, msg = validate_non_negative_number(-5, "Số câu hỏi")
        self.assertFalse(ok)
        self.assertIn("không được là số âm", msg)

    def test_non_negative_number_invalid_str(self):
        ok, msg = validate_non_negative_number("abc")
        self.assertFalse(ok)
        self.assertIn("phải là một số hợp lệ", msg)

    # ============================================================
    # 6. QUESTION AND OPTION VALIDATION
    # ============================================================
    def test_question_valid(self):
        opts = [
            Option.create("Python là ngôn ngữ thông dịch", True),
            Option.create("Python là ngôn ngữ biên dịch thuần túy", False),
            Option.create("Python chỉ chạy trên Windows", False),
            Option.create("Python không có thư viện mở", False),
        ]
        q = Question.create("topic_123", "Python là gì?", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertTrue(ok, msg)

    def test_question_missing_topic(self):
        opts = [Option.create(f"Opt {i}", i == 0) for i in range(4)]
        q = Question.create("", "Nội dung câu hỏi", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("chủ đề", msg)

    def test_question_empty_content(self):
        opts = [Option.create(f"Opt {i}", i == 0) for i in range(4)]
        q = Question.create("topic_1", "   ", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("không được rỗng", msg)

    def test_question_not_4_options(self):
        opts = [Option.create(f"Opt {i}", i == 0) for i in range(3)]
        q = Question.create("topic_1", "Câu hỏi?", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("đúng 4 phương án", msg)

    def test_question_duplicate_options(self):
        opts = [
            Option.create("Giống nhau", True),
            Option.create("giống nhau", False),  # duplicate case-insensitive
            Option.create("Khác C", False),
            Option.create("Khác D", False),
        ]
        q = Question.create("topic_1", "Câu hỏi?", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("trùng nội dung", msg)

    def test_question_no_correct_option(self):
        opts = [Option.create(f"Opt {i}", False) for i in range(4)]
        q = Question.create("topic_1", "Câu hỏi?", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("ít nhất 1 đáp án đúng", msg)

    def test_question_multiple_correct_options(self):
        opts = [Option.create(f"Opt {i}", i < 2) for i in range(4)]
        q = Question.create("topic_1", "Câu hỏi?", DifficultyLevel.DE, opts)
        ok, msg = validate_question(q)
        self.assertFalse(ok)
        self.assertIn("đúng 1 đáp án đúng", msg)

    def test_validate_question_data_helper(self):
        ok, msg = validate_question_data(
            content="Thủ đô của Việt Nam là gì?",
            options=["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng"],
            correct_index=0,
            difficulty="de"
        )
        self.assertTrue(ok, msg)


if __name__ == "__main__":
    unittest.main()
