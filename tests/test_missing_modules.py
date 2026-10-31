import json
import tempfile
import unittest
from pathlib import Path

from auth import AuthManager
from base_models import (
    DifficultyLevel,
    Exam,
    ExamResult,
    Option,
    Question,
    Subject,
    Topic,
)
from data_repository import JsonDataRepository
from exam_exporter import ExamExporterImpl
from exam_repository import ExamRepository
from gui.bar_chart import BarChart
from gui.stats_tab import StatsTab
from json_file_handler import JsonFileHandler
from sample_data import initialize_sample_data


class ExamExporterTests(unittest.TestCase):
    def test_exports_question_paper_and_answer_key_as_json(self):
        question = Question.create(
            "topic_1",
            "Which option is correct?",
            DifficultyLevel.DE,
            [
                Option.create("First", False),
                Option.create("Second", True),
            ],
        )
        exam = Exam.create("subject_1", "Sample exam", 10)
        exam.question_ids = [question.id]
        exam.shuffled_options = {
            question.id: [question.options[1].id, question.options[0].id]
        }

        with tempfile.TemporaryDirectory() as directory:
            paper_path = Path(directory) / "paper.json"
            key_path = Path(directory) / "key.json"
            exporter = ExamExporterImpl()
            exporter.export_exam(exam, [question], str(paper_path))
            exporter.export_answer_key(exam, [question], str(key_path))

            paper = json.loads(paper_path.read_text(encoding="utf-8"))
            key = json.loads(key_path.read_text(encoding="utf-8"))

        self.assertEqual(paper["exam"]["id"], exam.id)
        paper_question = paper["questions"][0]
        self.assertEqual(paper_question["id"], question.id)
        self.assertEqual(
            [option["id"] for option in paper_question["options"]],
            exam.shuffled_options[question.id],
        )
        self.assertTrue(all("is_correct" not in o for o in paper_question["options"]))
        self.assertEqual(
            key["answers"][0]["correct_option_ids"], question.correct_option_ids()
        )


class SampleDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.subjects_path = self.directory / "subjects_topics.json"
        self.questions_path = self.directory / "questions.json"
        self.users_path = self.directory / "users.json"
        self.handler = JsonFileHandler(self.directory / "backup")
        self.repository = JsonDataRepository(
            self.subjects_path, self.questions_path, handler=self.handler
        )
        self.auth_manager = AuthManager(self.users_path, self.handler)

    def tearDown(self):
        self.temp.cleanup()

    def test_initializes_missing_data_and_default_admin_idempotently(self):
        initialize_sample_data(self.repository, self.auth_manager)
        subjects = self.repository.list_subjects()
        topics = self.repository.list_topics()
        questions = self.repository.list_questions()
        admin = self.auth_manager.login("admin", "admin123")

        self.assertTrue(subjects)
        self.assertTrue(topics)
        self.assertTrue(questions)
        self.assertTrue(admin.is_admin)

        counts = (len(subjects), len(topics), len(questions))
        initialize_sample_data(self.repository, self.auth_manager)
        self.assertEqual(
            counts,
            (
                len(self.repository.list_subjects()),
                len(self.repository.list_topics()),
                len(self.repository.list_questions()),
            ),
        )

    def test_preserves_existing_subject_question_and_admin_data(self):
        subject = Subject.create("Existing subject")
        topic = Topic.create(subject.id, "Existing topic")
        question = Question.create(
            topic.id,
            "Existing question",
            DifficultyLevel.DE,
            [
                Option.create("Existing answer", True),
                Option.create("Wrong answer 1"),
                Option.create("Wrong answer 2"),
                Option.create("Wrong answer 3"),
            ],
        )
        self.repository.add_subject(subject)
        self.repository.add_topic(topic)
        self.repository.add_question(question)
        user = self.auth_manager.register(
            "admin", "custom-password", role="admin"
        )
        before_subjects = self.subjects_path.read_text(encoding="utf-8")
        before_questions = self.questions_path.read_text(encoding="utf-8")
        before_users = self.users_path.read_text(encoding="utf-8")

        initialize_sample_data(self.repository, self.auth_manager)

        self.assertEqual(before_subjects, self.subjects_path.read_text(encoding="utf-8"))
        self.assertEqual(before_questions, self.questions_path.read_text(encoding="utf-8"))
        self.assertEqual(before_users, self.users_path.read_text(encoding="utf-8"))
        self.auth_manager.login("admin", "custom-password")


class StatsAndChartTests(unittest.TestCase):
    def test_stats_visibility_separates_admin_and_regular_user(self):
        results = [
            ExamResult.create("exam_1", "alice"),
            ExamResult.create("exam_1", "bob"),
        ]
        admin = type("AdminUser", (), {"is_admin": True, "username": "admin"})()
        user = type("RegularUser", (), {"is_admin": False, "username": "alice"})()

        self.assertEqual(StatsTab.visible_results(results, admin), results)
        self.assertEqual(StatsTab.visible_results(results, user), [results[0]])

    def test_chart_scales_percentages_to_canvas_height(self):
        bars = BarChart.scaled_bars({"Loops": 50, "Lists": 100}, 100)

        self.assertEqual(bars, [("Loops", 50.0), ("Lists", 100.0)])


if __name__ == "__main__":
    unittest.main()
