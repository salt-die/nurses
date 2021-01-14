from . import Widget


class Layout(Widget):
    """Layouts are used to assign position and dimensions of contained widgets/sub-layouts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, size_hint=(1.0, 1.0), **kwargs)

    def refresh(self):
        self.window.erase()
        super().refresh()
