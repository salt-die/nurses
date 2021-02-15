import string

from . import ArrayPad
from .. import BACKSPACE, TAB, ENTER, LEFT, RIGHT, UP, DOWN, HOME, END, DELETE

KEYS = { BACKSPACE, TAB, ENTER, LEFT, RIGHT, UP, DOWN, HOME, END, DELETE, *map(ord, string.printable) }
EMPTY = chr(0x200B)  # zero-width space:  We need to differentiate from normal spaces in text.

class TextPad(ArrayPad):
    default_character = EMPTY
    cursor = ""
    cursor_color = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cursor_x = 0
        self._cursor_y = 0

    @property
    def text(self):
        return "".join("".join(char for char in row if char != EMPTY) for row in self.pad if not (row == EMPTY).all())

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

        super().refresh()

        offset = int(self.has_border)
        if self.cursor:
            self.window.addstr(offset + self._cursor_y, offset + self._cursor_x, self.cursor, self.cursor_color)
        else:
            self.window.chgat(offset + self._cursor_y, offset + self._cursor_x, 1, self.cursor_color)

    def on_press(self, key):
        if key not in KEYS:
            return

        pad = self.pad

        x, y = self._cursor_x, self._cursor_y
        row, col = self.min_row, self.min_col

        top_of_text = y == 0 and row == 0
        start_of_line = x == 0 and col == 0
        end_of_line = x + col == self.cols or x + col < self.cols and pad[row + y, col + x + 1] == EMPTY

        max_y, max_x = self.buffer[:-1, :-1].shape  # We don't use self.height, self.width as buffer will account for possible border

        if key == ENTER:
            if row + y == self.rows:
                self.rows += 1

            rest_of_line = pad[row + y, col + x:]
            if len(line_text := rest_of_line[rest_of_line != EMPTY]):
                text_len = len(line_text)
                # Resize if needed
                if new_cols := text_len - (pad[row + y + 1, -text_len:] == EMPTY).sum():
                    # Note that `self.cols` is an observable and we don't want to call `__set__` if new_cols is 0
                    self.cols += new_cols

                # Insert line_text at start of next row
                pad[row + y + 1, text_len:] = pad[row + y + 1, :-text_len]
                pad[row + y + 1, :text_len] = line_text

                # Erase
                pad[row + y, col + x:] = EMPTY

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
                pad[row + y, -1] = EMPTY
                if x == 0:
                    self.min_col -= 1
                else:
                    self._cursor_x -= 1

            # TODO:  Move the leading word to the end of the above line

        elif key == LEFT:
            if x != 0 or col != 0:
                if x == 0:
                    self.min_col -= 1
                else:
                    self._cursor_x -= 1

            # TODO: Move up a line if cursor is at start of a line

        elif key == RIGHT:
            if end_of_line:
                if row + y != self.rows and pad[row + y + 1, 0] != EMPTY:
                    self._cursor_x = 0
                    if y == max_y:
                        self.min_row += 1
                    else:
                        self._cursor_y += 1
            else:
                if x == max_x:
                    self.min_col += 1
                else:
                    self._cursor_x += 1

        elif key == DELETE:
            pad[row + y, col + x: -1] = pad[row + y, col + x + 1:]
            pad[row + y, -1] = EMPTY
            # TODO: Move next line up if at end of line

        elif key == HOME:
            self._cursor_x = 0
            self.min_col = 0

        elif key == END:
            line_length = (pad[y, :] != EMPTY).sum()
            if (curs_x := line_length - col) <= max_x:
                self._cursor_x = curs_x
            else:
                self.min_col = max(0, line_length - max_x)
                self._cursor_x = max_x if self.min_col else line_length

        else:
            if pad[row + y, -1] != EMPTY:
                self.cols += 1

            pad[row + y, col + x + 1:] = pad[row + y, col + x: -1]
            pad[row + y, col + x] = chr(key)

            if x == max_x:
                self.min_col += 1
            else:
                self._cursor_x += 1


        self.root.refresh()
        return True
