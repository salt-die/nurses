"""
on_press still needs implementing
"""
import curses

from . import Widget
from .. import UP, DOWN, ENTER


class Menu(Widget):
    """
    Notes
    -----
    `items` should be an iterable of pairs ("menu entry", callback)
    """
    move_up = UP
    move_down = DOWN
    select_key = ENTER
    open_close_key = None  # Alt + first letter of menu name?

    wrap = False

    selected_color = None

    def __init__(self, top, left, name, *items, **kwargs):
        raise NotImplementedError
        self.name = name
        self._items = dict(items)

        offset = bool(kwargs.get("border"))
        super().__init__(top, left, len(self._items) + 2 * offset, max(map(len, self._items) + 2 * offset, **kwargs))

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        h, w = self.parent.height, self.parent.width

        if self.window is None:
            self.window = self._closed_window = curses.newwin(1, self.width + 1)
            self._open_window = curses.newwin(self.height, self.width + 1)
            self.update_color(self.color)

    def on_press(self, key):
        ...
