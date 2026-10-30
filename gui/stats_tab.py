"""
gui/stats_tab.py
================
[D sở hữu] Tab Thống kê kết quả thi & phân tích tỷ lệ đúng theo chủ đề.
"""

import logging
import math
from tkinter import ttk, messagebox

from base_models import User
from config import (
    FONT_NORMAL, FONT_BOLD, FONT_TITLE, PADDING
)
from gui.bar_chart import BarChart

logger = logging.getLogger(__name__)


class StatsTab(ttk.Frame):
    """
    Tab Thống kê theo chủ đề và xem chi tiết bài làm.

    Parameters:
        parent      – Widget cha (thường là Notebook)
        data_repo   – JsonDataRepository (A) để tra cứu tên Môn / Chủ đề
        exam_repo   – ExamRepository (D) để đọc danh sách Đề & Kết quả thi
        grader      – GraderImpl (C) cung cấp hàm topic_statistics
        user        – Đối tượng User đang đăng nhập (Admin xem hết, User xem của mình)
    """

    def __init__(self, parent, data_repo, exam_repo, grader, user: User, **kwargs):
        super().__init__(parent, **kwargs)
        self.data_repo = data_repo
        self.exam_repo = exam_repo
        self.grader = grader
        self.user = user

        self._exams_cache = []
        self._results_cache = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        row = 0

        # ---------- Tiêu đề ----------
        lbl_title = ttk.Label(self, text="Thống kê & Phân tích Kết quả Thi", font=FONT_TITLE)
        lbl_title.grid(row=row, column=0, sticky="w", padx=PADDING, pady=(PADDING, 4))
        row += 1

        # ---------- Bộ lọc và Chọn Kết quả ----------
        frame_filter = ttk.LabelFrame(self, text="Chọn bài làm cần xem thống kê", padding=PADDING)
        frame_filter.grid(row=row, column=0, sticky="ew", padx=PADDING, pady=4)
        frame_filter.columnconfigure(1, weight=1)

        r = 0
        # Chọn đề thi
        ttk.Label(frame_filter, text="Đề thi:", font=FONT_NORMAL).grid(row=r, column=0, sticky="w", pady=2)
        self.cmb_exam = ttk.Combobox(frame_filter, state="readonly", font=FONT_NORMAL)
        self.cmb_exam.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=2)
        self.cmb_exam.bind("<<ComboboxSelected>>", self._on_exam_selected)
        r += 1

        # Chọn lượt làm bài
        ttk.Label(frame_filter, text="Bài làm:", font=FONT_NORMAL).grid(row=r, column=0, sticky="w", pady=2)
        self.cmb_result = ttk.Combobox(frame_filter, state="readonly", font=FONT_NORMAL)
        self.cmb_result.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=2)
        self.cmb_result.bind("<<ComboboxSelected>>", self._on_result_selected)

        row += 1

        # ---------- Khung nội dung chính (Chia 2 bên: Bảng tóm tắt & Biểu đồ Canvas) ----------
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.grid(row=row, column=0, sticky="nsew", padx=PADDING, pady=4)

        # Bên trái: Thông tin tổng quan & Bảng chủ đề
        frame_left = ttk.Frame(paned, padding=PADDING)
        paned.add(frame_left, weight=1)

        frame_left.columnconfigure(0, weight=1)
        frame_left.rowconfigure(2, weight=1)

        # Thẻ thông tin điểm số
        self.frame_summary = ttk.LabelFrame(frame_left, text="Tổng quan", padding=PADDING)
        self.frame_summary.grid(row=0, column=0, sticky="ew", pady=(0, PADDING))

        self.lbl_score = ttk.Label(self.frame_summary, text="Điểm số: -- / 10", font=FONT_BOLD)
        self.lbl_score.pack(anchor="w", pady=2)
        self.lbl_student = ttk.Label(self.frame_summary, text="Thí sinh: --", font=FONT_NORMAL)
        self.lbl_student.pack(anchor="w", pady=2)

        # Bảng danh sách chủ đề & tỷ lệ đúng
        ttk.Label(frame_left, text="Chi tiết theo chủ đề:", font=FONT_BOLD).grid(row=1, column=0, sticky="w", pady=2)

        cols = ("topic_name", "correct", "total", "percent")
        self.tree_stats = ttk.Treeview(frame_left, columns=cols, show="headings", height=8)
        self.tree_stats.heading("topic_name", text="Chủ đề")
        self.tree_stats.heading("correct", text="Số câu đúng")
        self.tree_stats.heading("total", text="Tổng số câu")
        self.tree_stats.heading("percent", text="Tỷ lệ đúng")

        self.tree_stats.column("topic_name", width=150)
        self.tree_stats.column("correct", width=80, anchor="center")
        self.tree_stats.column("total", width=80, anchor="center")
        self.tree_stats.column("percent", width=90, anchor="center")

        self.tree_stats.grid(row=2, column=0, sticky="nsew")

        # Scrollbar cho Treeview
        sb = ttk.Scrollbar(frame_left, orient="vertical", command=self.tree_stats.yview)
        self.tree_stats.configure(yscrollcommand=sb.set)
        sb.grid(row=2, column=1, sticky="ns")

        # Bên phải: Biểu đồ cột Canvas
        frame_right = ttk.LabelFrame(paned, text="Biểu đồ tỷ lệ đúng theo chủ đề (%)", padding=PADDING)
        paned.add(frame_right, weight=2)
        frame_right.columnconfigure(0, weight=1)
        frame_right.rowconfigure(0, weight=1)

        self.bar_chart = BarChart(frame_right, title="", max_value=100.0, unit="%")
        self.bar_chart.grid(row=0, column=0, sticky="nsew")

    # ==============================================================
    # XỬ LÝ DỮ LIỆU & SỰ KIỆN
    # ==============================================================

    def refresh(self):
        """Cập nhật danh sách Đề thi và Kết quả."""
        self._exams_cache = []
        self._results_cache = []
        self._current_filtered_results = []
        self.cmb_exam["values"] = []
        self.cmb_exam.set("")
        self.cmb_result["values"] = []
        self.cmb_result.set("")
        self._clear_display()

        if self.user.can("view_all_stats"):
            can_view_all = True
        elif self.user.can("view_own_stats"):
            can_view_all = False
        else:
            self.cmb_exam.set("Không có quyền xem thống kê")
            self.cmb_result.set("")
            messagebox.showerror(
                "Không có quyền",
                "Tài khoản hiện tại không được phép xem thống kê.",
                parent=self,
            )
            return

        if not self.exam_repo:
            self.cmb_exam.set("Chưa có đề thi")
            self.cmb_result.set("Chưa có lượt làm bài nào")
            return

        try:
            exams = self.exam_repo.list_exams()
            all_results = self.exam_repo.list_results()
        except (
            OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError
        ):
            logger.exception("Không thể tải danh sách đề và kết quả thi.")
            self.cmb_exam.set("Không thể tải danh sách đề")
            self.cmb_result.set("")
            messagebox.showerror(
                "Lỗi tải thống kê",
                "Không thể tải dữ liệu đề thi và kết quả. "
                "Vui lòng kiểm tra dữ liệu rồi thử làm mới.",
                parent=self,
            )
            return

        self._exams_cache = exams
        if can_view_all:
            self._results_cache = all_results
        else:
            username = self.user.username
            self._results_cache = [
                result for result in all_results
                if username and result.student_name == username
            ]

        # Hiển thị danh sách đề vào Combobox
        exam_titles = [e.title for e in self._exams_cache]
        self.cmb_exam["values"] = exam_titles
        if exam_titles:
            self.cmb_exam.current(0)
            self._on_exam_selected()
        else:
            self.cmb_exam.set("Chưa có đề thi")
            self.cmb_result.set("Chưa có lượt làm bài nào")

    def _on_exam_selected(self, event=None):
        """Khi chọn đề thi -> lọc danh sách kết quả làm bài của đề đó."""
        self._current_filtered_results = []
        self.cmb_result["values"] = []
        self.cmb_result.set("")
        self._clear_display()

        idx = self.cmb_exam.current()
        if idx < 0 or idx >= len(self._exams_cache):
            self.cmb_result.set("Chưa chọn đề thi")
            return

        selected_exam = self._exams_cache[idx]
        filtered_results = [
            r for r in self._results_cache if r.exam_id == selected_exam.id
        ]

        self._current_filtered_results = filtered_results
        result_labels = []
        for r in filtered_results:
            created = r.created_at.strftime("%d/%m/%Y %H:%M") if hasattr(r.created_at, "strftime") else str(r.created_at)
            name = r.student_name if r.student_name else "Thí sinh ẩn danh"
            result_labels.append(f"{name} - Điểm: {r.score} ({created})")

        self.cmb_result["values"] = result_labels
        if result_labels:
            self.cmb_result.current(0)
            self._on_result_selected()
        else:
            self.cmb_result.set("Chưa có lượt làm bài nào")

    def _on_result_selected(self, event=None):
        """Khi chọn kết quả bài làm cụ thể -> hiển thị lên Bảng & Vẽ biểu đồ Canvas."""
        if not hasattr(self, "_current_filtered_results") or not self._current_filtered_results:
            self._clear_display()
            return

        idx = self.cmb_result.current()
        if idx < 0 or idx >= len(self._current_filtered_results):
            self._clear_display()
            return

        result = self._current_filtered_results[idx]
        try:
            self._display_result_stats(result)
        except (
            OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError
        ):
            logger.exception("Không thể hiển thị thống kê của kết quả bài làm.")
            self._clear_display()
            messagebox.showerror(
                "Lỗi hiển thị thống kê",
                "Không thể đọc thống kê của lượt làm bài đã chọn. "
                "Vui lòng kiểm tra dữ liệu rồi thử làm mới.",
                parent=self,
            )

    def _display_result_stats(self, result):
        """Hiển thị dữ liệu chi tiết của 1 kết quả làm bài."""
        # 1. Cập nhật thẻ thông tin tổng quan
        name = result.student_name if result.student_name else "Thí sinh ẩn danh"
        score = float(result.score)
        if not math.isfinite(score):
            raise ValueError("Điểm số phải là một giá trị hữu hạn.")

        # 2. Lấy dữ liệu thống kê từ Grader
        topic_stats = (
            self.grader.topic_statistics(result)
            if self.grader else result.topic_stats
        )
        if not isinstance(topic_stats, dict):
            raise ValueError("Thống kê theo chủ đề phải có dạng dictionary.")

        chart_data = []
        table_rows = []
        for topic_id, stats in topic_stats.items():
            if not isinstance(topic_id, str) or not isinstance(stats, dict):
                raise ValueError("Dữ liệu thống kê theo chủ đề không hợp lệ.")

            topic_obj = self.data_repo.get_topic(topic_id) if self.data_repo else None
            topic_name = topic_obj.name if topic_obj else f"Chủ đề ({topic_id[:6]})"

            correct = stats.get("correct", 0)
            total = stats.get("total", 0)
            percent = float(stats.get("percent", 0.0))
            if (
                type(correct) is not int
                or type(total) is not int
                or not math.isfinite(percent)
            ):
                raise ValueError("Các giá trị thống kê theo chủ đề không hợp lệ.")

            table_rows.append((
                topic_name, correct, total, f"{percent:.1f}%"
            ))
            chart_data.append({
                "label": topic_name,
                "value": percent,
                "subtext": f"{correct}/{total} câu"
            })

        self.lbl_score.config(text=f"Điểm số: {score:.2f} / 10")
        self.lbl_student.config(text=f"Thí sinh: {name}")

        # 3. Thay nội dung cũ bằng dữ liệu của lượt làm bài mới
        self.tree_stats.delete(*self.tree_stats.get_children())
        for row in table_rows:
            self.tree_stats.insert("", "end", values=row)

        self.bar_chart.set_data(chart_data)

    def _clear_display(self):
        """Xóa toàn bộ hiển thị khi không có dữ liệu."""
        self.lbl_score.config(text="Điểm số: -- / 10")
        self.lbl_student.config(text="Thí sinh: --")
        self.tree_stats.delete(*self.tree_stats.get_children())
        self.bar_chart.clear()