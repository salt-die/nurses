from . import Widget


class LayoutBase(Widget):
    """
    Layouts are used to assign position and dimensions of contained widgets/sub-layouts.

    Once all widgets and sub-layouts have been added to `children` (and children's children),
    call `update` on the root layout to assign dimensions and positions to all children.
    """
    def __init_subclass__(cls):
        super().__init_subclass__()
        if not cls.update.__doc__:
            cls.update.__doc__ = LayoutBase.update.__doc__

    def refresh(self):
        self.window.erase()
        super().refresh()

    def add_widget(self, widget):
        super().add_widget(widget)
        self.update()

    @bind_to("height", "width")
    def update(self):
        """Set the positions and dimensions of sub-layouts and contained widgets, and call `update` on sub-layouts.
        """
