"""
exam_generator.py
==================
[C sở hữu] Sinh đề thi theo ma trận mức độ bằng rng.sample(),
trộn câu hỏi và phương án theo seed.

Dùng random.Random(seed) RIÊNG cho từng lần tạo đề,
KHÔNG dùng random.seed() toàn cục (tránh ảnh hưởng module khác).
"""

import random
from typing import Union

from base_models import (
    ExamGenerator as ExamGeneratorABC,
    ExamMatrixItem, Exam, Question, DifficultyLevel,
    QuestionRepository,
)


class ExamGeneratorImpl(ExamGeneratorABC):
    """
    Implement ABC ExamGenerator.

    Luồng chính:
    1. Nhận ma trận (list[ExamMatrixItem]) — mỗi dòng nói lấy bao nhiêu
       câu ở chủ đề nào, mức độ nào.
    2. Kiểm tra đủ câu hỏi cho TỪNG dòng ma trận trước khi sample.
    3. Dùng rng = random.Random(seed) để sample, trộn câu, trộn phương án.
    4. Lưu thứ tự phương án đã trộn vào Exam.shuffled_options.
    """

    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    # ------------------------------------------------------------------
    # PUBLIC: generate_exam
    # ------------------------------------------------------------------

    def generate_exam(self, subject_id: str, title: str,
                      matrix: list[ExamMatrixItem], seed: int) -> Exam:
        """
        Sinh đề mới theo ma trận.

        Raises:
            ValueError – ma trận rỗng, num_questions <= 0,
                         hoặc ngân hàng không đủ câu.
        """
        # --- Validate input ---
        if not matrix:
            raise ValueError("Ma trận đề không được rỗng")

        for item in matrix:
            if item.num_questions <= 0:
                raise ValueError(
                    f"Số câu phải > 0 (chủ đề '{item.topic_id}', "
                    f"mức '{item.difficulty.value}')"
                )

        # --- Kiểm tra đủ câu trước khi sample ---
        for item in matrix:
            available = self.question_repo.count_questions(
                item.topic_id, item.difficulty
            )
            if available < item.num_questions:
                raise ValueError(
                    f"Không đủ câu hỏi: chủ đề '{item.topic_id}', "
                    f"mức '{item.difficulty.value}' — "
                    f"cần {item.num_questions}, chỉ có {available}"
                )

        # --- Sample câu hỏi ---
        rng = random.Random(seed)
        selected_questions: list[Question] = []

        for item in matrix:
            pool = self.question_repo.list_questions(
                topic_id=item.topic_id, difficulty=item.difficulty
            )
            chosen = rng.sample(pool, item.num_questions)
            selected_questions.extend(chosen)

        # --- Trộn thứ tự câu hỏi ---
        rng.shuffle(selected_questions)

        # --- Trộn thứ tự phương án từng câu ---
        shuffled_options: dict[str, list[str]] = {}
        for q in selected_questions:
            option_ids = [opt.id for opt in q.options]
            rng.shuffle(option_ids)
            shuffled_options[q.id] = option_ids

        # --- Tạo đối tượng Exam ---
        exam = Exam.create(
            subject_id=subject_id,
            title=title,
            seed=seed,
            matrix=matrix,
        )
        exam.question_ids = [q.id for q in selected_questions]
        exam.shuffled_options = shuffled_options

        return exam

    # ------------------------------------------------------------------
    # PUBLIC: rebuild_exam
    # ------------------------------------------------------------------

    def rebuild_exam(self, exam: Exam) -> Exam:
        """
        Tái lập đúng thứ tự câu hỏi và phương án từ exam.seed + exam.matrix
        đã lưu. Cùng seed + cùng ngân hàng câu hỏi → sinh lại đề y hệt.

        Raises:
            ValueError – nếu exam.matrix rỗng (không đủ thông tin tái lập).
        """
        if not exam.matrix:
            raise ValueError(
                "Đề thi không lưu ma trận — không thể tái lập. "
                "Chỉ có thể tái lập đề được tạo bởi hệ thống này."
            )

        rebuilt = self.generate_exam(
            subject_id=exam.subject_id,
            title=exam.title,
            matrix=exam.matrix,
            seed=exam.seed,
        )
        # Giữ nguyên id và created_at gốc
        rebuilt.id = exam.id
        rebuilt.created_at = exam.created_at
        return rebuilt
