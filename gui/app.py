import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from auth import change_password
from base_models import Admin, User
from config import (
    APP_TITLE,
    COLOR_BG,
    COLOR_PRIMARY,
    COLOR_TEXT,
    FONT_NORMAL,
    FONT_TITLE,
    WINDOW_MIN_SIZE,
    WINDOW_SIZE,
)
from data_repository import JsonDataRepository
from exam_exporter import ExamExporterImpl
from exam_generator import ExamGeneratorImpl
from exam_repository import ExamRepository
from grader import GraderImpl
from gui.exam_tab import ExamTab
from gui.question_tab import QuestionTab
from gui.stats_tab import StatsTab
from gui.subject_topic_tab import SubjectTopicTab
from gui.take_exam_window import TakeExamWindow
from json_file_handler import JsonFileHandler


class MainApplication(tk.Tk):

    def __init__(
        self,
        current_user: User,
        repository: JsonDataRepository,
        file_handler: Optional[JsonFileHandler] = None,
    ):
        super().__init__()
        self.current_user = current_user
        self.repo = repository
        self.file_handler = file_handler or JsonFileHandler()
        self.exam_repo = ExamRepository()
        self.exam_generator = ExamGeneratorImpl(self.repo)
        self.exam_exporter = ExamExporterImpl()

        self.title(
            f"{APP_TITLE} - [{current_user.username} |"
            f" {current_user.role.upper()}]"
        )
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)

        self._build_menu()
        self._build_header()
        self._build_notebook()

    def _build_menu(self):
        menubar = tk.Menu(self)

        # Menu Tài khoản
        account_menu = tk.Menu(menubar, tearoff=0)
        account_menu.add_command(
            label="Đổi mật khẩu...", command=self.on_change_password
        )
        account_menu.add_separator()
        account_menu.add_command(label="Đăng xuất", command=self.on_logout)
        account_menu.add_command(label="Thoát ứng dụng", command=self.destroy)
        menubar.add_cascade(label="Tài khoản", menu=account_menu)

        # Menu Sao lưu & Khôi phục (chỉ Quản trị viên)
        if self.current_user.can("backup_restore"):
            data_menu = tk.Menu(menubar, tearoff=0)
            data_menu.add_command(
                label="Sao lưu dữ liệu ngay", command=self.on_backup
            )
            data_menu.add_command(
                label="Danh sách bản sao lưu...", command=self.on_list_backups
            )
            menubar.add_cascade(label="Dữ liệu & Sao lưu", menu=data_menu)

        self.config(menu=menubar)

    def _build_header(self):
        header = ttk.Frame(self, padding=(12, 8))
        header.pack(fill=tk.X)

        title_lbl = ttk.Label(
            header,
            text=f"📚 {APP_TITLE}",
            font=FONT_TITLE,
            foreground=COLOR_PRIMARY,
        )
        title_lbl.pack(side=tk.LEFT)

        role_badge = (
            f"👤 {self.current_user.username} ("
            f"{'Quản trị viên' if self.current_user.is_admin else 'Học viên'})"
        )
        user_lbl = ttk.Label(
            header, text=role_badge, font=FONT_NORMAL, foreground="#475569"
        )
        user_lbl.pack(side=tk.RIGHT)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        if self.current_user.can("manage_question"):
            self.tab_questions = QuestionTab(
                self.notebook, self.repo, current_user=self.current_user
            )
            self.notebook.add(
                self.tab_questions, text="  📝 Quản lý câu hỏi  "
            )

        if self.current_user.can("manage_subject_topic"):
            self.tab_subjects = SubjectTopicTab(
                self.notebook, self.repo, current_user=self.current_user
            )
            self.notebook.add(
                self.tab_subjects, text="  📂 Môn học & Chủ đề  "
            )

        self.tab_exam = None
        if (self.current_user.can("create_exam")
                or self.current_user.can("take_exam")):
            self.tab_exam = ExamTab(
                self.notebook,
                self.repo,
                self.exam_repo,
                self.exam_generator,
                self.current_user,
                exam_exporter=self.exam_exporter,
                on_take_exam=self._open_exam,
            )
            self.notebook.add(self.tab_exam, text="  🧪 Đề thi  ")

        self.tab_stats = None
        if (self.current_user.can("view_all_stats")
                or self.current_user.can("view_own_stats")):
            self.tab_stats = StatsTab(
                self.notebook,
                self.exam_repo,
                self.current_user,
                data_repo=self.repo,
            )
            self.notebook.add(self.tab_stats, text="  📊 Thống kê  ")

        info_frame = ttk.Frame(self.notebook, padding=16)
        ttk.Label(
            info_frame,
            text="Hệ thống quản lý ngân hàng câu hỏi",
            font=FONT_TITLE,
        ).pack(anchor="w", pady=(0, 10))

        info_text = (
            "Chào mừng bạn đến với Hệ thống Quản lý Ngân hàng Câu hỏi!\n\n"
            "Các tính năng chính:\n"
            "• Quản lý tài khoản, đăng ký, đăng nhập an toàn\n"
            "• Quản lý danh sách môn học, chủ đề, câu hỏi\n"
            "• Tạo đề theo ma trận, làm bài, xem điểm và thống kê\n"
            "• Nhập câu hỏi từ file văn bản (.txt) hoặc API\n"
        )
        ttk.Label(
            info_frame, text=info_text, justify=tk.LEFT, font=FONT_NORMAL
        ).pack(anchor="w")
        self.notebook.add(info_frame, text="  ℹ️ Thông tin & Trợ giúp  ")

    def _open_exam(self, exam):
        TakeExamWindow(
            self,
            exam=exam,
            data_repo=self.repo,
            grader=GraderImpl(),
            exam_repo=self.exam_repo,
            user=self.current_user,
            on_completed=self._on_exam_completed,
        )

    def _on_exam_completed(self, _result):
        if self.tab_stats is not None:
            self.tab_stats.refresh()

    def on_change_password(self):
        dlg = tk.Toplevel(self)
        dlg.title("Đổi mật khẩu")
        dlg.geometry("340x220")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Mật khẩu hiện tại:").pack(
            anchor="w", padx=15, pady=(15, 2)
        )
        ent_old = ttk.Entry(dlg, show="*", width=30)
        ent_old.pack(padx=15, pady=2)
        ent_old.focus()

        ttk.Label(dlg, text="Mật khẩu mới (tối thiểu 6 ký tự):").pack(
            anchor="w", padx=15, pady=(8, 2)
        )
        ent_new = ttk.Entry(dlg, show="*", width=30)
        ent_new.pack(padx=15, pady=2)

        ttk.Label(dlg, text="Xác nhận mật khẩu mới:").pack(
            anchor="w", padx=15, pady=(8, 2)
        )
        ent_confirm = ttk.Entry(dlg, show="*", width=30)
        ent_confirm.pack(padx=15, pady=2)

        def do_change():
            old_pw = ent_old.get()
            new_pw = ent_new.get()
            confirm_pw = ent_confirm.get()

            if new_pw != confirm_pw:
                messagebox.showerror(
                    "Lỗi",
                    "Mật khẩu mới và xác nhận mật khẩu không khớp.",
                    parent=dlg,
                )
                return

            try:
                change_password(self.current_user.username, old_pw, new_pw)
                messagebox.showinfo(
                    "Thành công", "Đổi mật khẩu thành công!", parent=dlg
                )
                dlg.destroy()
            except ValueError as e:
                messagebox.showerror("Lỗi đổi mật khẩu", str(e), parent=dlg)

        btn_box = ttk.Frame(dlg, padding=10)
        btn_box.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(btn_box, text="Xác nhận", command=do_change).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_box, text="Hủy", command=dlg.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def on_logout(self):
        confirm = messagebox.askyesno(
            "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất khỏi hệ thống?",
            parent=self,
        )
        if confirm:
            self.destroy()

    def on_backup(self):
        try:
            from config import QUESTIONS_FILE, SUBJECTS_TOPICS_FILE

            p1 = self.file_handler.backup(QUESTIONS_FILE)
            p2 = self.file_handler.backup(SUBJECTS_TOPICS_FILE)
            messagebox.showinfo(
                "Sao lưu thành công",
                f"Đã sao lưu dữ liệu:\n{p1.name}\n{p2.name}",
                parent=self,
            )
        except Exception as e:
            messagebox.showerror("Lỗi sao lưu", str(e), parent=self)

    def on_list_backups(self):
        backups = self.file_handler.list_backups()
        msg = f"Tìm thấy {len(backups)} bản sao lưu trong hệ thống:\n"
        for b in backups[:10]:
            msg += f"• {b.name}\n"
        if len(backups) > 10:
            msg += f"... và {len(backups) - 10} bản khác."
        messagebox.showinfo("Danh sách bản sao lưu", msg, parent=self)