"""Export exam papers and answer keys in supported file formats."""

import json
from pathlib import Path

from base_models import Exam, ExamExporter, Option, Question
from config import EXPORT_DIR


class _ExamExportBase(ExamExporter):
    """Shared validation and ordering for exam questions and options."""

    @staticmethod
    def _ordered_questions(
        exam: Exam, questions: list[Question]
    ) -> list[tuple[Question, list[Option]]]:
        questions_by_id = {question.id: question for question in questions}
        ordered = []

        for question_id in exam.question_ids:
            question = questions_by_id.get(question_id)
            if question is None:
                raise ValueError(
                    f"Câu hỏi có mã '{question_id}' không có trong danh sách."
                )

            shuffled_ids = exam.shuffled_options.get(question_id)
            if shuffled_ids is None:
                raise ValueError(
                    f"Đề thi không lưu thứ tự phương án cho câu hỏi "
                    f"'{question_id}'."
                )

            options_by_id = {option.id: option for option in question.options}
            ordered_options = []
            for option_id in shuffled_ids:
                option = options_by_id.get(option_id)
                if option is None:
                    raise ValueError(
                        f"Phương án '{option_id}' không tồn tại trong câu hỏi "
                        f"'{question_id}'."
                    )
                ordered_options.append(option)

            ordered.append((question, ordered_options))

        return ordered


class ExamExporterImpl(_ExamExportBase):
    """Write a JSON question paper and a separate JSON answer key."""

    @staticmethod
    def _write(path: str, data: dict) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def export_exam(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Export exam metadata and questions without exposing correct answers."""
        paper_questions = []
        for question, options in self._ordered_questions(exam, questions):
            paper_questions.append({
                "id": question.id,
                "topic_id": question.topic_id,
                "content": question.content,
                "difficulty": question.difficulty.value,
                "options": [
                    {"id": option.id, "content": option.content}
                    for option in options
                ],
            })

        self._write(file_path, {
            "exam": exam.to_dict(),
            "questions": paper_questions,
        })

    def export_answer_key(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Export correct option IDs separately from the question paper."""
        answers = [
            {
                "question_id": question.id,
                "correct_option_ids": question.correct_option_ids(),
            }
            for question, _options in self._ordered_questions(exam, questions)
        ]
        self._write(file_path, {
            "exam": exam.to_dict(),
            "answers": answers,
        })


class FileExamExporter(_ExamExportBase):
    """Export a UTF-8 text exam paper and its separate answer key."""

    @staticmethod
    def _prepare_output_path(file_path: str) -> Path:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = Path(file_path)
        if not output_path.is_absolute():
            output_path = EXPORT_DIR / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    def export_exam(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Write shuffled questions without marking the correct choices."""
        lines = [exam.title, ""]
        for index, (question, options) in enumerate(
            self._ordered_questions(exam, questions), start=1
        ):
            lines.append(f"Câu {index}: {question.content}")
            for option_index, option in enumerate(options):
                lines.append(f"  {chr(ord('A') + option_index)}. {option.content}")
            lines.append("")

        output_path = self._prepare_output_path(file_path)
        output_path.write_text("\n".join(lines), encoding="utf-8")

    def export_answer_key(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Write the answer labels using the shuffled exam order."""
        lines = [f"ĐÁP ÁN: {exam.title}", ""]
        for index, (question, options) in enumerate(
            self._ordered_questions(exam, questions), start=1
        ):
            correct_options = [
                (option_index, option)
                for option_index, option in enumerate(options)
                if option.is_correct
            ]
            if correct_options:
                answer_text = ", ".join(
                    f"{chr(ord('A') + option_index)}. {option.content}"
                    for option_index, option in correct_options
                )
            else:
                answer_text = "Không có phương án đúng"
            lines.append(f"Câu {index}: {question.content}")
            lines.append(f"  Đáp án: {answer_text}")
            lines.append("")

        output_path = self._prepare_output_path(file_path)
        output_path.write_text("\n".join(lines), encoding="utf-8")
