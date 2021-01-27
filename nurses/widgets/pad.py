import numpy as np

from . import ArrayWin


class Pad(ArrayWin):
    """
    Pads are windows that can be larger than the screen.  They have an extra buffer, `pad`: rectangular sections of `pad`
    will be copied to the buffer and pushed to the screen.

    Parameters
    ----------
    rows, cols:
        dimensions of pad

    min_row, min_col: optional
        the upper left corner of the pad region to be displayed (default is 0)
    """

    def __init__(self, *args, rows, cols, min_row=0, min_col=0, **kwargs):
        super().__init__(*args, **kwargs)

        self.rows = rows
        self.cols = cols
        self.min_row = min_row
        self.min_col = min_col

        self.pad = np.full((rows, cols), " ")
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
        buf_h, buf_w = self.buffer.shape
        min_row, min_col = self.min_row, self.min_col

        min_h, min_w = min(buf_h, self.rows - min_row), min(buf_w, self.cols - min_col)
        self.buffer[:min_h, :min_w] = self.pad[min_row: min_row + min_h, min_col: min_col + min_w]
        self.colors[:min_h, :min_w] = self.pad_colors[min_row: min_row + min_h, min_col: min_col + min_w]

        super().push()

    @bind_to("rows", "cols")
    def _resize_pad(self):
        old_rows, old_cols = self.pad.shape
        rows, cols = self.rows, self.cols
        min_rows, min_cols = min(rows, old_rows), min(cols, old_cols)

        new_pad = np.full((rows, cols), " ")
        new_pad[:min_rows, :min_cols] = self.pad[:min_rows, :min_cols]

        new_pad_colors = np.full((rows, cols), self.color)
        new_pad_colors[:min_rows, :min_cols] = self.pad_colors[:min_rows, :min_cols]

        self.pad = new_pad
        self.pad_colors = new_pad_colors
