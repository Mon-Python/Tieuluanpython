"""Export exams and their answer keys as UTF-8 text files."""

from pathlib import Path

from base_models import Exam, ExamExporter, Option, Question
from config import EXPORT_DIR


class FileExamExporter(ExamExporter):
    """Export an exam without answers and its separate answer key."""

    @staticmethod
    def _get_ordered_questions(
        exam: Exam, questions: list[Question]
    ) -> list[tuple[Question, list[Option]]]:
        questions_by_id = {question.id: question for question in questions}
        ordered: list[tuple[Question, list[Option]]] = []

        for question_id in exam.question_ids:
            question = questions_by_id.get(question_id)
            if question is None:
                raise ValueError(
                    f"Câu hỏi có mã '{question_id}' không có trong danh sách."
                )

            shuffled_option_ids = exam.shuffled_options.get(question_id)
            if shuffled_option_ids is None:
                raise ValueError(
                    f"Đề thi không lưu thứ tự phương án cho câu hỏi '{question_id}'."
                )

            options_by_id = {option.id: option for option in question.options}
            ordered_options = []
            for option_id in shuffled_option_ids:
                option = options_by_id.get(option_id)
                if option is None:
                    raise ValueError(
                        f"Phương án '{option_id}' không tồn tại trong câu hỏi "
                        f"'{question_id}'."
                    )
                ordered_options.append(option)

            ordered.append((question, ordered_options))

        return ordered

    @staticmethod
    def _prepare_output_path(file_path: str) -> Path:
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    def export_exam(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Write the exam questions and shuffled choices without answer markers."""
        lines = [exam.title, ""]
        for index, (question, options) in enumerate(
            self._get_ordered_questions(exam, questions), start=1
        ):
            lines.append(f"Câu {index}: {question.content}")
            for option_index, option in enumerate(options):
                label = chr(ord("A") + option_index)
                lines.append(f"  {label}. {option.content}")
            lines.append("")

        output_path = self._prepare_output_path(file_path)
        output_path.write_text("\n".join(lines), encoding="utf-8")

    def export_answer_key(
        self, exam: Exam, questions: list[Question], file_path: str
    ) -> None:
        """Write the correct choices using their positions in the shuffled exam."""
        lines = [f"ĐÁP ÁN: {exam.title}", ""]
        for index, (question, options) in enumerate(
            self._get_ordered_questions(exam, questions), start=1
        ):
            correct_options = [
                (option_index, option)
                for option_index, option in enumerate(options)
                if option.is_correct
            ]
            if correct_options:
                answers = ", ".join(
                    f"{chr(ord('A') + option_index)}. {option.content}"
                    for option_index, option in correct_options
                )
            else:
                answers = "Không có phương án đúng"
            lines.append(f"Câu {index}: {question.content}")
            lines.append(f"  Đáp án: {answers}")
            lines.append("")

        output_path = self._prepare_output_path(file_path)
        output_path.write_text("\n".join(lines), encoding="utf-8")


