import curses
from collections import defaultdict

from ._colors import ColorManager
from .scheduler import Scheduler
from .widget import Widget

GETCH_DELAY = .1
EXIT = ord('q')


class Singleton(type):
    instance = None

    def __call__(cls):
        if Singleton.instance is None:
            Singleton.instance = super().__call__()
        return Singleton.instance


class ScreenManager(Scheduler, metaclass=Singleton):
    """ScreenManager manages widgets and handles drawing to screen.
    """
    __slots__ = "screen", "colors", "widgets", "_groups"

    def __init__(self):
        self.screen = screen = curses.initscr()
        screen.keypad(True)
        screen.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()

        self.colors = ColorManager()
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

    async def getch(self, delay):
        while True:
            if not self.ready and not self.sleeping:
                return

            key = self.screen.getch()
            if key == EXIT:
                self.ready.clear()
                self.sleeping.clear()
                self.tasks.clear()
                return

            if key != -1:
                self.dispatch(key)

            await self.sleep(delay)

    def run(self, *coros, getch=True, getch_delay=GETCH_DELAY):
        if getch:
            self.run_soon(self.getch(GETCH_DELAY))
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
        """Utility method: return an async iterator over iterable with delay.
        """
        for i in iterable:
            yield i
            await self.sleep(delay)

    def new_widget(self, *args, group=None, create_with=Widget, **kwargs):
        """
        Create a new widget and append to widget stack.  Can group widgets if providing a hashable group.
        To create a new subclassed widget use `create_with=MyWidget` or `create_with="MyWidget"` (pass the class or the class' name).
        """
        if isinstance(create_with, str):
            create_with = Widget.types[create_with]

        widget = create_with(*args, **kwargs)
        self.widgets.append(widget)
        if group is not None:
            self._groups[group].append(widget)
        return widget

    def newwin(self, lines, cols):
        """Wraps curses.newwin.
        """
        # Curses will return ERR if creating a window wider or taller than our screen.
        # We can get around this by creating a tiny window and then resizing to be as large as we'd like.
        # TODO: Test this hack on linux.
        win = curses.newwin(1, 1)
        win.resize(lines, cols + 1)
        return win

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
