import curses

import numpy as np

from . import Widget


BORDER_STYLES = {
    "light" : "┌┐│─└┘",
    "heavy" : "┏┓┃━┗┛",
    "double": "╔╗║═╚╝",
    "curved": "╭╮│─╰╯",
}


class ArrayWin(Widget):
    """
    A Widget that uses a numpy array to store its state and uses a very numpy-ish api.

    Other Parameters
    ----------------
    border: optional
        The border type; one of `nurses.widget.BORDER_STYLES`. (by default a widget has no border)
    border_color: optional
        A curses color_pair.  If a border is given, border_color will be the color of the border. (the default is `color`)

    Notes
    -----
    __getitem__ and __setitem__ call the respective buffer functions directly, so one can slice
    and write to a Widget as if it was a numpy array.
    """
    def __init__(self, *args, border=None, border_color=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._buffer = None
        self._colors = None

        self.has_border = (border, border_color) if border is not None else False

    def update_geometry(self):
        if not self.has_root:
            return

        super().update_geometry()

        if self._buffer is None:
            h, w = self.height, self.width
            self._buffer = np.full((h, w), " ")
            self._colors = np.full((h, w), self.color)

            if self.has_border:
                self.border(*self.has_border)

    @property
    def colors(self):
        return self._colors[1: -1, 1: -1] if self.has_border else self._colors

    @colors.setter
    def colors(self, array):
        if self.has_border:
            self._colors[1: -1, 1: -1] = array
        else:
            self._colors = array

    @property
    def buffer(self):
        return self._buffer[1: -1, 1: -1] if self.has_border else self._buffer

    @buffer.setter
    def buffer(self, array):
        if self.has_border:
            self._buffer[1: -1, 1: -1] = array
        else:
            self._buffer = array

    def _resize(self):
        if self.window is None:
            return

        if self.has_border:
            self._buffer[:, -1] = self._buffer[-1] = " "  # Erase the right-most/bottom-most border in case widget expands

        height, width = self.height, self.width
        old_h, old_w = self._buffer.shape
        min_h, min_w = min(height, old_h), min(width, old_w)

        new_buffer = np.full((height, width), " ")
        new_buffer[:min_h, :min_w] = self._buffer[:min_h, :min_w]

        new_colors = np.full((height, width), self.color)
        new_colors[:min_h, :min_w] = self._colors[:min_h, :min_w]

        self._buffer = new_buffer
        self._colors = new_colors

        super()._resize()

        if self.has_border:
            self.border(*self.has_border)

    def push(self):
        """Write the buffers to the window.
        """
        it = np.nditer((self._buffer, self._colors), ["multi_index"])
        for char, color in it:
            y, x = it.multi_index
            self.window.addstr(y, x, str(char), color)

    def refresh(self):
        self.push()
        super().refresh()

    def __getitem__(self, key):
        """
        `buffer.__getitem__` except offset if `self.has_border` is truth-y
        (i.e., `buffer[1: -1, 1: -1].__getitem__` if `self.has_border`).
        """
        return self.buffer[key]

    def __setitem__(self, key, text):
        """
        Coerce `text` into a ndarray then call `buffer.__setitem__(key, text)`.

        Notes
        -----
        If `len(text) > 1`, `text` is coerced into an array or an array of arrays (depending on the presence of newlines).
        If the array's shape can't be cast to `self.buffer` it will be rotated and tried again (setting the text vertically).

        If `self.has_border` is truth-y then indices will be offset automatically.
        (i.e., `buffer[1: -1, 1: -1].__setitem__` will be called instead)

        Examples
        --------
        >>> my_widget[2:4, :13] = "Hello, World!\\nI'm a widget!"
        """
        if "\n" in text:
            text = np.array(tuple(map(tuple, text.rstrip("\n").splitlines())))
        elif len(text) > 1:
            text = np.array(tuple(text))

        try:
            self.buffer[key] = text
        except ValueError:
            self.buffer[key] = np.rot90(text if len(text.shape) == 2 else text[None, ], -1)  # Try to fit the text vertically

    def border(self, style="light", color=None, *, read_only=True):
        """
        Draw a border on the edges of the widget.

        Parameters
        ----------
        style: optional
            The style of the border, can be one of `nurses.widget.BORDER_STYLES`. (the default is "light")

        color: optional
            The color of the border.  (the default is the widget's `color`)

        Notes
        -----
        Calling this method sets the attribute `has_border` to `(style, color)`.

        Methods such as `__setitem__`, `roll`, `scroll`, `_resize` will take care to preserve the border
        as long as `has_border` is truth-y.  To disable this behavior set `has_border` to False or call
        this method with `read_only=False`.
        """
        self.has_border = read_only and (style, color)

        ul, ur, v, h, ll, lr = BORDER_STYLES[style]

        b = self._buffer
        b[(0, -1), :] = h
        b[:, (0, -1)] = v
        b[ 0,  0] = ul
        b[ 0, -1] = ur
        b[-1,  0] = ll
        b[-1, -1] = lr

        c = self._colors
        c[0] = c[-1] = c[:, 0] = c[:, -1] = color or self.color

    def roll(self, shift=1, vertical=False):
        """
        Roll the contents of the widget. Items that roll beyond the last position are re-introduced at the first.

        Parameters
        ----------
        shift: optional
            Number of places to shift the contents. `shift` may be negative. (the default is 1)

        vertical: optional
            Whether to roll vertically.  (the default is `False`, i.e., rolls are horizontal by default)
        """
        axis = (-shift, 0) if vertical else (0, -shift)
        self.buffer = np.roll(self.buffer, axis, (0, 1))
        self.colors = np.roll(self.colors, axis, (0, 1))

    def scroll(self, lines=1):
        """
        Scroll the contents of the buffer upwards or downwards, erasing the last/first lines.

        Parameters
        ----------
        lines: optional
            Number of lines to scroll. To scroll down, lines should be negative. (the default is 1)
        """
        self.roll(lines, vertical=True)
        slice_ = slice(-lines, None) if lines > 0 else slice(None, -lines)
        self.buffer[slice_] = " "
        self.colors[slice_] = self.color
