import string

from . import Widget
from .. import BACKSPACE, TAB, ENTER, LEFT, RIGHT, HOME, END, DELETE

KEYS = { BACKSPACE, TAB, ENTER, LEFT, RIGHT, HOME, END, DELETE, *map(ord, string.printable) }

class Textbox(Widget):
    cursor = ""
    cursor_color = None

    def __init__(self, top, left, width,*args, **kwargs):
        super().__init__(top, left, 3 if kwargs.get("border_style") else 1, width + 2 * bool(kwargs.get("border_style")), *args, **kwargs)
        self._gathering = False
        self._reset()

    def refresh(self):
        offset = int(self.has_border)
        width = self.width - 2 * offset

        self.window.hline(offset, offset, " ", width)  # Erase text
        self.window.addstr(offset, offset, self._input[self._input_offset: self._input_offset + width])

        if self.cursor_color is None:
            # The default cursor color pair can't be assigned until curses.init_scr has been called.
            from .. import colors
            self.cursor_color = colors.BLACK_ON_WHITE

        if self.cursor:
            self.window.addstr(offset, offset + self._cursor_x, self.cursor, self.cursor_color)
        else:
            self.window.chgat(offset, offset + self._cursor_x, 1, self.cursor_color)

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
        if not self._gathering or key not in KEYS:
            return

        text = self._input
        text_offset = self._input_offset
        cursor_x = self._cursor_x
        end = self.width - 2 * self.has_border - 1

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
