import curses
import numpy as np

BORDER_STYLES = {
    "light": "┌┐│─└┘",
    "heavy": "┏┓┃━┗┛",
    "double": "╔╗║═╚╝",
    "curved": "╭╮│─╰╯"
}

class Widget:
    """A widget contains a buffer that can be pushed to the widget's window by calling `refresh`
    or more simply by just using the widget's __setitem__.

    __getitem__ and __setitem__ call the respective buffer functions directly, so one can slice
    and write to a Widget as if it was a numpy array.
      ::args::
        top:                upper coordinate of widget relative to screen
        left:               left coordinate of widget relative to screen
        height:             height of the widget
        width:              width of the widget
        color (optional):   a curses color_pair.  Default color of this widget.

      ::kwargs::
        colors (optional):          an array of curses.color_pairs that indicates the color of each character

      ::Note::
        If some part of the widget moves out-of-bounds of the screen only the part that overlaps the screen will be drawn.

        Coordinates are (y, x) (both a curses and a numpy convention) with y being vertical and increasing as you move down
        and x being horizontal and increasing as you move right.  Top-left corner is (0, 0)
    """
    def __init__(self, top, left, height, width, color=None, **kwargs):
        self.top = top
        self.left = left
        self._height = height
        self._width = width

        self.color = curses.color_pair(0) if color is None else color

        self.has_border = False
        self.buffer = np.full((height, width), " ")
        if colors := kwargs.get("colors"):
            self.colors = colors
        else:
            self.colors = np.full((height, width), self.color)

        self.window = curses.newwin(height, width + 1)

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
        if self.has_border:
            self.border(*self.has_border)
        else:
            self.refresh

    def refresh(self):
        """Write the buffers to the window."""
        it = np.nditer((self._buffer, self._colors), ["multi_index"])
        for char, color in it:
            y, x = it.multi_index
            self.window.addstr(y, x, str(char), color)

    def __getitem__(self, key):
        """buffer.__getitem__ except offset if self.has_border is truth-y."""
        return self.buffer[key]

    def __setitem__(self, key, item):
        """buffer.__setitem__ except in cases where item is a string.
        If item is a string of length > 1: coerce string into a tuple or tuple of tuples.
        This convenience will allow one to update text on a widget more directly:
            `my_widget[2:4, :13] = "Hello, World!\nI'm a widget!"`

        If self.has_border is truth-y then indices will be offset automatically.
        """
        if isinstance(item, str):
            if "\n" in item:
                item = np.array(tuple(map(tuple, item.rstrip().splitlines())))
            elif len(item) > 1:
                item = np.array(tuple(item))

        try:
            self.buffer[key] = item
        except ValueError:
            self.buffer[key] = item.T if len(item.shape) == 2 else item[None, ].T  # Try to fit the text vertically

        self.refresh()

    def border(self, style="light", color=None, *, read_only=True):
        """Draw a border on the edges of the widget.
           `style` can be one of ["light", "heavy", "double", "curved"]

           Calling this method sets the attribute `has_border` to (style, color).
           Methods such as __getitem__, roll, scroll, resize will take care to preserve the border
           as long as `has_border` is truth-y.  To disable this behavior set `has_border` to False
           or call this method with `read_only=False`.
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

        if color is not None:
            c = self._colors
            c[0] = c[-1] = c[:, 0] = c[:, -1] = color

        self.refresh()

    def roll(self, shift=1, vertical=False):
        """Roll the contents of the buffer.
           Items that roll beyond the last position are re-introduced at the first.
        """
        axis = (-shift, 0) if vertical else (0, -shift)
        self.buffer = np.roll(self.buffer, axis, (0, 1))
        self.colors = np.roll(self.colors, axis, (0, 1))
        self.refresh()

    def scroll(self):
        """Scroll the contents of the buffer upwards, erasing the last line.
        """
        self.roll(vertical=True)
        self.buffer[-1] = " "
        self.colors[-1] = self.color
        self.refresh()

    def on_press(self, key):
        """Called when `key` is pressed and no widgets above this widget have handled the press.
           Return True if press is handled to stop dispatching.
        """
        pass
