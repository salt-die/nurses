from . import Widget

BACKSPACE = 8
TAB = 9
ENTER = 10
LEFT = 260
RIGHT = 261
HOME = 449
END = 455
DELETE = 462


class Textbox(Widget):
    CURSOR = "█"
    CURSOR_COLOR = 0

    def __init__(self, top, left, width,*args, **kwargs):
        super().__init__(top, left, 3 if kwargs.get("border") else 1, width + 2 * bool(kwargs.get("border")), *args, **kwargs)
        self._gathering = False
        self._reset()

    def refresh(self):
        offset = 1 if self.has_border else 0
        self.window.hline(offset, offset, " ", self.width - 2 * offset)
        self.window.addstr(offset, offset, self._input[self._input_offset: self._input_offset + self.width - 2 * offset])
        self.window.addstr(offset, offset + self._cursor_x, self.CURSOR, self.CURSOR_COLOR)

    def _reset(self):
        self._input = ""
        self._input_offset = 0
        self._cursor_x = 0

    async def gather(self):
        self._gathering = True

        from .. import ScreenManager  # We need the event loop, but we need to defer this import to avoid a circular import.
        sm = ScreenManager()

        self.root.refresh()

        while self._gathering:
            await sm.next_task()

        self.parent.remove_widget(self)

        try:
            return self._input
        finally:
            self._reset()

    def on_press(self, key):
        if not self._gathering:
            return

        text = self._input
        text_offset = self._input_offset
        cursor_x = self._cursor_x
        end = self.width - 2 * bool(self.has_border) - 1

        if key == ENTER:
            self._gathering = False

        elif key == TAB:
            self._input = f"{text[:text_offset + cursor_x]}    {text[text_offset + cursor_x:]}"
            if (to_end := end - cursor_x) < 4:
                self._input_offset += 4 - to_end
                self._cursor_x += to_end
            else:
                self._cursor_x += 4

        elif key == BACKSPACE:
            if cursor_x != 0 or text_offset != 0:
                self._input = text[:text_offset + cursor_x - 1] + text[text_offset + cursor_x:]
                if cursor_x == 0:
                    self._input_offset -= 1
                else:
                    self._cursor_x -= 1

        elif key == LEFT:
            if cursor_x != 0 or text_offset != 0:
                if cursor_x == 0:
                    self._input_offset -= 1
                else:
                    self._cursor_x -= 1

        elif key == RIGHT:
            if cursor_x + text_offset != len(text):
                if cursor_x != end:
                    self._cursor_x += 1
                else:
                    self._input_offset += 1

        elif key == DELETE:
            if text:
                self._input = text[:text_offset + cursor_x] + text[text_offset + cursor_x + 1:]

        elif key == HOME:
            self._cursor_x = 0
            self._input_offset = 0

        elif key == END:
            self._input_offset = max(0, len(text) - end)
            self._cursor_x = len(text) if self._input_offset == 0 else end

        else:
            self._input = f"{text[:text_offset + cursor_x]}{chr(key)}{text[text_offset + cursor_x:]}"
            if cursor_x == end:
                self._input_offset += 1
            else:
                self._cursor_x += 1

        self.root.refresh()
        return True
