from . import ArrayWin
from ..managers import ScreenManager

ENTER = 10


class Textbox(ArrayWin):
    """
    TODO: bounds checks in on_press, limit height?,
    ... : alternative async init (with metaclasses)? --- textboxes are meant as one-shot inputs mostly?
    ... : refresh root while gathering?
    ... : pass event loop into constructor?

    This is a incomplete, non-blocking version of a curses Textbox.  I've not decided exactly how I want this to behave yet.
    """
    CURSOR = "█"
    CURSOR_COLOR = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gathering = False
        self._col = 0

    def refresh(self):
        super().refresh()
        offset = 1 if self.has_border else 0
        self.window.addstr(offset, self._col + offset, self.CURSOR, self.CURSOR_COLOR)

    async def gather(self):
        self._gathering = True

        while self._gathering:
            await ScreenManager().next_task()

        self.parent.remove_widget(self)
        return "".join(self.buffer[0])

    def on_press(self, key):
        if not self._gathering:
            return

        if key == ENTER:
            self._gathering = False
        else:
            self[0, self._col] = chr(key)
            self._col += 1

        return True
