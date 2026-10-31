"""Unit tests for ExamRepository using isolated temporary JSON files."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from base_models import Exam, ExamResult
from exam_repository import ExamRepository
from json_file_handler import JsonFileHandler


class TestExamRepository(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.exams_path = self.tmp_path / "exams.json"
        self.results_path = self.tmp_path / "results.json"
        self.handler = JsonFileHandler(backup_dir=self.tmp_path / "backup")
        self.repo = ExamRepository(
            exams_path=self.exams_path,
            results_path=self.results_path,
            handler=self.handler,
        )

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def make_exam(exam_id="exam_1", title="Đề Python", question_ids=None):
        return Exam(
            id=exam_id,
            subject_id="subject_1",
            title=title,
            seed=123,
            question_ids=question_ids if question_ids is not None else ["question_1"],
            shuffled_options={"question_1": ["option_1", "option_2"]},
            matrix=[],
        )

    @staticmethod
    def make_result(result_id="result_1", exam_id="exam_1", score=8.5):
        return ExamResult(
            id=result_id,
            exam_id=exam_id,
            student_name="Nguyen Van A",
            score=score,
            topic_stats={"topic_1": {"correct": 3, "total": 4, "percent": 75.0}},
        )

    def test_list_exams_returns_empty_list_when_no_data(self):
        self.assertEqual(self.repo.list_exams(), [])

    def test_save_exam_adds_new_exam(self):
        exam = self.make_exam()

        self.repo.save_exam(exam)

        self.assertEqual(self.repo.list_exams(), [exam])

    def test_save_exam_updates_exam_with_same_id(self):
        self.repo.save_exam(self.make_exam(title="Tên cũ"))
        updated_exam = self.make_exam(title="Tên mới", question_ids=["question_2"])

        self.repo.save_exam(updated_exam)

        exams = self.repo.list_exams()
        self.assertEqual(len(exams), 1)
        self.assertEqual(exams[0].id, updated_exam.id)
        self.assertEqual(exams[0].title, "Tên mới")
        self.assertEqual(exams[0].question_ids, ["question_2"])

    def test_get_exam_returns_matching_exam_or_none(self):
        exam = self.make_exam()
        self.repo.save_exam(exam)

        self.assertEqual(self.repo.get_exam(exam.id), exam)
        self.assertIsNone(self.repo.get_exam("exam_missing"))

    def test_list_results_returns_empty_list_when_no_data(self):
        self.assertEqual(self.repo.list_results(), [])

    def test_save_result_adds_new_result(self):
        result = self.make_result()

        self.repo.save_result(result)

        self.assertEqual(self.repo.list_results(), [result])

    def test_save_result_updates_result_with_same_id(self):
        self.repo.save_result(self.make_result(score=6.0))
        updated_result = self.make_result(score=9.0)

        self.repo.save_result(updated_result)

        results = self.repo.list_results()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, updated_result.id)
        self.assertEqual(results[0].score, 9.0)

    def test_list_results_by_exam_filters_results(self):
        first = self.make_result(result_id="result_1", exam_id="exam_1")
        second = self.make_result(result_id="result_2", exam_id="exam_2")
        third = self.make_result(result_id="result_3", exam_id="exam_1")
        for result in (first, second, third):
            self.repo.save_result(result)

        self.assertEqual(
            self.repo.list_results_by_exam("exam_1"),
            [first, third],
        )

    def test_is_question_used_checks_saved_exams(self):
        self.repo.save_exam(self.make_exam(question_ids=["question_used"]))

        self.assertTrue(self.repo.is_question_used("question_used"))
        self.assertFalse(self.repo.is_question_used("question_unused"))

    def test_load_rows_raises_value_error_when_json_is_not_a_list(self):
        self.handler.write(self.exams_path, {"id": "exam_1"})

        with self.assertRaisesRegex(ValueError, "phải là danh sách"):
            self.repo._load_rows(self.exams_path)


if __name__ == "__main__":
    unittest.main()
    