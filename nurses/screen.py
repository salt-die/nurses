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

        curses.start_color()  # TODO: Add proper color management
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        self.widgets = []

    def erase(self):
        """Erase the screen."""
        self.screen.erase()

    def refresh(self):
        screen = self.screen
        screen.erase()

        h, w = screen.getmaxyx()
        for widget in self.widgets:
            y, x = widget.top, widget.left
            src_t = max(0, -y)
            src_l = max(0, -x)
            des_t = max(0, y)
            des_l = max(0, x)
            des_h = min(h - 1, des_t + widget.height)
            des_w = min(w - 1, des_l + widget.width)

            widget.window.overlay(screen, src_t, src_l, des_t, des_l, des_h, des_w)

        screen.refresh()

    def new_widget(self, *args, **kwargs):
        self.widgets.append(Widget(*args, **kwargs))
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