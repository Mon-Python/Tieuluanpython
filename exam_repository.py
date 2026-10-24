"""Lưu trữ đề thi và kết quả làm bài bằng JSON."""

from pathlib import Path
from typing import Optional, Union

from base_models import Exam, ExamResult
from config import EXAMS_FILE, RESULTS_FILE
from json_file_handler import JsonFileHandler


PathLike = Union[str, Path]


class ExamRepository:
	"""Đọc và ghi đề thi, kết quả qua JsonFileHandler."""

	def __init__(self,
				 exams_path: PathLike = EXAMS_FILE,
				 results_path: PathLike = RESULTS_FILE,
				 handler: Optional[JsonFileHandler] = None):
		self.exams_path = Path(exams_path)
		self.results_path = Path(results_path)
		self.handler = handler or JsonFileHandler()

	def _load_rows(self, path: Path) -> list[dict]:
		rows = self.handler.read(path, default=[])
		if not isinstance(rows, list):
			raise ValueError(f"File '{path.name}' sai cấu trúc (phải là danh sách).")
		return rows

	def _save_record(self, path: Path, record: dict) -> None:
		rows = self._load_rows(path)
		for index, row in enumerate(rows):
			if row.get("id") == record["id"]:
				rows[index] = record
				break
		else:
			rows.append(record)
		self.handler.write(path, rows)

	def list_exams(self) -> list[Exam]:
		"""Trả về toàn bộ đề thi đã lưu."""
		return [Exam.from_dict(row) for row in self._load_rows(self.exams_path)]

	def get_exam(self, exam_id: str) -> Optional[Exam]:
		"""Tìm đề thi theo ID; trả về None nếu không tìm thấy."""
		for exam in self.list_exams():
			if exam.id == exam_id:
				return exam
		return None

	def save_exam(self, exam: Exam) -> None:
		"""Lưu đề mới hoặc cập nhật đề đã có cùng ID."""
		self._save_record(self.exams_path, exam.to_dict())

	def list_results(self) -> list[ExamResult]:
		"""Trả về toàn bộ kết quả làm bài đã lưu."""
		return [ExamResult.from_dict(row) for row in self._load_rows(self.results_path)]

	def save_result(self, result: ExamResult) -> None:
		"""Lưu kết quả mới hoặc cập nhật kết quả đã có cùng ID."""
		self._save_record(self.results_path, result.to_dict())

	def list_results_by_exam(self, exam_id: str) -> list[ExamResult]:
		"""Trả về các kết quả thuộc đề thi có ID tương ứng."""
		return [result for result in self.list_results() if result.exam_id == exam_id]

	def is_question_used(self, question_id: str) -> bool:
		"""True nếu câu hỏi đã được lưu trong ít nhất một đề thi."""
		return any(question_id in exam.question_ids for exam in self.list_exams())
