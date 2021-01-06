TAB = 9


class Selectable:
    def on_press(self, key):
        if key == TAB and not self.is_selected:
            self.parent.on_bottom(-1)
            self.parent.on_top(self)
            return True
        return super().on_press(key)

    @property
    def is_selected(self):
        return self.parent.children[-1] is self