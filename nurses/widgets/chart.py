from collections import deque

from . import Widget

HEIGHTS = "⠀", "⣀", "⣤", "⣶", "⣿"


class Chart(Widget):
    """A Widget that provides a real-time view of some value over time.
    """
    def __init__(*args, values=None, maxlen=None, **kwargs):
        super().__init__(*args, **kwargs)

        if values is None:
            values = self.width * [0]
        elif len(values) < self.width:
            values = [0] * (self.width - len(values)) + values

        if max_len is not None:
            values = deque(values, maxlen=maxlen)

    def update(self, value):
        self.values.append(value)

    def refresh(self):
        ...
