"""
data_repository.py
===================
[A sở hữu] Quản lý dữ liệu Môn học - Chủ đề - Câu hỏi bằng file JSON.
Implement 2 "hợp đồng" trong base_models.py: SubjectTopicRepository, QuestionRepository.

Mọi đọc/ghi file đi qua JsonFileHandler; đường dẫn mặc định lấy từ config.py.
Mọi lỗi nghiệp vụ đều ném ValueError với thông báo hiển thị thẳng cho người dùng.
"""

from collections import Counter
from pathlib import Path
from typing import Callable, Optional, Union

from base_models import (
    Subject, Topic, Question, DifficultyLevel,
    SubjectTopicRepository, QuestionRepository,
)
from config import SUBJECTS_TOPICS_FILE, QUESTIONS_FILE
from json_file_handler import JsonFileHandler


def _norm(text: str) -> str:
    return text.strip().lower()


def _replace_row(rows: list, row_id: str, new_row: dict, label: str) -> None:
    """Thay dòng có id=row_id bằng new_row, giữ id và created_at gốc."""
    i = next((i for i, r in enumerate(rows) if r["id"] == row_id), None)
    if i is None:
        raise ValueError(f"Không tìm thấy {label} id='{row_id}'")
    new_row["id"] = row_id
    new_row["created_at"] = rows[i].get("created_at", new_row["created_at"])
    rows[i] = new_row


def _remove_row(rows: list, row_id: str, label: str) -> list:
    """Trả danh sách đã bỏ dòng có id=row_id; không có -> ValueError."""
    kept = [r for r in rows if r["id"] != row_id]
    if len(kept) == len(rows):
        raise ValueError(f"Không tìm thấy {label} id='{row_id}'")
    return kept


def _first(items, item_id: str):
    return next((x for x in items if x.id == item_id), None)


