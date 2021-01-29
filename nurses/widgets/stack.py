from .layout import Layout


class Stack(Layout):
    """A single file of widgets, either vertical or horizontal.
    """
    def __init__(self, vertical=True):
        super().__init__()
        self.is_vertical = vertical

    def update_geometry(self):
        if self.root is None:
            return

        frac = 1 / len(self.children)

        if self.is_vertical:
            for i, child in enumerate(self.children):
                child.size_hint = frac, 1.0
                child.pos_hint = i * frac, 0.0
        else:
            for i, child in enumerate(self.children):
                child.size_hint = 1.0, frac
                child.pos_hint = 0.0, i * frac

        super().update_geometry()
