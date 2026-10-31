import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from base_models import (
    DifficultyLevel,
    Exam,
    Option,
    Question,
    Subject,
    Topic,
    User,
)
from config import COLOR_ERROR, COLOR_PRIMARY, COLOR_SUCCESS
from gui.exam_tab import ExamTab
from gui.take_exam_window import TakeExamWindow


class TestStudentQuizFlow(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError as error:
            self.skipTest(f"Tk display is unavailable: {error}")

        self.addCleanup(self.root.destroy)

    def test_student_starts_quiz_for_selected_subject_and_difficulty(self):
        subject = Subject.create("Biology")
        another_subject = Subject.create("History")
        topic = Topic.create(subject.id, "Cells")
        empty_topic = Topic.create(subject.id, "Genetics")
        other_topic = Topic.create(another_subject.id, "Ancient history")

        data_repo = Mock()
        data_repo.list_subjects.return_value = [subject, another_subject]
        data_repo.get_question_bank_summary.return_value = {}
        data_repo.list_topics.side_effect = {
            subject.id: [topic, empty_topic],
            another_subject.id: [other_topic],
        }.get
        question_counts = {
            (topic.id, DifficultyLevel.KHO): 3,
            (empty_topic.id, DifficultyLevel.KHO): 0,
            (other_topic.id, DifficultyLevel.KHO): 8,
        }
        data_repo.count_questions.side_effect = (
            lambda topic_id, difficulty: question_counts.get(
                (topic_id, difficulty), 0
            )
        )

        generated_exam = Exam.create(subject.id, "Biology - Khó", seed=17)
        exam_generator = Mock()
        exam_generator.generate_exam.return_value = generated_exam
        exam_repo = Mock()
        exam_repo.list_exams.return_value = []
        on_take_exam = Mock()

        tab = ExamTab(
            self.root,
            data_repo,
            exam_repo,
            exam_generator,
            User.create("student", "hash"),
            on_take_exam=on_take_exam,
        )
        self.addCleanup(tab.destroy)
        tab.cmb_student_subject.current(0)
        tab.cmb_student_difficulty.set("Khó")

        tab._do_student_exam()

        exam_generator.generate_exam.assert_called_once_with(
            subject_id=subject.id,
            title="Biology - Khó",
            matrix=[
                unittest.mock.ANY,
            ],
            seed=unittest.mock.ANY,
        )
        generated_matrix = exam_generator.generate_exam.call_args.kwargs["matrix"]
        self.assertEqual(
            [
                (item.topic_id, item.difficulty, item.num_questions)
                for item in generated_matrix
            ],
            [(topic.id, DifficultyLevel.KHO, 3)],
        )
        exam_repo.save_exam.assert_called_once_with(generated_exam)
        on_take_exam.assert_called_once_with(generated_exam)

    def test_quiz_displays_every_question_with_four_choices(self):
        questions = [
            self._make_question("q1", "First question"),
            self._make_question("q2", "Second question"),
        ]
        exam = Exam.create("subject", "Quiz", seed=1)
        exam.question_ids = [question.id for question in questions]
        exam.shuffled_options = {
            question.id: [option.id for option in reversed(question.options)]
            for question in questions
        }
        data_repo = Mock()
        data_repo.get_question.side_effect = {
            question.id: question for question in questions
        }.get

        window = TakeExamWindow(self.root, exam, data_repo)
        self.addCleanup(window.destroy)

        self.assertEqual(set(window.question_widgets), {q.id for q in questions})
        for question in questions:
            with self.subTest(question=question.id):
                option_rows = window.question_widgets[question.id]["options"]
                self.assertEqual(len(option_rows), 4)
                self.assertEqual(
                    [row[0].id for row in option_rows],
                    exam.shuffled_options[question.id],
                )
                self.assertEqual(
                    [row[1].cget("text")[0] for row in option_rows],
                    list("ABCD"),
                )

    def test_submitted_quiz_marks_correct_and_incorrect_answers_with_colors(self):
        questions = [
            self._make_question("q1", "First question"),
            self._make_question("q2", "Second question"),
        ]
        exam = Exam.create("subject", "Quiz", seed=1)
        exam.question_ids = [question.id for question in questions]
        data_repo = Mock()
        data_repo.get_question.side_effect = {
            question.id: question for question in questions
        }.get
        data_repo.get_topic.return_value = Topic.create("subject", "Topic")
        exam_repo = Mock()

        window = TakeExamWindow(
            self.root, exam, data_repo, exam_repo=exam_repo
        )
        self.addCleanup(window.destroy)
        window.question_widgets[questions[0].id]["options"][0][1].invoke()
        window.question_widgets[questions[1].id]["options"][1][1].invoke()

        window._submit_and_grade()

        self.assertTrue(window.is_submitted)
        self.assertEqual(window.result.score, 5.0)
        self.assertEqual(
            str(window.question_widgets[questions[0].id]["options"][0][2].cget(
                "foreground"
            )),
            COLOR_SUCCESS,
        )
        self.assertEqual(
            str(window.question_widgets[questions[1].id]["options"][0][2].cget(
                "foreground"
            )),
            COLOR_SUCCESS,
        )
        self.assertEqual(
            str(window.question_widgets[questions[1].id]["options"][1][2].cget(
                "foreground"
            )),
            COLOR_ERROR,
        )
        self.assertEqual(
            str(window.lbl_result.cget("foreground")), COLOR_PRIMARY
        )
        exam_repo.save_result.assert_called_once_with(window.result)

    def test_student_can_cancel_or_confirm_exit_while_quiz_is_in_progress(self):
        question = self._make_question("q1", "Question")
        exam = Exam.create("subject", "Quiz", seed=1)
        exam.question_ids = [question.id]
        data_repo = Mock()
        data_repo.get_question.return_value = question
        window = TakeExamWindow(self.root, exam, data_repo)
        self.addCleanup(window.destroy)

        with patch("gui.take_exam_window.messagebox.askyesno", return_value=False) as ask:
            window._on_window_close()
            ask.assert_called_once()
            self.assertTrue(window.winfo_exists())

        with patch("gui.take_exam_window.messagebox.askyesno", return_value=True) as ask:
            window._on_window_close()
            ask.assert_called_once()
            self.assertFalse(window.winfo_exists())

    def test_student_can_exit_without_confirmation_after_submitting_quiz(self):
        question = self._make_question("q1", "Question")
        exam = Exam.create("subject", "Quiz", seed=1)
        exam.question_ids = [question.id]
        data_repo = Mock()
        data_repo.get_question.return_value = question
        data_repo.get_topic.return_value = Topic.create("subject", "Topic")
        window = TakeExamWindow(self.root, exam, data_repo)
        self.addCleanup(window.destroy)
        window._submit_and_grade()

        with patch("gui.take_exam_window.messagebox.askyesno") as ask:
            window._on_window_close()

        ask.assert_not_called()
        self.assertFalse(window.winfo_exists())

    @staticmethod
    def _make_question(question_id, content):
        options = [
            Option(id=f"{question_id}_correct", content="Correct", is_correct=True),
            Option(id=f"{question_id}_wrong_1", content="Wrong 1"),
            Option(id=f"{question_id}_wrong_2", content="Wrong 2"),
            Option(id=f"{question_id}_wrong_3", content="Wrong 3"),
        ]
        return Question(
            id=question_id,
            topic_id="topic",
            content=content,
            difficulty=DifficultyLevel.DE,
            options=options,
        )


if __name__ == "__main__":
    unittest.main()
