import curses

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
    """ScreenManager starts and closes curses, manages colors, and handles the event loop.
    """
    __slots__ = "screen", "colors", "root"

    def __init__(self):
        self.screen = screen = curses.initscr()
        screen.keypad(True)
        screen.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()

        self.colors = ColorManager()
        self.root = Widget(window=screen)

        super().__init__()

    def pause(self):
        """A blocking getch.
        """
        screen = self.screen
        screen.nodelay(False)
        key = screen.getch()
        screen.nodelay(True)
        return key

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
                self.root.dispatch(key)

            await self.sleep(delay)

    def run(self, *coros, getch=True, getch_delay=GETCH_DELAY):
        if getch:
            self.run_soon(self.getch(GETCH_DELAY))
        super().run(*coros)

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
