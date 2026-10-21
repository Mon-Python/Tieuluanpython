"""
grader.py
==========
[C sở hữu] Chấm điểm bài làm và thống kê theo chủ đề.

Implement ABC Grader trong base_models.py.
"""

from collections import defaultdict

from base_models import (
    Grader as GraderABC,
    Exam, Question, StudentAnswer, ExamResult,
)


class GraderImpl(GraderABC):
    """
    Chấm bài làm: so sánh đáp án học sinh với đáp án đúng,
    tính điểm và thống kê đúng/tổng/phần trăm theo chủ đề.
    """

    def grade(self, exam: Exam, questions: list[Question],
              answers: list[StudentAnswer]) -> ExamResult:
        """
        Chấm bài và tạo ExamResult.

        Quy tắc:
        - Mỗi câu trả lời đúng = 1 điểm (đúng option_id).
        - Bỏ trống (selected_option_ids rỗng) = 0 điểm.
        - Điểm tổng = tổng điểm / tổng số câu * 10 (thang 10).
        - Nếu đề không có câu nào → điểm = 0 (tránh chia cho 0).
        """
        # Tra nhanh: question_id -> Question
        q_map: dict[str, Question] = {q.id: q for q in questions}

        # Tra nhanh: question_id -> StudentAnswer
        ans_map: dict[str, StudentAnswer] = {a.question_id: a for a in answers}

        total_questions = len(exam.question_ids)
        correct_count = 0

        # Thống kê theo chủ đề: {topic_id: {"correct": int, "total": int}}
        topic_data: dict[str, dict] = defaultdict(
            lambda: {"correct": 0, "total": 0}
        )

        for qid in exam.question_ids:
            question = q_map.get(qid)
            if question is None:
                # Câu hỏi bị xóa khỏi ngân hàng → bỏ qua
                continue

            topic_id = question.topic_id
            topic_data[topic_id]["total"] += 1

            # Lấy đáp án đúng
            correct_ids = set(question.correct_option_ids())

            # Lấy đáp án học sinh chọn
            student_ans = ans_map.get(qid)
            if student_ans and student_ans.selected_option_ids:
                selected = set(student_ans.selected_option_ids)
            else:
                selected = set()

            # So khớp (single choice: đúng khi chọn đúng 1 đáp án)
            if selected == correct_ids:
                correct_count += 1
                topic_data[topic_id]["correct"] += 1

        # Tính điểm thang 10 (tránh chia cho 0)
        if total_questions > 0:
            score = round(correct_count / total_questions * 10, 2)
        else:
            score = 0.0

        # Tính phần trăm cho từng chủ đề
        topic_stats: dict[str, dict] = {}
        for tid, data in topic_data.items():
            total = data["total"]
            correct = data["correct"]
            percent = round(correct / total * 100, 1) if total > 0 else 0.0
            topic_stats[tid] = {
                "correct": correct,
                "total": total,
                "percent": percent,
            }

        # Tạo ExamResult
        result = ExamResult.create(
            exam_id=exam.id,
            student_name="",  # GUI sẽ điền tên người dùng đang đăng nhập
        )
        result.answers = list(answers)
        result.score = score
        result.topic_stats = topic_stats

        return result

    def topic_statistics(self, result: ExamResult) -> dict:
        """
        Trả {topic_id: {'correct': int, 'total': int, 'percent': float}}.
        D dùng dữ liệu này để vẽ biểu đồ cột trên Canvas.

        Nếu result chưa có topic_stats (bài cũ) → trả dict rỗng.
        """
        return dict(result.topic_stats) if result.topic_stats else {}
