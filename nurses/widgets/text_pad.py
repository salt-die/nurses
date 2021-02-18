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
        self._vert_x = None  # This keeps track of target cursor_x through vertical movement

    @property
    def text(self):
        return "".join("".join(char for char in row if char != self.default_character) for row in self.pad if not (row == self.default_character).all())

    @text.setter
    def text(self, contents):
        """
        rewrite pad contents with text
        """

    def refresh(self):
        # The default cursor color and selected text color can't be assigned until curses.init_scr has been called
        # so we defer the import as long as possible.
        if self.cursor_color is None:
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
            # TODO: overwrite selected text

            # Resize pad if we're at the bottom or there's text at the bottom.
            if row + y == self.rows - 1 or pad[-1, 0] != default:
                self.rows += 1

            # Move lines down
            pad[row + y + 2:] = pad[row + y + 1: -1]
            pad[row + y + 1] = default

            # Move rest of line onto next line
            rest_of_line = pad[row + y, col + x:]
            line_text = rest_of_line[rest_of_line != default]
            if text_len := len(line_text):
                # Insert line_text at start of next row
                pad[row + y + 1, :text_len] = line_text

                # Erase line_text from current row
                pad[row + y, col + x:] = default

            pad[row + y, col + x] = "\n"

            if y == max_y:
                self.min_row += 1
            else:
                self._cursor_y += 1

            self._cursor_x = 0
            self.min_col = 0

        elif key == TAB:
            # TODO: overwrite selected text

            if (to_end := max_x - x) < 4:
                self.min_col += 4 - to_end
                self._cursor_x += to_end
            else:
                self._cursor_x += 4

            if (new_col := col + max_x - self.cols) > 0:
                self.cols += new_col

            pad[row + y, self.min_col + self._cursor_x: ] = pad[row + y, self.min_col + self._cursor_x - 4: -4]
            pad[row + y, self.min_col + self._cursor_x - 4: self.min_col + self._cursor_x] = " "

        elif key == BACKSPACE:
            # TODO: overwrite selected text

            if x or col:
                pad[row + y, col + x - 1: -1] = pad[row + y, col + x: ]
                pad[row + y, -1] = default
                if x:
                    self._cursor_x -= 1
                else:
                    self.min_col -= 1

            elif y or row:
                # Join current line with previous line, i.e., delete the previous line's "\n"
                prev_line_length = (pad[row + y - 1, :] != default).sum() - 1  # -1 because we'll destroy the previous line's "\n"
                this_line_length = (pad[row + y, :] != default).sum()

                # Resize pad if the two lines are longer than pad's width
                if (new_col := prev_line_length + this_line_length - self.cols) > 0:
                    self.cols += new_col

                pad[row + y - 1, prev_line_length: prev_line_length + this_line_length] = pad[row + y, :this_line_length]

                # Move lines up
                pad[row + y: -1] = pad[row + y + 1:]
                pad[-1] = default

                # Logic same as left movement --- perhaps write a single routine?
                if (curs_x := prev_line_length - col) <= max_x:
                    self._cursor_x = curs_x
                else:
                    self.min_col = max(0, prev_line_length - max_x)
                    self._cursor_x = max_x if self.min_col else prev_line_length

                if y:
                    self._cursor_y -= 1
                else:
                    self.min_row -= 1

        elif key == LEFT or key == LEFT_2:
            # TODO: un-select text

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
            # TODO: un-select text

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
            # TODO: overwrite selected text

            pad[row + y, col + x: -1] = pad[row + y, col + x + 1:]
            pad[row + y, -1] = default

            # TODO: Move next word up if at end of line

        elif key == HOME:
            # TODO: un-select text
            self._cursor_x = 0
            self.min_col = 0

        elif key == END:
            # TODO: un-select text
            line_length = (pad[row + y, :] != default).sum()
            if line_length and pad[row + y, line_length - 1] == "\n":  # Skip over new lines
                line_length -= 1

            if (curs_x := line_length - col) <= max_x:
                self._cursor_x = curs_x
            else:
                self.min_col = max(0, line_length - max_x)
                self._cursor_x = max_x if self.min_col else line_length

        else:  # Print whatever key is pressed:
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
