from collections import ChainMap, defaultdict
import curses

from .. import managers  # Avoiding circular import.
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
    def root(self):
        return self

    def refresh(self):
        """Redraw children's windows.
        """
        self.window.erase()
        super().refresh()
        self.window.refresh()
