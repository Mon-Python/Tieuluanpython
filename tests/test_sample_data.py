"""Tests for safe sample-data creation using isolated JSON files."""

import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from base_models import DifficultyLevel, Option, Question, Subject, Topic
from data_repository import JsonDataRepository
from json_file_handler import JsonFileHandler, JsonFileError
from sample_data import (
    initialize_sample_data,
    seed_default_admin,
    seed_sample_data,
)


class TestSampleData(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.subjects_topics_path = self.root / "subjects_topics.json"
        self.questions_path = self.root / "questions.json"
        self.handler = JsonFileHandler(backup_dir=self.root / "backup")
        self.repo = self.make_repository()

    def make_repository(self):
        return JsonDataRepository(
            subjects_topics_path=self.subjects_topics_path,
            questions_path=self.questions_path,
            handler=self.handler,
        )

    def seed(self, seed=7):
        seed_sample_data(self.repo, random.Random(seed))

    def test_missing_files_are_initialized_with_sample_data(self):
        self.seed()

        subjects = self.repo.list_subjects()
        topics = self.repo.list_topics()
        questions = self.repo.list_questions()
        self.assertTrue(self.subjects_topics_path.is_file())
        self.assertTrue(self.questions_path.is_file())
        self.assertGreaterEqual(len(subjects), 2)
        self.assertGreaterEqual(len(topics), 4)
        self.assertGreaterEqual(len(questions), 16)
        for topic in topics:
            topic_questions = [
                question
                for question in questions
                if question.topic_id == topic.id
            ]
            self.assertGreaterEqual(len(topic_questions), 4)

    def test_questions_are_valid_and_have_both_difficulties(self):
        self.seed()

        subjects_by_id = {subject.id: subject for subject in self.repo.list_subjects()}
        topics_by_id = {topic.id: topic for topic in self.repo.list_topics()}
        questions = self.repo.list_questions()

        for topic in topics_by_id.values():
            self.assertIn(topic.subject_id, subjects_by_id)
        for question in questions:
            self.assertIn(question.topic_id, topics_by_id)
            valid, message = question.is_valid()
            self.assertTrue(valid, message)
            self.assertEqual(
                sum(option.is_correct for option in question.options), 1
            )
        self.assertIn(DifficultyLevel.DE, {q.difficulty for q in questions})
        self.assertIn(DifficultyLevel.KHO, {q.difficulty for q in questions})

    def test_correct_option_positions_are_shuffled(self):
        self.seed(seed=7)

        correct_positions = {
            index
            for question in self.repo.list_questions()
            for index, option in enumerate(question.options)
            if option.is_correct
        }

        self.assertGreater(len(correct_positions), 1)

    def test_repeated_initialization_does_not_duplicate_records(self):
        self.seed(seed=10)
        first = self.snapshot()

        self.seed(seed=99)

        self.assertEqual(self.snapshot(), first)

    def test_existing_valid_records_are_preserved(self):
        subject = Subject.create("Môn của người dùng")
        topic = Topic.create(subject.id, "Chủ đề riêng")
        self.repo.add_subject(subject)
        self.repo.add_topic(topic)
        question = Question.create(
            topic.id,
            "Câu hỏi hiện có?",
            DifficultyLevel.DE,
            self.make_options(),
        )
        self.repo.add_question(question)
        original_subjects = self.repo.list_subjects()
        original_topics = self.repo.list_topics()
        original_questions = self.repo.list_questions()

        self.seed()

        self.assertEqual(self.repo.get_subject(subject.id), subject)
        self.assertEqual(self.repo.get_topic(topic.id), topic)
        self.assertEqual(self.repo.get_question(question.id), question)
        for existing in original_subjects:
            self.assertIn(existing, self.repo.list_subjects())
        for existing in original_topics:
            self.assertIn(existing, self.repo.list_topics())
        for existing in original_questions:
            self.assertIn(existing, self.repo.list_questions())

    def test_existing_sample_names_match_without_case_or_outer_spaces(self):
        subject = Subject.create("  lập trình python ")
        topic = Topic.create(subject.id, " kiểu dữ liệu cơ bản ")
        self.repo.add_subject(subject)
        self.repo.add_topic(topic)

        self.seed()

        topic_questions = [
            question
            for question in self.repo.list_questions()
            if question.topic_id == topic.id
        ]
        self.assertEqual(len(topic_questions), 4)

    def test_duplicate_existing_question_content_does_not_count_twice(self):
        subject = Subject.create("Lập trình Python")
        topic = Topic.create(subject.id, "Kiểu dữ liệu cơ bản")
        self.repo.add_subject(subject)
        self.repo.add_topic(topic)
        duplicate = Question.create(
            topic.id,
            "Kiểu dữ liệu nào biểu diễn số nguyên trong Python?",
            DifficultyLevel.DE,
            self.make_options(),
        )
        self.repo.add_question(duplicate)
        second_copy = Question.create(
            topic.id,
            duplicate.content,
            DifficultyLevel.DE,
            self.make_options(),
        )
        self.repo.add_question(second_copy)

        self.seed()

        topic_questions = [
            question
            for question in self.repo.list_questions()
            if question.topic_id == topic.id
        ]
        self.assertEqual(len({q.content.casefold() for q in topic_questions}), 4)
        self.assertEqual(len(topic_questions), 5)

    def test_missing_questions_file_is_rebuilt_from_existing_topics(self):
        self.seed()
        subjects_before = self.repo.list_subjects()
        topics_before = self.repo.list_topics()
        self.questions_path.unlink()

        self.seed()

        self.assertTrue(self.questions_path.is_file())
        self.assertEqual(self.repo.list_subjects(), subjects_before)
        self.assertEqual(self.repo.list_topics(), topics_before)
        restored_repo = self.make_repository()
        restored_questions = restored_repo.list_questions()
        self.assertGreaterEqual(len(restored_questions), 16)
        self.assertGreaterEqual(
            len(restored_repo.list_subjects()), len(subjects_before)
        )
        self.assertGreaterEqual(
            len(restored_repo.list_topics()), len(topics_before)
        )
        topics_by_id = {topic.id: topic for topic in restored_repo.list_topics()}
        for question in restored_questions:
            self.assertIn(question.topic_id, topics_by_id)
            valid, message = question.is_valid()
            self.assertTrue(valid, message)
        for topic in restored_repo.list_topics():
            self.assertGreaterEqual(
                sum(q.topic_id == topic.id for q in restored_questions), 4
            )

    def test_missing_subject_store_is_rebuilt_when_no_questions_reference_it(self):
        self.seed()
        self.questions_path.unlink()
        self.subjects_topics_path.unlink()

        self.seed()

        self.assertTrue(self.subjects_topics_path.is_file())
        self.assertTrue(self.questions_path.is_file())
        restored_repo = self.make_repository()
        self.assertGreaterEqual(len(restored_repo.list_subjects()), 2)
        self.assertGreaterEqual(len(restored_repo.list_topics()), 4)
        self.assertGreaterEqual(len(restored_repo.list_questions()), 16)

    def test_empty_files_are_initialized(self):
        self.subjects_topics_path.write_text("", encoding="utf-8")
        self.questions_path.write_text(" \n", encoding="utf-8")

        self.seed()

        self.assertGreaterEqual(len(self.repo.list_subjects()), 2)
        self.assertGreaterEqual(len(self.repo.list_questions()), 16)

    def test_missing_subject_store_with_existing_questions_is_not_overwritten(self):
        self.seed()
        original_questions = self.questions_path.read_bytes()
        self.subjects_topics_path.unlink()

        with self.assertRaisesRegex(ValueError, "Không thể khôi phục"):
            self.seed()

        self.assertFalse(self.subjects_topics_path.exists())
        self.assertEqual(self.questions_path.read_bytes(), original_questions)

    def test_corrupted_json_is_reported_without_overwriting_file(self):
        self.subjects_topics_path.write_text("{bad json", encoding="utf-8")
        original_data = self.subjects_topics_path.read_bytes()

        with self.assertRaises(JsonFileError):
            self.seed()

        self.assertEqual(self.subjects_topics_path.read_bytes(), original_data)
        self.assertFalse(self.questions_path.exists())

    def test_corrupted_questions_json_is_reported_without_overwriting_file(self):
        self.handler.write(
            self.subjects_topics_path,
            {"subjects": [], "topics": []},
        )
        self.questions_path.write_text("{bad json", encoding="utf-8")
        original_subject_data = self.subjects_topics_path.read_bytes()
        original_question_data = self.questions_path.read_bytes()

        with self.assertRaises(JsonFileError):
            self.seed()

        self.assertEqual(
            self.subjects_topics_path.read_bytes(), original_subject_data
        )
        self.assertEqual(self.questions_path.read_bytes(), original_question_data)

    def test_wrong_json_structure_is_reported_before_writes(self):
        self.handler.write(self.subjects_topics_path, {"subjects": "wrong"})
        original_data = self.subjects_topics_path.read_bytes()

        with self.assertRaisesRegex(ValueError, "subjects"):
            self.seed()

        self.assertEqual(self.subjects_topics_path.read_bytes(), original_data)
        self.assertFalse(self.questions_path.exists())

    def test_inconsistent_question_reference_is_not_overwritten(self):
        self.handler.write(
            self.subjects_topics_path,
            {
                "subjects": [{"id": "subject_1", "name": "Existing"}],
                "topics": [],
            },
        )
        broken_question = {
            "id": "question_1",
            "topic_id": "missing_topic",
            "content": "Existing question?",
            "difficulty": "de",
            "options": [
                {"id": "o1", "content": "Correct", "is_correct": True},
                {"id": "o2", "content": "Wrong 1", "is_correct": False},
                {"id": "o3", "content": "Wrong 2", "is_correct": False},
                {"id": "o4", "content": "Wrong 3", "is_correct": False},
            ],
        }
        self.handler.write(self.questions_path, [broken_question])
        original_subject_data = self.subjects_topics_path.read_bytes()
        original_question_data = self.questions_path.read_bytes()

        with self.assertRaisesRegex(ValueError, "tham chiếu đến chủ đề"):
            self.seed()

        self.assertEqual(
            self.subjects_topics_path.read_bytes(), original_subject_data
        )
        self.assertEqual(self.questions_path.read_bytes(), original_question_data)

    def test_sample_selection_is_repeatable_with_same_random_seed(self):
        self.seed(seed=21)
        first_contents = sorted(q.content for q in self.repo.list_questions())

        second_root = self.root / "second"
        second_root.mkdir()
        second_repo = JsonDataRepository(
            subjects_topics_path=second_root / "subjects_topics.json",
            questions_path=second_root / "questions.json",
            handler=JsonFileHandler(backup_dir=second_root / "backup"),
        )
        seed_sample_data(second_repo, random.Random(21))

        self.assertEqual(
            first_contents,
            sorted(q.content for q in second_repo.list_questions()),
        )

    def test_admin_seed_reports_unavailable_auth_integration(self):
        self.seed()

        with self.assertRaisesRegex(NotImplementedError, "API xác thực"):
            seed_default_admin()

        self.assertEqual(len(self.repo.list_subjects()), 2)
        self.assertEqual(len(self.repo.list_questions()), 16)

    def test_application_initializer_adds_new_sample_subjects_to_existing_python_data(self):
        python = Subject.create("Lập trình Python")
        topic = Topic.create(python.id, "Chủ đề đã có")
        self.repo.add_subject(python)
        self.repo.add_topic(topic)
        existing_question = Question.create(
            topic.id,
            "Câu hỏi của người dùng?",
            DifficultyLevel.DE,
            self.make_options(),
        )
        self.repo.add_question(existing_question)

        initialize_sample_data(self.repo)

        self.assertEqual(
            self.repo.get_question(existing_question.id), existing_question
        )
        self.assertIn(
            "Kinh tế vi mô",
            {subject.name for subject in self.repo.list_subjects()},
        )
        self.assertGreaterEqual(
            len(self.repo.list_questions()), 17
        )

    def snapshot(self):
        return (
            self.repo.list_subjects(),
            self.repo.list_topics(),
            self.repo.list_questions(),
        )

    @staticmethod
    def make_options():
        return [
            Option(
                id=f"option_{index}",
                content=content,
                is_correct=index == 0,
            )
            for index, content in enumerate(
                ("Correct", "Wrong one", "Wrong two", "Wrong three")
            )
        ]


if __name__ == "__main__":
    unittest.main()
