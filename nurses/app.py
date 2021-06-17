from abc import ABC, abstractmethod
import asyncio
from contextlib import contextmanager
import curses

from .widgets import Root
from .keys import ESCAPE


@contextmanager
def curses_screen():
    screen = curses.initscr()
    screen.keypad(True)
    screen.nodelay(True)
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    curses.start_color()

    try:
        yield screen
    finally:
        screen.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.flushinp()
        curses.endwin()


class App(ABC):
    @abstractmethod
    async def main(self):
        pass

    async def getch(self, screen):
        while True:
            key = screen.getch()
            if key == ESCAPE:
                loop = asyncio.get_running_loop()
                loop.stop()
                loop.close()
                break

            if key == curses.KEY_RESIZE:
                self.root.update_geometry()
            elif key != curses.ERR:
                self.root.dispatch(key)
                curses.flushinp()

            await asyncio.sleep(0)

    async def _run(self):
        with curses_screen() as screen:
            await asyncio.gather((self.getch(scr), self.main()))

    def run(self):
        asyncio.run(self._run())
