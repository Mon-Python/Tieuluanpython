"""Tkinter tab showing role-filtered exam results and topic performance."""

import tkinter as tk
from tkinter import ttk

from grader import GraderImpl
from gui.bar_chart import BarChart


class StatsTab(ttk.Frame):
    """Display accessible result rows and selected-result topic statistics."""

    @staticmethod
    def visible_results(results, user):
        if user is None:
            return []
        if getattr(user, "is_admin", False):
            return list(results)
        username = getattr(user, "username", "")
        return [result for result in results
                if result.student_name == username]

    def __init__(self, parent, exam_repo, current_user, data_repo=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.exam_repo = exam_repo
        self.current_user = current_user
        self.data_repo = data_repo
        self.grader = GraderImpl()
        self._results = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Kết quả và thống kê theo chủ đề",
                  font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=8
        )

        content = ttk.Panedwindow(self, orient=tk.VERTICAL)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        result_frame = ttk.LabelFrame(content, text="Kết quả bài thi", padding=6)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        self.results_tree = ttk.Treeview(
            result_frame,
            columns=("student", "exam", "score", "date"),
            show="headings",
            height=7,
        )
        for column, title, width in (
            ("student", "Học viên", 150),
            ("exam", "Mã đề", 180),
            ("score", "Điểm / 10", 100),
            ("date", "Ngày làm", 180),
        ):
            self.results_tree.heading(column, text=title)
            self.results_tree.column(column, width=width, anchor="w")
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        self.results_tree.bind("<<TreeviewSelect>>", self._show_selected_stats)
        result_scroll = ttk.Scrollbar(
            result_frame, orient="vertical", command=self.results_tree.yview
        )
        result_scroll.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=result_scroll.set)
        content.add(result_frame, weight=1)

        topic_frame = ttk.LabelFrame(
            content, text="Thống kê theo chủ đề", padding=6
        )
        topic_frame.columnconfigure(0, weight=1)
        topic_frame.rowconfigure(1, weight=1)
        self.topic_text = tk.Text(
            topic_frame, height=5, wrap="word", state="disabled"
        )
        self.topic_text.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.chart = BarChart(topic_frame, height=170)
        self.chart.grid(row=1, column=0, sticky="nsew")
        content.add(topic_frame, weight=1)

    def refresh(self):
        """Reload result rows while enforcing the current user's visibility."""
        self.results_tree.delete(*self.results_tree.get_children())
        results = self.exam_repo.list_results() if self.exam_repo else []
        self._results = self.visible_results(results, self.current_user)
        for index, result in enumerate(self._results):
            self.results_tree.insert(
                "", "end", iid=str(index),
                values=(
                    result.student_name,
                    result.exam_id,
                    f"{result.score:.2f}",
                    result.created_at.strftime("%Y-%m-%d %H:%M"),
                ),
            )
        self._set_topic_stats({})

    def _show_selected_stats(self, _event=None):
        selection = self.results_tree.selection()
        if not selection:
            self._set_topic_stats({})
            return
        result = self._results[int(selection[0])]
        stats = self.grader.topic_statistics(result)
        names = {}
        for topic_id, values in stats.items():
            topic = self.data_repo.get_topic(topic_id) if self.data_repo else None
            names[topic_id] = topic.name if topic else topic_id
        self._set_topic_stats(stats, names)

    def _set_topic_stats(self, stats, topic_names=None):
        topic_names = topic_names or {}
        display_values = {
            topic_names.get(topic_id, topic_id): values.get("percent", 0.0)
            for topic_id, values in stats.items()
        }
        lines = [
            f"{topic_names.get(topic_id, topic_id)}: "
            f"{values.get('correct', 0)}/{values.get('total', 0)} đúng "
            f"({values.get('percent', 0.0):.1f}%)"
            for topic_id, values in stats.items()
        ]
        self.topic_text.configure(state="normal")
        self.topic_text.delete("1.0", tk.END)
        self.topic_text.insert(
            "1.0", "\n".join(lines) if lines else "Chọn một kết quả để xem thống kê."
        )
        self.topic_text.configure(state="disabled")
        self.chart.set_values(display_values)
