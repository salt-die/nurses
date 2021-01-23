from .layout import Layout


class Stack(Layout):
    """A single file of widgets, either vertical or horizontal.
    """
    def __init__(self, vertical=False, horizontal=False):
        super().__init__()
        self.is_vertical = vertical
        self.is_horizontal = horizontal

    def update_geometry(self):
        if not self.has_root:
            return

        for i, child in enumerate(self.children):
            if self.is_vertical:
                child.size_hint = 1 / len(self.children), None
                child.pos_hint = i / len(self.children), None
            else:
                child.size_hint = None, 1 / len(self.children)
                child.pos_hint = None, i / len(self.children)

        super().update_geometry()
