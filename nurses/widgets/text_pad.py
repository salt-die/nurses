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

    @property
    def text(self):
        """
        join contents of pad array
        """

    @text.setter
    def text(self, contents):
        """
        rewrite pad contents with text
        """

    def on_press(self, key):
        if key not in KEYS:
            return

        text = self.text
        text_offset = self._text_offset
        cursor_x = self._cursor_x
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
