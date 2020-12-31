import curses
from collections import defaultdict

from .colors import ColorDict
from .scheduler import Scheduler
from .widget import Widget


GETCH_DELAY = .1
EXIT = ord('q')


def _convert(pos, bounds):
    """Utility function that converts a fractional or negative position to an absolute one.
    """
    if isinstance(pos, float):
        if pos < 0: pos += 1
        return round(pos * bounds)
    if pos < 0: pos += bounds
    return pos


class Singleton(type):
    instance = None

    def __call__(cls):
        if Singleton.instance is None:
            Singleton.instance = super().__call__()
        return Singleton.instance


class ScreenManager(Scheduler, metaclass=Singleton):
    """ScreenManager manages widgets and handles drawing to screen.
    """
    def __init__(self):
        self.screen = screen = curses.initscr()
        screen.keypad(True)
        screen.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()

        self.colors = ColorDict()
        self.widgets = []
        self._groups = defaultdict(list)
        super().__init__()

    def pause(self):
        """Block until a key is pressed.
        """
        screen = self.screen
        screen.nodelay(False)
        key = screen.getch()
        screen.nodelay(True)
        return key

    def dispatch(self, key):
        for widget in reversed(self.widgets):
            if widget.on_press(key):
                break

    async def getch(self):
        while True:
            if not self.ready and not self.sleeping:
                return

            key = self.screen.getch()
            if key == EXIT:
                self.ready.clear()
                self.sleeping.clear()
                return

            if key != -1:
                self.dispatch(key)
            await self.sleep(GETCH_DELAY)

    def run(self, *coros):
        self.ready.append(self.getch())
        super().run(*coros)

    def refresh(self):
        # Notably, we don't use curses.panels as they aren't available for windows-curses...
        # ...upside is we don't error when moving a widget off-screen.
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
            des_w = min(w - 1, des_l + widget.width - 1)  # -1 compensates for the extra width of widget's window

            if widget.is_transparent:
                widget.window.overlay(screen, src_t, src_l, des_t, des_l, des_h, des_w)
            else:
                widget.window.overwrite(screen, src_t, src_l, des_t, des_l, des_h, des_w)

        screen.refresh()

    async def delayed(self, iterable, delay):
        """Utility method: return an async iterator over iterable with delay.  Refreshes ScreenManager every iteration.
        """
        for i in iterable:
            yield i
            self.refresh()
            await self.sleep(delay)

    def new_widget(self, *args, group=None, create_with=Widget, **kwargs):
        """
        Create a new widget and append to widget stack.  Can group widgets if providing a hashable group.
        To create a new subclassed widget use `create_with=MyWidget` or `create_with="MyWidget"` (pass the class or the class' name).
        """
        h, w = self.screen.getmaxyx()
        top, left, height, width, *rest = (0, 0, h, w) if not args else args

        top    = _convert(   top, h)
        left   = _convert(  left, w)
        height = _convert(height, h)
        width  = _convert( width, w)

        if isinstance(create_with, str):
            create_with = Widget.types[create_with]

        widget = create_with(top, left, height, width, *rest, **kwargs)
        self.widgets.append(widget)
        if group is not None:
            self._groups[group].append(widget)
        return widget

    def top(self, widget):
        """Given a widget or an index of a widget, widget is moved to top of widget stack (so it is drawn last).
        """
        widgets = self.widgets
        if isinstance(widget, int):
            widgets.append(widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.append(widget)

    def bottom(self, widget):
        """Given a widget or an index of a widget, widget is moved to bottom of widget stack (so it is drawn first).
        """
        widgets = self.widgets
        if isinstance(widget, int):
            widgets.insert(0, widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.insert(0, widget)

    def add_widget(self, widget):
        self.widgets.append(widget)

    def group(self, group):
        return self._groups[group]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.flushinp()
        curses.endwin()
