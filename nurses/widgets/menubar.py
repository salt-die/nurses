from . import Widget
from .. import LEFT, RIGHT, DOWN, TAB


class Menubar(Widget):
    """
    `menus` should be `Menu` widgets.  Menubars are automatically placed at row 0 of parent widget with width of parent.
    ::Warning:: Don't use `border` kwarg
    """
    activate = TAB
    move_left = LEFT
    move_right = RIGHT
    open_submenu = DOWN

    selected_color = None

    def __init__(self, *menus, **kwargs):
        super().__init__(0, 0, 1, None, size_hint=(None, 1.0), **kwargs)
        self.is_activated = False
        self.active_menu = None

        acc = 0
        for menu in menus:
            menu.color=self.color
            menu.selected_color=self.selected_color
            menu.top = 0
            menu.left = acc
            menu._menu_widget.top = 1
            menu._menu_widget.left = acc
            acc += menu.width + 1
            self.add_widget(menu)

    def on_press(self, key):
        active = self.active_menu
        menus = self.children

        if key == self.activate:
            self.is_activated = not self.is_activated

            if not self.is_activated:
                if not menus[active].is_closed:
                    menus[active].close_menu()
                self.active_menu = None
            else:
                self.active_menu = 0

            return True

        if not self.is_activated:
            return

        if not (menu := self.children[self.active_menu]).is_closed and menu.on_press(key):
            return True

        if key == self.move_left:
            if (open_menu := not menus[active].is_closed):
                menus[active].close_menu()

            self.active_menu = (active - 1) % len(menus)

            if open_menu:
                menus[self.active_menu].open_menu()

        elif key == self.move_right:
            if (open_menu := not menus[active].is_closed):
                menus[active].close_menu()

            self.active_menu = (active + 1) % len(menus)

            if open_menu:
                menus[self.active_menu].open_menu()

        elif key == self.open_submenu:
            menus[active].open_menu()
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
        self.window.chgat(0, 0, self.color)

    def refresh(self):
        for i, child in enumerate(self.children):
            child.window.chgat(0, 0, self.selected_color if i == self.active_menu else child.color)

        super().refresh()
