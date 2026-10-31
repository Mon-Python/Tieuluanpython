"""Unit tests for FileExamExporter using temporary output paths."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from base_models import DifficultyLevel, Exam, Option, Question
from exam_exporter import FileExamExporter


class TestFileExamExporter(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

        self.original_cwd = Path.cwd()
        os.chdir(self.tmp_path)
        self.addCleanup(os.chdir, self.original_cwd)

        self.export_dir = self.tmp_path / "data" / "export"
        export_dir_patch = patch("exam_exporter.EXPORT_DIR", self.export_dir)
        export_dir_patch.start()
        self.addCleanup(export_dir_patch.stop)

        self.exporter = FileExamExporter()
        self.question_one = Question(
            id="question_1",
            topic_id="topic_1",
            content="Question one?",
            difficulty=DifficultyLevel.DE,
            options=[
                Option(id="q1_a", content="Q1 choice A", is_correct=True),
                Option(id="q1_b", content="Q1 choice B", is_correct=False),
                Option(id="q1_c", content="Q1 choice C", is_correct=False),
                Option(id="q1_d", content="Q1 choice D", is_correct=False),
            ],
        )
        self.question_two = Question(
            id="question_2",
            topic_id="topic_1",
            content="Question two?",
            difficulty=DifficultyLevel.KHO,
            options=[
                Option(id="q2_a", content="Q2 choice A", is_correct=False),
                Option(id="q2_b", content="Q2 choice B", is_correct=False),
                Option(id="q2_c", content="Q2 choice C", is_correct=False),
                Option(id="q2_d", content="Q2 choice D", is_correct=True),
            ],
        )
        self.questions = [self.question_one, self.question_two]
        self.exam = Exam(
            id="exam_1",
            subject_id="subject_1",
            title="Đề kiểm tra Python",
            seed=42,
            question_ids=["question_2", "question_1"],
            shuffled_options={
                "question_1": ["q1_d", "q1_b", "q1_a", "q1_c"],
                "question_2": ["q2_b", "q2_d", "q2_c", "q2_a"],
            },
            matrix=[],
        )

    def test_export_exam_creates_file_with_question_and_shuffled_order(self):
        output_path = self.tmp_path / "exam.txt"

        self.exporter.export_exam(self.exam, self.questions, str(output_path))

        self.assertTrue(output_path.is_file())
        text = output_path.read_text(encoding="utf-8")
        self.assertIn(self.exam.title, text)
        self.assertIn("Question two?", text)
        self.assertIn("Question one?", text)
        self.assertLess(text.index("Question two?"), text.index("Question one?"))
        self.assertIn("  A. Q2 choice B", text)
        self.assertIn("  B. Q2 choice D", text)
        self.assertIn("  C. Q2 choice C", text)
        self.assertIn("  D. Q2 choice A", text)
        self.assertIn("  A. Q1 choice D", text)
        self.assertIn("  B. Q1 choice B", text)
        self.assertIn("  C. Q1 choice A", text)
        self.assertIn("  D. Q1 choice C", text)
        self.assertNotIn("Đáp án:", text)
        self.assertNotIn("ĐÁP ÁN:", text)

    def test_export_answer_key_uses_shuffled_positions_and_labels(self):
        output_path = self.tmp_path / "answer_key.txt"

        self.exporter.export_answer_key(self.exam, self.questions, str(output_path))

        self.assertTrue(output_path.is_file())
        text = output_path.read_text(encoding="utf-8")
        self.assertIn(f"ĐÁP ÁN: {self.exam.title}", text)
        self.assertIn("Câu 1: Question two?", text)
        self.assertIn("  Đáp án: B. Q2 choice D", text)
        self.assertIn("Câu 2: Question one?", text)
        self.assertIn("  Đáp án: C. Q1 choice A", text)
        self.assertLess(text.index("Câu 1:"), text.index("Câu 2:"))

    def test_export_exam_rejects_question_id_missing_from_questions(self):
        exam = Exam(
            id="exam_missing_question",
            subject_id="subject_1",
            title="Exam",
            question_ids=["question_missing"],
            shuffled_options={"question_missing": []},
        )

        with self.assertRaisesRegex(ValueError, "question_missing"):
            self.exporter.export_exam(
                exam, self.questions, str(self.tmp_path / "invalid_exam.txt")
            )

    def test_export_exam_rejects_option_id_missing_from_question(self):
        exam = Exam(
            id="exam_missing_option",
            subject_id="subject_1",
            title="Exam",
            question_ids=["question_1"],
            shuffled_options={"question_1": ["option_missing"]},
        )

        with self.assertRaisesRegex(ValueError, "option_missing"):
            self.exporter.export_exam(
                exam, self.questions, str(self.tmp_path / "invalid_option.txt")
            )

    def test_export_exam_rejects_missing_shuffled_options_entry(self):
        exam = Exam(
            id="exam_missing_shuffle",
            subject_id="subject_1",
            title="Exam",
            question_ids=["question_1"],
            shuffled_options={},
        )

        with self.assertRaisesRegex(ValueError, "không lưu thứ tự phương án"):
            self.exporter.export_exam(
                exam, self.questions, str(self.tmp_path / "missing_shuffle.txt")
            )

    def test_empty_file_path_raises_filesystem_error(self):
        with self.assertRaises(OSError):
            self.exporter.export_exam(self.exam, self.questions, "")

    def test_empty_exam_creates_file_with_title_and_no_question_lines(self):
        empty_exam = Exam(
            id="exam_empty",
            subject_id="subject_1",
            title="Empty exam",
            question_ids=[],
            shuffled_options={},
        )
        output_path = self.tmp_path / "empty_exam.txt"

        self.exporter.export_exam(empty_exam, self.questions, str(output_path))

        self.assertEqual(output_path.read_text(encoding="utf-8"), "Empty exam\n")

    def test_relative_exam_path_is_placed_in_export_dir(self):
        self.exporter.export_exam(self.exam, self.questions, "exam.txt")

        expected_path = self.export_dir / "exam.txt"
        self.assertTrue(
            expected_path.is_file(),
            f"README_NguoiD.md specifies data/export; expected {expected_path}",
        )

    def test_relative_answer_key_path_is_placed_in_export_dir(self):
        self.exporter.export_answer_key(
            self.exam, self.questions, "answer_key.txt"
        )

        expected_path = self.export_dir / "answer_key.txt"
        self.assertTrue(
            expected_path.is_file(),
            f"README_NguoiD.md specifies data/export; expected {expected_path}",
        )

    def test_relative_path_with_subdirectory_is_placed_in_export_dir(self):
        self.exporter.export_exam(
            self.exam, self.questions, str(Path("nested") / "exam.txt")
        )

        expected_path = self.export_dir / "nested" / "exam.txt"
        self.assertTrue(
            expected_path.is_file(),
            f"README_NguoiD.md specifies data/export; expected {expected_path}",
        )


if __name__ == "__main__":
    unittest.main()