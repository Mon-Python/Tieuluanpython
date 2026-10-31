"""Create a small starter question bank and default administrator account."""

from base_models import DifficultyLevel, Option, Question, Subject, Topic
from data_repository import JsonDataRepository
from auth import AuthManager
from config import ROLE_ADMIN


def _sample_question(topic_id, prompt, correct, distractors, difficulty):
    options = [Option.create(correct, True)]
    options.extend(Option.create(text) for text in distractors)
    return Question.create(topic_id, prompt, difficulty, options)


def initialize_sample_data(data_repo=None, auth_manager=None):
    """Seed empty stores without replacing any existing subjects, questions, or users."""
    data_repo = data_repo or JsonDataRepository()
    auth_manager = auth_manager or AuthManager()

    subjects = data_repo.list_subjects()
    if not subjects:
        subject = Subject.create(
            "Lập trình Python", "Kiến thức cơ bản về lập trình Python."
        )
        data_repo.add_subject(subject)
        subjects = [subject]

    topics = data_repo.list_topics()
    if not topics:
        topic = Topic.create(subjects[0].id, "Vòng lặp và danh sách")
        data_repo.add_topic(topic)
        topics = [topic]

    if not data_repo.list_questions():
        topic_id = topics[0].id
        questions = [
            _sample_question(
                topic_id,
                "Từ khóa nào thường được dùng để lặp qua các phần tử của một danh sách?",
                "for",
                ["class", "return", "import"],
                DifficultyLevel.DE,
            ),
            _sample_question(
                topic_id,
                "Chỉ số của phần tử đầu tiên trong một danh sách Python là bao nhiêu?",
                "0",
                ["1", "-1", "len(danh_sach)"],
                DifficultyLevel.DE,
            ),
            _sample_question(
                topic_id,
                "Hàm nào tạo một dãy số thường dùng cùng vòng lặp for?",
                "range()",
                ["print()", "input()", "type()"],
                DifficultyLevel.KHO,
            ),
        ]
        for question in questions:
            data_repo.add_question(question)

    if auth_manager.get_user_by_username("admin") is None:
        auth_manager.register(
            "admin", "admin123", role=ROLE_ADMIN
        )

    return data_repo
