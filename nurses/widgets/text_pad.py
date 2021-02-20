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
        self._last_x = None  # This keeps track of target cursor_x through vertical movement

    @staticmethod
    def _lines(text):
        """Yield each line of text including the newline."""
        start = 0
        for i, char in enumerate(text):
            if char == "\n":
                yield text[start: i + 1]
                start = i + 1
        yield text[start:]

    @property
    def text(self):
        return "".join("".join(char for char in row if char != self.default_character) for row in self.pad if not (row == self.default_character).all())

    @text.setter
    def text(self, contents):
        lines = tuple(self._lines(contents))

        if len(lines) > self.rows:
            self.rows = len(lines)

        if (cols := max(map(len, lines))) > self.cols:
            self.cols = cols

        self.pad[:] = self.default_character
        for i, line in enumerate(lines):
            self.pad[i, :len(line)] = tuple(line)

        self._set_min_col(len(line))
        self._set_min_row(i)

    @property
    def has_selection(self):
        return bool(self._select_start)

    @property
    def _max_x(self):
        return len(self.buffer[0]) - 1

    @property
    def _max_y(self):
        return len(self.buffer[:, 0]) - 1

    @property
    def _absolute_cursor(self):
        return self.min_row + self._cursor_y, self.min_col + self._cursor_x

    def _set_min_row(self, y):
        max_y = self._max_y

        if (curs_y := y - self.min_row) > max_y:
            self.min_row = y - max_y
            self._cursor_y = max_y
        elif curs_y < 0:
            self.min_row += curs_y
            self._cursor_y = 0
        else:
            self._cursor_y = curs_y

    def _set_min_col(self, x):
        """Move `self.min_col` if needed so that the cursor is visible."""
        max_x = self._max_x

        if (curs_x := x - self.min_col) > max_x:
            self.min_col = x - max_x
            self._cursor_x = max_x
        elif curs_x < 0:
            self.min_col += curs_x
            self._cursor_x = 0
        else:
            self._cursor_x = curs_x

    def _line_length(self, i, j=0):
        """Return the length of text of line `i` from `j`th character to end including the newline."""
        return (self.pad[i, j:] != self.default_character).sum()

    def unselect(self):
        self._select_start = self._select_end = None
        self.pad_colors[:] = self.color

    def delete_selection(self):
        if not self.has_selection:
            return

        self._last_x = None

        default = self.default_character
        pad = self.pad

        start_y, start_x = self._select_start
        end_y, end_x = self._select_end

        end_line_length = self._line_length(end_y, end_x)

        # Resize pad if the two lines are longer than pad's width
        if (new_col := start_x + end_line_length - self.cols) > 0:
            self.cols += new_col

        # Join start line and end line minus the selected text
        pad[start_y, start_x: start_x + end_line_length] = pad[end_y, end_x: end_x + end_line_length]
        pad[start_y, start_x + end_line_length:] = default

        if lines := end_y - start_y:
            # Move lines up
            pad[start_y + 1: -lines] = pad[end_y + 1:]
            pad[-lines] = default

        self._set_min_row(start_y)
        self._set_min_col(start_x)

        self.unselect()

    def _move_cursor_left(self):
        self._last_x = None
        curs_y, curs_x = self._absolute_cursor

        if curs_x:
            self._set_min_col(curs_x - 1)

        elif curs_y:
            self._set_min_row(curs_y - 1)

            line_length = self._line_length(curs_y - 1) - 1
            self._set_min_col(line_length)

    def _move_cursor_right(self):
        self._last_x = None

        cursor = curs_y, curs_x = self._absolute_cursor
        current_char = self.pad[cursor]

        if current_char == "\n":
            self._set_min_row(curs_y + 1)
            self._set_min_col(0)

        elif current_char != self.default_character:
            self._set_min_col(curs_x + 1)

    def _move_cursor_up(self):
        curs_y, curs_x = self._absolute_cursor

        if self._last_x is None or curs_y == curs_x == 0:
            self._last_x = curs_x

        if not curs_y:
            self._set_min_col(0)

        else:
            self._set_min_row(curs_y - 1)

            min_x = min(self._last_x, self._line_length(curs_y - 1) - 1)
            self._set_min_col(min_x)

    def _move_cursor_down(self):
        curs_y, curs_x = self._absolute_cursor

        line_length = self._line_length(curs_y)
        bottom_line = line_length == 0 or line_length != 0 and self.pad[curs_y, line_length - 1] != "\n"

        if self._last_x is None or bottom_line and curs_x == line_length:
            self._last_x = curs_x

        if bottom_line:
            self._set_min_col(line_length)

        else:
            self._set_min_row(curs_y + 1)

            next_line_length = self._line_length(curs_y + 1)
            if next_line_length and self.pad[curs_y + 1, next_line_length - 1] == "\n":
                next_line_length -= 1  # Don't put the cursor on a newline character

            min_x = min(self._last_x, next_line_length)
            self._set_min_col(min_x)

    def _highlight_selection(self):
        colors = self.pad_colors
        colors[:] = self.color
        start_y, start_x = self._select_start
        end_y, end_x = self._select_end
        selected_color = self.selected_color

        if lines := end_y - start_y:
            colors[start_y, start_x:] = selected_color
            if lines > 1:
                colors[start_y + 1: end_y] = selected_color
            colors[end_y, :end_x] = selected_color
        else:
            colors[start_y, start_x: end_x] = selected_color

        colors[self.pad == self.default_character] = self.color

    def on_press(self, key):
        if key not in KEYS:
            return

        default = self.default_character
        pad = self.pad

        cursor = curs_y, curs_x = self._absolute_cursor

        if key == ENTER:
            self.delete_selection()

            # Resize pad if we're at the bottom or there's text at the bottom.
            if curs_y == self.rows - 1 or pad[-1, 0] != default:
                self.rows += 1

            # Move lines down
            pad[curs_y + 2:] = pad[curs_y + 1: -1]
            pad[curs_y + 1] = default

            # Move rest of line onto next line
            text_len = self._line_length(curs_y, curs_x)
            if text_len:
                rest_of_line = pad[curs_y, curs_x: curs_x + text_len]

                # Insert line_text at start of next row
                pad[curs_y + 1, :text_len] = rest_of_line

                # Erase line_text from current row
                pad[curs_y, curs_x:] = default

            pad[cursor] = "\n"

            self._set_min_row(curs_y + 1)
            self._set_min_col(0)

        elif key == TAB:
            self.delete_selection()

            if (new_cols := self._line_length(curs_y) + 4 - self.cols) > 0:
                self.cols += new_cols

            pad[curs_y, curs_x + 4: ] = pad[curs_y, curs_x: -4]
            pad[curs_y, curs_x: curs_x + 4] = " "

            self._set_min_col(curs_x + 4)

        elif key == BACKSPACE:
            if not self.has_selection:
                if curs_x:
                    self._select_start = curs_y, curs_x - 1
                elif curs_y:
                    self._select_start = curs_y - 1, self._line_length(curs_y - 1) - 1
                else:
                    return True

                self._select_end = cursor

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
                self._select_start = self._select_end = cursor

            self._move_cursor_left()
            new_cursor = self._absolute_cursor

            if cursor == self._select_start:
                if new_cursor == cursor:  # Didn't move
                    return True

                self.pad_colors[new_cursor] = self.selected_color
                self._select_start = new_cursor

            else:
                self.pad_colors[new_cursor] = self.color
                self._select_end = new_cursor

        elif key == SRIGHT:
            if not self.has_selection:
                self._select_start = self._select_end = cursor

            if cursor == self._select_end:
                if pad[cursor] == default:
                    return True

                self.pad_colors[cursor] = self.selected_color
                self._move_cursor_right()
                self._select_end = self._absolute_cursor

            else:
                self.pad_colors[cursor] = self.color
                self._move_cursor_right()
                self._select_start = self._absolute_cursor

        elif key == UP or key == UP_2:
            self.unselect()
            self._move_cursor_up()

        elif key == DOWN or key == DOWN_2:
            self.unselect()
            self._move_cursor_down()

        elif key == SUP:
            if not self.has_selection:
                self._select_start = self._select_end = cursor

            was_before_start = cursor <= self._select_start

            self._move_cursor_up()

            new_cursor = self._absolute_cursor

            if new_cursor <= self._select_start:
                if not was_before_start:
                    self._select_end = self._select_start

                self._select_start = new_cursor

            else:
                self._select_end = new_cursor

            self._highlight_selection()

        elif key == SDOWN:
            if not self.has_selection:
                self._select_start = self._select_end = cursor

            was_after_end = cursor >= self._select_end

            self._move_cursor_down()

            new_cursor = self._absolute_cursor

            if new_cursor >= self._select_end:
                if not was_after_end:
                    self._select_start = self._select_end

                self._select_end = new_cursor

            else:
                self._select_start = new_cursor

            self._highlight_selection()

        elif key == PGUP:
            self.unselect()

            last_x = curs_x if self._last_x is None else self._last_x

            for _ in range(self._max_y - 1):
                self._move_cursor_up()

            self._last_x = last_x

        elif key == PGDN:
            self.unselect()

            last_x = curs_x if self._last_x is None else self._last_x

            for _ in range(self._max_y - 1):
                self._move_cursor_down()

            self._last_x = last_x

        elif key == DELETE:
            if not self.has_selection:
                if pad[cursor] == default:
                    return True

                self._select_start = cursor

                if pad[cursor] == "\n":
                    self._select_end = curs_y + 1, 0
                else:
                   self._select_end = curs_y, curs_x + 1

            self.delete_selection()

        elif key == HOME:
            self.unselect()
            self._last_x = None
            self._set_min_col(0)

        elif key == END:
            self.unselect()
            self._last_x = None

            line_length = self._line_length(curs_y)
            if line_length and pad[curs_y, line_length - 1] == "\n":
                line_length -= 1
            self._set_min_col(line_length)

        else:  # Print whatever key is pressed:
            self.delete_selection()

            if pad[curs_y, -1] != default:
                self.cols += 1

            pad[curs_y, curs_x + 1:] = pad[curs_y, curs_x: -1]
            pad[cursor] = chr(key)

            self._set_min_col(curs_x + 1)

        self.root.refresh()
        return True

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

            if start != end:
                row, col = self.min_row, self.min_col
                h, w = self.buffer.shape

                for y, x in np.argwhere(self.pad == "\n"):
                    if start <= (y, x) < end and row <= y < row + h and col <= x < col + w:
                        self.window.chgat(offset + y - row, offset + x - col, 1, self.selected_color)  # Show selected new lines
                return  # We won't draw cursor if there's a selection, so return early.

            self.unselect()

        if self.cursor:
            self.window.addstr(offset + self._cursor_y, offset + self._cursor_x, self.cursor, self.cursor_color)
        else:
            self.window.chgat(offset + self._cursor_y, offset + self._cursor_x, 1, self.cursor_color)
