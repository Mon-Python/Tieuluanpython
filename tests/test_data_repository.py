"""
test_data_repository.py  [A]
Chạy: python -m unittest discover tests -v   (hoặc pytest tests -v)
Dùng thư mục tạm riêng (tempfile) để không đụng dữ liệu thật trong data/.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base_models import Subject, Topic, Question, Option, DifficultyLevel
from data_repository import JsonDataRepository


def make_question(topic_id, content="1 + 1 = ?", difficulty=DifficultyLevel.DE,
                  texts=("2", "3", "4", "5")):
    """Tạo câu hỏi hợp lệ: phương án đầu tiên là đáp án đúng."""
    options = [Option.create(t, i == 0) for i, t in enumerate(texts)]
    return Question.create(topic_id, content, difficulty, options)


class TestJsonDataRepository(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.st_path = self.dir / "subjects_topics.json"
        self.q_path = self.dir / "questions.json"
        self.repo = JsonDataRepository(self.st_path, self.q_path)
        self.subject = Subject.create("Môn test")
        self.repo.add_subject(self.subject)
        self.topic = Topic.create(self.subject.id, "Chủ đề test")
        self.repo.add_topic(self.topic)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _q(self, **kw):
        return make_question(self.topic.id, **kw)

    # ---------- Subject ----------

    def test_add_and_get_subject(self):
        found = self.repo.get_subject(self.subject.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Môn test")

    def test_get_nonexistent_subject_returns_none(self):
        self.assertIsNone(self.repo.get_subject("khong_co"))

    def test_add_subject_duplicate_id_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_subject(self.subject)

    def test_add_subject_duplicate_name_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_subject(Subject.create("  MÔN TEST  "))

    def test_add_subject_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_subject(Subject.create("   "))

    def test_update_subject(self):
        self.subject.name = "Môn test (đã sửa)"
        self.repo.update_subject(self.subject.id, self.subject)
        self.assertEqual(self.repo.get_subject(self.subject.id).name, "Môn test (đã sửa)")

    def test_update_subject_keeps_created_at(self):
        old_created = self.repo.get_subject(self.subject.id).created_at
        self.repo.update_subject(self.subject.id, Subject.create("Tên mới"))
        found = self.repo.get_subject(self.subject.id)
        self.assertEqual(found.created_at, old_created)
        self.assertEqual(found.id, self.subject.id)

    def test_update_nonexistent_subject_raises(self):
        with self.assertRaises(ValueError):
            self.repo.update_subject("khong_co", Subject.create("X"))

    def test_update_subject_to_duplicate_name_raises(self):
        other = Subject.create("Môn khác")
        self.repo.add_subject(other)
        other.name = "Môn test"
        with self.assertRaises(ValueError):
            self.repo.update_subject(other.id, other)

    def test_delete_subject_success_when_no_topics(self):
        empty_subject = Subject.create("Môn không có chủ đề")
        self.repo.add_subject(empty_subject)
        self.repo.delete_subject(empty_subject.id)
        self.assertIsNone(self.repo.get_subject(empty_subject.id))

    def test_delete_subject_fails_when_has_topic(self):
        with self.assertRaises(ValueError):
            self.repo.delete_subject(self.subject.id)

    def test_delete_nonexistent_subject_raises(self):
        with self.assertRaises(ValueError):
            self.repo.delete_subject("khong_co")

    # ---------- Topic ----------

    def test_add_topic_with_invalid_subject_id_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.add_topic(Topic.create("subject_khong_ton_tai", "Chủ đề lỗi"))

    def test_add_topic_duplicate_id_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_topic(self.topic)

    def test_add_topic_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_topic(Topic.create(self.subject.id, ""))

    def test_add_topic_duplicate_name_same_subject_raises(self):
        with self.assertRaises(ValueError):
            self.repo.add_topic(Topic.create(self.subject.id, "chủ đề TEST"))

    def test_same_topic_name_allowed_in_other_subject(self):
        other = Subject.create("Môn khác")
        self.repo.add_subject(other)
        self.repo.add_topic(Topic.create(other.id, "Chủ đề test"))  # không lỗi

    def test_update_topic(self):
        self.topic.name = "Chủ đề test (đã sửa)"
        self.repo.update_topic(self.topic.id, self.topic)
        self.assertEqual(self.repo.get_topic(self.topic.id).name, "Chủ đề test (đã sửa)")

    def test_update_topic_with_invalid_subject_raises(self):
        bad = Topic.create("subject_khong_ton_tai", "X")
        with self.assertRaises(ValueError):
            self.repo.update_topic(self.topic.id, bad)

    def test_update_nonexistent_topic_raises(self):
        with self.assertRaises(ValueError):
            self.repo.update_topic("khong_co", Topic.create(self.subject.id, "X"))

    def test_delete_topic_success_when_no_question(self):
        empty_topic = Topic.create(self.subject.id, "Chủ đề rỗng")
        self.repo.add_topic(empty_topic)
        self.repo.delete_topic(empty_topic.id)
        self.assertIsNone(self.repo.get_topic(empty_topic.id))

    def test_delete_topic_fails_when_has_question(self):
        self.repo.add_question(self._q())
        with self.assertRaises(ValueError):
            self.repo.delete_topic(self.topic.id)

    def test_delete_nonexistent_topic_raises(self):
        with self.assertRaises(ValueError):
            self.repo.delete_topic("khong_co")

    def test_list_topics_filter_by_subject(self):
        other = Subject.create("Môn khác")
        self.repo.add_subject(other)
        t2 = Topic.create(other.id, "Chủ đề của môn khác")
        self.repo.add_topic(t2)
        result = self.repo.list_topics(self.subject.id)
        self.assertEqual([t.id for t in result], [self.topic.id])
        self.assertEqual(len(self.repo.list_topics()), 2)

    # ---------- Question: CRUD & validate ----------

    def test_add_question_success(self):
        q = self._q()
        self.repo.add_question(q)
        found = self.repo.get_question(q.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.content, "1 + 1 = ?")
        self.assertEqual(len(found.options), 4)

    def test_add_question_without_correct_option_raises_error(self):
        bad = Question.create(self.topic.id, "Câu lỗi", DifficultyLevel.DE,
                              [Option.create(c, False) for c in "ABCD"])
        with self.assertRaises(ValueError):
            self.repo.add_question(bad)

    def test_add_question_with_two_correct_options_raises_error(self):
        bad = Question.create(self.topic.id, "Câu lỗi", DifficultyLevel.DE,
                              [Option.create("A", True), Option.create("B", True),
                               Option.create("C", False), Option.create("D", False)])
        with self.assertRaises(ValueError):
            self.repo.add_question(bad)

    def test_add_question_with_empty_content_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.add_question(self._q(content="   "))

    def test_add_question_with_wrong_option_count_raises_error(self):
        bad = Question.create(self.topic.id, "Câu chỉ có 3 phương án", DifficultyLevel.DE,
                              [Option.create("A", True), Option.create("B", False),
                               Option.create("C", False)])
        with self.assertRaises(ValueError):
            self.repo.add_question(bad)

    def test_add_question_with_empty_option_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.add_question(self._q(texts=("2", "  ", "4", "5")))

    def test_add_question_with_duplicate_options_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.add_question(self._q(texts=("2", "3", "3", "5")))

    def test_add_question_with_unknown_topic_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.add_question(make_question("topic_khong_co"))

    def test_add_question_duplicate_id_raises_error(self):
        q = self._q()
        self.repo.add_question(q)
        with self.assertRaises(ValueError):
            self.repo.add_question(q)

    def test_update_question(self):
        q = self._q()
        self.repo.add_question(q)
        q.content = "1 + 1 = ? (đã sửa)"
        self.repo.update_question(q.id, q)
        self.assertEqual(self.repo.get_question(q.id).content, "1 + 1 = ? (đã sửa)")

    def test_update_question_keeps_created_at(self):
        q = self._q()
        self.repo.add_question(q)
        old_created = self.repo.get_question(q.id).created_at
        self.repo.update_question(q.id, self._q(content="Nội dung mới"))
        self.assertEqual(self.repo.get_question(q.id).created_at, old_created)

    def test_update_question_invalid_raises_and_keeps_old(self):
        q = self._q()
        self.repo.add_question(q)
        with self.assertRaises(ValueError):
            self.repo.update_question(q.id, self._q(content=""))
        self.assertEqual(self.repo.get_question(q.id).content, "1 + 1 = ?")

    def test_update_question_with_unknown_topic_raises(self):
        q = self._q()
        self.repo.add_question(q)
        with self.assertRaises(ValueError):
            self.repo.update_question(q.id, make_question("topic_khong_co"))

    def test_update_nonexistent_question_raises(self):
        with self.assertRaises(ValueError):
            self.repo.update_question("khong_co", self._q())

    def test_delete_question(self):
        q = self._q()
        self.repo.add_question(q)
        self.repo.delete_question(q.id)
        self.assertIsNone(self.repo.get_question(q.id))

    def test_delete_nonexistent_question_raises_error(self):
        with self.assertRaises(ValueError):
            self.repo.delete_question("id_khong_ton_tai")

    # ---------- usage_checker ----------

    def test_delete_question_blocked_when_used_in_exam(self):
        q = self._q()
        self.repo.add_question(q)
        repo2 = JsonDataRepository(self.st_path, self.q_path,
                                   usage_checker=lambda qid: qid == q.id)
        with self.assertRaises(ValueError) as ctx:
            repo2.delete_question(q.id)
        self.assertIn("đề thi", str(ctx.exception))
        self.assertIsNotNone(repo2.get_question(q.id))  # vẫn còn

    def test_delete_question_allowed_when_not_used(self):
        q = self._q()
        self.repo.add_question(q)
        repo2 = JsonDataRepository(self.st_path, self.q_path,
                                   usage_checker=lambda qid: False)
        repo2.delete_question(q.id)
        self.assertIsNone(repo2.get_question(q.id))

    def test_is_question_used(self):
        self.assertFalse(self.repo.is_question_used("bat_ky"))  # không có checker
        repo2 = JsonDataRepository(self.st_path, self.q_path,
                                   usage_checker=lambda qid: qid == "q_dung")
        self.assertTrue(repo2.is_question_used("q_dung"))
        self.assertFalse(repo2.is_question_used("q_khac"))

    # ---------- List / count / search ----------

    def test_list_questions_filter_by_difficulty(self):
        easy_q = self._q()
        hard_q = self._q(content="Câu khó", difficulty=DifficultyLevel.KHO)
        self.repo.add_question(easy_q)
        self.repo.add_question(hard_q)
        result = self.repo.list_questions(difficulty=DifficultyLevel.DE)
        self.assertEqual([q.id for q in result], [easy_q.id])

    def test_list_questions_filter_by_topic(self):
        topic2 = Topic.create(self.subject.id, "Chủ đề khác")
        self.repo.add_topic(topic2)
        q1 = self._q()
        q2 = make_question(topic2.id, content="Câu ở chủ đề khác")
        self.repo.add_question(q1)
        self.repo.add_question(q2)
        result = self.repo.list_questions(topic_id=self.topic.id)
        self.assertEqual([q.id for q in result], [q1.id])

    def test_count_questions(self):
        self.repo.add_question(self._q())
        self.assertEqual(self.repo.count_questions(self.topic.id, DifficultyLevel.DE), 1)
        self.assertEqual(self.repo.count_questions(self.topic.id, DifficultyLevel.KHO), 0)

    def test_search_by_keyword_in_content(self):
        q1 = self._q(content="Thủ đô của Pháp là gì?", texts=("Paris", "Rome", "Berlin", "Madrid"))
        q2 = self._q(content="1 + 1 = ?")
        self.repo.add_question(q1)
        self.repo.add_question(q2)
        result = self.repo.search_questions(keyword="THỦ ĐÔ")
        self.assertEqual([q.id for q in result], [q1.id])

    def test_search_by_keyword_in_option(self):
        q1 = self._q(content="Câu A", texts=("Paris", "Rome", "Berlin", "Madrid"))
        self.repo.add_question(q1)
        self.repo.add_question(self._q(content="Câu B"))
        result = self.repo.search_questions(keyword="paris")
        self.assertEqual([q.id for q in result], [q1.id])

    def test_search_keyword_and_difficulty(self):
        q1 = self._q(content="Python dễ", difficulty=DifficultyLevel.DE)
        q2 = self._q(content="Python khó", difficulty=DifficultyLevel.KHO)
        self.repo.add_question(q1)
        self.repo.add_question(q2)
        result = self.repo.search_questions(keyword="python", difficulty=DifficultyLevel.KHO)
        self.assertEqual([q.id for q in result], [q2.id])

    def test_search_no_match_returns_empty(self):
        self.repo.add_question(self._q())
        self.assertEqual(self.repo.search_questions(keyword="khong_co_tu_nay"), [])

    def test_search_empty_criteria_returns_all(self):
        self.repo.add_question(self._q())
        self.repo.add_question(self._q(content="Câu 2"))
        self.assertEqual(len(self.repo.search_questions()), 2)

    def test_search_by_subject(self):
        other = Subject.create("Môn khác")
        self.repo.add_subject(other)
        t2 = Topic.create(other.id, "Chủ đề môn khác")
        self.repo.add_topic(t2)
        q1 = self._q()
        q2 = make_question(t2.id, content="Câu môn khác")
        self.repo.add_question(q1)
        self.repo.add_question(q2)
        result = self.repo.search_questions(subject_id=other.id)
        self.assertEqual([q.id for q in result], [q2.id])

    # ---------- Summary ----------

    def test_question_bank_summary_structure(self):
        self.repo.add_question(self._q())
        summary = self.repo.get_question_bank_summary()
        self.assertEqual(summary[self.subject.id]["subject_name"], "Môn test")
        counts = summary[self.subject.id]["topics"][self.topic.id]["counts"]
        self.assertEqual(counts["de"], 1)
        self.assertEqual(counts["kho"], 0)

    def test_question_bank_summary_counts_multiple(self):
        for i in range(3):
            self.repo.add_question(self._q(content=f"Dễ {i}"))
        self.repo.add_question(self._q(content="Khó", difficulty=DifficultyLevel.KHO))
        counts = self.repo.get_question_bank_summary()[self.subject.id]["topics"][self.topic.id]["counts"]
        self.assertEqual(counts, {"de": 3, "kho": 1})

    # ---------- Lưu trữ ----------

    def test_data_persists_across_repository_instances(self):
        q = self._q()
        self.repo.add_question(q)
        repo2 = JsonDataRepository(self.st_path, self.q_path)
        self.assertIsNotNone(repo2.get_subject(self.subject.id))
        self.assertIsNotNone(repo2.get_question(q.id))

    def test_empty_repository_with_no_files(self):
        fresh = JsonDataRepository(self.dir / "moi" / "a.json", self.dir / "moi" / "b.json")
        self.assertEqual(fresh.list_subjects(), [])
        self.assertEqual(fresh.list_questions(), [])
        self.assertEqual(fresh.get_question_bank_summary(), {})

    def test_corrupted_questions_file_raises_value_error(self):
        self.q_path.write_text("{hong", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.repo.list_questions()

    def test_empty_questions_file_is_treated_as_no_questions(self):
        self.q_path.write_text("", encoding="utf-8")
        self.assertEqual(self.repo.list_questions(), [])

    def test_wrong_structure_questions_file_raises(self):
        self.q_path.write_text('{"khong": "phai list"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.repo.list_questions()


if __name__ == "__main__":
    unittest.main()