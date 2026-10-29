"""Create safe, repeatable sample subject, topic, and question data."""

import random
from typing import Optional

from base_models import DifficultyLevel, Question, Subject, Topic, Option
from data_repository import JsonDataRepository


_SAMPLE_BANK = {
    ("Lập trình Python", "Kiểu dữ liệu cơ bản"): [
        (DifficultyLevel.DE, "Kiểu dữ liệu nào biểu diễn số nguyên trong Python?",
         ("int", "str", "list", "dict"), 0),
        (DifficultyLevel.DE, "Giá trị nào sau đây có kiểu bool?",
         ("True", "'True'", "1.0", "None"), 0),
        (DifficultyLevel.DE, "Kiểu dữ liệu nào phù hợp để lưu nhiều phần tử có thứ tự?",
         ("list", "int", "bool", "float"), 0),
        (DifficultyLevel.KHO, "Biểu thức nào tạo một dictionary rỗng?",
         ("{}", "[]", "()", "set()"), 0),
        (DifficultyLevel.KHO, "Kết quả của len({'a': 1, 'b': 2}) là gì?",
         ("2", "1", "3", "Lỗi TypeError"), 0),
    ],
    ("Lập trình Python", "Điều khiển luồng"): [
        (DifficultyLevel.DE, "Từ khóa nào bắt đầu một nhánh điều kiện trong Python?",
         ("if", "for", "def", "import"), 0),
        (DifficultyLevel.DE, "Vòng lặp nào thường dùng để duyệt từng phần tử của danh sách?",
         ("for", "try", "with", "class"), 0),
        (DifficultyLevel.DE, "Từ khóa nào kết thúc vòng lặp ngay lập tức?",
         ("break", "continue", "pass", "return"), 0),
        (DifficultyLevel.KHO, "Trong vòng lặp, continue thực hiện điều gì?",
         ("Bỏ qua phần còn lại của lượt hiện tại",
          "Kết thúc toàn bộ chương trình",
          "Thoát khỏi vòng lặp",
          "Khởi tạo lại biến vòng lặp"), 0),
        (DifficultyLevel.KHO, "range(2, 8, 2) tạo ra dãy nào?",
         ("2, 4, 6", "2, 4, 6, 8", "1, 3, 5, 7", "2, 6, 8"), 0),
    ],
    ("Kinh tế vi mô", "Cung và cầu"): [
        (DifficultyLevel.DE, "Theo quy luật cầu, khi giá tăng thì lượng cầu thường thế nào?",
         ("Giảm", "Tăng", "Không đổi trong mọi trường hợp", "Bằng không"), 0),
        (DifficultyLevel.DE, "Đường cung thường dốc lên vì giá cao hơn khuyến khích điều gì?",
         ("Tăng lượng cung", "Giảm chi phí cố định", "Giảm nhu cầu", "Xóa bỏ khan hiếm"), 0),
        (DifficultyLevel.DE, "Điểm cân bằng thị trường xảy ra khi nào?",
         ("Lượng cung bằng lượng cầu",
          "Giá bằng không",
          "Lượng cung luôn lớn hơn lượng cầu",
          "Doanh nghiệp không có chi phí"), 0),
        (DifficultyLevel.KHO, "Nếu cầu tăng còn cung không đổi, giá cân bằng thường thay đổi ra sao?",
         ("Tăng", "Giảm", "Không đổi chắc chắn", "Bằng không"), 0),
        (DifficultyLevel.KHO, "Một yếu tố nào có thể làm đường cung dịch chuyển sang phải?",
         ("Công nghệ sản xuất tốt hơn",
          "Thuế sản xuất tăng",
          "Chi phí đầu vào tăng",
          "Số nhà sản xuất giảm"), 0),
    ],
    ("Kinh tế vi mô", "Chi phí và lựa chọn"): [
        (DifficultyLevel.DE, "Chi phí cơ hội của một lựa chọn là gì?",
         ("Giá trị của phương án tốt nhất bị từ bỏ",
          "Tổng doanh thu của mọi phương án",
          "Khoản tiền đã chi trong quá khứ",
          "Mức giá thị trường thấp nhất"), 0),
        (DifficultyLevel.DE, "Chi phí cố định trong ngắn hạn thường có đặc điểm nào?",
         ("Không đổi theo sản lượng trong phạm vi phù hợp",
          "Luôn bằng không",
          "Tăng đúng bằng sản lượng",
          "Chỉ xuất hiện khi doanh thu bằng không"), 0),
        (DifficultyLevel.DE, "Chi phí biến đổi thường thay đổi theo yếu tố nào?",
         ("Sản lượng sản xuất",
          "Tên doanh nghiệp",
          "Ngày thành lập doanh nghiệp",
          "Số trang trong báo cáo"), 0),
        (DifficultyLevel.KHO, "Chi phí cận biên được tính gần đúng bằng cách nào?",
         ("Mức tăng tổng chi phí chia cho mức tăng sản lượng",
          "Tổng doanh thu chia cho số khách hàng",
          "Chi phí cố định trừ lợi nhuận",
          "Giá bán nhân với chi phí cố định"), 0),
        (DifficultyLevel.KHO, "Khi lợi ích cận biên lớn hơn chi phí cận biên, lựa chọn hợp lý thường là gì?",
         ("Tăng hoạt động thêm một đơn vị",
          "Dừng mọi hoạt động ngay",
          "Giảm sản lượng về không",
          "Bỏ qua cả lợi ích và chi phí"), 0),
    ],
}

