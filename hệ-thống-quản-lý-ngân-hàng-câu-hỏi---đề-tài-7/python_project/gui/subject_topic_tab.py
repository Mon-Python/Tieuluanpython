"""gui/subject_topic_tab.py
========================
[B sở hữu] Tab Quản lý Môn học và Chủ đề:
- 2 Bảng Treeview trực quan: Bảng Môn học và Bảng Chủ đề thuộc môn được chọn.
- Đầy đủ các chức năng CRUD cho cả Môn học và Chủ đề.
- Ràng buộc toàn vẹn dữ liệu cha - con nghiêm ngặt:
  + Không cho phép xóa môn học nếu còn chủ đề trực thuộc.
  + Không cho phép xóa chủ đề nếu còn câu hỏi trực thuộc trong ngân hàng đề.
- Chỉ hiển thị cho Quản trị viên (Admin) theo phân quyền.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List

from base_models import Subject, Topic, User
from config import PADDING
from data_repository import JsonDataRepository


class SubjectTopicTab(ttk.Frame):
    def __init__(self, master, repository: JsonDataRepository,
                 current_user: Optional[User] = None, **kwargs):
        super().__init__(master, padding=PADDING, **kwargs)
        self.repo = repository
        self.current_user = current_user
        self.selected_subject_id: Optional[str] = None
        self.selected_topic_id: Optional[str] = None
        self._build_ui()
        self.reload_subjects()

    def _build_ui(self):
        # Chia làm 2 cột: Cột trái (Môn học), Cột phải (Chủ đề con)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ==========================================
        # 1. KHUNG TRÁI: MÔN HỌC (SUBJECTS)
        # ==========================================
        left_frame = ttk.LabelFrame(paned, text="Danh mục Môn học", padding=8)
        paned.add(left_frame, weight=1)

        cols_s = ("id", "name", "desc")
        self.tree_subj = ttk.Treeview(left_frame, columns=cols_s, show="headings", selectmode="browse")
        self.tree_subj.heading("id", text="Mã môn")
        self.tree_subj.heading("name", text="Tên môn học")
        self.tree_subj.heading("desc", text="Mô tả")

        self.tree_subj.column("id", width=85, anchor="center")
        self.tree_subj.column("name", width=180, anchor="w")
        self.tree_subj.column("desc", width=160, anchor="w")

        s_scroll_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree_subj.yview)
        self.tree_subj.configure(yscrollcommand=s_scroll_y.set)

        self.tree_subj.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        s_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_subj.bind("<<TreeviewSelect>>", self.on_subject_select)

        # Nút CRUD Môn học
        s_btn_box = ttk.Frame(left_frame, padding=(0, 6, 0, 0))
        s_btn_box.pack(fill=tk.X)

        ttk.Button(s_btn_box, text="➕ Thêm môn", command=self.on_add_subject).pack(side=tk.LEFT, padx=2)
        ttk.Button(s_btn_box, text="✏️ Sửa môn", command=self.on_edit_subject).pack(side=tk.LEFT, padx=2)
        ttk.Button(s_btn_box, text="🗑️ Xóa môn", command=self.on_delete_subject).pack(side=tk.LEFT, padx=2)

        # ==========================================
        # 2. KHUNG PHẢI: CHỦ ĐỀ (TOPICS)
        # ==========================================
        right_frame = ttk.LabelFrame(paned, text="Danh mục Chủ đề (theo Môn đã chọn)", padding=8)
        paned.add(right_frame, weight=1)

        self.lbl_current_subj = ttk.Label(
            right_frame,
            text="👉 Hãy chọn một môn học ở bên trái để xem các chủ đề con",
            font=("Segoe UI", 9, "bold"),
            foreground="#2563eb"
        )
        self.lbl_current_subj.pack(anchor="w", pady=(0, 4))

        cols_t = ("id", "name", "q_count")
        self.tree_topic = ttk.Treeview(right_frame, columns=cols_t, show="headings", selectmode="browse")
        self.tree_topic.heading("id", text="Mã chủ đề")
        self.tree_topic.heading("name", text="Tên chủ đề")
        self.tree_topic.heading("q_count", text="Số câu hỏi")

        self.tree_topic.column("id", width=95, anchor="center")
        self.tree_topic.column("name", width=220, anchor="w")
        self.tree_topic.column("q_count", width=85, anchor="center")

        t_scroll_y = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree_topic.yview)
        self.tree_topic.configure(yscrollcommand=t_scroll_y.set)

        self.tree_topic.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        t_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_topic.bind("<<TreeviewSelect>>", self.on_topic_select)

        # Nút CRUD Chủ đề
        t_btn_box = ttk.Frame(right_frame, padding=(0, 6, 0, 0))
        t_btn_box.pack(fill=tk.X)

        self.btn_add_topic = ttk.Button(t_btn_box, text="➕ Thêm chủ đề", command=self.on_add_topic)
        self.btn_add_topic.pack(side=tk.LEFT, padx=2)

        self.btn_edit_topic = ttk.Button(t_btn_box, text="✏️ Sửa chủ đề", command=self.on_edit_topic)
        self.btn_edit_topic.pack(side=tk.LEFT, padx=2)

        self.btn_del_topic = ttk.Button(t_btn_box, text="🗑️ Xóa chủ đề", command=self.on_delete_topic)
        self.btn_del_topic.pack(side=tk.LEFT, padx=2)

    def reload_subjects(self):
        """Tải lại danh sách môn học vào treeview."""
        for r in self.tree_subj.get_children():
            self.tree_subj.delete(r)

        subjects = self.repo.list_subjects()
        for s in subjects:
            self.tree_subj.insert("", tk.END, iid=s.id, values=(s.id, s.name, s.description))

        if subjects:
            # Tự động chọn dòng đầu tiên
            first_id = subjects[0].id
            self.tree_subj.selection_set(first_id)
            self.selected_subject_id = first_id
            self.reload_topics(first_id)
        else:
            self.reload_topics(None)

    def on_subject_select(self, event=None):
        selected = self.tree_subj.selection()
        if selected:
            subj_id = selected[0]
            self.selected_subject_id = subj_id
            self.reload_topics(subj_id)

    def reload_topics(self, subject_id: Optional[str]):
        """Tải lại danh sách chủ đề thuộc môn được chọn."""
        for r in self.tree_topic.get_children():
            self.tree_topic.delete(r)

        if not subject_id:
            self.lbl_current_subj.config(text="👉 Vui lòng chọn một môn học để quản lý chủ đề.")
            return

        subj = self.repo.get_subject(subject_id)
        if subj:
            self.lbl_current_subj.config(text=f"📚 Môn hiện tại: {subj.name} (Mã: {subj.id})")

        topics = self.repo.list_topics(subject_id=subject_id)
        for t in topics:
            # Đếm số câu hỏi của chủ đề này
            q_count = len(self.repo.list_questions(topic_id=t.id))
            self.tree_topic.insert("", tk.END, iid=t.id, values=(t.id, t.name, f"{q_count} câu"))

    def on_topic_select(self, event=None):
        selected = self.tree_topic.selection()
        if selected:
            self.selected_topic_id = selected[0]

    # ============================================================
    # CRUD MÔN HỌC
    # ============================================================
    def on_add_subject(self):
        dlg = tk.Toplevel(self)
        dlg.title("Thêm môn học mới")
        dlg.geometry("380x220")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Tên môn học (*):", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 2))
        ent_name = ttk.Entry(dlg, width=40)
        ent_name.pack(padx=15, pady=2)
        ent_name.focus()

        ttk.Label(dlg, text="Mô tả tóm tắt:").pack(anchor="w", padx=15, pady=(8, 2))
        ent_desc = ttk.Entry(dlg, width=40)
        ent_desc.pack(padx=15, pady=2)

        def on_save():
            name = ent_name.get().strip()
            desc = ent_desc.get().strip()
            if not name:
                messagebox.showerror("Thiếu thông tin", "Tên môn học không được để trống.", parent=dlg)
                return

            subj = Subject.create(name=name, description=desc)
            try:
                self.repo.add_subject(subj)
                messagebox.showinfo("Thành công", f"Đã thêm môn học '{name}'!", parent=dlg)
                dlg.destroy()
                self.reload_subjects()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=dlg)

        btn_box = ttk.Frame(dlg, padding=10)
        btn_box.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(btn_box, text="💾 Lưu", command=on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_box, text="Hủy", command=dlg.destroy).pack(side=tk.RIGHT, padx=5)

    def on_edit_subject(self):
        if not self.selected_subject_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn môn học cần sửa.", parent=self)
            return

        subj = self.repo.get_subject(self.selected_subject_id)
        if not subj:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Sửa môn học: {subj.name}")
        dlg.geometry("380x220")
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Tên môn học (*):", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=(15, 2))
        ent_name = ttk.Entry(dlg, width=40)
        ent_name.pack(padx=15, pady=2)
        ent_name.insert(0, subj.name)

        ttk.Label(dlg, text="Mô tả tóm tắt:").pack(anchor="w", padx=15, pady=(8, 2))
        ent_desc = ttk.Entry(dlg, width=40)
        ent_desc.pack(padx=15, pady=2)
        ent_desc.insert(0, subj.description)

        def on_save():
            name = ent_name.get().strip()
            desc = ent_desc.get().strip()
            if not name:
                messagebox.showerror("Thiếu thông tin", "Tên môn học không được để trống.", parent=dlg)
                return

            updated = Subject(id=subj.id, name=name, description=desc, created_at=subj.created_at)
            try:
                self.repo.update_subject(subj.id, updated)
                messagebox.showinfo("Thành công", "Đã cập nhật môn học!", parent=dlg)
                dlg.destroy()
                self.reload_subjects()
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e), parent=dlg)

        btn_box = ttk.Frame(dlg, padding=10)
        btn_box.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Button(btn_box, text="💾 Lưu thay đổi", command=on_save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_box, text="Hủy", command=dlg.destroy).pack(side=tk.RIGHT, padx=5)

    def on_delete_subject(self):
        if not self.selected_subject_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn môn học cần xóa.", parent=self)
            return

        subj = self.repo.get_subject(self.selected_subject_id)
        if not subj:
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa môn học",
            f"Bạn có chắc chắn muốn xóa môn học '{subj.name}' (Mã: {subj.id})?",
            icon="warning",
            parent=self
        )
        if not confirm:
            return

        try:
            self.repo.delete_subject(subj.id)
            messagebox.showinfo("Đã xóa", f"Môn học '{subj.name}' đã được xóa.", parent=self)
            self.selected_subject_id = None
            self.reload_subjects()
        except ValueError as e:
            # Bắt lỗi ràng buộc cha - con từ repository
            messagebox.showerror(
                "Không thể xóa môn học",
                f"{str(e)}\n\n💡 Hướng dẫn xử lý: Vui lòng xóa hoặc chuyển toàn bộ chủ đề thuộc môn học này sang môn khác trước.",
                parent=self
            )

    # ============================================================
    # CRUD CHỦ ĐỀ
    # ============================================================
    def on_add_topic(self):
        if not self.selected_subject_id:
            messagebox.showwarning("Chưa chọn môn", "Vui lòng chọn một môn học ở danh sách bên trái trước.", parent=self)
            return

        name = simpledialog.askstring("Thêm chủ đề mới", "Nhập tên chủ đề mới:", parent=self)
        if not name or not name.strip():
            return

        topic = Topic.create(subject_id=self.selected_subject_id, name=name.strip())
        try:
            self.repo.add_topic(topic)
            messagebox.showinfo("Thành công", f"Đã thêm chủ đề '{name.strip()}'!", parent=self)
            self.reload_topics(self.selected_subject_id)
        except ValueError as e:
            messagebox.showerror("Lỗi khi thêm chủ đề", str(e), parent=self)

    def on_edit_topic(self):
        selected = self.tree_topic.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn chủ đề cần sửa.", parent=self)
            return

        topic_id = selected[0]
        topic = self.repo.get_topic(topic_id)
        if not topic:
            return

        new_name = simpledialog.askstring("Sửa tên chủ đề", "Nhập tên mới cho chủ đề:", initialvalue=topic.name, parent=self)
        if not new_name or not new_name.strip():
            return

        updated = Topic(id=topic.id, subject_id=topic.subject_id, name=new_name.strip(), created_at=topic.created_at)
        try:
            self.repo.update_topic(topic.id, updated)
            messagebox.showinfo("Thành công", "Đã cập nhật chủ đề thành công!", parent=self)
            self.reload_topics(self.selected_subject_id)
        except ValueError as e:
            messagebox.showerror("Lỗi khi sửa chủ đề", str(e), parent=self)

    def on_delete_topic(self):
        selected = self.tree_topic.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn chủ đề cần xóa.", parent=self)
            return

        topic_id = selected[0]
        topic = self.repo.get_topic(topic_id)
        if not topic:
            return

        confirm = messagebox.askyesno(
            "Xác nhận xóa chủ đề",
            f"Bạn có chắc chắn muốn xóa chủ đề '{topic.name}'?",
            icon="warning",
            parent=self
        )
        if not confirm:
            return

        try:
            self.repo.delete_topic(topic_id)
            messagebox.showinfo("Đã xóa", f"Chủ đề '{topic.name}' đã được xóa.", parent=self)
            self.reload_topics(self.selected_subject_id)
        except ValueError as e:
            # Bắt lỗi ràng buộc còn câu hỏi thuộc chủ đề
            messagebox.showerror(
                "Không thể xóa chủ đề",
                f"{str(e)}\n\n💡 Hướng dẫn xử lý: Vui lòng xóa hết các câu hỏi thuộc chủ đề này trong tab 'Quản lý câu hỏi' trước khi xóa chủ đề.",
                parent=self
            )
