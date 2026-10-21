"""
gui/take_exam_window.py
========================
[C sở hữu] Cửa sổ làm bài thi trắc nghiệm (Tkinter Toplevel).

Chức năng:
- Hiển thị bài thi theo danh sách câu hỏi và thứ tự phương án đã trộn (shuffled_options).
- Cho phép điều hướng từng câu hoặc nhảy nhanh qua bảng câu hỏi bên phải.
- Theo dõi tiến độ làm bài (câu đã làm / chưa làm).
- Hộp thoại cảnh báo khi đóng cửa sổ giữa chừng (chưa nộp bài).
- Xác nhận trước khi nộp bài (cảnh báo số câu chưa làm).
- Chấm điểm tự động qua Grader, lưu kết quả qua ExamRepository (nếu có).
- Chế độ xem lại bài thi (Review mode) sau khi nộp: hiện câu đúng/sai, đáp án đúng.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from base_models import (
    Exam, Question, Option, StudentAnswer, ExamResult, User,
)
from grader import GraderImpl
from config import (
    FONT_NORMAL, FONT_BOLD, FONT_TITLE, PADDING,
    COLOR_PRIMARY, COLOR_BG, COLOR_SUCCESS, COLOR_ERROR,
)


class TakeExamWindow(tk.Toplevel):
    """
    Cửa sổ làm bài thi.

    Parameters:
        parent       – widget cha
        exam         – đối tượng Exam
        data_repo    – JsonDataRepository (để lấy nội dung Question)
        grader       – GraderImpl (chấm bài)
        exam_repo    – ExamRepository (lưu kết quả, tùy chọn)
        user         – User đang đăng nhập (lấy tên học sinh)
        on_completed – callback(result: ExamResult) sau khi nộp và chấm điểm
    """

    def __init__(self, parent, exam: Exam, data_repo,
                 grader: Optional[GraderImpl] = None,
                 exam_repo=None,
                 user: Optional[User] = None,
                 on_completed: Optional[Callable[[ExamResult], None]] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self.exam = exam
        self.data_repo = data_repo
        self.grader = grader or GraderImpl()
        self.exam_repo = exam_repo
        self.user = user
        self.on_completed = on_completed

        # Tải danh sách câu hỏi
        self.questions: list[Question] = []
        self._load_questions()

        if not self.questions:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu câu hỏi cho đề thi này!")
            self.destroy()
            return

        # Trạng thái bài làm
        self.current_idx = 0
        # {question_id: selected_option_id}
        self.selected_answers: dict[str, str] = {}
        self.is_submitted = False
        self.result: Optional[ExamResult] = None

        # Thiết lập cửa sổ
        self.title(f"Làm bài thi: {self.exam.title}")
        self.geometry("900x650")
        self.minsize(800, 550)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Xây dựng giao diện
        self._build_ui()
        self._display_question(self.current_idx)

    # ==============================================================
    # KHỞI TẠO DỮ LIỆU
    # ==============================================================

    def _load_questions(self):
        """Tải các câu hỏi theo thứ tự question_ids trong đề."""
        for qid in self.exam.question_ids:
            q = self.data_repo.get_question(qid)
            if q is not None:
                self.questions.append(q)

    # ==============================================================
    # GIAO DIỆN CHÍNH
    # ==============================================================

    def _build_ui(self):
        self.columnconfigure(0, weight=3)  # Vùng câu hỏi
        self.columnconfigure(1, weight=1)  # Bảng điều hướng
        self.rowconfigure(1, weight=1)

        # 1. Header
        header_frame = ttk.Frame(self, padding=PADDING)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        student_name = self.user.username if self.user and self.user.username else "Thí sinh"
        lbl_exam_title = ttk.Label(
            header_frame,
            text=f"Đề thi: {self.exam.title}",
            font=FONT_TITLE,
            foreground=COLOR_PRIMARY,
        )
        lbl_exam_title.pack(side="left")

        self.lbl_info = ttk.Label(
            header_frame,
            text=f"Thí sinh: {student_name} | Số câu: {len(self.questions)}",
            font=FONT_BOLD,
        )
        self.lbl_info.pack(side="right")

        # 2. Main Question Frame (Bên trái)
        self.question_frame = ttk.LabelFrame(self, text="Nội dung câu hỏi", padding=PADDING * 2)
        self.question_frame.grid(row=1, column=0, sticky="nsew", padx=PADDING, pady=PADDING)
        self.question_frame.columnconfigure(0, weight=1)
        self.question_frame.rowconfigure(1, weight=1)

        # Tiêu đề số thứ tự câu hỏi
        self.lbl_q_number = ttk.Label(self.question_frame, text="", font=FONT_BOLD)
        self.lbl_q_number.grid(row=0, column=0, sticky="w", pady=(0, 6))

        # Nội dung câu hỏi
        self.txt_q_content = tk.Text(
            self.question_frame,
            wrap="word",
            height=5,
            font=FONT_NORMAL,
            relief="solid",
            bd=1,
            padx=8,
            pady=8,
        )
        self.txt_q_content.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.txt_q_content.config(state="disabled")

        # Khung chứa 4 phương án trắc nghiệm
        self.options_frame = ttk.Frame(self.question_frame)
        self.options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.options_frame.columnconfigure(0, weight=1)

        self.opt_var = tk.StringVar(value="")
        self.opt_radios: list[ttk.Radiobutton] = []
        self.opt_labels: list[ttk.Label] = []

        labels = ["A", "B", "C", "D"]
        for i in range(4):
            opt_row = ttk.Frame(self.options_frame)
            opt_row.grid(row=i, column=0, sticky="w", pady=4)

            radio = ttk.Radiobutton(
                opt_row,
                text="",
                value="",
                variable=self.opt_var,
                command=self._on_option_selected,
            )
            radio.pack(side="left")

            lbl_feedback = ttk.Label(opt_row, text="", font=FONT_BOLD)
            lbl_feedback.pack(side="left", padx=8)

            self.opt_radios.append(radio)
            self.opt_labels.append(lbl_feedback)

        # Thanh điều hướng câu (Trước / Bỏ chọn / Tiếp theo)
        nav_btns_frame = ttk.Frame(self.question_frame)
        nav_btns_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        self.btn_prev = ttk.Button(nav_btns_frame, text="◀ Câu trước", command=self._prev_question)
        self.btn_prev.pack(side="left", padx=4)

        self.btn_clear = ttk.Button(nav_btns_frame, text="Bỏ chọn", command=self._clear_selection)
        self.btn_clear.pack(side="left", padx=4)

        self.btn_next = ttk.Button(nav_btns_frame, text="Câu tiếp ▶", command=self._next_question)
        self.btn_next.pack(side="left", padx=4)

        # 3. Sidebar (Bên phải - Danh sách câu hỏi & Nộp bài)
        sidebar_frame = ttk.LabelFrame(self, text="Tiến độ & Điều hướng", padding=PADDING)
        sidebar_frame.grid(row=1, column=1, sticky="nsew", padx=(0, PADDING), pady=PADDING)
        sidebar_frame.columnconfigure(0, weight=1)
        sidebar_frame.rowconfigure(1, weight=1)

        self.lbl_progress = ttk.Label(sidebar_frame, text="Đã làm: 0/0 câu", font=FONT_BOLD)
        self.lbl_progress.grid(row=0, column=0, pady=(0, 8), sticky="w")

        # Khung chứa các nút câu hỏi dạng lưới cuộn được
        btn_canvas = tk.Canvas(sidebar_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar_frame, orient="vertical", command=btn_canvas.yview)
        self.grid_frame = ttk.Frame(btn_canvas)

        self.grid_frame.bind(
            "<Configure>",
            lambda e: btn_canvas.configure(scrollregion=btn_canvas.bbox("all")),
        )
        btn_canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        btn_canvas.configure(yscrollcommand=scrollbar.set)

        btn_canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Tạo các nút số câu hỏi
        self.q_buttons: list[tk.Button] = []
        cols = 4
        for idx in range(len(self.questions)):
            r, c = divmod(idx, cols)
            btn = tk.Button(
                self.grid_frame,
                text=str(idx + 1),
                width=4,
                relief="groove",
                command=lambda i=idx: self._jump_to_question(i),
            )
            btn.grid(row=r, column=c, padx=3, pady=3)
            self.q_buttons.append(btn)

        # Nút nộp bài
        self.btn_submit = tk.Button(
            sidebar_frame,
            text="🏁 NỘP BÀI",
            font=FONT_BOLD,
            bg=COLOR_PRIMARY,
            fg="white",
            relief="raised",
            pady=8,
            command=self._confirm_submit,
        )
        self.btn_submit.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    # ==============================================================
    # HIỂN THỊ CÂU HỎI
    # ==============================================================

    def _display_question(self, index: int):
        """Hiển thị nội dung câu hỏi tại vị trí index."""
        if not (0 <= index < len(self.questions)):
            return

        self.current_idx = index
        q = self.questions[index]

        # Cập nhật số thứ tự và nội dung
        self.lbl_q_number.config(
            text=f"Câu {index + 1} / {len(self.questions)}  [Mức độ: {q.difficulty.value.upper()}]"
        )
        self.txt_q_content.config(state="normal")
        self.txt_q_content.delete("1.0", "end")
        self.txt_q_content.insert("1.0", q.content)
        self.txt_q_content.config(state="disabled")

        # Lấy thứ tự phương án đã trộn từ exam.shuffled_options
        shuffled_ids = self.exam.shuffled_options.get(q.id)
        if not shuffled_ids:
            shuffled_ids = [opt.id for opt in q.options]

        opt_by_id = {opt.id: opt for opt in q.options}
        ordered_options = [opt_by_id[oid] for oid in shuffled_ids if oid in opt_by_id]

        # Đặt lại Radiobuttons
        self.opt_var.set(self.selected_answers.get(q.id, ""))

        labels = ["A", "B", "C", "D"]
        for i, opt in enumerate(ordered_options):
            if i < len(self.opt_radios):
                radio = self.opt_radios[i]
                lbl_feedback = self.opt_labels[i]

                radio.config(
                    text=f"{labels[i]}.  {opt.content}",
                    value=opt.id,
                    state="disabled" if self.is_submitted else "normal",
                )

                # Chế độ xem lại (Review mode)
                if self.is_submitted:
                    if opt.is_correct:
                        lbl_feedback.config(text="✓ Đáp án đúng", foreground=COLOR_SUCCESS)
                    elif self.selected_answers.get(q.id) == opt.id:
                        lbl_feedback.config(text="✗ Bạn đã chọn", foreground=COLOR_ERROR)
                    else:
                        lbl_feedback.config(text="")
                else:
                    lbl_feedback.config(text="")

        # Cập nhật trạng thái các nút Trước / Tiếp
        self.btn_prev.config(state="normal" if index > 0 else "disabled")
        self.btn_next.config(state="normal" if index < len(self.questions) - 1 else "disabled")
        if self.is_submitted:
            self.btn_clear.config(state="disabled")

        self._update_progress_and_buttons()

    def _update_progress_and_buttons(self):
        """Cập nhật màu sắc các nút ở bảng điều hướng và nhãn tiến độ."""
        answered_count = len(self.selected_answers)
        total = len(self.questions)
        self.lbl_progress.config(text=f"Đã làm: {answered_count}/{total} câu")

        for idx, btn in enumerate(self.q_buttons):
            qid = self.questions[idx].id
            is_answered = qid in self.selected_answers

            if self.is_submitted:
                # Nếu đã nộp bài: đúng xanh lá, sai đỏ, bỏ trống xám
                q = self.questions[idx]
                correct_id = q.correct_option_ids()[0] if q.correct_option_ids() else ""
                chosen_id = self.selected_answers.get(qid, "")
                if chosen_id == correct_id:
                    btn.config(bg="#bbf7d0", fg="#166534")  # Xanh nhạt
                else:
                    btn.config(bg="#fecaca", fg="#991b1b")  # Đỏ nhạt
            else:
                if idx == self.current_idx:
                    btn.config(relief="solid", bd=2)
                else:
                    btn.config(relief="groove", bd=1)

                if is_answered:
                    btn.config(bg="#dbeafe", fg="#1e40af")  # Đã làm: xanh dương
                else:
                    btn.config(bg="#f1f5f9", fg="#334155")  # Chưa làm: xám

    # ==============================================================
    # XỬ LÝ LỰA CHỌN ĐÁP ÁN & ĐIỀU HƯỚNG
    # ==============================================================

    def _on_option_selected(self):
        """Lưu đáp án đã chọn cho câu hiện tại."""
        if self.is_submitted:
            return
        qid = self.questions[self.current_idx].id
        selected = self.opt_var.get()
        if selected:
            self.selected_answers[qid] = selected
        self._update_progress_and_buttons()

    def _clear_selection(self):
        """Bỏ chọn đáp án cho câu hỏi hiện tại."""
        if self.is_submitted:
            return
        qid = self.questions[self.current_idx].id
        if qid in self.selected_answers:
            del self.selected_answers[qid]
        self.opt_var.set("")
        self._update_progress_and_buttons()

    def _prev_question(self):
        if self.current_idx > 0:
            self._display_question(self.current_idx - 1)

    def _next_question(self):
        if self.current_idx < len(self.questions) - 1:
            self._display_question(self.current_idx + 1)

    def _jump_to_question(self, index: int):
        self._display_question(index)

    # ==============================================================
    # NỘP BÀI & CHẤM ĐIỂM
    # ==============================================================

    def _confirm_submit(self):
        """Xác nhận trước khi nộp bài."""
        if self.is_submitted:
            self.destroy()
            return

        total = len(self.questions)
        answered = len(self.selected_answers)
        unanswered = total - answered

        if unanswered > 0:
            msg = (
                f"Bạn còn {unanswered} câu chưa trả lời!\n\n"
                "Bạn có chắc chắn muốn nộp bài ngay bây giờ không?"
            )
        else:
            msg = "Bạn đã hoàn thành tất cả câu hỏi.\nBạn có chắc chắn muốn nộp bài không?"

        if not messagebox.askyesno("Xác nhận nộp bài", msg, parent=self):
            return

        self._submit_and_grade()

    def _submit_and_grade(self):
        """Thu thập bài làm, gọi Grader chấm điểm và lưu kết quả."""
        self.is_submitted = True

        # Gom danh sách StudentAnswer
        student_answers: list[StudentAnswer] = []
        for q in self.questions:
            chosen = self.selected_answers.get(q.id)
            selected_ids = [chosen] if chosen else []
            student_answers.append(
                StudentAnswer(question_id=q.id, selected_option_ids=selected_ids)
            )

        # Chấm bài qua Grader
        self.result = self.grader.grade(self.exam, self.questions, student_answers)
        student_name = self.user.username if self.user and self.user.username else "Thí sinh"
        self.result.student_name = student_name

        # Lưu kết quả qua exam_repository nếu có
        if self.exam_repo is not None:
            try:
                if hasattr(self.exam_repo, "save_result"):
                    self.exam_repo.save_result(self.result)
            except Exception as e:
                messagebox.showwarning("Lưu kết quả", f"Không thể lưu kết quả bài thi: {e}", parent=self)

        # Thông báo callback
        if self.on_completed:
            try:
                self.on_completed(self.result)
            except Exception:
                pass

        # Cập nhật giao diện sang chế độ xem lại
        self.btn_submit.config(text="✕ ĐÓNG CỬA SỔ", bg="#64748b")
        self._show_result_summary()
        self._display_question(self.current_idx)

    def _show_result_summary(self):
        """Hiện thông báo kết quả bài thi và thống kê theo chủ đề."""
        if not self.result:
            return

        correct_count = sum(
            1 for q in self.questions
            if self.selected_answers.get(q.id) in q.correct_option_ids()
        )
        total = len(self.questions)

        stats_lines = []
        for tid, data in self.result.topic_stats.items():
            topic = self.data_repo.get_topic(tid)
            topic_name = topic.name if topic else tid
            stats_lines.append(
                f"- {topic_name}: {data['correct']}/{data['total']} câu ({data['percent']}%)"
            )

        detail_text = (
            f"Điểm số: {self.result.score} / 10\n"
            f"Số câu đúng: {correct_count} / {total}\n\n"
            "Thống kê theo chủ đề:\n" + "\n".join(stats_lines) + "\n\n"
            "Bạn có thể xem lại từng câu hỏi để đối chiếu đáp án đúng."
        )

        messagebox.showinfo("Kết quả thi", detail_text, parent=self)

    # ==============================================================
    # ĐÓNG CỬA SỔ
    # ==============================================================

    def _on_window_close(self):
        """Cảnh báo khi người dùng đóng cửa sổ giữa chừng chưa nộp bài."""
        if not self.is_submitted:
            if not messagebox.askyesno(
                "Cảnh báo",
                "Bài làm chưa được nộp!\nNếu bạn thoát bây giờ, kết quả sẽ không được lưu.\n\n"
                "Bạn có chắc chắn muốn thoát không?",
                parent=self,
            ):
                return
        self.destroy()
