"""
gui/exam_tab.py
================
[C sở hữu] Tab tạo đề thi trong Notebook chính.

Quản trị viên: form tạo đề (chọn môn, nhập ma trận theo chủ đề × mức độ,
               nhập seed, đặt tên), Treeview ma trận, nút Tạo đề / Tái lập / Xuất.
Người dùng thường: chỉ thấy danh sách đề và nút Làm bài.
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from base_models import (
    ExamMatrixItem, Exam, DifficultyLevel, User,
)
from config import (
    FONT_NORMAL, FONT_BOLD, FONT_TITLE, PADDING,
    COLOR_PRIMARY, COLOR_BG, COLOR_SUCCESS, COLOR_ERROR,
)


class ExamTab(ttk.Frame):
    """
    Tab Tạo đề & Danh sách đề.

    Parameters:
        parent          – widget cha (thường là Notebook)
        data_repo       – JsonDataRepository instance (A)
        exam_repo       – ExamRepository instance (D) — cần hàm save_exam, list_exams...
        exam_generator  – ExamGeneratorImpl instance (C)
        exam_exporter   – ExamExporter instance (D) — None nếu D chưa viết
        user            – đối tượng User đang đăng nhập
        on_take_exam    – callback(exam) khi người dùng bấm Làm bài
    """

    def __init__(self, parent, data_repo, exam_repo, exam_generator,
                 user: User, exam_exporter=None,
                 on_take_exam=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.data_repo = data_repo
        self.exam_repo = exam_repo
        self.exam_gen = exam_generator
        self.exam_exporter = exam_exporter
        self.user = user
        self.on_take_exam = on_take_exam

        # Dữ liệu phụ trợ
        self._subjects = []         # list[Subject]
        self._summary = {}          # get_question_bank_summary()
        self._matrix_rows = []      # list[ExamMatrixItem] hiện tại
        self._exams_cache = []      # list[Exam] đã lưu

        self._build_ui()
        self._refresh_subjects()
        self._refresh_exam_list()

    # ==============================================================
    # BUILD UI
    # ==============================================================

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        row = 0

        # ---------- Tiêu đề ----------
        lbl_title = ttk.Label(self, text="Quản lý Đề thi", font=FONT_TITLE)
        lbl_title.grid(row=row, column=0, sticky="w", padx=PADDING, pady=(PADDING, 4))
        row += 1

        # ---------- Form tạo đề (chỉ Admin) ----------
        if self.user.can("create_exam"):
            self._frame_create = ttk.LabelFrame(self, text="Tạo đề mới",
                                                 padding=PADDING)
            self._frame_create.grid(row=row, column=0, sticky="ew",
                                     padx=PADDING, pady=4)
            self._frame_create.columnconfigure(1, weight=1)
            row += 1
            self._build_create_form(self._frame_create)

        # ---------- Danh sách đề ----------
        frame_list = ttk.LabelFrame(self, text="Danh sách đề đã tạo",
                                     padding=PADDING)
        frame_list.grid(row=row, column=0, sticky="nsew", padx=PADDING, pady=4)
        frame_list.columnconfigure(0, weight=1)
        frame_list.rowconfigure(0, weight=1)
        self.rowconfigure(row, weight=1)
        row += 1
        self._build_exam_list(frame_list)

    # ---------- Form tạo đề ----------

    def _build_create_form(self, parent):
        r = 0

        # Môn học
        ttk.Label(parent, text="Môn học:", font=FONT_NORMAL).grid(
            row=r, column=0, sticky="w", pady=2)
        self.cmb_subject = ttk.Combobox(parent, state="readonly", font=FONT_NORMAL)
        self.cmb_subject.grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 0))
        self.cmb_subject.bind("<<ComboboxSelected>>", self._on_subject_changed)
        r += 1

        # Tên đề
        ttk.Label(parent, text="Tên đề:", font=FONT_NORMAL).grid(
            row=r, column=0, sticky="w", pady=2)
        self.ent_title = ttk.Entry(parent, font=FONT_NORMAL)
        self.ent_title.grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 0))
        r += 1

        # Seed
        ttk.Label(parent, text="Seed:", font=FONT_NORMAL).grid(
            row=r, column=0, sticky="w", pady=2)
        frame_seed = ttk.Frame(parent)
        frame_seed.grid(row=r, column=1, sticky="ew", pady=2, padx=(4, 0))
        self.ent_seed = ttk.Entry(frame_seed, font=FONT_NORMAL, width=15)
        self.ent_seed.pack(side="left")
        ttk.Button(frame_seed, text="Ngẫu nhiên",
                   command=self._random_seed).pack(side="left", padx=4)
        r += 1

        # --- Ma trận ---
        ttk.Label(parent, text="Ma trận đề:", font=FONT_BOLD).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(8, 2))
        r += 1

        # Treeview ma trận
        cols_matrix = ("topic", "difficulty", "num", "available")
        self.tree_matrix = ttk.Treeview(parent, columns=cols_matrix,
                                         show="headings", height=5)
        self.tree_matrix.heading("topic", text="Chủ đề")
        self.tree_matrix.heading("difficulty", text="Mức độ")
        self.tree_matrix.heading("num", text="Số câu")
        self.tree_matrix.heading("available", text="Có sẵn")
        self.tree_matrix.column("topic", width=180)
        self.tree_matrix.column("difficulty", width=80, anchor="center")
        self.tree_matrix.column("num", width=70, anchor="center")
        self.tree_matrix.column("available", width=70, anchor="center")
        self.tree_matrix.grid(row=r, column=0, columnspan=2, sticky="ew", pady=2)
        r += 1

        # Thêm dòng ma trận
        frame_add = ttk.Frame(parent)
        frame_add.grid(row=r, column=0, columnspan=2, sticky="ew", pady=2)

        ttk.Label(frame_add, text="Chủ đề:", font=FONT_NORMAL).pack(side="left")
        self.cmb_topic = ttk.Combobox(frame_add, state="readonly",
                                       font=FONT_NORMAL, width=18)
        self.cmb_topic.pack(side="left", padx=2)

        ttk.Label(frame_add, text="Mức độ:", font=FONT_NORMAL).pack(side="left")
        self.cmb_diff = ttk.Combobox(frame_add, state="readonly",
                                      font=FONT_NORMAL, width=8,
                                      values=["Dễ", "Khó"])
        self.cmb_diff.current(0)
        self.cmb_diff.pack(side="left", padx=2)

        ttk.Label(frame_add, text="Số câu:", font=FONT_NORMAL).pack(side="left")
        self.spn_num = ttk.Spinbox(frame_add, from_=1, to=100, width=5,
                                    font=FONT_NORMAL)
        self.spn_num.set(5)
        self.spn_num.pack(side="left", padx=2)

        ttk.Button(frame_add, text="Thêm dòng",
                   command=self._add_matrix_row).pack(side="left", padx=4)
        ttk.Button(frame_add, text="Xóa dòng chọn",
                   command=self._remove_matrix_row).pack(side="left", padx=4)
        r += 1

        # Nút hành động
        frame_btn = ttk.Frame(parent)
        frame_btn.grid(row=r, column=0, columnspan=2, sticky="e", pady=(8, 0))

        ttk.Button(frame_btn, text="🎲 Tạo đề",
                   command=self._do_generate).pack(side="left", padx=4)

        if self.user.can("export_exam"):
            ttk.Button(frame_btn, text="📄 Xuất đề",
                       command=self._do_export).pack(side="left", padx=4)

    # ---------- Danh sách đề ----------

    def _build_exam_list(self, parent):
        cols_exam = ("title", "num_q", "seed", "created")
        self.tree_exams = ttk.Treeview(parent, columns=cols_exam,
                                        show="headings", height=6)
        self.tree_exams.heading("title", text="Tên đề")
        self.tree_exams.heading("num_q", text="Số câu")
        self.tree_exams.heading("seed", text="Seed")
        self.tree_exams.heading("created", text="Ngày tạo")
        self.tree_exams.column("title", width=250)
        self.tree_exams.column("num_q", width=70, anchor="center")
        self.tree_exams.column("seed", width=80, anchor="center")
        self.tree_exams.column("created", width=150, anchor="center")
        self.tree_exams.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(parent, orient="vertical",
                                   command=self.tree_exams.yview)
        self.tree_exams.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        frame_btn = ttk.Frame(parent)
        frame_btn.grid(row=1, column=0, columnspan=2, sticky="e", pady=(4, 0))

        if self.user.can("take_exam"):
            ttk.Button(frame_btn, text="📝 Làm bài",
                       command=self._do_take_exam).pack(side="left", padx=4)

        if self.user.can("create_exam"):
            ttk.Button(frame_btn, text="🔄 Tái lập đề",
                       command=self._do_rebuild).pack(side="left", padx=4)

        ttk.Button(frame_btn, text="🔃 Làm mới",
                   command=self._refresh_exam_list).pack(side="left", padx=4)

    # ==============================================================
    # DATA HELPERS
    # ==============================================================

    def _refresh_subjects(self):
        """Cập nhật combobox Môn học."""
        self._subjects = self.data_repo.list_subjects()
        self._summary = self.data_repo.get_question_bank_summary()
        if not hasattr(self, "cmb_subject"):
            return
        names = [s.name for s in self._subjects]
        self.cmb_subject["values"] = names
        if names:
            self.cmb_subject.current(0)
            self._on_subject_changed()

    def _on_subject_changed(self, event=None):
        """Khi chọn môn → cập nhật combobox Chủ đề."""
        idx = self.cmb_subject.current()
        if idx < 0 or idx >= len(self._subjects):
            return
        subj = self._subjects[idx]
        topics = self.data_repo.list_topics(subj.id)
        self.cmb_topic["values"] = [t.name for t in topics]
        self._current_topics = topics
        if topics:
            self.cmb_topic.current(0)

    def _selected_subject(self):
        idx = self.cmb_subject.current()
        if idx < 0 or idx >= len(self._subjects):
            return None
        return self._subjects[idx]

    def _refresh_exam_list(self):
        """Cập nhật Treeview danh sách đề."""
        self.tree_exams.delete(*self.tree_exams.get_children())
        if self.exam_repo is None:
            return
        try:
            self._exams_cache = self.exam_repo.list_exams()
        except Exception:
            self._exams_cache = []
        for exam in self._exams_cache:
            created = exam.created_at.strftime("%d/%m/%Y %H:%M") \
                if hasattr(exam.created_at, "strftime") else str(exam.created_at)
            self.tree_exams.insert("", "end", iid=exam.id,
                                    values=(exam.title,
                                            len(exam.question_ids),
                                            exam.seed,
                                            created))

    def _get_selected_exam(self) -> Optional[Exam]:
        sel = self.tree_exams.selection()
        if not sel:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một đề thi.")
            return None
        exam_id = sel[0]
        return next((e for e in self._exams_cache if e.id == exam_id), None)

    # ==============================================================
    # ACTIONS
    # ==============================================================

    def _random_seed(self):
        self.ent_seed.delete(0, "end")
        self.ent_seed.insert(0, str(random.randint(1, 999_999)))

    def _add_matrix_row(self):
        """Thêm 1 dòng vào ma trận đề."""
        if not hasattr(self, "_current_topics") or not self._current_topics:
            messagebox.showwarning("Thiếu dữ liệu", "Chưa có chủ đề nào.")
            return
        idx = self.cmb_topic.current()
        if idx < 0:
            return
        topic = self._current_topics[idx]
        diff_text = self.cmb_diff.get()
        difficulty = DifficultyLevel.DE if diff_text == "Dễ" else DifficultyLevel.KHO

        try:
            num = int(self.spn_num.get())
            if num <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số câu phải là số nguyên dương.")
            return

        # Tìm số câu có sẵn
        available = self.data_repo.count_questions(topic.id, difficulty)

        item = ExamMatrixItem(topic_id=topic.id, difficulty=difficulty,
                              num_questions=num)
        self._matrix_rows.append(item)

        self.tree_matrix.insert("", "end",
                                 values=(topic.name,
                                         "Dễ" if difficulty == DifficultyLevel.DE else "Khó",
                                         num, available))

    def _remove_matrix_row(self):
        """Xóa dòng ma trận đang chọn."""
        sel = self.tree_matrix.selection()
        if not sel:
            return
        idx = self.tree_matrix.index(sel[0])
        self.tree_matrix.delete(sel[0])
        if 0 <= idx < len(self._matrix_rows):
            self._matrix_rows.pop(idx)

    def _do_generate(self):
        """Bấm nút Tạo đề."""
        subj = self._selected_subject()
        if subj is None:
            messagebox.showwarning("Thiếu", "Vui lòng chọn môn học.")
            return

        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Thiếu", "Vui lòng nhập tên đề.")
            return

        seed_text = self.ent_seed.get().strip()
        if not seed_text:
            seed = random.randint(1, 999_999)
            self.ent_seed.delete(0, "end")
            self.ent_seed.insert(0, str(seed))
        else:
            try:
                seed = int(seed_text)
            except ValueError:
                messagebox.showerror("Lỗi", "Seed phải là số nguyên.")
                return

        if not self._matrix_rows:
            messagebox.showwarning("Thiếu", "Ma trận đề đang rỗng. "
                                   "Hãy thêm ít nhất 1 dòng.")
            return

        try:
            exam = self.exam_gen.generate_exam(
                subject_id=subj.id,
                title=title,
                matrix=list(self._matrix_rows),
                seed=seed,
            )
        except ValueError as e:
            messagebox.showerror("Không thể tạo đề", str(e))
            return

        # Lưu đề
        if self.exam_repo is not None:
            try:
                self.exam_repo.save_exam(exam)
            except Exception as e:
                messagebox.showerror("Lỗi lưu", str(e))
                return

        messagebox.showinfo("Thành công",
                            f"Đã tạo đề '{title}' với {len(exam.question_ids)} câu.\n"
                            f"Seed: {seed}")

        # Reset form
        self._matrix_rows.clear()
        self.tree_matrix.delete(*self.tree_matrix.get_children())
        self.ent_title.delete(0, "end")
        self.ent_seed.delete(0, "end")
        self._refresh_exam_list()

    def _do_rebuild(self):
        """Tái lập đề từ seed đã lưu."""
        exam = self._get_selected_exam()
        if exam is None:
            return

        try:
            rebuilt = self.exam_gen.rebuild_exam(exam)
        except ValueError as e:
            messagebox.showerror("Không thể tái lập", str(e))
            return

        # Cập nhật lại exam trong repo
        if self.exam_repo is not None:
            try:
                self.exam_repo.save_exam(rebuilt)
            except Exception as e:
                messagebox.showerror("Lỗi lưu", str(e))
                return

        messagebox.showinfo("Tái lập thành công",
                            f"Đề '{rebuilt.title}' đã được tái lập "
                            f"với {len(rebuilt.question_ids)} câu.")
        self._refresh_exam_list()

    def _do_export(self):
        """Xuất đề và đáp án ra file."""
        exam = self._get_selected_exam()
        if exam is None:
            return

        if self.exam_exporter is None:
            messagebox.showinfo("Chưa sẵn sàng",
                                "Chức năng xuất đề chưa được tích hợp (chờ D).")
            return

        questions = [self.data_repo.get_question(qid)
                     for qid in exam.question_ids]
        questions = [q for q in questions if q is not None]

        from config import EXPORT_DIR
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        exam_path = str(EXPORT_DIR / f"{exam.id}_de.txt")
        key_path = str(EXPORT_DIR / f"{exam.id}_dapan.txt")

        try:
            self.exam_exporter.export_exam(exam, questions, exam_path)
            self.exam_exporter.export_answer_key(exam, questions, key_path)
            messagebox.showinfo("Xuất thành công",
                                f"Đề: {exam_path}\nĐáp án: {key_path}")
        except Exception as e:
            messagebox.showerror("Lỗi xuất file", str(e))

    def _do_take_exam(self):
        """Mở cửa sổ làm bài."""
        exam = self._get_selected_exam()
        if exam is None:
            return

        if self.on_take_exam:
            self.on_take_exam(exam)
        else:
            try:
                from gui.take_exam_window import TakeExamWindow
                from grader import GraderImpl
                TakeExamWindow(
                    self,
                    exam=exam,
                    data_repo=self.data_repo,
                    grader=GraderImpl(),
                    exam_repo=self.exam_repo,
                    user=self.user,
                )
            except Exception as e:
                messagebox.showerror("Lỗi mở bài thi", f"Không thể mở cửa sổ làm bài: {e}")

    # ==============================================================
    # PUBLIC: refresh khi tab được chọn
    # ==============================================================

    def refresh(self):
        """Gọi khi tab được hiện (Notebook <<NotebookTabChanged>>)."""
        self._refresh_subjects()
        self._refresh_exam_list()