_MIN_QUESTIONS_PER_TOPIC = 4


def _normalized_name(name: str) -> str:
    return name.strip().casefold()


_SAMPLE_BANK_BY_NAME = {
    (_normalized_name(subject), _normalized_name(topic)): questions
    for (subject, topic), questions in _SAMPLE_BANK.items()
}


def _read_and_validate_rows(repository: JsonDataRepository):
    """Read both stores before any write, rejecting malformed or orphaned data."""
    store = repository.handler.read(repository.subjects_topics_path, default={})
    if not isinstance(store, dict):
        raise ValueError(
            f"File '{repository.subjects_topics_path.name}' phải là object."
        )
    subjects_rows = store.get("subjects", [])
    topics_rows = store.get("topics", [])
    if not isinstance(subjects_rows, list) or not isinstance(topics_rows, list):
        raise ValueError(
            f"File '{repository.subjects_topics_path.name}' phải chứa danh sách "
            "'subjects' và 'topics'."
        )
    if any(not isinstance(row, dict) for row in subjects_rows + topics_rows):
        raise ValueError(
            f"File '{repository.subjects_topics_path.name}' có bản ghi không hợp lệ."
        )

    question_rows = repository.handler.read(
        repository.questions_path, default=[]
    )
    if not isinstance(question_rows, list):
        raise ValueError(
            f"File '{repository.questions_path.name}' phải là danh sách."
        )
    if any(not isinstance(row, dict) for row in question_rows):
        raise ValueError(
            f"File '{repository.questions_path.name}' có bản ghi không hợp lệ."
        )

    subjects = repository.list_subjects()
    topics = repository.list_topics()
    questions = repository.list_questions()

    if not repository.subjects_topics_path.exists() and questions:
        raise ValueError(
            "Không thể khôi phục subjects_topics.json an toàn: "
            "các câu hỏi hiện có không cho biết môn học của từng chủ đề."
        )

    subject_ids = {subject.id for subject in subjects}
    topic_ids = {topic.id for topic in topics}
    if len(subject_ids) != len(subjects):
        raise ValueError("Dữ liệu môn học có ID trùng lặp.")
    if len(topic_ids) != len(topics):
        raise ValueError("Dữ liệu chủ đề có ID trùng lặp.")
    if len({_normalized_name(subject.name) for subject in subjects}) != len(subjects):
        raise ValueError("Dữ liệu môn học có tên trùng lặp.")
    if any(topic.subject_id not in subject_ids for topic in topics):
        raise ValueError("Có chủ đề tham chiếu đến môn học không tồn tại.")
    topic_names = [
        (topic.subject_id, _normalized_name(topic.name))
        for topic in topics
    ]
    if len(set(topic_names)) != len(topics):
        raise ValueError("Dữ liệu chủ đề có tên trùng trong cùng môn học.")

    question_ids = [question.id for question in questions]
    if len(set(question_ids)) != len(question_ids):
        raise ValueError("Dữ liệu câu hỏi có ID trùng lặp.")
    for question in questions:
        if question.topic_id not in topic_ids:
            raise ValueError(
                f"Câu hỏi '{question.id}' tham chiếu đến chủ đề "
                f"'{question.topic_id}' không tồn tại."
            )
        valid, reason = question.is_valid()
        if not valid:
            raise ValueError(
                f"Câu hỏi hiện có '{question.id}' không hợp lệ: {reason}."
            )

    return subjects, topics, questions


