from ...managers import ScreenManager

def selector():
    while True:
        for widget in ScreenManager().root.walk_widget_tree():
            if isinstance(widget, Selectable):
                Selectable._Selectable__selected = widget
                yield


class Selectable:
    __selected = None
    __selector = selector()

    SELECT_KEY = 9  # Tab

    @property
    def is_selected(self):
        return Selectable.__selected is self

    def on_press(self, key):
        if key == self.SELECT_KEY:
            next(Selectable.__selector)
            return True

        return super().on_press(key)
