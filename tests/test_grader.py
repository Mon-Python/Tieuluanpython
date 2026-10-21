"""
test_grader.py  [C]
Chạy: python -m unittest tests/test_grader.py -v
      hoặc pytest tests/test_grader.py -v

Kiểm thử chấm điểm: đúng hết, sai hết, bỏ trống, đúng một phần,
thống kê theo chủ đề, bài rỗng (tránh chia cho 0).
Dùng dữ liệu dựng tay trong bộ nhớ, không cần file JSON.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import (
    Exam, Question, Option, DifficultyLevel,
    StudentAnswer, ExamResult, ExamMatrixItem,
)
from grader import GraderImpl


class TestGrader(unittest.TestCase):
    """Bộ kiểm thử cho GraderImpl (≥ 10 trường hợp)."""

    # ============================================================
    # Dựng dữ liệu mẫu
    # ============================================================

    def setUp(self):
        self.grader = GraderImpl()

        # --- Tạo 4 câu hỏi thuộc 2 chủ đề ---
        # Chủ đề "topic_A": câu 1, 2
        self.q1 = self._make_question("q_001", "topic_A", "Câu 1?")
        self.q2 = self._make_question("q_002", "topic_A", "Câu 2?")
        # Chủ đề "topic_B": câu 3, 4
        self.q3 = self._make_question("q_003", "topic_B", "Câu 3?")
        self.q4 = self._make_question("q_004", "topic_B", "Câu 4?")

        self.all_questions = [self.q1, self.q2, self.q3, self.q4]

        # --- Tạo đề gồm 4 câu ---
        self.exam = Exam.create("subj_1", "Đề test", seed=0)
        self.exam.id = "exam_test"
        self.exam.question_ids = ["q_001", "q_002", "q_003", "q_004"]

    def _make_question(self, qid, topic_id, content):
        """Tạo câu hỏi: đáp án đúng luôn là opt_X_correct."""
        opts = [
            Option(id=f"{qid}_correct", content="Đúng", is_correct=True),
            Option(id=f"{qid}_wrong1", content="Sai 1", is_correct=False),
            Option(id=f"{qid}_wrong2", content="Sai 2", is_correct=False),
            Option(id=f"{qid}_wrong3", content="Sai 3", is_correct=False),
        ]
        return Question(id=qid, topic_id=topic_id, content=content,
                        difficulty=DifficultyLevel.DE, options=opts)

    def _answer(self, question_id, selected_id):
        """Tạo StudentAnswer nhanh."""
        ids = [selected_id] if selected_id else []
        return StudentAnswer(question_id=question_id,
                             selected_option_ids=ids)

    # ============================================================
    # 1. Đúng hết → 10 điểm
    # ============================================================

    def test_all_correct(self):
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", "q_002_correct"),
            self._answer("q_003", "q_003_correct"),
            self._answer("q_004", "q_004_correct"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 10.0)

    # ============================================================
    # 2. Sai hết → 0 điểm
    # ============================================================

    def test_all_wrong(self):
        answers = [
            self._answer("q_001", "q_001_wrong1"),
            self._answer("q_002", "q_002_wrong2"),
            self._answer("q_003", "q_003_wrong3"),
            self._answer("q_004", "q_004_wrong1"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 0.0)

    # ============================================================
    # 3. Bỏ trống hết → 0 điểm
    # ============================================================

    def test_all_blank(self):
        answers = [
            self._answer("q_001", None),
            self._answer("q_002", None),
            self._answer("q_003", None),
            self._answer("q_004", None),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 0.0)

    # ============================================================
    # 4. Không nộp đáp án nào (list rỗng) → 0 điểm
    # ============================================================

    def test_no_answers_submitted(self):
        result = self.grader.grade(self.exam, self.all_questions, [])
        self.assertEqual(result.score, 0.0)

    # ============================================================
    # 5. Đúng một phần → điểm tỉ lệ
    # ============================================================

    def test_partial_correct(self):
        """Đúng 2/4 câu → 5.0 điểm."""
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", "q_002_wrong1"),
            self._answer("q_003", "q_003_correct"),
            self._answer("q_004", "q_004_wrong2"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 5.0)

    # ============================================================
    # 6. Đúng 1/4 → 2.5 điểm
    # ============================================================

    def test_one_correct(self):
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", "q_002_wrong1"),
            self._answer("q_003", "q_003_wrong1"),
            self._answer("q_004", "q_004_wrong1"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 2.5)

    # ============================================================
    # 7. Thống kê theo chủ đề — đúng hết topic_A, sai hết topic_B
    # ============================================================

    def test_topic_statistics_split(self):
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", "q_002_correct"),
            self._answer("q_003", "q_003_wrong1"),
            self._answer("q_004", "q_004_wrong2"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        stats = self.grader.topic_statistics(result)

        self.assertEqual(stats["topic_A"]["correct"], 2)
        self.assertEqual(stats["topic_A"]["total"], 2)
        self.assertEqual(stats["topic_A"]["percent"], 100.0)

        self.assertEqual(stats["topic_B"]["correct"], 0)
        self.assertEqual(stats["topic_B"]["total"], 2)
        self.assertEqual(stats["topic_B"]["percent"], 0.0)

    # ============================================================
    # 8. Thống kê theo chủ đề — đúng một phần cả 2 topic
    # ============================================================

    def test_topic_statistics_partial(self):
        answers = [
            self._answer("q_001", "q_001_correct"),   # topic_A đúng
            self._answer("q_002", "q_002_wrong1"),     # topic_A sai
            self._answer("q_003", "q_003_correct"),    # topic_B đúng
            self._answer("q_004", "q_004_wrong1"),     # topic_B sai
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        stats = self.grader.topic_statistics(result)

        self.assertEqual(stats["topic_A"]["correct"], 1)
        self.assertEqual(stats["topic_A"]["total"], 2)
        self.assertEqual(stats["topic_A"]["percent"], 50.0)

        self.assertEqual(stats["topic_B"]["correct"], 1)
        self.assertEqual(stats["topic_B"]["total"], 2)
        self.assertEqual(stats["topic_B"]["percent"], 50.0)

    # ============================================================
    # 9. Đề rỗng (0 câu) → 0 điểm, không lỗi chia cho 0
    # ============================================================

    def test_empty_exam_no_division_by_zero(self):
        empty_exam = Exam.create("subj_1", "Đề rỗng", seed=0)
        empty_exam.question_ids = []
        result = self.grader.grade(empty_exam, [], [])
        self.assertEqual(result.score, 0.0)
        stats = self.grader.topic_statistics(result)
        self.assertEqual(stats, {})

    # ============================================================
    # 10. ExamResult chứa đúng exam_id và answers
    # ============================================================

    def test_result_metadata(self):
        answers = [self._answer("q_001", "q_001_correct")]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.exam_id, "exam_test")
        self.assertTrue(result.id.startswith("result_"))
        self.assertEqual(len(result.answers), 1)

    # ============================================================
    # 11. Bỏ trống 1 câu, đúng 3 câu còn lại → 7.5 điểm
    # ============================================================

    def test_mix_blank_and_correct(self):
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", None),               # bỏ trống
            self._answer("q_003", "q_003_correct"),
            self._answer("q_004", "q_004_correct"),
        ]
        result = self.grader.grade(self.exam, self.all_questions, answers)
        self.assertEqual(result.score, 7.5)

    # ============================================================
    # 12. topic_statistics trả dict rỗng khi result chưa có stats
    # ============================================================

    def test_topic_statistics_empty_result(self):
        result = ExamResult.create("exam_x", "Học sinh X")
        stats = self.grader.topic_statistics(result)
        self.assertEqual(stats, {})

    # ============================================================
    # 13. Câu hỏi bị thiếu trong question list → bỏ qua, không crash
    # ============================================================

    def test_missing_question_ignored(self):
        """Đề có 4 câu nhưng chỉ truyền 2 question → vẫn chấm được."""
        partial_questions = [self.q1, self.q3]
        answers = [
            self._answer("q_001", "q_001_correct"),
            self._answer("q_002", "q_002_correct"),  # q2 không có trong list
            self._answer("q_003", "q_003_wrong1"),
            self._answer("q_004", "q_004_correct"),  # q4 không có trong list
        ]
        result = self.grader.grade(self.exam, partial_questions, answers)
        # Chỉ tính 2 câu có question: q1 đúng, q3 sai → 1/4 * 10 = 2.5
        self.assertEqual(result.score, 2.5)


if __name__ == "__main__":
    unittest.main()
