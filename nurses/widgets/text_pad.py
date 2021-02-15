"""
most of this is copy/pasted from Textbox, Nonfunctional atm
"""

from . import ArrayPad
from .. import BACKSPACE, TAB, ENTER, LEFT, RIGHT, UP, DOWN, HOME, END, DELETE

KEYS = { BACKSPACE, TAB, ENTER, LEFT, RIGHT, UP, DOWN, HOME, END, DELETE, *map(ord, string.printable) }


class TextPad(ArrayPad):
    cursor = ""
    cursor_color = None

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
        super().__init__(*args, **kwargs)

        self.pad[...] = chr(0x200B)  # zero-width space:  We need to differentiate from normal spaces in text.
        self._cursor_x = 0
        self._cursor_y = 0

    @property
    def text(self):
        return "\n".join("".join(char for char in row if char != chr(0x200B)) for row in self.pad)

    @text.setter
    def text(self, contents):
        """
        rewrite pad contents with text
        """

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

    def on_press(self, key):
        if key not in KEYS:
            return

        text = self.text
        x, y = self._cursor_x, self._cursor_y
        end = self.width - 2 * self.has_border - 1

        if key == ENTER:
            ...  # New line

        elif key == TAB:
            self._input = f"{text[:text_offset + cursor_x]}    {text[text_offset + cursor_x:]}"
            if (to_end := end - cursor_x) < 4:
                self._text_offset += 4 - to_end
                self._cursor_x += to_end
            else:
                self._cursor_x += 4

        elif key == BACKSPACE:
            if cursor_x != 0 or text_offset != 0:
                self._input = text[:text_offset + cursor_x - 1] + text[text_offset + cursor_x:]
                if cursor_x == 0:
                    self._text_offset -= 1
                else:
                    self._cursor_x -= 1

        elif key == LEFT:
            if cursor_x != 0 or text_offset != 0:
                if cursor_x == 0:
                    self._text_offset -= 1
                else:
                    self._cursor_x -= 1

        elif key == RIGHT:
            if cursor_x + text_offset != len(text):
                if cursor_x != end:
                    self._cursor_x += 1
                else:
                    self._text_offset += 1

        elif key == DELETE:
            if text:
                self._input = text[:text_offset + cursor_x] + text[text_offset + cursor_x + 1:]

        elif key == HOME:
            self._cursor_x = 0
            self._text_offset = 0

        elif key == END:
            self._text_offset = max(0, len(text) - end)
            self._cursor_x = len(text) if self._text_offset == 0 else end

        else:
            self._input = f"{text[:text_offset + cursor_x]}{chr(key)}{text[text_offset + cursor_x:]}"
            if cursor_x == end:
                self._text_offset += 1
            else:
                self._cursor_x += 1

        self.root.refresh()
        return True
