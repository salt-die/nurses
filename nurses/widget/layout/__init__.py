from abc import abstractmethod

from .. import Widget


class Layout(Widget):
    """
    Layouts are used to assign position and dimensions of contained widgets/sub-layouts.

    Once all widgets and sub-layouts have been added to `children` (and children's children),
    call `update` on the root layout to assign dimensions and positions to all children.
    """
    layouts = { }  # Registry of subclasses of Layout

    def __init_subclass__(cls):
        Layout.layouts[cls.__name__] = cls
        if not cls.update.__doc__:
            cls.update.__doc__ = Layout.update.__doc__

    @abstractmethod
    def update(self):
        """Set the positions and dimensions of sub-layouts and contained widgets, and call `update` on sub-layouts.
        """
