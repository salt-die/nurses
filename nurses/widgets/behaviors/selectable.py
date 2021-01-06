class Selectable:
    SELECT_KEY = 9  # Tab

    def on_press(self, key):
        if key == self.SELECT_KEY and not self.is_selected:
            self.parent.on_bottom(-1)
            self.parent.on_top(self)
            return True
        return super().on_press(key)

    @property
    def is_selected(self):
        return self.parent.children[-1] is self