from itertools import cycle

from nurses import colors, ScreenManager
from nurses.widgets import ArrayWin, DigitalClock
from nurses.widgets.behaviors import Selectable, Movable, Bouncing


VELOCITY = .5


class MovingClock(Bouncing, DigitalClock):
    def __init__(self, top=0, left=0, *args, **kwargs):
        super().__init__(top, left, *args, pos=complex(top, left), vel= (1 + 1j) * VELOCITY / abs(1 + 1j), **kwargs)


class Window(ArrayWin, Movable, Selectable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, border="light", **kwargs)

    def refresh(self):
        if self.is_selected:
            if self.has_border[0] != "heavy":
                self.border("heavy", colors.BLUE_ON_BLACK)
        elif self.has_border[0] != "light":
            self.border()

        super().refresh()

    def on_press(self, key):
        if key == self.select_key:
            return super().on_press(key)

        if self.is_selected:
            if super().on_press(key):
                return True


class Notepad(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._col = 0
        self.cursor_color = colors.BLACK_ON_WHITE

    def update_cursor(self):
        if self._col == 0:
            self.colors[-2] = self.color
        else:
            self.colors[-1, self._col - 1] = self.color

        self.colors[-1, self._col] = self.cursor_color if self.is_selected else self.color

    def on_press(self, key):
        if super().on_press(key):
            return True

        if self.is_selected:
            if key == 10:  # Enter
                self.scroll()
                self._col = 0
            # Presumably, would need to handle other non-character keypresses, e.g., delete, backspace, tab, etc.
            else:
                if self._col == self.width - 3:  # End of a line, we'll roll it
                    self[-1, :-1] = self[-1, 1:]
                    self[-1, -1] = " "
                else:
                    self._col += 1
                self.buffer[-1, self._col - 1] = chr(key)

            self.update_cursor()
            return True

    def refresh(self):
        self.update_cursor()
        super().refresh()


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient(20))

    sm.root.add_widget(Notepad(0, 0, size_hint=(.5, .5)))
    sm.root.add_widget(Notepad(pos_hint=(0, .5), size_hint=(.5, .5)))
    sm.root.add_widget(Notepad(pos_hint=(.5, 0), size_hint=(.5, .5)))
    mc = sm.root.new_widget(pos_hint=(.5, .5), size_hint=(.5, .5), create_with=Window).new_widget(1, 1, delay=.1, create_with=MovingClock)
    mc.schedule_bounce()

    sm.schedule(lambda: mc.update_color(next(rainbow)), delay=.1)
    sm.schedule(sm.root.refresh)
    sm.run()
