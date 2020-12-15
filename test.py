from random import random, choice
import time

from nurses import ScreenManager


with ScreenManager() as sm:
    widgets = [sm.new_widget(5 * i, 0, 4, 15) for i in range(5)]
    for widget in widgets:
        widget[1:3, 1:14] = "Hello, World!\nI'm a widget!"
        widget.colors[1:3, 5:-5] = sm.color(3)
        widget.border(choice(("light", "heavy", "double", "curved")), sm.color(2))

    for i in range(30):
        for widget in widgets:
            widget.left += round(random())
            widget.top += round(random())
        sm.refresh()
        time.sleep(.2)
