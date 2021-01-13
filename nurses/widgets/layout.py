from . import Widget


class Layout(Widget):
    """Layouts are used to assign position and dimensions of contained widgets/sub-layouts.
    """

    def refresh(self):
        self.window.erase()
        super().refresh()
