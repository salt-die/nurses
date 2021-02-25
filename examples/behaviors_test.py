from itertools import cycle
from random import random

from nurses import colors, ScreenManager
from nurses.widgets import ArrayWin, Chart, DigitalClock, TextPad
from nurses.widgets.behaviors import Selectable, Movable, Bouncing


class MovingClock(Bouncing, DigitalClock):
    ...


class Window(ArrayWin, Movable, Selectable):
    select_key = 0  # Ctrl + `
    move_up = move_up_alt = 480  # Ctrl + Up
    move_left = move_left_alt = 443  # Ctrl + Right
    move_down = move_down_alt = 481  # Ctrl + Down
    move_right = move_right_alt = 444  # Ctrl + Left

    def __init__(self, *args, **kwargs):
        super().__init__(*args, border_style="light", **kwargs)

    def refresh(self):
        if self.is_selected:
            if self.border_style != "heavy":
                self.border("heavy", colors.BLUE_ON_BLACK)
        elif self.border_style != "light":
            self.border()

        super().refresh()

    def on_press(self, key):
        if key == self.select_key or self.is_selected:
            return super().on_press(key)


class Notepad(Window, TextPad):
    ...


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient(20))
    blue_to_purple = colors.gradient(20, (0, 255, 255), (103, 15, 215), "blue_to_purple")

    sm.root.add_widget(Notepad(0, 0, size_hint=(.5, .5)))
    sm.root.add_widget(Notepad(pos_hint=(0, .5), size_hint=(.5, .5)))
    chart = sm.root.new_widget(pos_hint=(.5, .0), size_hint=(.5, .5), create_with=Window).new_widget(
        maxlen=200, gradient=blue_to_purple, y_label=5, create_with=Chart)
    mc = sm.root.new_widget(pos_hint=(.5, .5), size_hint=(.5, .5), create_with=Window).new_widget(1, 1, delay=.1, create_with=MovingClock)
    mc.schedule_bounce()

    sm.schedule(lambda: mc.update_color(next(rainbow)), delay=.1)
    sm.schedule(lambda: chart.update(random() * 50), delay=.1)
    sm.schedule(sm.root.refresh)
    sm.run()
