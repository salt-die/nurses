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

        for i, child in enumerate(self.children):
            if self.is_vertical:
                child.size_hint = 1 / len(self.children), 1.0
                child.pos_hint = i / len(self.children), 0.0
            else:
                child.size_hint = 1.0, 1 / len(self.children)
                child.pos_hint = 0.0, i / len(self.children)

        super().update_geometry()
