"""
TODO:
* Skip over "/n"
* Keep track of old _cursor_x when moving up/ down
"""

import string

from . import ArrayPad
from .. import (
    BACKSPACE,
    TAB,
    ENTER,
    DOWN,
    UP,
    LEFT,
    RIGHT,
    SLEFT,
    SRIGHT,
    HOME,
    UP_2,
    LEFT_2,
    RIGHT_2,
    DOWN_2,
    PGUP,
    END,
    PGDN,
    DELETE,
    SUP,
    SDOWN,
)

KEYS = {
    BACKSPACE, TAB, ENTER, DOWN, UP, LEFT, RIGHT,
    SLEFT, SRIGHT, HOME, UP_2, LEFT_2, RIGHT_2, DOWN_2,
    PGUP, END, PGDN, DELETE, SUP, SDOWN,
    *map(ord, string.printable)
}
EMPTY = chr(0x200B)  # zero-width space:  We need to differentiate from normal spaces in text.


class TextPad(ArrayPad):
    default_character = EMPTY
    cursor = ""
    cursor_color = None
    selected_color = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cursor_x = 0
        self._cursor_y = 0
        self._select_start = None
        self._select_end = None

    @property
    def text(self):
        return "".join("".join(char for char in row if char != self.default_character) for row in self.pad if not (row == self.default_character).all())

    @text.setter
    def text(self, contents):
        """
        rewrite pad contents with text
        """

    def refresh(self):
        if self.cursor_color is None:
            # The default cursor color pair can't be assigned until curses.init_scr has been called.
            # So we defer the import as long as possible.
            from .. import colors
            self.cursor_color = colors.BLACK_ON_WHITE

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        super().refresh()

        offset = int(self.has_border)
        if self.cursor:
            self.window.addstr(offset + self._cursor_y, offset + self._cursor_x, self.cursor, self.cursor_color)
        else:
            self.window.chgat(offset + self._cursor_y, offset + self._cursor_x, 1, self.cursor_color)

    def on_press(self, key):
        if key not in KEYS:
            return

        default = self.default_character
        pad = self.pad

        y, x  = self._cursor_y, self._cursor_x
        row, col = self.min_row, self.min_col

        max_y, max_x = self.buffer[1:, 1:].shape  # We don't use self.height, self.width as buffer will account for possible border

        if key == ENTER:
            if row + y == self.rows - 1:
                self.rows += 1

            rest_of_line = pad[row + y, col + x:]
            line_text = rest_of_line[rest_of_line != default]
            text_len = len(line_text)
            if text_len:
                if (pad[-1] != default).any():
                    self.rows += 1
                # Move lines down
                pad[row + y + 2:]  = pad[row + y + 1: -1]
                pad[row + y + 1] = default
                # Insert line_text at start of next row
                pad[row + y + 1, text_len:] = pad[row + y + 1, :-text_len]
                pad[row + y + 1, :text_len] = line_text

                # Erase
                pad[row + y, col + x:] = default

            pad[row + y, col + x] = "\n"

            if y == max_y:
                self.min_row += 1
            else:
                self._cursor_y += 1

            self._cursor_x = 0
            self.min_col = 0

        elif key == TAB:
            if (to_end := max_x - x) < 4:
                self.min_col += 4 - to_end
                self._cursor_x += to_end
            else:
                self._cursor_x += 4

            if (new_col := col + max_x - self.cols) > 0:
                self.cols += new_col

            pad[row + y, col + self._cursor_x: ] = pad[row + y, col + self._cursor_x - 4: -4]
            pad[row + y, col + self._cursor_x - 4: col + self._cursor_x] = " "

        elif key == BACKSPACE:
            if x != 0 or col != 0:
                pad[row + y, col + x - 1: -1] = pad[row + y, col + x: ]
                pad[row + y, -1] = default
                if x == 0:
                    self.min_col -= 1
                else:
                    self._cursor_x -= 1

            # TODO:  Move the leading word to the end of the above line

        elif key == LEFT or key == LEFT_2:
            if x:
                self._cursor_x -= 1

            elif col:
                self.min_col -= 1

            elif y or row:
                line_length = (pad[row + y - 1, :] != default).sum() - 1
                if (curs_x := line_length - col) <= max_x:
                    self._cursor_x = curs_x
                else:
                    self.min_col = max(0, line_length - max_x)
                    self._cursor_x = max_x if self.min_col else line_length

                if y:
                    self._cursor_y -= 1
                else:
                    self.min_row -= 1

        elif key == RIGHT or key == RIGHT_2:
            if pad[row + y, col + x] == "\n":
                self._cursor_x = 0
                self.min_col = 0
                if y == max_y:
                    self.min_row += 1
                else:
                    self._cursor_y += 1

            elif pad[row + y, col + x] != default:
                if x == max_x:
                    self.min_col += 1
                else:
                    self._cursor_x += 1

        elif key == SLEFT:
            ...

        elif key == SRIGHT:
            ...

        elif key == UP or key == UP_2:
            ...

        elif key == DOWN or key == DOWN_2:
            ...

        elif key == PGUP:
            ...

        elif key == PGDN:
            ...

        elif key == DELETE:
            pad[row + y, col + x: -1] = pad[row + y, col + x + 1:]
            pad[row + y, -1] = default
            # TODO: Move next word up if at end of line

        elif key == HOME:
            self._cursor_x = 0
            self.min_col = 0

        elif key == END:
            line_length = (pad[row + y, :] != default).sum()
            if line_length and pad[row + y, line_length - 1] == "\n":  # Skip over new lines
                line_length -= 1

            if (curs_x := line_length - col) <= max_x:
                self._cursor_x = curs_x
            else:
                self.min_col = max(0, line_length - max_x)
                self._cursor_x = max_x if self.min_col else line_length

        else:
            if pad[row + y, -1] != default:
                self.cols += 1

            pad[row + y, col + x + 1:] = pad[row + y, col + x: -1]
            pad[row + y, col + x] = chr(key)

            if x == max_x:
                self.min_col += 1
            else:
                self._cursor_x += 1


        self.root.refresh()
        return True
