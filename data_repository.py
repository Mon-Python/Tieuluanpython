"""
data_repository.py
===================
[A sở hữu] Quản lý dữ liệu Môn học - Chủ đề - Câu hỏi bằng file JSON.
Implement 2 "hợp đồng" trong base_models.py:
    - SubjectTopicRepository  -> CRUD Môn học, Chủ đề
    - QuestionRepository      -> CRUD Câu hỏi + kiểm tra hợp lệ

Mọi đọc/ghi file đi qua JsonFileHandler; đường dẫn mặc định lấy từ config.py.
Mọi lỗi nghiệp vụ đều ném ValueError với thông báo có thể hiển thị thẳng cho người dùng.
"""

from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Union

from base_models import (
    Subject, Topic, Question, Option,
    DifficultyLevel,
    SubjectTopicRepository, QuestionRepository,
)
from config import SUBJECTS_TOPICS_FILE, QUESTIONS_FILE
from json_file_handler import JsonFileHandler

PathLike = Union[str, Path]


# ============================================================
# Chuyển đổi object <-> dict (JSON không lưu trực tiếp object Python)
# ============================================================

def _subject_to_dict(s: Subject) -> dict:
    return {"id": s.id, "name": s.name, "description": s.description,
            "created_at": s.created_at.isoformat()}


def _subject_from_dict(d: dict) -> Subject:
    return Subject(id=d["id"], name=d["name"], description=d.get("description", ""),
                   created_at=datetime.fromisoformat(d["created_at"]))


def _topic_to_dict(t: Topic) -> dict:
    return {"id": t.id, "subject_id": t.subject_id, "name": t.name,
            "created_at": t.created_at.isoformat()}


def _topic_from_dict(d: dict) -> Topic:
    return Topic(id=d["id"], subject_id=d["subject_id"], name=d["name"],
                 created_at=datetime.fromisoformat(d["created_at"]))


def _question_to_dict(q: Question) -> dict:
    return {
        "id": q.id,
        "topic_id": q.topic_id,
        "content": q.content,
        "difficulty": q.difficulty.value,
        "options": [asdict(o) for o in q.options],
        "created_at": q.created_at.isoformat(),
    }


def _question_from_dict(d: dict) -> Question:
    options = [Option(id=o["id"], content=o["content"], is_correct=o["is_correct"])
               for o in d["options"]]
    return Question(
        id=d["id"],
        topic_id=d["topic_id"],
        content=d["content"],
        difficulty=DifficultyLevel(d["difficulty"]),
        options=options,
        created_at=datetime.fromisoformat(d["created_at"]),
    )


def _norm(text: str) -> str:
    return text.strip().lower()


# ============================================================
# Class chính
# ============================================================

