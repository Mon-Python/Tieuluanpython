"""
test_exam_generator.py  [C]
Chạy: python -m unittest tests/test_exam_generator.py -v
      hoặc pytest tests/test_exam_generator.py -v

Kiểm thử sinh đề: đủ/thiếu câu, ma trận rỗng, số câu = 0 hoặc âm,
cùng seed → cùng đề, khác seed → đề khác, tái lập đề.
Dùng thư mục tạm riêng, không đụng dữ liệu thật.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import (
    Subject, Topic, Question, Option, DifficultyLevel, ExamMatrixItem,
)
from data_repository import JsonDataRepository
from json_file_handler import JsonFileHandler
from exam_generator import ExamGeneratorImpl


class TestExamGenerator(unittest.TestCase):
    """Bộ kiểm thử cho ExamGeneratorImpl (≥ 10 trường hợp)."""

    # ============================================================
    # Dựng dữ liệu mẫu
    # ============================================================

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        handler = JsonFileHandler(backup_dir=self.tmp / "backup")
        self.repo = JsonDataRepository(
            subjects_topics_path=self.tmp / "st.json",
            questions_path=self.tmp / "q.json",
            handler=handler,
        )
        self.gen = ExamGeneratorImpl(self.repo)

        # Tạo 1 môn, 2 chủ đề
        self.subj = Subject.create("Lập trình Python")
        self.topic_loop = Topic.create(self.subj.id, "Vòng lặp")
        self.topic_func = Topic.create(self.subj.id, "Hàm")

        # Cần thêm to_dict cho Subject/Topic/Question trước khi dùng repo
        # (repo gọi .to_dict()). Nếu chưa có → test sẽ báo lỗi rõ ràng.
        self._add_subject(self.subj)
        self._add_topic(self.topic_loop)
        self._add_topic(self.topic_func)

        # Tạo câu hỏi: 5 câu dễ + 3 câu khó cho Vòng lặp,
        #               4 câu dễ + 2 câu khó cho Hàm
        self.q_loop_easy = self._make_questions(
            self.topic_loop.id, DifficultyLevel.DE, 5
        )
        self.q_loop_hard = self._make_questions(
            self.topic_loop.id, DifficultyLevel.KHO, 3
        )
        self.q_func_easy = self._make_questions(
            self.topic_func.id, DifficultyLevel.DE, 4
        )
        self.q_func_hard = self._make_questions(
            self.topic_func.id, DifficultyLevel.KHO, 2
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- helpers ---

    def _add_subject(self, s: Subject):
        self.repo.add_subject(s)

    def _add_topic(self, t: Topic):
        self.repo.add_topic(t)

    def _make_questions(self, topic_id, difficulty, count):
        questions = []
        for i in range(count):
            opts = [
                Option.create(f"Đáp án đúng {i}", True),
                Option.create(f"Sai A {i}", False),
                Option.create(f"Sai B {i}", False),
                Option.create(f"Sai C {i}", False),
            ]
            q = Question.create(topic_id, f"Câu hỏi {difficulty.value} {i}",
                                difficulty, opts)
            self.repo.add_question(q)
            questions.append(q)
        return questions

    def _simple_matrix(self, topic_id, difficulty, num):
        return [ExamMatrixItem(topic_id=topic_id,
                               difficulty=difficulty,
                               num_questions=num)]

    # ============================================================
    # 1. Sinh đề thành công (đủ câu)
    # ============================================================

    def test_generate_exam_basic(self):
        """Sinh đề với 1 dòng ma trận, đủ câu → thành công."""
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 3)
        exam = self.gen.generate_exam(self.subj.id, "Đề kiểm tra 1",
                                      matrix, seed=42)
        self.assertEqual(len(exam.question_ids), 3)
        self.assertEqual(len(exam.shuffled_options), 3)
        self.assertEqual(exam.seed, 42)
        self.assertEqual(exam.subject_id, self.subj.id)
        self.assertEqual(len(exam.matrix), 1)

    # ============================================================
    # 2. Ma trận nhiều dòng
    # ============================================================

    def test_generate_exam_multi_matrix(self):
        """Ma trận 2 chủ đề, 2 mức độ → tổng câu đúng."""
        matrix = [
            ExamMatrixItem(self.topic_loop.id, DifficultyLevel.DE, 2),
            ExamMatrixItem(self.topic_loop.id, DifficultyLevel.KHO, 1),
            ExamMatrixItem(self.topic_func.id, DifficultyLevel.DE, 3),
        ]
        exam = self.gen.generate_exam(self.subj.id, "Đề đa chủ đề",
                                      matrix, seed=99)
        self.assertEqual(len(exam.question_ids), 6)

    # ============================================================
    # 3. Ma trận rỗng → ValueError
    # ============================================================

    def test_empty_matrix_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.gen.generate_exam(self.subj.id, "Đề rỗng", [], seed=1)
        self.assertIn("rỗng", str(ctx.exception))

    # ============================================================
    # 4. Số câu = 0 → ValueError
    # ============================================================

    def test_zero_questions_raises(self):
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 0)
        with self.assertRaises(ValueError):
            self.gen.generate_exam(self.subj.id, "Đề 0 câu", matrix, seed=1)

    # ============================================================
    # 5. Số câu âm → ValueError
    # ============================================================

    def test_negative_questions_raises(self):
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, -2)
        with self.assertRaises(ValueError):
            self.gen.generate_exam(self.subj.id, "Đề âm", matrix, seed=1)

    # ============================================================
    # 6. Không đủ câu hỏi → ValueError
    # ============================================================

    def test_not_enough_questions_raises(self):
        """Yêu cầu 10 câu dễ Vòng lặp nhưng chỉ có 5."""
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 10)
        with self.assertRaises(ValueError) as ctx:
            self.gen.generate_exam(self.subj.id, "Đề thiếu", matrix, seed=1)
        self.assertIn("Không đủ", str(ctx.exception))

    # ============================================================
    # 7. Cùng seed → cùng đề (question_ids và shuffled_options giống nhau)
    # ============================================================

    def test_same_seed_same_exam(self):
        matrix = [
            ExamMatrixItem(self.topic_loop.id, DifficultyLevel.DE, 3),
            ExamMatrixItem(self.topic_func.id, DifficultyLevel.DE, 2),
        ]
        exam_a = self.gen.generate_exam(self.subj.id, "A", matrix, seed=123)
        exam_b = self.gen.generate_exam(self.subj.id, "B", matrix, seed=123)
        self.assertEqual(exam_a.question_ids, exam_b.question_ids)
        self.assertEqual(exam_a.shuffled_options, exam_b.shuffled_options)

    # ============================================================
    # 8. Khác seed → đề khác (rất khó trùng)
    # ============================================================

    def test_different_seed_different_exam(self):
        matrix = [
            ExamMatrixItem(self.topic_loop.id, DifficultyLevel.DE, 4),
            ExamMatrixItem(self.topic_func.id, DifficultyLevel.DE, 3),
        ]
        exam_a = self.gen.generate_exam(self.subj.id, "A", matrix, seed=1)
        exam_b = self.gen.generate_exam(self.subj.id, "B", matrix, seed=9999)
        # Ít nhất thứ tự câu hoặc phương án phải khác
        differs = (exam_a.question_ids != exam_b.question_ids
                   or exam_a.shuffled_options != exam_b.shuffled_options)
        self.assertTrue(differs)

    # ============================================================
    # 9. Mỗi câu có đủ 4 option_ids trong shuffled_options
    # ============================================================

    def test_shuffled_options_have_4_ids(self):
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 3)
        exam = self.gen.generate_exam(self.subj.id, "Đề", matrix, seed=7)
        for qid, opt_ids in exam.shuffled_options.items():
            self.assertEqual(len(opt_ids), 4,
                             f"Câu {qid} không đủ 4 phương án trong shuffled_options")

    # ============================================================
    # 10. Không có câu trùng trong đề
    # ============================================================

    def test_no_duplicate_questions(self):
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 5)
        exam = self.gen.generate_exam(self.subj.id, "Đề", matrix, seed=55)
        self.assertEqual(len(exam.question_ids), len(set(exam.question_ids)))

    # ============================================================
    # 11. Tái lập đề (rebuild_exam) cho kết quả y hệt
    # ============================================================

    def test_rebuild_exam_matches_original(self):
        matrix = [
            ExamMatrixItem(self.topic_loop.id, DifficultyLevel.DE, 3),
            ExamMatrixItem(self.topic_func.id, DifficultyLevel.KHO, 2),
        ]
        original = self.gen.generate_exam(self.subj.id, "Gốc", matrix, seed=42)
        rebuilt = self.gen.rebuild_exam(original)
        self.assertEqual(rebuilt.question_ids, original.question_ids)
        self.assertEqual(rebuilt.shuffled_options, original.shuffled_options)
        # Giữ id và created_at gốc
        self.assertEqual(rebuilt.id, original.id)
        self.assertEqual(rebuilt.created_at, original.created_at)

    # ============================================================
    # 12. Tái lập đề khi matrix rỗng → ValueError
    # ============================================================

    def test_rebuild_exam_without_matrix_raises(self):
        from base_models import Exam
        exam = Exam.create(self.subj.id, "Đề trống", seed=1, matrix=[])
        with self.assertRaises(ValueError) as ctx:
            self.gen.rebuild_exam(exam)
        self.assertIn("ma trận", str(ctx.exception).lower())

    # ============================================================
    # 13. Exam có đúng title và subject_id
    # ============================================================

    def test_exam_metadata(self):
        matrix = self._simple_matrix(self.topic_loop.id, DifficultyLevel.DE, 1)
        exam = self.gen.generate_exam(self.subj.id, "Kiểm tra 15 phút",
                                      matrix, seed=0)
        self.assertEqual(exam.title, "Kiểm tra 15 phút")
        self.assertEqual(exam.subject_id, self.subj.id)
        self.assertTrue(exam.id.startswith("exam_"))


if __name__ == "__main__":
    unittest.main()
