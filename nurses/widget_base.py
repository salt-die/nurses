from abc import ABCMeta
from . import screen_manager as sm


class WidgetMeta(ABCMeta):
    ATTRS = "top", "left", "height", "width", "window", "is_transparent"

    def __call__(cls, *args, **kwargs):
        # We're going to check that a widget has the attributes it needs to fulfill our widget api.
        widget = super().__call__(*args, **kwargs)
        for attr in WidgetMeta.ATTRS:
            if not hasattr(widget, attr):
                raise TypeError(f"{cls.__name__} missing required attribute {attr}")
        return widget


class WidgetBase(metaclass=WidgetMeta):
    def __init__(self, top=0, left=0, height=None, width=None, transparent=False):
        h, w = sm.ScreenManager().screen.getmaxyx()
        if height is None:
            height = h
        if width is None:
            width = w

        self.top    = self.convert(   top, h)
        self.left   = self.convert(  left, w)
        self.height = self.convert(h if height is None else height, h)
        self.width  = self.convert(w if width is None else width, w)

        self.window = sm.ScreenManager().newwin(self.height, self.width)
        self.is_transparent = transparent

    @staticmethod
    def convert(pos, bounds):
        """Utility function that converts a fractional or negative position to an absolute one.
        """
        if isinstance(pos, float):
            pos = round(pos * bounds)
        if pos < 0:
            pos += bounds
        return pos
