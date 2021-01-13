from collections import defaultdict
import curses

from . import Widget


class Root(Widget):
    """Only meant to be instantiated by the ScreenManager.
    """
    def __init__(self, window=None):
        self.children = [ ]
        self.group = defaultdict(list)

        self.top, self.left = 0, 0
        self.height, self.width = window.getmaxyx()
        self.window = window

    @property
    def has_root(self):
        return True

    @property
    def root(self):
        return self

    def update_geometry(self, resize=False):
        """Called when widgets are added or window is resized.
        """
        if resize:
            # TODO: If terminal isn't automatically resized on linux, fallback to `curses.resizeterm(h, w)`
            #  ...: Windows curses automatically calls a resize on a resize event...
            self.height, self.width = self.window.getmaxyx()

        for child in self.children:
            child.update_geometry()

    def refresh(self):
        """Redraw children's windows.
        """
        self.window.erase()
        super().refresh()
        self.window.refresh()
