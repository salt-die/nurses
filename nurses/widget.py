import curses

import numpy as np


class Widget:  # TODO:  Widget will inherit from EventListener as soon as we have one.
    """A widget contains a buffer that can be pushed to the widget's window by calling `refresh`
    or more simply by just using the widget's __setitem__.

    __getitem__ and __setitem__ call the respective buffer functions directly, so one can slice
    and write to a Widget as if it was a numpy array.
      ::args::
        top:                        upper coordinate of widget relative to screen
        left:                       left coordinate of widget relative to screen
        height:                     height of the widget
        width:                      width of the widget
        default_color (optional):   a curses color_pair.  Default color of this widget.

      ::kwargs::
        transparency (optional):    a boolean mask that indicates which characters to write to widget's window
        colors (optional):          an array of curses.color_pairs that indicates the color of each character

      ::Note::
        If some part of the widget moves out-of-bounds of the screen only the part that overlaps the screen will be drawn.

        Coordinates are (y, x) (both a curses and a numpy convention) with y being vertical and increasing as you move down
        and x being horizontal and increasing as you move right.  Top-left corner is (0, 0)
    """
    def __init__(self, top, left, height, width, default_color=None, **kwargs):
        self.top = top
        self.left = left
        self._height = height
        self._width = width

        self.default_color = curses.color_pair(0) if default_color is None else default_color

        self.buffer = np.full((height, width), " ")

        if colors := kwargs.get("colors"):
            self.colors = colors
        else:
            self.colors = np.full((height, width), self.default_color)

        if transparency := kwargs.get("transparency"):
            self.transparency = transparency
        else:
            self.transparency = np.zeros_like(self.buffer, dtype=bool)

        self.window = curses.newwin(height, width + 1)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._height = val
        self.resize()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self.resize()

    def resize(self):
        height, width = self.height, self.width
        old_h, old_w = self.buffer.shape
        min_h, min_w = min(height, old_h), min(width, old_w)

        new_buffer = np.full((height, width), " ")
        new_buffer[:min_h, :min_w] = self.buffer[:min_h, :min_w]

        new_colors = np.full((height, width), self.default_color)
        new_colors[:min_h, :min_w] = self.colors[:min_h, :min_w]

        new_trans = np.zeros_like(new_buffer, dtype=bool)
        new_trans[:min_h, :min_w] = self.transparency[:min_h, :min_w]

        self.buffer = new_buffer
        self.colors = new_colors
        self.transparency = new_trans
        self.window.resize(height, width + 1)

    def refresh(self):
        """Write the buffers to the window."""
        it = np.nditer((self.transparency, self.buffer, self.colors), ["multi_index"])
        for trans, char, color in it:
            if trans: continue
            y, x = it.multi_index
            self.window.addstr(y, x, str(char), color)

    def __getitem__(self, key):
        return self.buffer[key]

    def __setitem__(self, key, item):
        """buffer.__setitem__ except in cases where item is a string.
        If item is a string of length > 1: coerce string into a tuple or tuple of tuples.
        This convenience will allow one to update text on a widget more directly:
            my_widget[2:4, :13] = "Hello, World!\nI'm a widget!"
        """
        if isinstance(item, str):
            if "\n" in item:
                item = np.array(tuple(map(tuple, item.rstrip().splitlines())))
                if item.shape != self[key].shape:
                    # Attempt to fit the text by making it vertical.
                    item = item.T
            elif len(item) > 1:
                item = tuple(item)

        self.buffer[key] = item
        self.refresh()

    def border(self, style="light", color=None):
        """Draw a border on the edges of the widget.
           style can be one of ["light", "heavy", "double", "curved"]
        """
        styles = {
            "light": "┌┐│─└┘",
            "heavy": "┏┓┃━┗┛",
            "double": "╔╗║═╚╝",
            "curved": "╭╮│─╰╯"
        }

        ul, ur, v, h, ll, lr = styles[style]

        self[0] = h
        self[-1] = h
        self[:, 0] = v
        self[:, -1] = v
        self[0, 0] = ul
        self[0, -1] = ur
        self[-1, 0] = ll
        self[-1, -1] = lr

        if color is not None:
            c = self.colors
            c[0] = c[-1] = c[:, 0] = c[:, -1] = color

        self.refresh()

    def roll(self, shift=1, vertical=False):
        for attr in ("buffer", "colors", "transparency"):
            setattr(self, attr, np.roll(getattr(self, attr), (-shift, 0) if vertical else (0, -shift), (0, 1)))
        self.refresh()

    def scroll(self):
        for attr in ("buffer", "colors", "transparency"):
            setattr(self, attr, np.roll(getattr(self, attr), (-1, 0), (0, 1)))
        self.buffer[-1] = " "
        self.colors[-1] = self.default_color
        self.transparency[-1] = False
        self.refresh()