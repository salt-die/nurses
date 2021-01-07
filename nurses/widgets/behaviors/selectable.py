from collections import deque


class Selectable:
    __selected = None
    __selectables = deque()

    SELECT_KEY = 9  # Tab

    def __new__(cls, *args, selected=False, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)

        if Selectable.__selected is None or selected:
            Selectable.__selected = instance

        Selectable.__selectables.append(instance)

        return instance

    @property
    def is_selected(self):
        return Selectable.__selected is self

    def on_press(self, key):
        if key == self.SELECT_KEY and self.is_selected:
            while Selectable.__selectables[0] is not self:
                Selectable.__selectables.rotate(-1)
            Selectable.__selectables.rotate(-1)
            Selectable.__selected = Selectable.__selectables[0]
            return True

        return super().on_press(key)
