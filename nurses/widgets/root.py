from collections import defaultdict
import curses
import os

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
            try:  # linux
                w, h = self.width, self.height = os.get_terminal_size()
                curses.resizeterm(h, w)
            except AttributeError:  # windows
                h, w = self.height, self.width = self.window.getmaxyx()
                os.system(f"mode con cols={w} lines={h}")

        for child in self.children:
            child.update_geometry()

    def refresh(self):
        """Redraw children's windows.
        """
        self.window.erase()
        super().refresh()
        self.window.refresh()
