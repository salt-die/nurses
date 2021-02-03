from . import ArrayWin

ENTER = 10


class Textbox(ArrayWin):
    CURSOR = "█"
    CURSOR_COLOR = 0

    def __init__(self, top, left, width,*args, **kwargs):
        super().__init__(top, left, 3 if kwargs.get("border") else 1, width + 2 * bool(kwargs.get("border")), *args, **kwargs)
        self._input = ""
        self._gathering = False
        self._col = 0

    def refresh(self):
        super().refresh()
        offset = 1 if self.has_border else 0
        self.window.addstr(offset, self._col + offset, self.CURSOR, self.CURSOR_COLOR)

    async def gather(self):
        self._gathering = True

        from .. import ScreenManager  # We need the event loop, but we need to defer this import to avoid circularity.
        sm = ScreenManager()

        self.root.refresh()

        while self._gathering:
            await sm.next_task()

        self.parent.remove_widget(self)
        return self._input

    def on_press(self, key):
        if not self._gathering:
            return

        if key == ENTER:
            self._gathering = False
        # TODO: Check for arrow keys / delete / backspace
        else:
            self._input += chr(key)
            self[0, self._col] = chr(key)

            if self._col == self.width - 2 * bool(self.has_border) - 1:
                self.roll()
            else:
                self._col += 1

        self.root.refresh()
        return True
