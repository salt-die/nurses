from . import Widget


class Layout(Widget):
    """
    Layouts are used to assign position and dimensions of contained widgets/sub-layouts.

    Notes
    -----
    A layout's width, height are the same as its parent.
    """
    def __init__(self):
        super().__init__(size_hint=(1.0, 1.0))

    def refresh(self):
        self.window.erase()
        super().refresh()
