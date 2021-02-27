from itertools import cycle
from random import random

from nurses import colors, ScreenManager, CUP, CRIGHT, CDOWN, CLEFT
from nurses.widgets import ArrayWin, DigitalClock, TextPad
from nurses.widgets.behaviors import Selectable, Movable, Bouncing


class MovingClock(Bouncing, DigitalClock):
    ...


class Window(ArrayWin, Movable, Selectable):
    select_key = 0  # Ctrl + `
    move_up = move_up_alt = CUP
    move_left = move_left_alt = CRIGHT
    move_down = move_down_alt = CDOWN
    move_right = move_right_alt = CLEFT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, border_style="light", **kwargs)

    def refresh(self):
        if self.is_selected:
            if self.border_style != "heavy":
                self.border("heavy", colors.BLUE_ON_BLACK)
        elif self.border_style != "light":
            self.border()

        super().refresh()


class Notepad(Window, TextPad):
    ...


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient(20))
    blue_to_purple = colors.gradient(20, (0, 255, 255), (103, 15, 215), "blue_to_purple")

    sm.root.add_widget(Notepad(0, 0, size_hint=(.5, .5)))
    ur = sm.root.new_widget(pos_hint=(.0, .5), size_hint=(.5, .5), create_with=Window)
    lr = sm.root.new_widget(pos_hint=(.5, .0), size_hint=(.5, .5), create_with=Window)
    ll = sm.root.new_widget(pos_hint=(.5, .5), size_hint=(.5, .5), create_with=Window)

    # Setup Menubar in upper-right window
    ur._out = 1
    def add_text(text):
        if ur._out == len(ur.buffer[:, 0]):
            ur.scroll()
        else:
            ur._out += 1

        ur[ur._out - 1, :len(text)] = text

    menu = (
        ("1st Entry", lambda: add_text("1st Entry Selected")),
        ("2nd Entry", lambda: add_text("2nd Entry Selected")),
        ("3rd Entry", lambda: add_text("3rd Entry Selected")),
    )

    ur.new_widget(
        ("Menu1", menu),
        ("Menu2", menu),
        ("Menu3", menu),
        color=colors.BLACK_ON_WHITE,
        selected_color=colors.WHITE_ON_BLACK,
        border_style="light",
        create_with="Menubar",
    )

    # Chart to lower-right window
    chart = lr.new_widget(maxlen=200, gradient=blue_to_purple, y_label=5, size_hint=(1., 1.), create_with="Chart")

    # Moving clock to lower-left window
    mc = ll.new_widget(1, 1, delay=.1, create_with=MovingClock)
    mc.schedule_bounce()

    sm.schedule(lambda: mc.update_color(next(rainbow)), delay=.1)
    sm.schedule(lambda: chart.update(random() * 50), delay=.1)
    sm.schedule(sm.root.refresh)
    sm.run()
