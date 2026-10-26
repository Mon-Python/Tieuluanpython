"""test_import.py
==============
[B] Kiểm thử nhập câu hỏi từ file mẫu trong import_questions.py:
- File không tồn tại -> báo lỗi rõ ràng, không crash
- File rỗng -> báo lỗi file rỗng
- File chỉ chứa chú thích (#) và dòng trống
- Dòng sai số lượng trường (ít hơn 7 trường, nhiều hơn 8 trường)
- Dòng sai mức độ (không phải de/kho)
- Dòng phương án để trống
- Dòng phương án bị trùng lặp
- Dòng đáp án đúng không phải A, B, C, D
- File hỗn hợp: vừa có dòng đúng vừa có dòng sai (dòng đúng được lưu, dòng sai được báo cáo chi tiết)
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import Subject, Topic
from data_repository import JsonDataRepository
from import_questions import import_questions_from_file, parse_question_line


class TestImportQuestions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.st_path = self.temp_dir / "subjects_topics.json"
        self.q_path = self.temp_dir / "questions.json"
        self.repo = JsonDataRepository(self.st_path, self.q_path)

        # Tạo sẵn môn và chủ đề hợp lệ trong repo
        self.subject = Subject.create("Lập trình Python")
        self.repo.add_subject(self.subject)
        self.topic = Topic.create(self.subject.id, "Cú pháp cơ bản")
        self.repo.add_topic(self.topic)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_import_nonexistent_file(self):
        missing = self.temp_dir / "khong_ton_tai.txt"
        count, errors = import_questions_from_file(missing, self.repo)
        self.assertEqual(count, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("Không tìm thấy file", errors[0])

    def test_import_empty_file(self):
        empty_file = self.temp_dir / "rong.txt"
        empty_file.write_text("", encoding="utf-8")
        count, errors = import_questions_from_file(empty_file, self.repo)
        self.assertEqual(count, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("rỗng hoặc không chứa dữ liệu", errors[0])

    def test_import_only_comments_and_blank_lines(self):
        f = self.temp_dir / "comments.txt"
        f.write_text("# Day la chu thich\n\n# Chu thich khac\n  \n", encoding="utf-8")
        count, errors = import_questions_from_file(f, self.repo)
        self.assertEqual(count, 0)
        self.assertIn("rỗng hoặc không chứa dữ liệu", errors[0])

    def test_parse_line_wrong_fields_count(self):
        q, err = parse_question_line("Cau hoi thieu truong|de|A|B", 1)
        self.assertIsNone(q)
        self.assertIn("Sai định dạng", err)

    def test_parse_line_invalid_difficulty(self):
        line = f"{self.topic.id}|Cau hoi?|trung_binh|A|B|C|D|A"
        q, err = parse_question_line(line, 2)
        self.assertIsNone(q)
        self.assertIn("Mức độ", err)

    def test_parse_line_duplicate_options(self):
        line = f"{self.topic.id}|Cau hoi?|de|Phuong an A|phuong an a|C|D|A"
        q, err = parse_question_line(line, 3)
        self.assertIsNone(q)
        self.assertIn("trùng lặp nội dung", err)

    def test_parse_line_invalid_correct_answer(self):
        line = f"{self.topic.id}|Cau hoi?|de|A|B|C|D|E"
        q, err = parse_question_line(line, 4)
        self.assertIsNone(q)
        self.assertIn("Đáp án đúng", err)

    def test_import_mixed_valid_and_invalid_lines(self):
        sample_content = (
            f"# File kiem thu\n"
            f"{self.topic.id}|Cau 1 hop le|de|A1|B1|C1|D1|A\n"
            f"{self.topic.id}|Cau 2 sai dap an|de|A2|B2|C2|D2|X\n"
            f"{self.topic.id}|Cau 3 hop le|kho|A3|B3|C3|D3|B\n"
            f"Dong nay thieu truong hoan toan\n"
            f"{self.topic.id}|Cau 5 trung phuong an|de|Giong|giong|C|D|A\n"
        )
        sample_file = self.temp_dir / "sample_mixed.txt"
        sample_file.write_text(sample_content, encoding="utf-8")

        added, errors = import_questions_from_file(sample_file, self.repo)
        self.assertEqual(added, 2, "2 câu hợp lệ phải được thêm vào ngân hàng")
        self.assertEqual(len(errors), 3, "3 dòng sai phải được ghi nhận lỗi")
        self.assertEqual(len(self.repo.list_questions()), 2)

    def test_import_with_default_topic_id(self):
        # Định dạng 7 trường không có topic_id ở đầu
        content = "Tu khoa ham la gi?|de|def|fun|function|defun|A\n"
        f = self.temp_dir / "seven_fields.txt"
        f.write_text(content, encoding="utf-8")

        added, errors = import_questions_from_file(f, self.repo, default_topic_id=self.topic.id)
        self.assertEqual(added, 1)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.repo.list_questions()), 1)


if __name__ == "__main__":
    unittest.main()
