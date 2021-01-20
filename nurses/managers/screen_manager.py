import curses

from .meta import Singleton
from .scheduler import Scheduler
from ..widgets import Root

GETCH_DELAY = .05
EXIT = ord('q')


class ScreenManager(Scheduler, metaclass=Singleton):
    """
    ScreenManager starts and closes curses, handles events (getching for now, hopefully mouse
    input in the future), and schedules and runs coroutines.
    """

    __slots__ = "screen", "root"

    def __init__(self):
        self.screen = screen = curses.initscr()
        screen.keypad(True)
        screen.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()

        self.root = Root(screen=screen)  # Top-level widget: getch dispatching will start here.

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
                return

            if key == curses.KEY_RESIZE:
                self.root.update_geometry()
            elif key != curses.ERR:
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
