"""gui/question_editor.py
======================
[B sở hữu] Custom Widget QuestionEditor kế thừa tk.Frame:
- Cho phép nhập/sửa nội dung câu hỏi, 4 phương án lựa chọn (A, B, C, D).
- Radiobutton chọn phương án đúng duy nhất (Single Choice).
- Combobox chọn mức độ khó (Dễ / Khó).
- Tích hợp kiểm tra tính hợp lệ tức thì qua validators.py và Question.is_valid().
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from base_models import DifficultyLevel, Option, Question
from validators import validate_question_data


class QuestionEditor(ttk.Frame):
    """
    Custom Widget chuyên biệt kế thừa ttk.Frame phục vụ nhập/sửa câu hỏi trắc nghiệm.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.editing_question_id: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        # Thiết lập cột co dãn
        self.columnconfigure(1, weight=1)

        # 1. Hàng: Mức độ khó
        lbl_diff = ttk.Label(self, text="Mức độ khó:", font=("Segoe UI", 9, "bold"))
        lbl_diff.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.var_diff = tk.StringVar(value="de")
        self.cbo_diff = ttk.Combobox(
            self,
            textvariable=self.var_diff,
            values=["Dễ (de)", "Khó (kho)"],
            state="readonly",
            width=20
        )
        self.cbo_diff.current(0)
        self.cbo_diff.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # 2. Hàng: Nội dung câu hỏi
        lbl_content = ttk.Label(self, text="Nội dung câu hỏi:", font=("Segoe UI", 9, "bold"))
        lbl_content.grid(row=1, column=0, sticky="nw", padx=5, pady=5)

        self.txt_content = tk.Text(self, height=4, width=50, wrap="word", font=("Segoe UI", 10))
        self.txt_content.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 3. Khung 4 phương án trả lời
        grp_options = ttk.LabelFrame(self, text="Các phương án trả lời (chọn nút tròn để đánh dấu ĐÁP ÁN ĐÚNG)")
        grp_options.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        grp_options.columnconfigure(2, weight=1)

        self.correct_var = tk.IntVar(value=0)  # 0, 1, 2, 3 tương ứng A, B, C, D
        self.option_entries: List[ttk.Entry] = []
        labels = ["A", "B", "C", "D"]

        for i, lbl in enumerate(labels):
            rb = ttk.Radiobutton(
                grp_options,
                text=f"Đáp án {lbl}",
                value=i,
                variable=self.correct_var
            )
            rb.grid(row=i, column=0, sticky="w", padx=8, pady=4)

            lbl_opt = ttk.Label(grp_options, text=f"{lbl}:", font=("Segoe UI", 9, "bold"))
            lbl_opt.grid(row=i, column=1, sticky="e", padx=(5, 2), pady=4)

            entry = ttk.Entry(grp_options, font=("Segoe UI", 9))
            entry.grid(row=i, column=2, sticky="ew", padx=8, pady=4)
            self.option_entries.append(entry)

    def set_question(self, question: Optional[Question]):
        """Nạp dữ liệu câu hỏi vào form để chỉnh sửa."""
        self.clear()
        if not question:
            return

        self.editing_question_id = question.id

        # Mức độ
        if question.difficulty == DifficultyLevel.KHO or question.difficulty == "kho":
            self.cbo_diff.current(1)
        else:
            self.cbo_diff.current(0)

        # Nội dung
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert("1.0", question.content)

        # 4 Phương án
        for i, opt in enumerate(question.options[:4]):
            self.option_entries[i].delete(0, tk.END)
            self.option_entries[i].insert(0, opt.content)
            if opt.is_correct:
                self.correct_var.set(i)

    def get_question(self, topic_id: str) -> Optional[Question]:
        """
        Đọc và kiểm tra tính hợp lệ dữ liệu từ form:
        - Nếu hợp lệ: trả về đối tượng Question (giữ nguyên ID cũ nếu đang sửa).
        - Nếu không hợp lệ: hiện hộp thoại cảnh báo và trả về None.
        """
        content = self.txt_content.get("1.0", tk.END).strip()
        diff_choice = "kho" if "kho" in self.cbo_diff.get().lower() else "de"
        diff_level = DifficultyLevel.KHO if diff_choice == "kho" else DifficultyLevel.DE
        
        options_text = [entry.get().strip() for entry in self.option_entries]
        correct_idx = self.correct_var.get()

        ok, msg = validate_question_data(
            content=content,
            options=options_text,
            correct_index=correct_idx,
            difficulty=diff_choice
        )

        if not ok:
            messagebox.showerror("Dữ liệu câu hỏi chưa hợp lệ", msg, parent=self)
            return None

        # Tạo đối tượng Option
        opts = [Option.create(content=txt, is_correct=(i == correct_idx))
                for i, txt in enumerate(options_text)]

        if self.editing_question_id:
            # Sửa câu hỏi cũ
            q = Question(
                id=self.editing_question_id,
                topic_id=topic_id,
                content=content,
                difficulty=diff_level,
                options=opts
            )
        else:
            # Tạo câu hỏi mới
            q = Question.create(
                topic_id=topic_id,
                content=content,
                difficulty=diff_level,
                options=opts
            )

        return q

    def clear(self):
        """Làm sạch toàn bộ form nhập."""
        self.editing_question_id = None
        self.txt_content.delete("1.0", tk.END)
        self.cbo_diff.current(0)
        self.correct_var.set(0)
        for entry in self.option_entries:
            entry.delete(0, tk.END)
