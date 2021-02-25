import numpy as np

from . import ArrayWin


class ArrayPad(ArrayWin):
    """
    :class: ArrayPads are windows that can be larger than the screen.  They have an extra buffer, `pad`. Rectangular sections of `pad`
    will be copied to the buffer and pushed to the screen.  Pad colors are stored in `pad_colors`.

    Parameters
    ----------
    rows, cols:
        dimensions of pad

    min_row, min_col: optional
        the upper left corner of the pad region to be displayed (default is 0)
    """

    left_scrollbar = False
    right_scrollbar = False
    top_scrollbar = False
    bottom_scrollbar = False

    up_arrow = "⯅"
    down_arrow = "⯆"
    left_arrow = "⯇"
    right_arrow = "⯈"

    bar_indicator = "█"
    bar_indicator_thickness = 3
    bar_fill = "░"
    bar_color = 0

    def __init__(self, *args, rows=None, cols=None, min_row=0, min_col=0, **kwargs):
        self._rows = rows
        self._cols = cols
        self.min_row = min_row
        self.min_col = min_col
        self.pad = self.pad_colors= None

        super().__init__(*args, **kwargs)

    def update_geometry(self):
        if self.root is None:
            return

        super().update_geometry()

        if self.pad is None:
            rows = self.__dict__["rows"] = self.height if self._rows is None else self._rows
            cols = self.__dict__["cols"] = self.width if self._cols is None else self._cols
            del self._rows
            del self._cols
            self.pad = np.full((rows, cols), self.default_character)
            self.pad_colors = np.full((rows, cols), self.color)

    def __getitem__(self, key):
        return self.pad[key]

    def __setitem__(self, key, text):
        """
        Coerce `text` into a ndarray then call `pad.__setitem__(key, text)`.

        Notes
        -----
        If `len(text) > 1`, `text` is coerced into an array or an array of arrays (depending on the presence of newlines).
        If the array's shape can't be cast to `self.buffer` it will be rotated and tried again (setting the text vertically).
        """
        if "\n" in text:
            text = np.array(tuple(map(tuple, text.rstrip("\n").splitlines())))
        elif len(text) > 1:
            text = np.array(tuple(text))

        try:
            self.pad[key] = text
        except ValueError:
            self.pad[key] = np.rot90(text if len(text.shape) == 2 else text[None, ], -1)  # Try to fit the text vertically

    def push(self):
        """Write the buffers to the window.
        """
        top, bottom = self.top_scrollbar, self.bottom_scrollbar
        left, right = self.left_scrollbar, self.right_scrollbar

        buf_h, buf_w = self.buffer.shape
        buf_h -= top + bottom
        buf_w -= left + right

        min_row, min_col = self.min_row, self.min_col

        min_h, min_w = min(buf_h, self.rows - min_row), min(buf_w, self.cols - min_col)
        self.buffer[top: top + min_h, left: left + min_w] = self.pad[min_row: min_row + min_h, min_col: min_col + min_w]
        self.colors[top: top + min_h, left: left + min_w] = self.pad_colors[min_row: min_row + min_h, min_col: min_col + min_w]

        if top:
            self.buffer[0, left: -right or None] = self._bar(vertical=False)
            self.colors[0, left: -right or None] = self.bar_color
        if bottom:
            self.buffer[-1, left: -right or None] = self._bar(vertical=False)
            self.colors[-1, left: -right or None] = self.bar_color
        if left:
            self.buffer[top: -bottom or None, 0] = self._bar()
            self.colors[top: -bottom or None, 0] = self.bar_color
        if right:
            self.buffer[top: -bottom or None, -1] = self._bar()
            self.colors[top: -bottom or None, -1] = self.bar_color

        super().push()

    def _bar(self, vertical=True):
        if vertical:
            start, end = self.up_arrow, self.down_arrow
            length = self.buffer.shape[0] - self.bottom_scrollbar - self.top_scrollbar
            percent = self.min_row / (self.rows - length)
        else:
            start, end = self.left_arrow, self.right_arrow
            length = self.buffer.shape[1] - self.left_scrollbar - self.right_scrollbar
            percent = self.min_col / (self.cols - length)

        filler_amount = length - self.bar_indicator_thickness - 2
        start_filler = int(percent * filler_amount)

        return tuple(
            f'{start}{self.bar_fill * start_filler}'
            f'{self.bar_indicator * self.bar_indicator_thickness}'
            f'{self.bar_fill * (filler_amount - start_filler)}{end}'
        )

    @bind_to("rows", "cols")
    def _resize_pad(self):
        old_rows, old_cols = self.pad.shape
        rows, cols = self.rows, self.cols
        min_rows, min_cols = min(rows, old_rows), min(cols, old_cols)

        new_pad = np.full((rows, cols), self.default_character)
        new_pad[:min_rows, :min_cols] = self.pad[:min_rows, :min_cols]

        new_pad_colors = np.full((rows, cols), self.color)
        new_pad_colors[:min_rows, :min_cols] = self.pad_colors[:min_rows, :min_cols]

        self.pad = new_pad
        self.pad_colors = new_pad_colors

    def refresh(self):
        """Redraw widget.
        """
        self.push()

        h, w = self.height, self.width
        for widget in self.children:
            if widget is None:
                continue

            widget.refresh()
            y, x = widget.top - self.min_row, widget.left - self.min_col
            src_t, des_t = (-y, 0) if y < 0 else (0, y)
            src_l, des_l = (-x, 0) if x < 0 else (0, x)
            des_h = min(h - 1, des_t + widget.height)
            des_w = min(w - 1, des_l + widget.width - 1)

            widget.overlay(self.window, src_t, src_l, des_t, des_l, des_h, des_w)