def _build_sample_questions(
    topic: Topic,
    subject_name: str,
    questions: list[Question],
    rng: random.Random,
) -> list[Question]:
    candidates = _SAMPLE_BANK_BY_NAME.get(
        (_normalized_name(subject_name), _normalized_name(topic.name)), []
    )
    existing_contents = {
        _normalized_name(question.content)
        for question in questions
        if question.topic_id == topic.id
    }
    needed = max(0, _MIN_QUESTIONS_PER_TOPIC - len(existing_contents))
    available = [
        item
        for item in candidates
        if _normalized_name(item[1]) not in existing_contents
    ]
    if needed > len(available):
        raise ValueError(
            f"Không đủ câu hỏi mẫu khác nhau cho chủ đề '{topic.name}'."
        )

    selected = rng.sample(available, needed)
    new_questions = []
    for difficulty, content, choices, correct_index in selected:
        shuffled_choices = [
            (choice, index == correct_index)
            for index, choice in enumerate(choices)
        ]
        rng.shuffle(shuffled_choices)
        options = [
            Option.create(choice, is_correct)
            for choice, is_correct in shuffled_choices
        ]
        question = Question.create(topic.id, content, difficulty, options)
        valid, reason = question.is_valid()
        if not valid:
            raise ValueError(
                f"Câu hỏi mẫu cho chủ đề '{topic.name}' không hợp lệ: {reason}."
            )
        new_questions.append(question)
    return new_questions


def seed_sample_data(
    repository: Optional[JsonDataRepository] = None,
    rng: Optional[random.Random] = None,
) -> None:
    """Add missing sample records while preserving valid existing learning data.

    Pass a repository with temporary paths in tests. ``rng`` can be a dedicated
    ``random.Random`` instance for repeatable sample selection.
    """
    repository = repository or JsonDataRepository()
    rng = rng or random.Random()

    subjects, topics, questions = _read_and_validate_rows(repository)
    subjects_to_add = []
    topics_to_add = []

    subjects_by_name = {
        _normalized_name(subject.name): subject for subject in subjects
    }
    topics_by_parent_and_name = {
        (topic.subject_id, _normalized_name(topic.name)): topic
        for topic in topics
    }

    target_topics: list[tuple[str, Subject, Topic]] = []
    for subject_name, topic_name in _SAMPLE_BANK:
        normalized_subject_name = _normalized_name(subject_name)
        subject = subjects_by_name.get(normalized_subject_name)
        if subject is None:
            subject = Subject.create(subject_name)
            subjects_by_name[normalized_subject_name] = subject
            subjects_to_add.append(subject)

        topic_key = (subject.id, _normalized_name(topic_name))
        topic = topics_by_parent_and_name.get(topic_key)
        if topic is None:
            topic = Topic.create(subject.id, topic_name)
            topics_by_parent_and_name[topic_key] = topic
            topics_to_add.append(topic)
        target_topics.append((subject_name, subject, topic))

    questions_to_add = []
    for subject_name, subject, topic in target_topics:
        questions_to_add.extend(
            _build_sample_questions(topic, subject_name, questions, rng)
        )

    for subject in subjects_to_add:
        repository.add_subject(subject)
    for topic in topics_to_add:
        repository.add_topic(topic)
    for question in questions_to_add:
        repository.add_question(question)


def seed_default_admin() -> None:
    """Admin seeding is pending the authentication API from the project owner."""
    raise NotImplementedError(
        "Chưa thể tạo Admin mặc định: cần API xác thực chính thức từ thành viên B."
    )


if __name__ == "__main__":
    seed_sample_data()
