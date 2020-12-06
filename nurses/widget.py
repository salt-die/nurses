import curses
import numpy as np


class Widget:  # TODO:  Widget will inherit from EventListener as soon as we have one.
    """Widget class contains a buffer that can be pushed to the screen by calling `refresh`.  __getitem__ and __setitem__ call the respective
       buffer functions directly, so one can slice and write to a Widget as if it was a numpy array.
        ::args::
            screen:                  nurses screen that manages widgets, not to be confused with curses screen
            ul:                      upper-left coordinate of widget. Note that the top-left corner of the screen is (0, 0).
                                     Coordinates are (y, x) (both a curses and a numpy convention) with y being vertical and
                                     increasing as you move down and x being horizontal and increasing as you move right.
            height:                  height of the widget
            width:                   width of the widget
            color_pair (optional):   a curses color_pair.  Default color of this widget.

        ::kwargs::
            transparency (optional): a boolean mask that indicates which cells in the buffer to write
            colors (optional):       an array of curses.color_pairs that indicate what color each cell in the buffer should be

        ::Note::
            If some part of the widget moves out-of-bounds of the screen only the part that overlaps the screen will be drawn.
    """
    def __init__(self, screen, ul, height, width, color_pair=None, **kwargs):
        self.screen = screen
        self.ul = ul
        self.height = height
        self.width = width

        self.buffer = np.full((height, width), " ")

        if (colors := kwargs.get("colors")) is None:
            if color_pair is None:
                color_pair = curses.color_pair(1)  # TODO: Maybe grab screen.screen's default color instead
            self.colors = np.full((height, width), color_pair)
        else:
            self.colors = colors

        if (transparency := kwargs.get("transparency")) is None:
            self.transparency = np.zeros_like(self.buffer, dtype=bool)
        else:
            self.transparency = transparency

        self.tempwin = None

    @property
    def ul(self):
        return self._ul

    @ul.setter
    def ul(self, val):
        self._ul = val
        self.has_moved = True

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._height = val
        self.has_resized = True

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val
        self.has_resized = True

    def refresh(self):
        scr_hgt, scr_wth = self.screen.screen.getmaxyx()
        scr_wth -= 1
        height, width = self.height, self.width
        y, x = self.ul

        scr_t = max(0, y)
        scr_l = max(0, x)
        wid_t = max(0, -y)
        wid_l = max(0, -x)
        h = min(scr_hgt - scr_t, y + height)
        w = min(scr_wth - scr_l, x + width)

        if h <= 0 or w <= 0:
            return  # Widget is off screen or otherwise not-displayable.

        bounds = slice(wid_t, wid_t + h), slice(wid_l, wid_l + w)

        tempwin = self.tempwin
        if self.has_moved or self.has_resized:
            self.has_moved = self.has_resized = False
            if tempwin is not None:
                tempwin.erase()
                tempwin.refresh()
            self.tempwin = tempwin = curses.newwin(h, w + 1, scr_t, scr_l)
        tempwin.erase()

        it = np.nditer((self.transparency[bounds], self.buffer[bounds], self.colors[bounds]), ["multi_index"])
        for trans, pix, color in it:
            if trans: continue
            y, x = it.multi_index
            tempwin.addstr(y, x, str(pix), color)
        tempwin.refresh()

    def __getitem__(self, key):
        return self.buffer[key]

    def __setitem__(self, key, item):
        """Mirrors np.array __setitem__ except in cases where item is a string.
           In that case, we'll break the string into a tuple or tuple of tuples.
           This convenience will allow one to update text on a widget more directly:
                my_widget[2:4, :13] = "Hello, World!\nI'm a widget!"
        """
        if isinstance(item, str):
            if "\n" in item:
                item = map(tuple, item.splitlines())
            elif len(item) > 1:
                item = tuple(item)

        self.buffer[key] = item

    def border(self, style="light", color=None):
        """Draw a border on the edges of the widget.
           style can be one of ["light", "heavy", "double", "curved"]
        """
        styles = {
            "light": "┌┐│─└┘",
            "heavy": "┏┓┃━┗┛",
            "double": "╔╗║║╚╝",
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
            self.colors[0] = color
            self.colors[-1] = color
            self.colors[:, 0] = color
            self.colors[:, -1] = color
