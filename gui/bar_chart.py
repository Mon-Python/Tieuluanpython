"""
gui/bar_chart.py
================
[D sở hữu] Custom Widget vẽ biểu đồ cột bằng tk.Canvas.
Dùng chung cho nhiều loại thống kê (thống kê theo chủ đề, điểm số,...).
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Optional, Union

from config import (
    COLOR_CHART_BAR, COLOR_TEXT, FONT_FAMILY, FONT_NORMAL, PADDING
)


class BarChart(ttk.Frame):
    """
    Widget biểu đồ cột linh hoạt sử dụng Canvas.
    Data input format:
    data = [
        {"label": "Chủ đề A", "value": 85.5, "subtext": "17/20 câu"},
        {"label": "Chủ đề B", "value": 60.0, "subtext": "6/10 câu"},
        ...
    ]
    Hoặc dict đơn giản: {"Chủ đề A": 85.5, "Chủ đề B": 60.0}
    """

    def __init__(self, parent, title: str = "", max_value: float = 100.0,
                 unit: str = "%", bar_color: str = COLOR_CHART_BAR, **kwargs):
        super().__init__(parent, **kwargs)
        self.chart_title = title
        self.max_value = (
            max_value if math.isfinite(max_value) and max_value > 0 else 100.0
        )
        self.unit = unit
        self.bar_color = bar_color
        self._raw_data: list[dict] = []

        self._build_ui()
        self.canvas.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Tiêu đề biểu đồ
        if self.chart_title:
            self.lbl_title = ttk.Label(
                self, text=self.chart_title,
                font=(FONT_FAMILY, 11, "bold"), anchor="center"
            )
            self.lbl_title.grid(row=0, column=0, sticky="ew", pady=(0, PADDING))

        # Canvas chính để vẽ
        self.canvas = tk.Canvas(
            self, bg="white", highlightthickness=1,
            highlightbackground="#cbd5e1"
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

    def set_data(self, data: Union[list[dict], dict[str, float]]) -> None:
        """
        Nạp dữ liệu mới và cập nhật lại biểu đồ.
        """
        if isinstance(data, dict):
            source_data = [
                (str(label), value, "") for label, value in data.items()
            ]
        elif isinstance(data, list):
            source_data = []
            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise TypeError(
                        f"Chart item at index {index} must be a dictionary."
                    )
                source_data.append((
                    str(item.get("label", "")),
                    item.get("value", 0.0),
                    str(item.get("subtext", "")) if "subtext" in item else "",
                ))
        else:
            raise TypeError("Chart data must be a list of dictionaries or a dictionary.")

        new_data = []
        for index, (label, value, subtext) in enumerate(source_data):
            try:
                numeric_value = float(value)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    f"Chart value at index {index} must be a finite number."
                ) from exc
            if not math.isfinite(numeric_value):
                raise ValueError(
                    f"Chart value at index {index} must be a finite number."
                )
            new_data.append({
                "label": label,
                "value": numeric_value,
                "subtext": subtext,
            })

        self._raw_data = new_data
        self.draw()

    def clear(self) -> None:
        """Xóa trắng biểu đồ."""
        self._raw_data.clear()
        self.canvas.delete("all")

    def _on_resize(self, event):
        """Vẽ lại biểu đồ khi thay đổi kích thước cửa sổ."""
        self.draw(event.width, event.height)

    def draw(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        """Vẽ toàn bộ trục, lưới và các cột dữ liệu lên Canvas."""
        self.canvas.delete("all")

        canvas_w = self.canvas.winfo_width() if width is None else width
        canvas_h = self.canvas.winfo_height() if height is None else height
        if canvas_w <= 1 or canvas_h <= 1:
            return

        if not self._raw_data:
            self.canvas.create_text(
                canvas_w / 2, canvas_h / 2,
                text="Không có dữ liệu thống kê",
                font=FONT_NORMAL, fill="#94a3b8"
            )
            return

        # Căn chỉnh lề
        margin_left = 50
        margin_right = 20
        margin_top = 30
        margin_bottom = 50

        plot_w = canvas_w - margin_left - margin_right
        plot_h = canvas_h - margin_top - margin_bottom
        if plot_w <= 0 or plot_h <= 0:
            return

        # 1. Vẽ các đường lưới ngang & Nhãn trục Y
        grid_steps = 4
        for i in range(grid_steps + 1):
            val = (self.max_value / grid_steps) * i
            y = margin_top + plot_h - (plot_h * (i / grid_steps))

            # Đường lưới
            self.canvas.create_line(
                margin_left, y, margin_left + plot_w, y,
                fill="#e2e8f0", dash=(2, 2)
            )
            # Nhãn giá trị Y
            self.canvas.create_text(
                margin_left - 8, y,
                text=f"{val:g}{self.unit}",
                anchor="e", font=(FONT_FAMILY, 8), fill="#64748b"
            )

        # Trục Y và trục X
        self.canvas.create_line(
            margin_left, margin_top, margin_left, margin_top + plot_h,
            fill="#94a3b8", width=1.5
        )
        self.canvas.create_line(
            margin_left, margin_top + plot_h, margin_left + plot_w, margin_top + plot_h,
            fill="#94a3b8", width=1.5
        )

        # 2. Vẽ các cột
        n = len(self._raw_data)
        slot_w = plot_w / n
        bar_w = min(slot_w * 0.55, 60)  # Giới hạn chiều rộng tối đa của cột

        for i, item in enumerate(self._raw_data):
            val = min(max(item["value"], 0.0), self.max_value)
            h = (val / self.max_value) * plot_h

            # Tọa độ cột
            center_x = margin_left + (i + 0.5) * slot_w
            x0 = center_x - bar_w / 2
            x1 = center_x + bar_w / 2
            y1 = margin_top + plot_h
            y0 = y1 - h

            # Vẽ hình chữ nhật cột
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=self.bar_color, outline="#1d4ed8", width=1
            )

            # Giá trị trên đỉnh cột
            val_text = f"{val:.1f}{self.unit}"
            self.canvas.create_text(
                center_x, y0 - 8,
                text=val_text,
                font=(FONT_FAMILY, 9, "bold"), fill=COLOR_TEXT
            )

            # Tên nhãn bên dưới trục X (Cắt bớt nếu quá dài)
            label = item["label"]
            display_label = label if len(label) <= 12 else label[:9] + "..."
            self.canvas.create_text(
                center_x, y1 + 12,
                text=display_label,
                font=(FONT_FAMILY, 8), fill=COLOR_TEXT, anchor="n"
            )

            # Chú thích phụ (ví dụ: số câu đúng/tổng câu)
            if item.get("subtext"):
                self.canvas.create_text(
                    center_x, y1 + 28,
                    text=item["subtext"],
                    font=(FONT_FAMILY, 7), fill="#64748b", anchor="n"
                )