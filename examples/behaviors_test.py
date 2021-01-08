from itertools import product

import numpy as np

from nurses import ScreenManager, colors
from nurses.widgets.arraywin import ArrayWin, push_buffer
from nurses.widgets.behaviors import Selectable, Movable


class Notepad(ArrayWin, Movable, Selectable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, border="light", **kwargs)
        self._col = 0
        self.cursor_color = colors.BLACK_ON_WHITE
        self.update_cursor()

    @push_buffer
    def update_cursor(self):
        if self._col == 0:
            self.colors[-2] = self.color
        else:
            self.colors[-1, self._col - 1] = self.color

        self.colors[-1, self._col] = self.cursor_color if self.is_selected else self.color

    def on_press(self, key):
        if key == self.select_key:
            return super().on_press(key)

        if self.is_selected:
            if super().on_press(key):
                return True

            if key == 10:  # Enter
                self.scroll()
                self._col = 0
            # Presumably, would need to handle other non-character keypresses, e.g., delete, backspace, tab, etc.
            else:
                if self._col == self.width - 3:  # End of a line, we'll roll it
                    self[-1] = np.roll(self[-1], -1)
                    self[-1, -1] = " "
                else:
                    self._col += 1
                self.buffer[-1, self._col - 1] = chr(key)

            self.update_cursor()
            return True

    def refresh(self):
        if self.is_selected:
            if self.has_border[0] != "heavy":
                self.border("heavy", colors.BLUE_ON_BLACK, push=False)
                self.update_cursor()
        elif self.has_border[0] != "light":
            self.border(push=False)
            self.update_cursor()


with ScreenManager() as sm:
    for y, x in product((0, .5), repeat=2):
        sm.root.new_widget(y, x, .5, .5, create_with=Notepad)
    sm.schedule(sm.root.refresh)
    sm.run()
