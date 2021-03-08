import curses

from . import Widget
from .. import UP, DOWN, UP_2, DOWN_2, ENTER


class Menu(Widget):
    """
    Notes
    -----
    `items` should be an iterable of pairs ("menu entry", callback)
    """
    move_up = UP
    move_up_alt = UP_2
    move_down = DOWN
    move_down_alt = DOWN_2
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

        border_style, border_color = kwargs.pop("border_style", None), kwargs.pop("border_color", None)
        border = 2 * bool(border_style)
        super().__init__(top, left, 1, len(self.name), **kwargs)

        for kwarg in ("move_up", "move_up_alt", "move_down", "move_down_alt", "select_key", "open_close_key", "selected_color"):
            kwargs.pop(kwarg, None)

        self._menu_widget = Widget(
            top + 1,
            left,
            len(self) + border,
            max(map(len, self.items)) + border,
            border_style=border_style,
            border_color=border_color,
            **kwargs,
        )

    def __len__(self):
        return len(self.items)

    @property
    def is_open(self):
        return not self.is_closed

    def open_menu(self):
        self.is_closed = False
        self._selected_entry = 0
        self.parent.add_widget(self._menu_widget)

    def close_menu(self):
        self.is_closed = True
        self.parent.remove_widget(self._menu_widget)

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        if self.window is None:
            self.window = curses.newwin(self.height, self.width + 1)
            self.update_color(self.color)
            self.window.addstr(0, 0, self.name)

            menu = self._menu_widget
            menu.parent = self.parent
            menu.update_geometry()
            menu.window.bkgd(" ", self.color)

            offset = int(menu.has_border)
            for i, item in enumerate(self.items):
                menu.window.addstr(i + offset, offset, item)

    def refresh(self):
        if self.is_closed:
            return

        menu = self._menu_widget
        offset = int(menu.has_border)
        for i, item in enumerate(self.items):
            self._menu_widget.window.chgat(i + offset, offset, menu.width - 2 * offset, self.color if i != self._selected_entry else self.selected_color)

    def on_press(self, key):
        if key == self.open_close_key:
            self.open_menu() if self.is_closed else self.close_menu()
            self.root.refresh()
            return True

        if self.is_closed:
            return

        if key == self.move_up or key == self.move_up_alt:
            self._selected_entry = (self._selected_entry - 1) % len(self)

        elif key == self.move_down or key == self.move_down_alt:
            self._selected_entry = (self._selected_entry + 1) % len(self)

        elif key == self.select_key:
            self._callbacks[self._selected_entry]()
            self.close_menu()

        else:
            return

        self.root.refresh()
        return True
