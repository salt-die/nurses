import curses
from .widget import Widget


class Singleton(type):
    instance = None
    def __call__(cls):
        if type(cls).instance is None:
            type(cls).instance = super().__call__()
        return type(cls).instance


class ScreenManager(metaclass=Singleton):
    """Screen maintains widget order and contains convenience method for creating new widgets.
    """
    def __init__(self):
        self.screen = curses.initscr()
        self.screen.keypad(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        self.widgets = []

    def refresh(self):
        for widget in self.widgets:
            widget.refresh()

    def new_widget(self, ul: "upper-left coordinate: (y, x)"=None, height=None, width=None):
        if ul is None:
            ul = 0, 0
        if height is None:
            height = curses.LINES
        if width is None:
            width = curses.COLS

        self.widgets.append(Widget(self, ul, height, width))
        return self.widgets[-1]

    def pull_to_front(self, widget):
        """Provide the widget or the index of the widget to pull_to_front."""
        widgets = self.widgets
        if isinstance(widget, int):
            widgets.append(widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.append(widget)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def color(self, n):
        return curses.color_pair(n)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()