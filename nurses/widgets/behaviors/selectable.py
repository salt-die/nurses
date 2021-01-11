from collections import deque
from weakref import ref

selectables = deque()

class Selectable:
    __selected = None

    select_key = 9  # Tab

    def __init__(self, *args, **kwargs):
        selectables.append(ref(self))
        super().__init__(*args, **kwargs)

    @property
    def is_selected(self):
        return Selectable.__selected is self

    def on_press(self, key):
        if key == self.select_key:
            while selectables[0]() is None:
                selectables.popleft()
            Selectable.__selected = selectables[0]()
            selectables.rotate(-1)

            Selectable.__selected.parent.pull_to_front(Selectable.__selected)
            return True

        return super().on_press(key)
