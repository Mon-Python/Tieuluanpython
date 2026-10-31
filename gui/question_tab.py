"""gui/question_tab.py
===================
[B sở hữu] Tab Quản lý ngân hàng câu hỏi:
- Treeview danh sách câu hỏi: Mã, Môn học, Chủ đề, Mức độ, Nội dung, Đáp án đúng.
- Tìm kiếm kết hợp đa tiêu chí: Từ khóa (tìm trong câu & phương án), Môn học, Chủ đề, Mức độ.
- Các thao tác CRUD hoàn chỉnh với kiểm tra quyền Quản trị viên (User.can('manage_question')).
- Xác nhận trước khi xóa; bắt ValueError từ repository (ví dụ câu hỏi đã nằm trong đề) và hiển thị thông báo hướng dẫn cụ thể.
- Nút Nhập câu hỏi từ file văn bản (.txt) và Nhập từ API (Open Trivia DB).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict

from base_models import DifficultyLevel, Option, Question, User
from config import ROLE_ADMIN, COLOR_PRIMARY, PADDING
from data_repository import JsonDataRepository
from gui.question_editor import QuestionEditor
from import_questions import import_questions_from_file
from api_import import import_questions_from_api


class QuestionTab(ttk.Frame):
    def __init__(self, master, repository: JsonDataRepository,
                 current_user: Optional[User] = None, **kwargs):
        super().__init__(master, padding=PADDING, **kwargs)
        self.repo = repository
        self.current_user = current_user
        self.selected_question_id: Optional[str] = None
        self._build_ui()
        self.reload_data()

    def _build_ui(self):
        # 1. KHUNG TÌM KIẾM & BỘ LỌC ĐA TIÊU CHÍ (>= 2 tiêu chí theo yêu cầu)
        filter_frame = ttk.LabelFrame(self, text="Tìm kiếm & Bộ lọc câu hỏi", padding=8)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 8))

        # Hàng 1: Từ khóa + Mức độ
        ttk.Label(filter_frame, text="Từ khóa tìm kiếm:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.ent_search = ttk.Entry(filter_frame, width=28)
        self.ent_search.grid(row=0, column=1, sticky="w", padx=4, pady=4)
        self.ent_search.bind("<Return>", lambda e: self.on_search())

        ttk.Label(filter_frame, text="Mức độ khó:").grid(row=0, column=2, sticky="w", padx=(16, 4), pady=4)
        self.cbo_filter_diff = ttk.Combobox(
            filter_frame,
            values=["-- Tất cả --", "Dễ (de)", "Khó (kho)"],
            state="readonly",
            width=14
        )
        self.cbo_filter_diff.current(0)
        self.cbo_filter_diff.grid(row=0, column=3, sticky="w", padx=4, pady=4)
        self.cbo_filter_diff.bind("<<ComboboxSelected>>", lambda e: self.on_search())

        # Hàng 2: Môn học + Chủ đề
        ttk.Label(filter_frame, text="Môn học:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.cbo_filter_subj = ttk.Combobox(filter_frame, state="readonly", width=26)
        self.cbo_filter_subj.grid(row=1, column=1, sticky="w", padx=4, pady=4)
        self.cbo_filter_subj.bind("<<ComboboxSelected>>", self.on_subject_filter_change)

        ttk.Label(filter_frame, text="Chủ đề:").grid(row=1, column=2, sticky="w", padx=(16, 4), pady=4)
        self.cbo_filter_topic = ttk.Combobox(filter_frame, state="readonly", width=22)
        self.cbo_filter_topic.grid(row=1, column=3, sticky="w", padx=4, pady=4)
        self.cbo_filter_topic.bind("<<ComboboxSelected>>", lambda e: self.on_search())

        # Các nút lọc
        btn_box = ttk.Frame(filter_frame)
        btn_box.grid(row=0, column=4, rowspan=2, padx=(20, 4), sticky="nsew")

        btn_search = ttk.Button(btn_box, text="🔍 Tìm kiếm", command=self.on_search)
        btn_search.pack(fill=tk.X, pady=2)

        btn_reset = ttk.Button(btn_box, text="🔄 Đặt lại", command=self.on_reset_filters)
        btn_reset.pack(fill=tk.X, pady=2)

        # 2. BẢNG HIỂN THỊ CÂU HỎI (Treeview)
        tree_container = ttk.Frame(self)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=4)

        cols = ("id", "subject", "topic", "diff", "content", "correct")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="Mã câu")
        self.tree.heading("subject", text="Môn học")
        self.tree.heading("topic", text="Chủ đề")
        self.tree.heading("diff", text="Mức độ")
        self.tree.heading("content", text="Nội dung câu hỏi")
        self.tree.heading("correct", text="Đáp án đúng")

        self.tree.column("id", width=95, anchor="center")
        self.tree.column("subject", width=140, anchor="w")
        self.tree.column("topic", width=140, anchor="w")
        self.tree.column("diff", width=75, anchor="center")
        self.tree.column("content", width=420, anchor="w")
        self.tree.column("correct", width=130, anchor="w")

        scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self.on_edit_question())

        # Thanh trạng thái đếm số lượng câu
        self.lbl_status = ttk.Label(self, text="Đang tải dữ liệu...", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(fill=tk.X, padx=5, pady=(2, 6))

        # 3. KHUNG CÁC NÚT THAO TÁC CRUD & NHẬP DỮ LIỆU
        action_bar = ttk.Frame(self)
        action_bar.pack(fill=tk.X, padx=5, pady=(4, 0))

        can_manage = self.current_user and self.current_user.can("manage_question")

        if can_manage:
            self.btn_add = ttk.Button(action_bar, text="➕ Thêm câu hỏi", command=self.on_add_question)
            self.btn_add.pack(side=tk.LEFT, padx=3)

            self.btn_edit = ttk.Button(action_bar, text="✏️ Sửa câu hỏi", command=self.on_edit_question)
            self.btn_edit.pack(side=tk.LEFT, padx=3)

            self.btn_del = ttk.Button(action_bar, text="🗑️ Xóa câu hỏi", command=self.on_delete_question)
            self.btn_del.pack(side=tk.LEFT, padx=3)

            sep = ttk.Separator(action_bar, orient=tk.VERTICAL)
            sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

            self.btn_import_file = ttk.Button(action_bar, text="📁 Nhập từ file (.txt)", command=self.on_import_file)
            self.btn_import_file.pack(side=tk.LEFT, padx=3)

            self.btn_import_api = ttk.Button(action_bar, text="🌐 Nhập từ API (OpenTDB)", command=self.on_import_api)
            self.btn_import_api.pack(side=tk.LEFT, padx=3)
        else:
            lbl_perm = ttk.Label(
                action_bar,
                text="ℹ️ Chế độ xem: Tài khoản học viên/thường chỉ có quyền xem danh sách câu hỏi.",
                foreground="#64748b"
            )
            lbl_perm.pack(side=tk.LEFT, padx=4)

    def reload_data(self):
        """Tải lại danh sách môn học, chủ đề và câu hỏi."""
        subjects = self.repo.list_subjects()
        self.subject_map = {s.name: s.id for s in subjects}
        self.cbo_filter_subj["values"] = ["-- Tất cả môn --"] + [s.name for s in subjects]
        self.cbo_filter_subj.current(0)

        self.on_subject_filter_change()
        self.on_search()

    def on_subject_filter_change(self, event=None):
        """Khi môn học thay đổi, cập nhật danh sách chủ đề tương ứng."""
        selected_subj_name = self.cbo_filter_subj.get()
        if not selected_subj_name or selected_subj_name == "-- Tất cả môn --":
            topics = self.repo.list_topics()
        else:
            subj_id = self.subject_map.get(selected_subj_name)
            topics = self.repo.list_topics(subject_id=subj_id)

        self.topic_map = {t.name: t.id for t in topics}
        self.cbo_filter_topic["values"] = ["-- Tất cả chủ đề --"] + [t.name for t in topics]
        self.cbo_filter_topic.current(0)
        self.on_search()

    def on_search(self, event=None):
        """Tìm kiếm câu hỏi theo từ khóa, môn, chủ đề, mức độ."""
        keyword = self.ent_search.get().strip()

        # Mức độ
        diff_str = self.cbo_filter_diff.get()
        diff = None
        if "Dễ" in diff_str:
            diff = DifficultyLevel.DE
        elif "Khó" in diff_str:
            diff = DifficultyLevel.KHO

        # Môn
        subj_name = self.cbo_filter_subj.get()
        subj_id = self.subject_map.get(subj_name) if subj_name != "-- Tất cả môn --" else None

        # Chủ đề
        topic_name = self.cbo_filter_topic.get()
        topic_id = self.topic_map.get(topic_name) if topic_name != "-- Tất cả chủ đề --" else None

        # Gọi hàm tìm kiếm đã có trong repo của A
        results = self.repo.search_questions(
            keyword=keyword,
            topic_id=topic_id,
            difficulty=diff,
            subject_id=subj_id
        )

        # Xóa các dòng cũ trên treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        all_topics = {t.id: t for t in self.repo.list_topics()}
        all_subjects = {s.id: s for s in self.repo.list_subjects()}

        for q in results:
            t = all_topics.get(q.topic_id)
            topic_name = t.name if t else q.topic_id
            s = all_subjects.get(t.subject_id) if t else None
            subj_name = s.name if s else ""

            diff_display = "Dễ" if q.difficulty == DifficultyLevel.DE or q.difficulty == "de" else "Khó"

            correct_opts = [o.content for o in q.options if o.is_correct]
            correct_display = correct_opts[0] if correct_opts else "N/A"

            self.tree.insert("", tk.END, iid=q.id, values=(
                q.id,
                subj_name,
                topic_name,
                diff_display,
                q.content,
                correct_display
            ))

        self.lbl_status.config(
            text=f"Hiển thị {len(results)} câu hỏi phù hợp (Tổng số câu trong ngân hàng: {len(self.repo.list_questions())})"
        )

    def on_reset_filters(self):
        """Đặt lại bộ lọc tìm kiếm về mặc định."""
        self.ent_search.delete(0, tk.END)
        self.cbo_filter_diff.current(0)
        self.cbo_filter_subj.current(0)
        self.on_subject_filter_change()

    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        if selected:
            self.selected_question_id = selected[0]

    def _select_topic_dialog(self, title: str) -> Optional[str]:
        """Hộp thoại chọn Chủ đề cho câu hỏi mới."""
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.geometry("380x180")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Chọn Chủ đề cho câu hỏi:", font=("Segoe UI", 10, "bold")).pack(pady=10)

        topics = self.repo.list_topics()
        if not topics:
            messagebox.showwarning("Chưa có chủ đề", "Hệ thống chưa có chủ đề nào. Vui lòng tạo chủ đề trước.", parent=dlg)
            dlg.destroy()
            return None

        topic_names = [f"{t.name} (id: {t.id})" for t in topics]
        cbo = ttk.Combobox(dlg, values=topic_names, state="readonly", width=35)
        cbo.current(0)
        cbo.pack(pady=5)

        chosen_id = [None]

        def on_ok():
            idx = cbo.current()
            if idx >= 0:
                chosen_id[0] = topics[idx].id
            dlg.destroy()

        btn_box = ttk.Frame(dlg)
        btn_box.pack(pady=15)
        ttk.Button(btn_box, text="Xác nhận", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_box, text="Hủy", command=dlg.destroy).pack(side=tk.LEFT, padx=5)

        self.wait_window(dlg)
        return chosen_id[0]

    def on_add_question(self):
        """Mở cửa sổ thêm câu hỏi mới."""
        topic_id = self._select_topic_dialog("Thêm câu hỏi mới")
        if not topic_id:
            return

        dlg = tk.Toplevel(self)
        dlg.title("Thêm câu hỏi vào ngân hàng")
        dlg.geometry("640x500")
        dlg.transient(self)
        dlg.grab_set()

        editor = QuestionEditor(dlg, padding=10)
        editor.pack(fill=tk.BOTH, expand=True)

        def on_save():
            new_q = editor.get_question(topic_id)
            if not new_q:
                return

            try:
                self.repo.add_question(new_q)
                messagebox.showinfo("Thành công", f"Đã thêm câu hỏi mã '{new_q.id}' vào ngân hàng!", parent=dlg)
                dlg.destroy()
                self.on_search()
            except ValueError as e:
                messagebox.showerror("Lỗi khi thêm câu hỏi", str(e), parent=dlg)

        btn_box = ttk.Frame(dlg, padding=8)
        btn_box.pack(fill=tk.X)
        ttk.Button(btn_box, text="💾 Lưu câu hỏi", command=on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_box, text="Hủy bỏ", command=dlg.destroy).pack(side=tk.RIGHT, padx=5)

    def on_edit_question(self):
        """Mở cửa sổ chỉnh sửa câu hỏi đã chọn."""
        if not self.current_user or not self.current_user.can("manage_question"):
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một câu hỏi trong danh sách để sửa.", parent=self)
            return

        q_id = selected[0]
        q = self.repo.get_question(q_id)
        if not q:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu câu hỏi này.", parent=self)
            return

        if self.repo.is_question_used(q_id):
            if not messagebox.askyesno(
                "Cảnh báo câu hỏi trong đề thi",
                "Câu hỏi này đã nằm trong một hoặc nhiều đề thi đã tạo!\n"
                "Bạn có chắc chắn muốn chỉnh sửa nội dung không?",
                parent=self
            ):
                return

        dlg = tk.Toplevel(self)
        dlg.title(f"Sửa câu hỏi [{q.id}]")
        dlg.geometry("640x500")
        dlg.transient(self)
        dlg.grab_set()

        editor = QuestionEditor(dlg, padding=10)
        editor.pack(fill=tk.BOTH, expand=True)
        editor.set_question(q)

        def on_save():
            updated_q = editor.get_question(q.topic_id)
            if not updated_q:
                return

            try:
                self.repo.update_question(q.id, updated_q)
                messagebox.showinfo("Thành công", "Đã cập nhật câu hỏi thành công!", parent=dlg)
                dlg.destroy()
                self.on_search()
            except ValueError as e:
                messagebox.showerror("Lỗi khi sửa", str(e), parent=dlg)

        btn_box = ttk.Frame(dlg, padding=8)
        btn_box.pack(fill=tk.X)
        ttk.Button(btn_box, text="💾 Lưu thay đổi", command=on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_box, text="Hủy", command=dlg.destroy).pack(side=tk.RIGHT, padx=5)

    def on_delete_question(self):
        """Xóa câu hỏi đã chọn với xác nhận và bắt lỗi ràng buộc."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn câu hỏi cần xóa.", parent=self)
            return

        q_id = selected[0]

        # Hộp thoại xác nhận thao tác quan trọng theo mục 6 & 7.2
        confirm = messagebox.askyesno(
            "Xác nhận xóa câu hỏi",
            f"Bạn có chắc chắn muốn xóa câu hỏi mã '{q_id}' khỏi hệ thống?\n"
            "Thao tác này sẽ xóa vĩnh viễn câu hỏi khỏi ngân hàng đề.",
            icon="warning",
            parent=self
        )
        if not confirm:
            return

        try:
            self.repo.delete_question(q_id)
            messagebox.showinfo("Đã xóa", f"Câu hỏi '{q_id}' đã được xóa thành công.", parent=self)
            self.on_search()
        except ValueError as e:
            # Bắt ValueError từ repository (ví dụ câu hỏi đã nằm trong đề)
            messagebox.showerror(
                "Không thể xóa câu hỏi",
                f"{str(e)}\n\n💡 Hướng dẫn xử lý: Hãy chỉnh sửa nội dung câu hỏi thay vì xóa, hoặc hủy đề thi chứa câu hỏi này trước.",
                parent=self
            )

    def on_import_file(self):
        """Nhập hàng loạt câu hỏi từ file văn bản mẫu .txt."""
        path = filedialog.askopenfilename(
            title="Chọn file câu hỏi mẫu (.txt)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            parent=self
        )
        if not path:
            return

        topics = self.repo.list_topics()
        default_topic_id = topics[0].id if topics else ""

        added, errors = import_questions_from_file(path, self.repo, default_topic_id=default_topic_id)

        msg = f"Đã nhập thành công: {added} câu hỏi vào ngân hàng đề.\n"
        if errors:
            msg += f"\nPhát hiện {len(errors)} vấn đề cần lưu ý:\n"
            msg += "\n".join(errors[:8])
            if len(errors) > 8:
                msg += f"\n... và {len(errors) - 8} dòng lỗi khác."

        if added > 0:
            messagebox.showinfo("Kết quả nhập file", msg, parent=self)
        else:
            messagebox.showwarning("Kết quả nhập file", msg, parent=self)

        self.on_search()

    def on_import_api(self):
        """Nhập câu hỏi tự động từ Web API (Open Trivia DB)."""
        topic_id = self._select_topic_dialog("Chọn chủ đề lưu câu hỏi từ API")
        if not topic_id:
            return

        # Xác nhận số lượng
        confirm = messagebox.askyesno(
            "Nhập câu hỏi từ API",
            "Hệ thống sẽ tải 10 câu hỏi trắc nghiệm tự động từ Open Trivia DB, "
            "làm sạch HTML entities, chuyển đổi sang 4 phương án và lưu vào ngân hàng đề.\n\n"
            "Bạn có muốn tiếp tục?",
            parent=self
        )
        if not confirm:
            return

        added, errors = import_questions_from_api(
            topic_id=topic_id,
            repository=self.repo,
            amount=10
        )

        msg = f"Đã nhập thành công {added} câu hỏi từ API.\n"
        if errors:
            msg += "\nChi tiết thông báo:\n" + "\n".join(errors[:5])

        if added > 0:
            messagebox.showinfo("Kết quả từ API", msg, parent=self)
        else:
            messagebox.showwarning("Kết quả từ API", msg, parent=self)

        self.on_search()
