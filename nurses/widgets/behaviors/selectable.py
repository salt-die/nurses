from collections import deque
from weakref import ref

selectables = deque()

class Selectable:
    __selected = None

    SELECT_KEY = 9  # Tab

    def __init__(self, *args, **kwargs):
        selectables.append(ref(self))
        super().__init__(*args, **kwargs)

    @property
    def is_selected(self):
        return Selectable.__selected is self

    def on_press(self, key):
        if key == self.SELECT_KEY:
            while selectables[0]() is None:
                selectables.popleft()
            Selectable.__selected = selectables[0]()
            selectables.rotate(-1)

            Selectable.__selected.parent.on_top(Selectable.__selected)
            return True

        return super().on_press(key)
