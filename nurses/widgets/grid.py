from .layout import Layout


class Grid(Layout):
    def __init__(self, *args, rows, cols,**kwargs):
        super().__init__(*args, **kwargs)
        self._rows = rows
        self._cols = cols
        self.children = [None for _ in range(rows * cols)]

    def add_widget(self, widget, row=None, col=None):
        if row is None and col is None:
            for i, child in enumerate(self.children):
                if child is None:
                    self.children[i] = widget
                    break
            else:
                raise ValueError("too many children")
        else:
            self.children[self._cols * row + col] = widget

        widget.parent = self
        widget.update_geometry()

    def update_geometry(self):
        if not self.has_root:
            return

        pass

        super().update_geometry()
