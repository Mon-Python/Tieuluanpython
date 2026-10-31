"""
gui/take_exam_window.py
========================
Cửa sổ làm bài trắc nghiệm và xem lại kết quả bằng Tkinter.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional

from base_models import Exam, ExamResult, Question, StudentAnswer, User
from config import (
    COLOR_ERROR,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    FONT_BOLD,
    FONT_NORMAL,
    FONT_TITLE,
    PADDING,
)
from grader import GraderImpl


class TakeExamWindow(tk.Toplevel):
    """Cửa sổ hiển thị toàn bộ câu hỏi theo thứ tự từ trên xuống."""

    def __init__(
        self,
        parent,
        exam: Exam,
        data_repo,
        grader: Optional[GraderImpl] = None,
        exam_repo=None,
        user: Optional[User] = None,
        on_completed: Optional[Callable[[ExamResult], None]] = None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.exam = exam
        self.data_repo = data_repo
        self.grader = grader or GraderImpl()
        self.exam_repo = exam_repo
        self.user = user
        self.on_completed = on_completed

        self.questions: list[Question] = []
        self._load_questions()
        if not self.questions:
            messagebox.showerror(
                "Lỗi", "Không tìm thấy dữ liệu câu hỏi cho đề thi này!",
                parent=self,
            )
            self.destroy()
            return

        invalid_question = next(
            (question for question in self.questions
             if len(question.options) != 4),
            None,
        )
        if invalid_question is not None:
            messagebox.showerror(
                "Lỗi",
                f"Câu hỏi '{invalid_question.id}' không có đúng 4 phương án.",
                parent=self,
            )
            self.destroy()
            return

        self.selected_answers: dict[str, str] = {}
        self.is_submitted = False
        self.result: Optional[ExamResult] = None
        self.question_widgets = {}

        self.title(f"Làm bài thi: {self.exam.title}")
        self.geometry("900x700")
        self.minsize(700, 500)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._build_ui()

    def _load_questions(self):
        """Tải câu hỏi theo đúng thứ tự đã lưu trong đề."""
        for question_id in self.exam.question_ids:
            question = self.data_repo.get_question(question_id)
            if question is not None:
                self.questions.append(question)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, padding=PADDING)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(
            header,
            text=f"Đề thi: {self.exam.title}",
            font=FONT_TITLE,
            foreground=COLOR_PRIMARY,
        ).grid(row=0, column=0, sticky="w")

        student_name = (
            self.user.username if self.user and self.user.username
            else "Thí sinh"
        )
        ttk.Label(
            header,
            text=f"Thí sinh: {student_name} | Số câu: {len(self.questions)}",
            font=FONT_BOLD,
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))
        ttk.Button(
            header, text="Thoát", command=self._on_window_close
        ).grid(row=0, column=2, padx=(8, 0))

        self.lbl_result = ttk.Label(
            self,
            text="",
            font=FONT_BOLD,
            justify=tk.LEFT,
            wraplength=840,
            takefocus=True,
        )
        self.lbl_result.grid(
            row=1, column=0, sticky="ew", padx=PADDING, pady=(0, PADDING)
        )

        content = ttk.Frame(self)
        content.grid(
            row=2, column=0, sticky="nsew", padx=PADDING, pady=(0, PADDING)
        )
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self.question_canvas = tk.Canvas(
            content,
            highlightthickness=2,
            highlightbackground="#64748b",
            highlightcolor=COLOR_PRIMARY,
            takefocus=True,
        )
        scrollbar = ttk.Scrollbar(
            content, orient="vertical", command=self.question_canvas.yview
        )
        self.question_canvas.configure(yscrollcommand=scrollbar.set)
        self.question_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        for key in ("<Up>", "<Down>", "<Prior>", "<Next>"):
            self.question_canvas.bind(key, self._scroll_questions)

        self.questions_frame = ttk.Frame(self.question_canvas)
        self.questions_window = self.question_canvas.create_window(
            (0, 0), window=self.questions_frame, anchor="nw"
        )
        self.question_canvas.bind("<Configure>", self._resize_question_content)
        self.questions_frame.bind(
            "<Configure>",
            lambda _event: self.question_canvas.configure(
                scrollregion=self.question_canvas.bbox("all")
            ),
        )

        for index, question in enumerate(self.questions):
            self._build_question(index, question)

        footer = ttk.Frame(self, padding=PADDING)
        footer.grid(row=3, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.lbl_progress = ttk.Label(
            footer,
            text=f"Đã làm: 0/{len(self.questions)} câu",
            font=FONT_BOLD,
        )
        self.lbl_progress.grid(row=0, column=0, sticky="w")
        self.btn_exit = ttk.Button(
            footer, text="Thoát", command=self._on_window_close
        )
        self.btn_exit.grid(row=0, column=1, padx=(8, 0))
        self.btn_submit = ttk.Button(
            footer, text="Hoàn thành", command=self._confirm_submit
        )
        self.btn_submit.grid(row=0, column=2, padx=(8, 0))

    def _build_question(self, index: int, question: Question):
        card = ttk.LabelFrame(
            self.questions_frame, text=f"Câu {index + 1}", padding=PADDING
        )
        card.pack(fill=tk.X, padx=4, pady=4)
        card.columnconfigure(0, weight=1)

        status = ttk.Label(card, text="Chưa trả lời", font=FONT_BOLD)
        status.grid(row=0, column=0, sticky="w", pady=(0, 4))
        content = ttk.Label(
            card,
            text=question.content,
            font=FONT_NORMAL,
            wraplength=720,
            justify=tk.LEFT,
        )
        content.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        option_by_id = {option.id: option for option in question.options}
        ordered_ids = self.exam.shuffled_options.get(question.id, [])
        seen_ids = set()
        ordered_options = []
        for option_id in ordered_ids:
            option = option_by_id.get(option_id)
            if option is not None and option_id not in seen_ids:
                ordered_options.append(option)
                seen_ids.add(option_id)
        ordered_options.extend(
            option for option in question.options if option.id not in seen_ids
        )

        answer_var = tk.StringVar(value="")
        option_rows = []
        for option_index, option in enumerate(ordered_options):
            row = ttk.Frame(card)
            row.grid(row=option_index + 2, column=0, sticky="ew", pady=2)
            row.columnconfigure(0, weight=1)

            radio = ttk.Radiobutton(
                row,
                text=f"{'ABCD'[option_index]}. {option.content}",
                value=option.id,
                variable=answer_var,
                command=lambda qid=question.id, var=answer_var:
                    self._on_option_selected(qid, var.get()),
            )
            radio.bind(
                "<FocusIn>",
                lambda event: self._ensure_question_visible(event.widget),
            )
            radio.grid(row=0, column=0, sticky="w")
            feedback = ttk.Label(row, text="", font=FONT_BOLD)
            feedback.grid(row=0, column=1, sticky="e", padx=(8, 0))
            option_rows.append((option, radio, feedback))

        self.question_widgets[question.id] = {
            "status": status,
            "content": content,
            "answer_var": answer_var,
            "options": option_rows,
        }

    def _resize_question_content(self, event):
        self.question_canvas.itemconfigure(
            self.questions_window, width=event.width
        )
        wraplength = max(200, event.width - 48)
        for widgets in self.question_widgets.values():
            widgets["content"].config(wraplength=wraplength)

    def _ensure_question_visible(self, widget):
        self.question_canvas.update_idletasks()
        region = self.question_canvas.bbox("all")
        if region is None:
            return

        canvas_top = self.question_canvas.canvasy(0)
        canvas_bottom = canvas_top + self.question_canvas.winfo_height()
        widget_top = (
            widget.winfo_rooty() - self.question_canvas.winfo_rooty()
            + canvas_top
        )
        widget_bottom = widget_top + widget.winfo_height()
        if widget_top < canvas_top:
            self.question_canvas.yview_moveto(widget_top / max(1, region[3]))
        elif widget_bottom > canvas_bottom:
            target_top = widget_bottom - self.question_canvas.winfo_height()
            self.question_canvas.yview_moveto(target_top / max(1, region[3]))

    def _scroll_questions(self, event):
        if event.keysym == "Up":
            self.question_canvas.yview_scroll(-1, "units")
        elif event.keysym == "Down":
            self.question_canvas.yview_scroll(1, "units")
        elif event.keysym == "Prior":
            self.question_canvas.yview_scroll(-1, "pages")
        else:
            self.question_canvas.yview_scroll(1, "pages")
        return "break"

    def _on_option_selected(self, question_id: str, option_id: str):
        if self.is_submitted:
            return
        self.selected_answers[question_id] = option_id
        self.lbl_progress.config(
            text=f"Đã làm: {len(self.selected_answers)}/{len(self.questions)} câu"
        )

    def _confirm_submit(self):
        if self.is_submitted:
            return

        unanswered = len(self.questions) - len(self.selected_answers)
        if unanswered:
            message = (
                f"Bạn còn {unanswered} câu chưa trả lời.\n"
                "Bạn có chắc chắn muốn hoàn thành bài kiểm tra không?"
            )
        else:
            message = (
                "Bạn đã hoàn thành tất cả câu hỏi.\n"
                "Bạn có chắc chắn muốn nộp bài không?"
            )

        if messagebox.askyesno("Xác nhận hoàn thành", message, parent=self):
            self._submit_and_grade()

    def _submit_and_grade(self):
        if self.is_submitted:
            return

        student_answers = [
            StudentAnswer(
                question_id=question.id,
                selected_option_ids=(
                    [self.selected_answers[question.id]]
                    if question.id in self.selected_answers else []
                ),
            )
            for question in self.questions
        ]
        result = self.grader.grade(self.exam, self.questions, student_answers)
        result.student_name = (
            self.user.username if self.user and self.user.username
            else "Thí sinh"
        )

        if self.exam_repo is not None and hasattr(self.exam_repo, "save_result"):
            try:
                self.exam_repo.save_result(result)
            except (OSError, ValueError) as exc:
                messagebox.showwarning(
                    "Lưu kết quả",
                    f"Không thể lưu kết quả bài thi: {exc}",
                    parent=self,
                )

        self.result = result
        self.is_submitted = True
        self.btn_submit.config(state="disabled")
        for index, question in enumerate(self.questions):
            widgets = self.question_widgets[question.id]
            is_correct = self._is_correct(question)
            widgets["status"].config(
                text=(
                    f"Câu {index + 1} - {'ĐÚNG' if is_correct else 'SAI'}"
                ),
                foreground=COLOR_SUCCESS if is_correct else COLOR_ERROR,
            )
            for option, radio, feedback in widgets["options"]:
                radio.config(state="disabled")
                if option.is_correct:
                    feedback.config(
                        text="✓ Đáp án đúng", foreground=COLOR_SUCCESS
                    )
                elif self.selected_answers.get(question.id) == option.id:
                    feedback.config(
                        text="✗ Bạn đã chọn", foreground=COLOR_ERROR
                    )

        self.lbl_progress.config(
            text=f"Đã hoàn thành: {len(self.questions)}/{len(self.questions)} câu"
        )
        self._show_result_summary()

        if self.on_completed is not None:
            try:
                self.on_completed(result)
            except Exception as exc:
                messagebox.showwarning(
                    "Cập nhật thống kê",
                    f"Không thể cập nhật thống kê sau khi nộp bài: {exc}",
                    parent=self,
                )

    def _is_correct(self, question: Question) -> bool:
        selected = self.selected_answers.get(question.id)
        return bool(selected) and {selected} == set(question.correct_option_ids())

    def _show_result_summary(self):
        if self.result is None:
            return

        correct_count = sum(
            self._is_correct(question) for question in self.questions
        )
        stats_lines = []
        for topic_id, data in self.result.topic_stats.items():
            topic = self.data_repo.get_topic(topic_id)
            topic_name = topic.name if topic else topic_id
            stats_lines.append(
                f"• {topic_name}: {data['correct']}/{data['total']} câu "
                f"({data['percent']}%)"
            )
        summary = (
            f"Kết quả: {self.result.score}/10 | "
            f"Số câu đúng: {correct_count}/{len(self.questions)}"
        )
        if stats_lines:
            summary += "\n" + "\n".join(stats_lines)
        self.lbl_result.config(text=summary, foreground=COLOR_PRIMARY)
        self.lbl_result.focus_set()

    def _on_window_close(self):
        """Yêu cầu xác nhận khi thoát trước khi nộp bài."""
        if not self.is_submitted and not messagebox.askyesno(
            "Thoát bài kiểm tra",
            "Bài làm chưa được hoàn thành và kết quả sẽ không được lưu.\n"
            "Bạn có chắc chắn muốn thoát không?",
            parent=self,
        ):
            return
        self.destroy()