class JsonDataRepository(SubjectTopicRepository, QuestionRepository):
    """
    2 file JSON: subjects_topics ({"subjects": [], "topics": []}) và questions (list).
    usage_checker: hàm (question_id) -> bool do D cung cấp (ExamRepository.is_question_used),
    truyền từ ngoài vào để KHÔNG import exam_repository -> tránh import vòng.
    """

    def __init__(self,
                 subjects_topics_path: Union[str, Path] = SUBJECTS_TOPICS_FILE,
                 questions_path: Union[str, Path] = QUESTIONS_FILE,
                 usage_checker: Optional[Callable[[str], bool]] = None,
                 handler: Optional[JsonFileHandler] = None):
        self.subjects_topics_path = Path(subjects_topics_path)
        self.questions_path = Path(questions_path)
        self.usage_checker = usage_checker
        self.handler = handler or JsonFileHandler()

    # ---------------- Đọc/ghi nội bộ ----------------

    def _read(self, path: Path, default, kind: type, expect: str):
        data = self.handler.read(path, default=default)
        if not isinstance(data, kind):
            raise ValueError(f"File '{path.name}' sai cấu trúc (phải là {expect}).")
        return data

    def _load_store(self) -> dict:
        store = self._read(self.subjects_topics_path, {}, dict,
                           "object có 'subjects' và 'topics'")
        store.setdefault("subjects", [])
        store.setdefault("topics", [])
        return store

    def _save_store(self, store: dict) -> None:
        self.handler.write(self.subjects_topics_path, store)

    def _load_questions(self) -> list:
        return self._read(self.questions_path, [], list, "danh sách câu hỏi")

    def _save_questions(self, rows: list) -> None:
        self.handler.write(self.questions_path, rows)

    @staticmethod
    def _check_name(name: str, label: str) -> None:
        if not name or not name.strip():
            raise ValueError(f"Tên {label} không được để trống")

    # ============================================================
    # Môn học
    # ============================================================

    def add_subject(self, subject: Subject) -> None:
        self._check_name(subject.name, "môn học")
        store = self._load_store()
        if any(s["id"] == subject.id for s in store["subjects"]):
            raise ValueError(f"subject id='{subject.id}' đã tồn tại")
        if any(_norm(s["name"]) == _norm(subject.name) for s in store["subjects"]):
            raise ValueError(f"Môn học '{subject.name.strip()}' đã tồn tại")
        store["subjects"].append(subject.to_dict())
        self._save_store(store)

    def update_subject(self, subject_id: str, subject: Subject) -> None:
        self._check_name(subject.name, "môn học")
        store = self._load_store()
        if any(s["id"] != subject_id and _norm(s["name"]) == _norm(subject.name)
               for s in store["subjects"]):
            raise ValueError(f"Môn học '{subject.name.strip()}' đã tồn tại")
        _replace_row(store["subjects"], subject_id, subject.to_dict(), "subject")
        self._save_store(store)

    def delete_subject(self, subject_id: str) -> None:
        store = self._load_store()
        if any(t["subject_id"] == subject_id for t in store["topics"]):
            raise ValueError("Không thể xóa môn học vì vẫn còn chủ đề thuộc môn này. "
                             "Hãy xóa hết chủ đề con trước.")
        store["subjects"] = _remove_row(store["subjects"], subject_id, "subject")
        self._save_store(store)

    def list_subjects(self) -> list[Subject]:
        return [Subject.from_dict(s) for s in self._load_store()["subjects"]]

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        return _first(self.list_subjects(), subject_id)

    # ============================================================
    # Chủ đề
    # ============================================================

    def _check_topic(self, store: dict, topic: Topic, own_id: Optional[str]) -> None:
        """Kiểm tra chung cho add/update: tên, môn tồn tại, không trùng tên trong môn."""
        self._check_name(topic.name, "chủ đề")
        if topic.subject_id not in {s["id"] for s in store["subjects"]}:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        if any(t["id"] != own_id and t["subject_id"] == topic.subject_id
               and _norm(t["name"]) == _norm(topic.name) for t in store["topics"]):
            raise ValueError(f"Chủ đề '{topic.name.strip()}' đã tồn tại trong môn học này")

    def add_topic(self, topic: Topic) -> None:
        store = self._load_store()
        self._check_topic(store, topic, own_id=None)
        if any(t["id"] == topic.id for t in store["topics"]):
            raise ValueError(f"topic id='{topic.id}' đã tồn tại")
        store["topics"].append(topic.to_dict())
        self._save_store(store)

    def update_topic(self, topic_id: str, topic: Topic) -> None:
        store = self._load_store()
        if not any(t["id"] == topic_id for t in store["topics"]):
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        self._check_topic(store, topic, own_id=topic_id)
        _replace_row(store["topics"], topic_id, topic.to_dict(), "topic")
        self._save_store(store)

    def delete_topic(self, topic_id: str) -> None:
        n = sum(1 for q in self._load_questions() if q["topic_id"] == topic_id)
        if n:
            raise ValueError(f"Không thể xóa chủ đề vì còn {n} câu hỏi "
                             "thuộc chủ đề này. Hãy xóa hết câu hỏi con trước.")
        store = self._load_store()
        store["topics"] = _remove_row(store["topics"], topic_id, "topic")
        self._save_store(store)

    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]:
        topics = [Topic.from_dict(t) for t in self._load_store()["topics"]]
        return [t for t in topics if not subject_id or t.subject_id == subject_id]

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        return _first(self.list_topics(), topic_id)

    # ============================================================
    # Câu hỏi
    # ============================================================

    def _validate_question(self, q: Question, topic_ids: set) -> None:
        ok, msg = q.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if q.topic_id not in topic_ids:
            raise ValueError(f"topic_id '{q.topic_id}' không tồn tại")

    def _topic_ids(self) -> set:
        return {t["id"] for t in self._load_store()["topics"]}

    def _add_many(self, questions: list[Question]) -> list:
        """Thêm nhiều câu, CHỈ ĐỌC/GHI FILE 1 LẦN. Trả [(số thứ tự 1-based, ValueError)]."""
        topic_ids, rows = self._topic_ids(), self._load_questions()
        ids = {r["id"] for r in rows}
        errors = []
        for n, q in enumerate(questions, 1):
            try:
                self._validate_question(q, topic_ids)
                if q.id in ids:
                    raise ValueError(f"question id='{q.id}' đã tồn tại")
            except ValueError as e:
                errors.append((n, e))
                continue
            rows.append(q.to_dict())
            ids.add(q.id)
        if len(errors) < len(questions):
            self._save_questions(rows)
        return errors

    def add_question(self, question: Question) -> None:
        errors = self._add_many([question])
        if errors:
            raise errors[0][1]

    def add_questions(self, questions: list[Question]) -> tuple[int, list[str]]:
        """
        [B] Nhập hàng loạt (file/API): câu hợp lệ được lưu, câu lỗi được báo lại.
        Trả (số câu đã thêm, ["Câu 3: <lý do>", ...]) - không ném lỗi vì 1 câu sai.
        """
        errors = self._add_many(questions)
        return len(questions) - len(errors), [f"Câu {n}: {e}" for n, e in errors]

    def update_question(self, question_id: str, question: Question) -> None:
        self._validate_question(question, self._topic_ids())
        rows = self._load_questions()
        _replace_row(rows, question_id, question.to_dict(), "câu hỏi")
        self._save_questions(rows)

    def is_question_used(self, question_id: str) -> bool:
        """True nếu câu hỏi đã nằm trong đề nào đó. [B] dùng để cảnh báo trước khi sửa."""
        return bool(self.usage_checker and self.usage_checker(question_id))

    def delete_question(self, question_id: str) -> None:
        kept = _remove_row(self._load_questions(), question_id, "câu hỏi")
        if self.is_question_used(question_id):
            raise ValueError("Không thể xóa câu hỏi vì đã nằm trong đề thi (xóa sẽ làm hỏng đề và "
                             "kết quả cũ). Hãy sửa nội dung câu hỏi thay vì xóa.")
        self._save_questions(kept)

    def get_question(self, question_id: str) -> Optional[Question]:
        return _first(self.list_questions(), question_id)

    def list_questions(self, topic_id: Optional[str] = None,
                       difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        return [q for q in map(Question.from_dict, self._load_questions())
                if (not topic_id or q.topic_id == topic_id)
                and (not difficulty or q.difficulty == difficulty)]

    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        """[C] dùng để kiểm tra đủ số câu trước khi sample()."""
        return len(self.list_questions(topic_id, difficulty))

    def search_questions(self, keyword: str = "",
                        topic_id: Optional[str] = None,
                        difficulty: Optional[DifficultyLevel] = None,
                        subject_id: Optional[str] = None) -> list[Question]:
        """
        Tìm kiếm kết hợp AND: keyword (trong nội dung câu hoặc 1 phương án, không phân biệt
        hoa/thường), topic_id, difficulty, subject_id. Tiêu chí bỏ trống thì không lọc.
        """
        kw = _norm(keyword)
        topic_ids = {t.id for t in self.list_topics(subject_id)} if subject_id else None
        return [q for q in self.list_questions(topic_id, difficulty)
                if (topic_ids is None or q.topic_id in topic_ids)
                and (not kw or kw in q.content.lower()
                     or any(kw in o.content.lower() for o in q.options))]

    # ============================================================
    # Tổng hợp cho GUI (B, C)
    # ============================================================

    def get_question_bank_summary(self) -> dict:
        """
        {subject_id: {"subject_name": str,
                      "topics": {topic_id: {"topic_name": str, "counts": {"de": int, "kho": int}}}}}
        Đọc câu hỏi MỘT lần rồi đếm bằng Counter.
        """
        counter = Counter((q["topic_id"], q["difficulty"]) for q in self._load_questions())
        return {
            s.id: {"subject_name": s.name,
                   "topics": {t.id: {"topic_name": t.name,
                                     "counts": {lv.value: counter.get((t.id, lv.value), 0)
                                                for lv in DifficultyLevel}}
                              for t in self.list_topics(s.id)}}
            for s in self.list_subjects()
        }
