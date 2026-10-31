"""A small Canvas-based chart for topic performance percentages."""

import tkinter as tk


class BarChart(tk.Canvas):
    """Draw labeled percentage bars and expose a deterministic scaling helper."""

    @staticmethod
    def scaled_bars(values, height):
        return [
            (label, max(0.0, float(value)) * max(0.0, float(height)) / 100.0)
            for label, value in values.items()
        ]

    def __init__(self, master=None, **kwargs):
        kwargs.setdefault("height", 180)
        kwargs.setdefault("background", "white")
        kwargs.setdefault("highlightthickness", 1)
        super().__init__(master, **kwargs)
        self._values = {}
        self.bind("<Configure>", self._redraw)

    def set_values(self, values):
        self._values = dict(values or {})
        self._draw()

    def _redraw(self, _event=None):
        self._draw()

    def _draw(self):
        self.delete("all")
        if not self._values:
            self.create_text(
                10, 12, anchor="nw", text="Chưa có thống kê theo chủ đề."
            )
            return

        width = max(self.winfo_width(), 220)
        height = max(self.winfo_height(), 100)
        row_height = max(28, (height - 12) / len(self._values))
        bar_height = min(16, row_height - 8)

        for index, (label, bar_height_value) in enumerate(
            self.scaled_bars(self._values, row_height - 8)
        ):
            top = 6 + index * row_height
            self.create_text(8, top + bar_height / 2, anchor="w", text=str(label))
            label_width = min(max(len(str(label)) * 7 + 20, 85), width * 0.45)
            bar_left = label_width
            bar_width = max(1, width - bar_left - 48)
            self.create_rectangle(
                bar_left, top, bar_left + bar_width, top + bar_height,
                fill="#e2e8f0", outline="",
            )
            self.create_rectangle(
                bar_left, top,
                bar_left + bar_width * bar_height_value / max(row_height - 8, 1),
                top + bar_height,
                fill="#2563eb", outline="",
            )
            self.create_text(
                width - 8, top + bar_height / 2, anchor="e",
                text=f"{float(self._values[label]):.1f}%",
            )
