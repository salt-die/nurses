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
        self.is_closed = True
        self.name = name

        self.items = []
        self._callbacks = []
        for item, callback in items:
            self.items.append(item)
            self._callbacks.append(callback)

        border = 2 * bool(kwargs.get("border_style"))
        super().__init__(top, left, 1 + border, len(self.name) + border, **kwargs)

        for kwarg in ("move_up", "move_down", "select_key", "open_close_key", "selected_color"):
            kwargs.pop(kwarg, None)

        self._menu_widget = Widget(top + 1 + border, left, len(self) + border, max(map(len, self.items)) + border, **kwargs)

    def __len__(self):
        return len(self.items)

    @property
    def is_open(self):
        return not self.is_closed

    def open_menu(self):
        self.is_closed = False
        self._selected_entry = 0
        self.root.add_widget(self._menu_widget)

    def close_menu(self):
        self.is_closed = True
        self.root.remove_widget(self._menu_widget)

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        if self.window is None:
            offset = int(self.has_border)
            self.window = curses.newwin(self.height, self.width + 1)
            self.update_color(self.color)
            self.window.addstr(offset, offset, self.name)

            self._menu_widget.window = curses.newwin(self._menu_widget.height, self._menu_widget.width + 1)

            for i, item in enumerate(self.items, start=offset):
                self._menu_widget.window.addstr(i, offset, item)

            if self.has_border:
                self.border(self.border_style, self.border_color)
                self._menu_widget.border(self.border_style, self.border_color)

    def refresh(self):
        if self.is_closed:
            return

        offset = int(self.has_border)
        for i, item in enumerate(self.items):
            self._menu_widget.window.chgat(i + offset, offset, len(item), self.color if i != self._selected_entry else self.selected_color)

    def on_press(self, key):
        if key == self.open_close_key:
            self.open_menu() if self.is_closed else self.close_menu()
            self.root.refresh()
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