class JsonDataRepository(SubjectTopicRepository, QuestionRepository):
    """
    Lưu trữ bằng 2 file JSON:
        - subjects_topics_path: Môn học + Chủ đề  (dict {"subjects": [], "topics": []})
        - questions_path: Câu hỏi                  (list)

    usage_checker: hàm (question_id) -> bool do D cung cấp (ExamRepository.is_question_used).
    Truyền từ ngoài vào (main.py) để KHÔNG import exam_repository -> tránh import vòng.
    """

    def __init__(self,
                 subjects_topics_path: PathLike = SUBJECTS_TOPICS_FILE,
                 questions_path: PathLike = QUESTIONS_FILE,
                 usage_checker: Optional[Callable[[str], bool]] = None,
                 handler: Optional[JsonFileHandler] = None):
        self.subjects_topics_path = Path(subjects_topics_path)
        self.questions_path = Path(questions_path)
        self.usage_checker = usage_checker
        self.handler = handler or JsonFileHandler()

    # ---------------- Hàm nội bộ đọc/ghi ----------------

    def _load_store(self) -> dict:
        store = self.handler.read(self.subjects_topics_path,
                                  default={"subjects": [], "topics": []})
        if not isinstance(store, dict):
            raise ValueError(f"File '{self.subjects_topics_path.name}' sai cấu trúc "
                             "(phải là object có 'subjects' và 'topics').")
        store.setdefault("subjects", [])
        store.setdefault("topics", [])
        return store

    def _save_store(self, store: dict) -> None:
        self.handler.write(self.subjects_topics_path, store)

    def _load_questions(self) -> list:
        data = self.handler.read(self.questions_path, default=[])
        if not isinstance(data, list):
            raise ValueError(f"File '{self.questions_path.name}' sai cấu trúc "
                             "(phải là danh sách câu hỏi).")
        return data

    def _save_questions(self, questions: list) -> None:
        self.handler.write(self.questions_path, questions)

    @staticmethod
    def _check_name(name: str, label: str) -> None:
        if not name or not name.strip():
            raise ValueError(f"Tên {label} không được để trống")

    # ============================================================
    # Môn học (Subject)
    # ============================================================

    def add_subject(self, subject: Subject) -> None:
        self._check_name(subject.name, "môn học")
        store = self._load_store()
        if any(s["id"] == subject.id for s in store["subjects"]):
            raise ValueError(f"subject id='{subject.id}' đã tồn tại")
        if any(_norm(s["name"]) == _norm(subject.name) for s in store["subjects"]):
            raise ValueError(f"Môn học '{subject.name.strip()}' đã tồn tại")
        store["subjects"].append(_subject_to_dict(subject))
        self._save_store(store)

    def update_subject(self, subject_id: str, subject: Subject) -> None:
        self._check_name(subject.name, "môn học")
        store = self._load_store()
        index = next((i for i, s in enumerate(store["subjects"]) if s["id"] == subject_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        if any(s["id"] != subject_id and _norm(s["name"]) == _norm(subject.name)
               for s in store["subjects"]):
            raise ValueError(f"Môn học '{subject.name.strip()}' đã tồn tại")
        new_dict = _subject_to_dict(subject)
        new_dict["id"] = subject_id                                     # giữ id gốc
        new_dict["created_at"] = store["subjects"][index]["created_at"]  # giữ ngày tạo gốc
        store["subjects"][index] = new_dict
        self._save_store(store)

    def delete_subject(self, subject_id: str) -> None:
        store = self._load_store()
        if any(t["subject_id"] == subject_id for t in store["topics"]):
            raise ValueError(
                "Không thể xóa môn học vì vẫn còn chủ đề thuộc môn này. "
                "Hãy xóa hết chủ đề con trước."
            )
        new_subjects = [s for s in store["subjects"] if s["id"] != subject_id]
        if len(new_subjects) == len(store["subjects"]):
            raise ValueError(f"Không tìm thấy subject id='{subject_id}'")
        store["subjects"] = new_subjects
        self._save_store(store)

    def list_subjects(self) -> list[Subject]:
        return [_subject_from_dict(s) for s in self._load_store()["subjects"]]

    def get_subject(self, subject_id: str) -> Optional[Subject]:
        for s in self.list_subjects():
            if s.id == subject_id:
                return s
        return None

    # ============================================================
    # Chủ đề (Topic)
    # ============================================================

    def add_topic(self, topic: Topic) -> None:
        self._check_name(topic.name, "chủ đề")
        store = self._load_store()
        if topic.subject_id not in {s["id"] for s in store["subjects"]}:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        if any(t["id"] == topic.id for t in store["topics"]):
            raise ValueError(f"topic id='{topic.id}' đã tồn tại")
        if any(t["subject_id"] == topic.subject_id and _norm(t["name"]) == _norm(topic.name)
               for t in store["topics"]):
            raise ValueError(f"Chủ đề '{topic.name.strip()}' đã tồn tại trong môn học này")
        store["topics"].append(_topic_to_dict(topic))
        self._save_store(store)

    def update_topic(self, topic_id: str, topic: Topic) -> None:
        self._check_name(topic.name, "chủ đề")
        store = self._load_store()
        index = next((i for i, t in enumerate(store["topics"]) if t["id"] == topic_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        if topic.subject_id not in {s["id"] for s in store["subjects"]}:
            raise ValueError(f"subject_id '{topic.subject_id}' không tồn tại")
        if any(t["id"] != topic_id and t["subject_id"] == topic.subject_id
               and _norm(t["name"]) == _norm(topic.name) for t in store["topics"]):
            raise ValueError(f"Chủ đề '{topic.name.strip()}' đã tồn tại trong môn học này")
        new_dict = _topic_to_dict(topic)
        new_dict["id"] = topic_id
        new_dict["created_at"] = store["topics"][index]["created_at"]
        store["topics"][index] = new_dict
        self._save_store(store)

    def delete_topic(self, topic_id: str) -> None:
        # Chặn xóa nếu còn câu hỏi thuộc chủ đề - tránh câu hỏi "mồ côi"
        remaining = [q for q in self._load_questions() if q["topic_id"] == topic_id]
        if remaining:
            raise ValueError(
                f"Không thể xóa chủ đề vì còn {len(remaining)} câu hỏi "
                "thuộc chủ đề này. Hãy xóa hết câu hỏi con trước."
            )
        store = self._load_store()
        new_topics = [t for t in store["topics"] if t["id"] != topic_id]
        if len(new_topics) == len(store["topics"]):
            raise ValueError(f"Không tìm thấy topic id='{topic_id}'")
        store["topics"] = new_topics
        self._save_store(store)

    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]:
        topics = [_topic_from_dict(t) for t in self._load_store()["topics"]]
        if subject_id:
            topics = [t for t in topics if t.subject_id == subject_id]
        return topics

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        for t in self.list_topics():
            if t.id == topic_id:
                return t
        return None

    # ============================================================
    # Câu hỏi (Question)
    # ============================================================

    def add_question(self, question: Question) -> None:
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")
        questions = self._load_questions()
        if any(q["id"] == question.id for q in questions):
            raise ValueError(f"question id='{question.id}' đã tồn tại")
        questions.append(_question_to_dict(question))
        self._save_questions(questions)

    def update_question(self, question_id: str, question: Question) -> None:
        ok, msg = question.is_valid()
        if not ok:
            raise ValueError(f"Câu hỏi không hợp lệ: {msg}")
        if self.get_topic(question.topic_id) is None:
            raise ValueError(f"topic_id '{question.topic_id}' không tồn tại")
        questions = self._load_questions()
        index = next((i for i, q in enumerate(questions) if q["id"] == question_id), None)
        if index is None:
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")
        new_dict = _question_to_dict(question)
        new_dict["id"] = question_id
        new_dict["created_at"] = questions[index]["created_at"]
        questions[index] = new_dict
        self._save_questions(questions)

    def is_question_used(self, question_id: str) -> bool:
        """True nếu câu hỏi đã nằm trong đề nào đó. [B] dùng để cảnh báo trước khi sửa."""
        return bool(self.usage_checker and self.usage_checker(question_id))

    def delete_question(self, question_id: str) -> None:
        questions = self._load_questions()
        new_questions = [q for q in questions if q["id"] != question_id]
        if len(new_questions) == len(questions):
            raise ValueError(f"Không tìm thấy câu hỏi id='{question_id}'")
        if self.is_question_used(question_id):
            raise ValueError(
                "Không thể xóa câu hỏi vì đã nằm trong đề thi (xóa sẽ làm hỏng đề và "
                "kết quả cũ). Hãy sửa nội dung câu hỏi thay vì xóa."
            )
        self._save_questions(new_questions)

    def get_question(self, question_id: str) -> Optional[Question]:
        for q in self._load_questions():
            if q["id"] == question_id:
                return _question_from_dict(q)
        return None

    def list_questions(self, topic_id: Optional[str] = None,
                       difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        questions = [_question_from_dict(q) for q in self._load_questions()]
        if topic_id:
            questions = [q for q in questions if q.topic_id == topic_id]
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        return questions

    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        """[C] dùng để kiểm tra đủ số câu trước khi sample()."""
        return len(self.list_questions(topic_id=topic_id, difficulty=difficulty))

    def search_questions(self, keyword: str = "",
                         topic_id: Optional[str] = None,
                         difficulty: Optional[DifficultyLevel] = None,
                         subject_id: Optional[str] = None) -> list[Question]:
        """
        Tìm kiếm theo nhiều tiêu chí (kết hợp AND):
          1) keyword: có trong nội dung câu hỏi HOẶC nội dung 1 phương án (không phân biệt hoa/thường)
          2) topic_id, 3) difficulty, 4) subject_id (mọi chủ đề thuộc môn đó)
        Tiêu chí bỏ trống thì không lọc. [B] dùng cho ô tìm kiếm ở tab Câu hỏi.
        """
        kw = _norm(keyword)
        subject_topic_ids = ({t.id for t in self.list_topics(subject_id)}
                             if subject_id else None)
        result = []
        for q in self.list_questions(topic_id=topic_id, difficulty=difficulty):
            if subject_topic_ids is not None and q.topic_id not in subject_topic_ids:
                continue
            if kw and kw not in q.content.lower() \
                    and not any(kw in o.content.lower() for o in q.options):
                continue
            result.append(q)
        return result

    # ============================================================
    # Hàm tổng hợp - phục vụ GUI (B, C) và kiểm tra ma trận (C)
    # ============================================================

    def get_question_bank_summary(self) -> dict:
        """
        {subject_id: {"subject_name": str,
                      "topics": {topic_id: {"topic_name": str,
                                            "counts": {"de": int, "kho": int}}}}}
        Đọc câu hỏi MỘT lần rồi đếm bằng Counter (không đọc lại file cho mỗi cặp).
        """
        counter = Counter((q["topic_id"], q["difficulty"]) for q in self._load_questions())
        summary = {}
        for subject in self.list_subjects():
            topics_summary = {}
            for topic in self.list_topics(subject.id):
                counts = {lv.value: counter.get((topic.id, lv.value), 0)
                          for lv in DifficultyLevel}
                topics_summary[topic.id] = {"topic_name": topic.name, "counts": counts}
            summary[subject.id] = {"subject_name": subject.name, "topics": topics_summary}
        return summary