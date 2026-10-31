"""Export exam papers and answer keys as JSON files."""

import json
from pathlib import Path

from base_models import ExamExporter


class ExamExporterImpl(ExamExporter):
    """Write a student-safe exam paper and its separate answer key."""

    @staticmethod
    def _exam_metadata(exam):
        return exam.to_dict() if hasattr(exam, "to_dict") else dict(exam)

    @staticmethod
    def _ordered_questions(exam, questions):
        by_id = {question.id: question for question in questions}
        ordered_ids = getattr(exam, "question_ids", None) or list(by_id)
        return [by_id[question_id] for question_id in ordered_ids
                if question_id in by_id]

    @staticmethod
    def _write(path, data):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def export_exam(self, exam, questions, path):
        """Export exam metadata and questions without exposing correct answers."""
        paper_questions = []
        shuffled = getattr(exam, "shuffled_options", {}) or {}
        for question in self._ordered_questions(exam, questions):
            options_by_id = {option.id: option for option in question.options}
            ordered_ids = shuffled.get(question.id, [])
            ordered_options = [options_by_id[option_id] for option_id in ordered_ids
                               if option_id in options_by_id]
            ordered_options.extend(
                option for option in question.options
                if option.id not in set(ordered_ids)
            )
            paper_questions.append({
                "id": question.id,
                "topic_id": question.topic_id,
                "content": question.content,
                "difficulty": question.difficulty.value,
                "options": [
                    {"id": option.id, "content": option.content}
                    for option in ordered_options
                ],
            })

        self._write(path, {
            "exam": self._exam_metadata(exam),
            "questions": paper_questions,
        })

    def export_answer_key(self, exam, questions, path):
        """Export the correct option IDs separately from the question paper."""
        answers = [
            {
                "question_id": question.id,
                "correct_option_ids": question.correct_option_ids(),
            }
            for question in self._ordered_questions(exam, questions)
        ]
        self._write(path, {
            "exam": self._exam_metadata(exam),
            "answers": answers,
        })
