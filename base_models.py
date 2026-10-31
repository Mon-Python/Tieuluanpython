"""
base_models.py
================
File TRUNG TÂM chứa class cha / cấu trúc dữ liệu dùng chung cho toàn dự án
"Quản lý ngân hàng câu hỏi & tạo đề kiểm tra" (Đề tài 7).

QUY TẮC CHO CẢ NHÓM:
- KHÔNG copy các class dưới đây sang file khác, chỉ import.
- KHÔNG tự ý đổi tên field. Muốn thêm field -> báo A, sửa DUY NHẤT ở file này.
- Mỗi class ABC là "hợp đồng": class con PHẢI implement đủ @abstractmethod.

PHÂN CÔNG (theo README từng thành viên):
- A: hạ tầng (config, JsonFileHandler), base_models, data_repository, app.py
- B: tài khoản (auth), validators, nhập câu hỏi, tab Câu hỏi / Môn-Chủ đề
- C: ExamGenerator, Grader, tab Tạo đề / Làm bài
- D: exam_repository, ExamExporter, dữ liệu mẫu, thống kê, đăng nhập, tài liệu
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from config import PERMISSIONS, ROLE_ADMIN, ROLE_USER


# ============================================================
# 1. ENUM
# ============================================================

class DifficultyLevel(str, Enum):
    """Mức độ câu hỏi. Dùng Enum thay vì gõ tay "de"/"kho" để tránh sai chính tả."""
    DE = "de"      # Dễ
    KHO = "kho"    # Khó


# ============================================================
# 2. HELPER
# ============================================================

def generate_id(prefix: str) -> str:
    """Mọi entity đều dùng hàm này để sinh id. Mẫu: <prefix>_<8 ký tự hex>."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat()


def _str_to_dt(value) -> datetime:
    """Chuỗi ISO -> datetime. Thiếu/rỗng (file cũ) -> thời điểm hiện tại."""
    return datetime.fromisoformat(value) if value else datetime.now()


# ============================================================
# 3. BASE ENTITY
# ============================================================

@dataclass
class BaseEntity:
    id: str
    created_at: datetime = field(default_factory=datetime.now)


# ============================================================
# 4. NGƯỜI DÙNG & PHÂN QUYỀN
# ============================================================

