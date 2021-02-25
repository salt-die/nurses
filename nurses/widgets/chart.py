from collections import deque

from . import ArrayWin

FULL = "⣿"
FRACTION = "⠀", "⣀", "⣤", "⣶", "⣿"


class Chart(ArrayWin):
    """
    A Widget that provides a real-time view of some value over time.

    Notes
    -----
    If `y_label` or `x_label` are set as any positive integer `n`, labels will be
    turned on and `n` labels will be printed.
    """
    values = None
    maxlen = None
    gradient = None

    y_label = False
    y_label_width = 5

    def update_geometry(self):
        if self.root is None:
            return

        super().update_geometry()

        if self.values is None:
            self.values = self.width * [0]
        elif len(self.values) < self.width:
            self.values = [0] * (self.width - len(self.values)) + self.values

        if self.maxlen is not None:
            self.values = deque(self.values, maxlen=self.maxlen)

    def update(self, value):
        self.values.append(value)

    def refresh(self):
        n_labels = self.y_label
        y_label_width = self.y_label_width * bool(n_labels) + 2
        h, w = self.buffer[1:, 1:].shape

        it = reversed(self.values)
        values = tuple(next(it) for _ in range(w - y_label_width))
        max_v = max(values)

        gradient = self.gradient

        self[:] = " "
        self.colors[:] = self.color

        if y_label_width:
            self[:, y_label_width] = "|"

            # Print y labels
            for i in range(n_labels):
                percent_of_height = i / (n_labels - 1)
                value = f"{percent_of_height * max_v:.1f}"  # TODO: attribute to specify places after decimal
                self[round((1 - percent_of_height) * h), :y_label_width - 2] = f"{value:>{y_label_width - 2}}"

        # Print vertical bars
        for i, value in enumerate(reversed(values)):
            percent_of_height = value / max_v
            whole, fraction = divmod(percent_of_height * h * 4, 4)

            row = round((1 - percent_of_height) * h)
            self[row + 1:, i + y_label_width + 1] = FULL
            self[row, i + y_label_width + 1] = FRACTION[round(fraction)]

            if gradient is not None:
                self.colors[row: , i + y_label_width + 1] = gradient[round(percent_of_height * (len(gradient) - 1))]

        super().refresh()
