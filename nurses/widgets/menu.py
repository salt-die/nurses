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
    open_close_key = None

    selected_color = None

    def __init__(self, top, left, name, items, **kwargs):
        self.name = name

        self._items = []
        self._callbacks = []
        for item, callback in items:
            self._items.append(item)
            self._callbacks.append(callback)

        offset = bool(kwargs.get("border_style"))
        super().__init__(top, left, len(self._items) + 2 * offset, max(map(len, self._items)) + 2 * offset, **kwargs)

    @property
    def is_closed(self):
        return self.window is self._closed_window

    def __len__(self):
        return len(self._items)

    def open_menu(self):
        self.window = self._open_window
        self._selected_entry = 0

    def close_menu(self):
        self.window = self._closed_window

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        if self.window is None:
            self._closed_window = curses.newwin(1, self.width + 1)
            self._closed_window.attrset(self.color)
            self._closed_window.addstr(0, 0, self.name)

            self._open_window = curses.newwin(self.height, self.width + 1)
            self._open_window.attrset(self.color)

            self.window = self._open_window  # Temporarily set `window` to open so we can set a border if needed
            if self.has_border:
                self.border(self.border_style, self.border_color)
                offset = 1
            else:
                offset = 0

            for i, item in enumerate(self._items, start=offset):
                self._open_window.addstr(i, offset, item)

            self.window = self._closed_window

    def refresh(self):
        if self.is_closed:
            return

        offset = int(self.has_border)
        for i, item in enumerate(self._items):
            self._open_window.chgat(i + offset, offset, len(item), self.color if i != self._selected_entry else self.selected_color)

    def on_press(self, key):
        if key == self.open_close_key:
            self.open_menu() if self.is_closed else self.close_menu()
            return True

        if self.is_closed:
            return

        if key == self.move_up:
            self._selected_entry = (self._selected_entry - 1) % len(self)
        elif key == self.move_down:
            self._selected_entry = (self._selected_entry + 1) % len(self)
        elif key == self.select_key:
            self._callbacks[self._selected_entry]()
            self.close_menu()
        else:
            return

        self.root.refresh()
        return True
