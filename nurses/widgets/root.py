from collections import defaultdict
import curses

from .widget import Widget


class Root(Widget):
    """Only meant to be instantiated by the ScreenManager.
    """
    height = None  # We don't want Widget's height, width properties
    width = None

    def __init__(self, window=None):
        self.children = [ ]
        self.group = defaultdict(list)

        self.top, self.left = 0, 0
        self.window = window
        self.update_geometry()

    @property
    def has_root(self):
        return True

    @property
    def root(self):
        return self

    def update_geometry(self):
        """Update geometry of child windows with size or position hints when screen is resized.
        """
        # TODO: If terminal isn't automatically resized on linux, fallback to `curses.resizeterm(h, w)`
        #  ...: Windows curses automatically calls a resize on a resize event...
        h, w = self.window.getmaxyx()
        self.height = h
        self.width = w - 1

        for child in self.children:
            child.update_geometry()

    def refresh(self):
        """Redraw children's windows.
        """
        self.window.erase()
        super().refresh()
        self.window.refresh()
