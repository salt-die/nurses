import curses

from .widget import Widget
from .colors import ColorDict

class Wrapper(type):
    instance = None

    def __call__(self):
        if Wrapper.instance is None:
            Wrapper.instance = curses.wrapper(super().__call__)
        return Wrapper.instance


class ScreenManager(metaclass=Wrapper):
    """ScreenManager manages widgets and handles drawing to screen.
    """
    def __init__(self, screen):
        self.screen = screen
        self.screen.keypad(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        self.widgets = []
        self.colors = ColorDict()

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
        """Same as calling Widget directly except the widget is automatically appended to widget stack."""
        self.widgets.append(Widget(*args, **kwargs))
        return self.widgets[-1]

    def pull_to_front(self, widget):
        """Given a widget or an index of a widget, widget is moved to top of widget stack (so it is drawn last)"""
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
