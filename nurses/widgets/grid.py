from .layout import Layout


class Grid(Layout):
    def __init__(self, rows, cols):
        super().__init__()
        self._rows = rows
        self._cols = cols
        # Note: This layout is unique in that it uses a placeholder for children widgets.
        self.children = [None for _ in range(rows * cols)]

    def add_widget(self, widget, row=None, col=None):
        if row is None and col is None:
            for i, child in enumerate(self.children):
                if child is None:
                    self.children[i] = widget
                    break
            else:
                raise ValueError("too many children")
        elif row is not None and col is not None:
            self.children[self._cols * row + col] = widget
        else:
            raise ValueError("need both row and col")

        widget.parent = self
        widget.update_geometry()

    def update_geometry(self):
        if not self.has_root:
            return

        h = 1 / self._rows
        w = 1 / self._cols

        for i, child in enumerate(self.children):
            if child is not None:
                child.size_hint = h, w

                y, x = divmod(i, self._cols)
                child.pos_hint = y * h, x * w

        super().update_geometry()
