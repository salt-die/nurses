import string

import numpy as np

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
        self.unselect()
        self._vert_x = None  # This keeps track of target cursor_x through vertical movement

    @property
    def text(self):
        return "".join("".join(char for char in row if char != self.default_character) for row in self.pad if not (row == self.default_character).all())

    @text.setter
    def text(self, contents):
        """
        rewrite pad contents with text
        """

    @property
    def has_selection(self):
        return bool(self._select_start)

    def refresh(self):
        # The default cursor color and selected text color can't be assigned until curses.init_scr has been called
        # so we defer the import as long as possible.
        if self.cursor_color is None:
            from .. import colors
            self.cursor_color = colors.BLACK_ON_WHITE

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.WHITE_ON_BLUE

        super().refresh()

        offset = int(self.has_border)

        if self.has_selection:
            start, end = self._select_start, self._select_end

            if start == end:
                self.unselect()
            else:
                row, col = self.min_row, self.min_col
                h, w = self.buffer.shape

                for y, x in np.argwhere(self.pad == "\n"):
                    if (
                        start <= (y, x) < end and
                        (row, col) <= (y, x) < (row + h, col + w)
                    ):
                        self.window.chgat(offset + y - row, offset + x - col, 1, self.selected_color)  # Show selected new lines
                return

        if self.cursor:
            self.window.addstr(offset + self._cursor_y, offset + self._cursor_x, self.cursor, self.cursor_color)
        else:
            self.window.chgat(offset + self._cursor_y, offset + self._cursor_x, 1, self.cursor_color)

    def unselect(self):
        self._select_start = self._select_end = None
        self.pad_colors[:] = self.color

    def delete_selection(self):
        if not self.has_selection:
            return

        default = self.default_character
        pad = self.pad
        row, col = self.min_row, self.min_col
        max_y, max_x = self.buffer[1:, 1:].shape

        start_y, start_x = self._select_start
        end_y, end_x = self._select_end

        end_line_length = (pad[end_y, end_x:] != default).sum()

        # Resize pad if the two lines are longer than pad's width
        if (new_col := start_x + end_line_length - self.cols) > 0:
            self.cols += new_col

        pad[start_y, start_x: start_x + end_line_length] = pad[end_y, end_x: end_x + end_line_length]
        pad[start_y, start_x + end_line_length:] = default

        if lines := end_y - start_y:
            # Move lines up
            pad[start_y + 1: -lines] = pad[end_y + 1:]
            pad[-lines] = default

        if (curs_x := start_x - col) <= max_x:
            self._cursor_x = curs_x
        else:
            self.min_col = max(0, start_x - max_x)
            self._cursor_x = max_x if self.min_col else start_x

        if (curs_y := start_y - row) <= max_y:
            self._cursor_y = curs_y
        else:
            self.min_row = max(0, start_y - max_y)
            self._cursor_y = max_y if self.min_row else start_y

        self.unselect()

    def _move_cursor_left(self):
        y, x  = self._cursor_y, self._cursor_x
        row, col = self.min_row, self.min_col
        max_x = len(self.buffer[0]) - 1

        if x:
            self._cursor_x -= 1

        elif col:
            self.min_col -= 1

        elif y or row:
            line_length = (self.pad[row + y - 1, :] != self.default_character).sum() - 1
            if (curs_x := line_length - col) <= max_x:
                self._cursor_x = curs_x
            else:
                self.min_col = max(0, line_length - max_x)
                self._cursor_x = max_x if self.min_col else line_length

            if y:
                self._cursor_y -= 1
            else:
                self.min_row -= 1

    def _move_cursor_right(self):
        pad = self.pad
        y, x  = self._cursor_y, self._cursor_x
        row, col = self.min_row, self.min_col
        max_y, max_x = self.buffer[1:, 1:].shape

        if pad[row + y, col + x] == "\n":
            self._cursor_x = 0
            self.min_col = 0
            if y == max_y:
                self.min_row += 1
            else:
                self._cursor_y += 1

        elif pad[row + y, col + x] != self.default_character:
            if x == max_x:
                self.min_col += 1
            else:
                self._cursor_x += 1

    def on_press(self, key):
        if key not in KEYS:
            return

        default = self.default_character
        pad = self.pad

        y, x  = self._cursor_y, self._cursor_x
        row, col = self.min_row, self.min_col

        max_y, max_x = self.buffer[1:, 1:].shape  # We don't use self.height, self.width as buffer will account for possible border

        if key == ENTER:
            self.delete_selection()

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
            self.delete_selection()

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
            if not self.has_selection:
                if x or col:
                    self._select_start = row + y, col + x - 1
                elif y or row:
                    self._select_start = row + y - 1, (pad[row + y - 1, :] != default).sum() - 1
                else:
                    return True
                self._select_end = row + y, col + x

            self.delete_selection()

        elif key == LEFT or key == LEFT_2:
            if self.has_selection:
                self.unselect()
            else:
                self._move_cursor_left()

        elif key == RIGHT or key == RIGHT_2:
            if self.has_selection:
                self.unselect()
            else:
                self._move_cursor_right()

        elif key == SLEFT:
            if not self.has_selection:
                self._select_start = self._select_end = row + y, col + x

            if (row + y, col + x) == self._select_start:
                self._move_cursor_left()
                self.pad_colors[self.min_row + self._cursor_y, self.min_col + self._cursor_x] = self.selected_color
                self._select_start = self.min_row + self._cursor_y, self.min_col + self._cursor_x

            else:
                self._move_cursor_left()
                self.pad_colors[self.min_row + self._cursor_y, self.min_col + self._cursor_x] = self.color
                self._select_end = self.min_row + self._cursor_y, self.min_col + self._cursor_x

        elif key == SRIGHT:
            if not self.has_selection:
                self._select_start = self._select_end = row + y, col + x

            if (row + y, col + x) == self._select_end:
                self.pad_colors[row + y, col + x] = self.selected_color
                self._move_cursor_right()
                self._select_end =  self.min_row + self._cursor_y, self.min_col + self._cursor_x

            else:
                self.pad_colors[row + y, col + x] = self.color
                self._move_cursor_right()
                self._select_start = self.min_row + self._cursor_y, self.min_col + self._cursor_x

        elif key == UP or key == UP_2:
            ...

        elif key == DOWN or key == DOWN_2:
            ...

        elif key == SUP:
            ...

        elif key == SDOWN:
            ...

        elif key == PGUP:
            ...

        elif key == PGDN:
            ...

        elif key == DELETE:
            if not self.has_selection:
                if pad[row + y, col + x] == default:
                    return True

                self._select_start = row + y, col + x

                if pad[row + y, col + x] == "\n":
                    self._select_end = row + y + 1, 0
                else:
                   self._select_end = row + y, col + x + 1

            self.delete_selection()

        elif key == HOME:
            self.unselect()
            self._cursor_x = 0
            self.min_col = 0

        elif key == END:
            self.unselect()
            line_length = (pad[row + y, :] != default).sum()
            if line_length and pad[row + y, line_length - 1] == "\n":  # Skip over new lines
                line_length -= 1

            if (curs_x := line_length - col) <= max_x:
                self._cursor_x = curs_x
            else:
                self.min_col = max(0, line_length - max_x)
                self._cursor_x = max_x if self.min_col else line_length

        else:  # Print whatever key is pressed:
            self.delete_selection()

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
