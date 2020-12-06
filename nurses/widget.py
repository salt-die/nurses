import curses
import numpy as np


class Widget:  # TODO:  Widget will inherit from EventListener as soon as we have one.
    """Widget class contains a buffer that can be pushed to the screen by calling `refresh`.  __getitem__ and __setitem__ call the respective
       buffer functions directly, so one can slice and write to a Widget as if it was a numpy array.
        ::args::
            screen:                  nurses screen that manages widgets, not to be confused with curses screen
            ul:                      upper-left coordinate of widget. Note that the top-left corner of the screen is (0, 0).
                                     Coordinates are (y, x) with y being vertical and increasing as you move down and
                                     x being horizontal and increasing as you move right.
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

    def refresh(self):
        screen = self.screen.screen
        height, width = self.height, self.width
        y, x = self.ul

        scr_t = max(0, y)
        scr_l = max(0, x)
        wid_t = max(0, -y)
        wid_l = max(0, -x)
        h = min(screen.height - scr_t, y + height)
        w = min(screen.width - scr_l, x + width)

        if h <= 0 or w <= 0:
            return  # Widget is off screen or otherwise not-displayable.

        # It may be more performant to create a new curses window, write to it and refresh it than writing to the main screen.
        # More performant if it prevents curses from refreshing all the characters on the screen instead of just the ones we may have changed.
        # This is simple enough to add.
        bounds = slice(wid_t, wid_t + h), slice(wid_l, wid_l + w)
        it = np.nditer((self.transparency[bounds], self.buffer[bounds], self.colors[bounds]), ["multi_index"])

        for trans, pix, color in it:
            if trans: continue
            y, x = it.multi_index
            screen.addstr(scr_t + y, scr_l + x, pix, color))

    def __getitem__(self, key):
        return self.buffer[key]

    def __setitem__(self, key, item):
        """Mirrors np.array __setitem__ except in cases where item is a string.
           In that case, we'll break the string into a tuple or tuple of tuples.
           This convenience will allow one to update text on a widget more directly:
                my_widget[2:4, :13] = "Hello, World!\nI'm a widget!"
        """
        if isinstance(item, str):
            item = item.splitlines()
            if len(item) = 1:
                item ,= item
            else:
                item = map(tuple, item)
            item = tuple(item)

        self.buffer[key] = item

    def rectangle(self, style="default", ul, height, width):
        """Draw a (height, width) rectangle at ul. (ul is relative to this widget's upper-left corner)"""