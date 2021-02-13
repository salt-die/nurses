from . import Widget
from . import Menu
from .. import LEFT, RIGHT, DOWN, TAB


class Menubar(Widget):
    """
    `menus` should be an iterable of `(name: str, Iterable[(menu_entry: str, callback: callable)])`.

    Menubars are automatically placed at row 0 of parent widget with width of parent.

    ::Warning:: kwarg `border_style` not supported yet.
    """
    activate = TAB
    move_left = LEFT
    move_right = RIGHT
    open_submenu = DOWN

    selected_color = None

    def __init__(self, *menus, **kwargs):
        kwargs.pop("border_style", None)  # TODO: Allow borders
        super().__init__(0, 0, 1, None, size_hint=(None, 1.0), **kwargs)

        self.deactivate()

        for kwarg in ("activate", "move_left", "move_right", "open_submenu"):
            kwargs.pop(kwarg, None)

        acc = 0
        for name, items in menus:
            menu = self.new_widget(0, acc, name, items, create_with=Menu, **kwargs)
            acc += menu.width + 1

    def deactivate(self):
        self.is_activated = False
        self.active_menu = None
        self._submenu_open = False

    def on_press(self, key):
        active = self.active_menu
        menus = self.children

        if key == self.activate:
            if self.is_activated:
                if menus[active].is_open:
                    menus[active].close_menu()
                self.deactivate()
            else:
                self.is_activated = True
                self.active_menu = 0

            self.root.refresh()
            return True

        if not self.is_activated:
            return

        if menus[active].is_open and menus[active].on_press(key):
            return True

        if key == self.move_left:
            if open_menu := menus[active].is_open:
                menus[active].close_menu()

            self.active_menu = (active - 1) % len(menus)

            if open_menu:
                menus[self.active_menu].open_menu()

        elif key == self.move_right:
            if open_menu := menus[active].is_open:
                menus[active].close_menu()

            self.active_menu = (active + 1) % len(menus)

            if open_menu:
                menus[self.active_menu].open_menu()

        elif key == self.open_submenu:
            menus[active].open_menu()
            self._submenu_open = True

        else:
            return

        self.root.refresh()
        return True

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        super().update_geometry()

    def refresh(self):
        menus = self.children
        active = self.active_menu

        if self.is_activated and menus[active].is_closed and self._submenu_open:  # submenu entry was selected
            self.deactivate()

        for i, menu in enumerate(menus):
            menu.window.chgat(0, 0, self.selected_color if i == active else menu.color)

        super().refresh()

    def update_color(self, color):
        super().update_color(color)
        self.window.chgat(0, 0, self.color)