@dataclass
class User(BaseEntity):
    """
    Người dùng thường. Quyền xác định bằng PERMISSIONS trong config.py.
    Lưu ý: password_hash + salt do auth.py (B) tạo; KHÔNG bao giờ lưu mật khẩu thô.
    """
    username: str = ""
    password_hash: str = ""
    salt: str = ""
    role: str = ROLE_USER
    email: str = ""

    @staticmethod
    def create(username: str, password_hash: str, salt: str = "",
               email: str = "", role: str = ROLE_USER) -> "User":
        cls = Admin if role == ROLE_ADMIN else User
        return cls(id=generate_id("user"), username=username,
                   password_hash=password_hash, salt=salt, role=role, email=email)

    def can(self, action: str) -> bool:
        """Người dùng thường: chỉ được các action có ROLE_USER trong PERMISSIONS."""
        return self.role in PERMISSIONS.get(action, set())

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    def to_dict(self) -> dict:
        return {"id": self.id, "username": self.username,
                "password_hash": self.password_hash, "salt": self.salt,
                "role": self.role, "email": self.email,
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "User":
        """role == admin -> trả về Admin, ngược lại User."""
        cls = Admin if d.get("role") == ROLE_ADMIN else User
        return cls(id=d["id"], username=d.get("username", ""),
                   password_hash=d.get("password_hash", ""), salt=d.get("salt", ""),
                   role=d.get("role", ROLE_USER), email=d.get("email", ""),
                   created_at=_str_to_dt(d.get("created_at")))


@dataclass
class Admin(User):
    """Quản trị viên: ghi đè can() - được mọi action đã khai báo trong PERMISSIONS."""
    role: str = ROLE_ADMIN

    def can(self, action: str) -> bool:
        # Action sai chính tả -> False (không phải True), để lỗi lộ ra khi test
        return action in PERMISSIONS


# ============================================================
# 5. DỮ LIỆU CHÍNH: Môn học - Chủ đề - Câu hỏi - Phương án - Đề thi - Kết quả
# ============================================================

@dataclass
class Subject(BaseEntity):
    """Môn học. Ví dụ: Lập trình Python, Kinh tế vi mô..."""
    name: str = ""
    description: str = ""

    @staticmethod
    def create(name: str, description: str = "") -> "Subject":
        return Subject(id=generate_id("subj"), name=name, description=description)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description,
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "Subject":
        return Subject(id=d["id"], name=d.get("name", ""),
                       description=d.get("description", ""),
                       created_at=_str_to_dt(d.get("created_at")))


@dataclass
class Topic(BaseEntity):
    """Chủ đề thuộc 1 môn học. Ví dụ môn Python -> chủ đề 'Vòng lặp'."""
    subject_id: str = ""
    name: str = ""

    @staticmethod
    def create(subject_id: str, name: str) -> "Topic":
        return Topic(id=generate_id("topic"), subject_id=subject_id, name=name)

    def to_dict(self) -> dict:
        return {"id": self.id, "subject_id": self.subject_id, "name": self.name,
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "Topic":
        return Topic(id=d["id"], subject_id=d.get("subject_id", ""),
                     name=d.get("name", ""),
                     created_at=_str_to_dt(d.get("created_at")))


@dataclass
class Option:
    """Một phương án trả lời (KHÔNG kế thừa BaseEntity vì không cần created_at)."""
    id: str
    content: str
    is_correct: bool = False

    @staticmethod
    def create(content: str, is_correct: bool = False) -> "Option":
        return Option(id=generate_id("opt"), content=content, is_correct=is_correct)

    def to_dict(self) -> dict:
        return {"id": self.id, "content": self.content, "is_correct": self.is_correct}

    @staticmethod
    def from_dict(d: dict) -> "Option":
        return Option(id=d["id"], content=d.get("content", ""),
                      is_correct=d.get("is_correct", False))


@dataclass
class Question(BaseEntity):
    """
    Câu hỏi trong ngân hàng đề.
    options là list[Option]; đáp án đúng nằm trong Option.is_correct,
    KHÔNG tạo thêm field 'answer' riêng để tránh 2 nguồn dữ liệu lệch nhau.
    """
    topic_id: str = ""
    content: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.DE
    options: list[Option] = field(default_factory=list)

    @staticmethod
    def create(topic_id: str, content: str, difficulty: DifficultyLevel,
               options: list[Option]) -> "Question":
        return Question(id=generate_id("q"), topic_id=topic_id, content=content,
                        difficulty=difficulty, options=options)

    def correct_option_ids(self) -> list[str]:
        return [opt.id for opt in self.options if opt.is_correct]

    def is_valid(self) -> tuple[bool, str]:
        """
        Kiểm tra nội dung và đáp án (yêu cầu đề bài). Mọi người dùng lại hàm này,
        KHÔNG viết validate riêng. Hệ thống chỉ hỗ trợ 1 đáp án đúng/câu.
        """
        if not self.content.strip():
            return False, "Nội dung câu hỏi không được rỗng"
        if len(self.options) != 4:
            return False, "Câu hỏi phải có đúng 4 phương án"
        if any(not o.content.strip() for o in self.options):
            return False, "Nội dung các phương án không được để trống"
        normalized = [o.content.strip().lower() for o in self.options]
        if len(set(normalized)) != len(normalized):
            return False, "Các phương án không được trùng nội dung nhau"
        correct_count = len(self.correct_option_ids())
        if correct_count == 0:
            return False, "Câu hỏi phải có ít nhất 1 đáp án đúng"
        if correct_count > 1:
            return False, "Câu hỏi chỉ được có đúng 1 đáp án đúng (single choice)"
        return True, "OK"

    def to_dict(self) -> dict:
        return {"id": self.id, "topic_id": self.topic_id, "content": self.content,
                "difficulty": self.difficulty.value,
                "options": [o.to_dict() for o in self.options],
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "Question":
        return Question(id=d["id"], topic_id=d.get("topic_id", ""),
                        content=d.get("content", ""),
                        difficulty=DifficultyLevel(d.get("difficulty", "de")),
                        options=[Option.from_dict(o) for o in d.get("options", [])],
                        created_at=_str_to_dt(d.get("created_at")))


@dataclass
class ExamMatrixItem:
    """1 dòng trong ma trận đề: lấy bao nhiêu câu ở mức độ nào, thuộc chủ đề nào."""
    topic_id: str
    difficulty: DifficultyLevel
    num_questions: int

    def to_dict(self) -> dict:
        return {"topic_id": self.topic_id, "difficulty": self.difficulty.value,
                "num_questions": self.num_questions}

    @staticmethod
    def from_dict(d: dict) -> "ExamMatrixItem":
        return ExamMatrixItem(topic_id=d["topic_id"],
                              difficulty=DifficultyLevel(d["difficulty"]),
                              num_questions=d["num_questions"])


@dataclass
class Exam(BaseEntity):
    """
    Đề thi được sinh ra. seed dùng để TÁI LẬP đề: cùng seed + cùng ngân hàng
    câu hỏi + cùng matrix -> sinh lại đúng đề y hệt.
    """
    subject_id: str = ""
    title: str = ""
    seed: int = 0
    question_ids: list[str] = field(default_factory=list)
    # Thứ tự phương án đã trộn của từng câu: {question_id: [option_id, ...]}
    shuffled_options: dict = field(default_factory=dict)
    # Ma trận dùng để sinh đề (C cần để rebuild_exam)
    matrix: list[ExamMatrixItem] = field(default_factory=list)

    @staticmethod
    def create(subject_id: str, title: str, seed: int,
               matrix: Optional[list[ExamMatrixItem]] = None) -> "Exam":
        return Exam(id=generate_id("exam"), subject_id=subject_id, title=title,
                    seed=seed, matrix=list(matrix) if matrix else [])

    def to_dict(self) -> dict:
        return {"id": self.id, "subject_id": self.subject_id, "title": self.title,
                "seed": self.seed, "question_ids": list(self.question_ids),
                "shuffled_options": {k: list(v) for k, v in self.shuffled_options.items()},
                "matrix": [m.to_dict() for m in self.matrix],
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "Exam":
        return Exam(id=d["id"], subject_id=d.get("subject_id", ""),
                    title=d.get("title", ""), seed=d.get("seed", 0),
                    question_ids=list(d.get("question_ids", [])),
                    shuffled_options={k: list(v) for k, v in
                                      d.get("shuffled_options", {}).items()},
                    matrix=[ExamMatrixItem.from_dict(m) for m in d.get("matrix", [])],
                    created_at=_str_to_dt(d.get("created_at")))


@dataclass
class StudentAnswer:
    """
    Câu trả lời của học sinh cho 1 câu hỏi.
    QUY ƯỚC: selected_option_ids có ĐÚNG 1 phần tử, hoặc rỗng nếu bỏ trống
    (hệ thống chỉ có single choice).
    """
    question_id: str
    selected_option_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"question_id": self.question_id,
                "selected_option_ids": list(self.selected_option_ids)}

    @staticmethod
    def from_dict(d: dict) -> "StudentAnswer":
        return StudentAnswer(question_id=d["question_id"],
                             selected_option_ids=list(d.get("selected_option_ids", [])))


@dataclass
class ExamResult(BaseEntity):
    """Kết quả làm bài của 1 học sinh cho 1 đề."""
    exam_id: str = ""
    student_name: str = ""
    answers: list[StudentAnswer] = field(default_factory=list)
    score: float = 0.0
    # Thống kê theo chủ đề: {topic_id: {"correct": int, "total": int, "percent": float}}
    # (dùng dict, KHÔNG dùng tuple - tuple sẽ thành list khi lưu JSON)
    topic_stats: dict = field(default_factory=dict)

    @staticmethod
    def create(exam_id: str, student_name: str) -> "ExamResult":
        return ExamResult(id=generate_id("result"), exam_id=exam_id,
                          student_name=student_name)

    def to_dict(self) -> dict:
        return {"id": self.id, "exam_id": self.exam_id,
                "student_name": self.student_name,
                "answers": [a.to_dict() for a in self.answers],
                "score": self.score, "topic_stats": dict(self.topic_stats),
                "created_at": _dt_to_str(self.created_at)}

    @staticmethod
    def from_dict(d: dict) -> "ExamResult":
        return ExamResult(id=d["id"], exam_id=d.get("exam_id", ""),
                          student_name=d.get("student_name", ""),
                          answers=[StudentAnswer.from_dict(a) for a in d.get("answers", [])],
                          score=d.get("score", 0.0),
                          topic_stats=dict(d.get("topic_stats", {})),
                          created_at=_str_to_dt(d.get("created_at")))


# ============================================================
# 6. ABSTRACT CLASSES - "hợp đồng" cho từng mảng chức năng
# ============================================================

class SubjectTopicRepository(ABC):
    """
    [A] CRUD đầy đủ cho Môn học và Chủ đề.

    RÀNG BUỘC (mọi implementation):
    - delete_subject: PHẢI raise ValueError nếu môn học còn chủ đề con.
    - delete_topic: PHẢI raise ValueError nếu chủ đề còn câu hỏi con.
    """

    @abstractmethod
    def add_subject(self, subject: Subject) -> None: pass

    @abstractmethod
    def update_subject(self, subject_id: str, subject: Subject) -> None: pass

    @abstractmethod
    def delete_subject(self, subject_id: str) -> None: pass

    @abstractmethod
    def add_topic(self, topic: Topic) -> None: pass

    @abstractmethod
    def update_topic(self, topic_id: str, topic: Topic) -> None: pass

    @abstractmethod
    def delete_topic(self, topic_id: str) -> None: pass

    @abstractmethod
    def list_subjects(self) -> list[Subject]: pass

    @abstractmethod
    def list_topics(self, subject_id: Optional[str] = None) -> list[Topic]: pass

    @abstractmethod
    def get_subject(self, subject_id: str) -> Optional[Subject]: pass

    @abstractmethod
    def get_topic(self, topic_id: str) -> Optional[Topic]: pass


class QuestionRepository(ABC):
    """
    [A] CRUD ngân hàng câu hỏi. Mọi implementation (JSON, CSV, SQLite...) PHẢI
    có đủ các hàm này, đúng kiểu tham số/trả về.
    """

    @abstractmethod
    def add_question(self, question: Question) -> None: pass

    @abstractmethod
    def update_question(self, question_id: str, question: Question) -> None: pass

    @abstractmethod
    def delete_question(self, question_id: str) -> None: pass

    @abstractmethod
    def get_question(self, question_id: str) -> Optional[Question]: pass

    @abstractmethod
    def list_questions(self, topic_id: Optional[str] = None,
                       difficulty: Optional[DifficultyLevel] = None) -> list[Question]:
        """Lọc câu hỏi theo chủ đề và/hoặc mức độ."""
        pass

    @abstractmethod
    def count_questions(self, topic_id: str, difficulty: DifficultyLevel) -> int:
        """
        Đếm số câu theo (chủ đề, mức độ).
        [C] PHẢI gọi TRƯỚC khi sample() để tránh lỗi 'sample lớn hơn population'.
        """
        pass


class ExamGenerator(ABC):
    """
    [C] Tạo đề theo ma trận (rng.sample) và trộn câu/phương án theo seed.
    PHẢI dùng rng = random.Random(seed) RIÊNG cho từng lần tạo đề, KHÔNG dùng
    random.seed() toàn cục.
    """

    @abstractmethod
    def generate_exam(self, subject_id: str, title: str,
                      matrix: list[ExamMatrixItem], seed: int) -> Exam:
        """Sinh đề mới theo ma trận; lưu matrix vào Exam.matrix."""
        pass

    @abstractmethod
    def rebuild_exam(self, exam: Exam) -> Exam:
        """Tái lập đúng thứ tự câu/phương án từ exam.seed + exam.matrix đã lưu."""
        pass


class Grader(ABC):
    """[C] Chấm điểm và thống kê theo chủ đề."""

    @abstractmethod
    def grade(self, exam: Exam, questions: list[Question],
              answers: list[StudentAnswer]) -> ExamResult: pass

    @abstractmethod
    def topic_statistics(self, result: ExamResult) -> dict:
        """Trả {topic_id: {'correct': int, 'total': int, 'percent': float}} để [D] vẽ biểu đồ."""
        pass


class ExamExporter(ABC):
    """[D] Xuất đề và đáp án ra file JSON riêng biệt."""

    @abstractmethod
    def export_exam(self, exam: Exam, questions: list[Question], file_path: str) -> None:
        """Xuất đề (không kèm đáp án đúng)."""
        pass

    @abstractmethod
    def export_answer_key(self, exam: Exam, questions: list[Question], file_path: str) -> None:
        """Xuất riêng đáp án."""
        pass


# ============================================================
# 7. VÍ DỤ NHANH (chạy thử: python base_models.py)
# ============================================================

if __name__ == "__main__":
    subj = Subject.create("Lập trình Python")
    topic = Topic.create(subj.id, "Vòng lặp for/while")
    opts = [
        Option.create("for chạy trước khi kiểm tra điều kiện", False),
        Option.create("for lặp qua từng phần tử của một iterable", True),
        Option.create("while không thể dùng break", False),
        Option.create("for chỉ dùng được với số nguyên", False),
    ]
    q = Question.create(topic.id, "Đặc điểm nào đúng về vòng lặp for trong Python?",
                        DifficultyLevel.KHO, opts)
    print("Question hợp lệ?", q.is_valid())
    admin = User.create("admin", "hash", "salt", role=ROLE_ADMIN)
    print(type(admin).__name__, admin.can("manage_question"),
          User.create("sv", "h", "s").can("manage_question"))