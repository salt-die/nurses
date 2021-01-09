from contextlib import contextmanager
import curses

import numpy as np

from . import Widget


BORDER_STYLES = {
    "light" : "┌┐│─└┘",
    "heavy" : "┏┓┃━┗┛",
    "double": "╔╗║═╚╝",
    "curved": "╭╮│─╰╯",
}


def push_buffer(method):
    """
    Most methods that modify the buffer will automatically write the buffer to the window afterwards.
    This decorator provides a `push` parameter to these methods that can be set to False to disable
    this behavior.
    """
    def wrapper(self, *args, push=True, **kwargs):
        method(self, *args, **kwargs)
        if push:
            self.push()
    wrapper.__name__ = method.__name__
    wrapper.__doc__ = method.__doc__
    return wrapper


@contextmanager
def disable_method(obj, methodname):
    old = getattr(obj, methodname)
    try:
        setattr(obj, methodname, lambda:None)
        yield
    finally:
        setattr(obj, methodname, old)


class ArrayWin(Widget):
    """
    A Widget that uses a numpy array to store its state and uses a very numpy-ish api.

    Parameters
    ----------
    top, left, height, width: optional
        Upper and left-most coordinates of widget relative to parent, and dimensions of the widget. Fractional arguments
        are interpreted as percentage of parent, and parent width or height will be added to negative arguments.
        (the defaults are 0, 0, parent's max height, parent's max width)
    color: optional
       A curses color_pair, the default color of this widget. (the default is `curses.color_pair(0)`)

    Other Parameters
    ----------------
    colors: optional
        A ndarray of curses.color_pairs with same dimensions as widget. (the default is `np.full((height, width), color))`)
    border: optional
        The border type; one of `nurses.widget.BORDER_STYLES`. (by default a widget has no border)
    border_color: optional
        A curses color_pair.  If a border is given, border_color will be the color of the border. (the default is `color`)
    transparent: optional
        If true, widget will overlay other widgets instead of overwrite them (whitespace will be "see-through"). (the default is `False`)

    Notes
    -----
    __getitem__ and __setitem__ call the respective buffer functions directly, so one can slice
    and write to a Widget as if it was a numpy array.

    If some part of the widget moves out-of-bounds of the screen only the part that overlaps the screen will be drawn.

    Coordinates are (y, x) (both a curses and a numpy convention) with y being vertical and increasing as you move down
    and x being horizontal and increasing as you move right.  Top-left corner is (0, 0)
    """
    def __init__(self, *args, color=None, colors=None, border=None, border_color=None, **kwargs):
        with disable_method(self, "_resize"):  # We're not ready for our properties to call this method
            super().__init__(*args, **kwargs)

        h, w = self.height, self.width
        self._buffer = np.full((h, w), " ")

        self.color = color or curses.color_pair(0)

        self._colors = colors or np.full((h, w), self.color)

        if border:
            self.border(border, border_color)
        else:
            self.has_border = False

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._height = val
        self._resize()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self._resize()

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
        self.window.erase()
        self.window.resize(height, width + 1)
        self.border(*self.has_border) if self.has_border else self.push()

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

        self.push()

    @push_buffer
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
        self.has_border = style, color

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

    @push_buffer
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

    @push_buffer
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

    def update_color(self, color):
        self.colors[:] = color
