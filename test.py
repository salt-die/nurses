from random import random, choice
import time

from nurses import ScreenManager


with ScreenManager() as sm:
    for i in range(5):
        widget = sm.new_widget(5 * i, 0, 4, 15)
        widget[1:-1, 1:-1] = "Hello, World!\nI'm a widget!"
        widget.colors[1:3, 5:-5] = sm.color(3)
        widget.border(choice(("light", "heavy", "double", "curved")), sm.color(2))

    for i in range(30):
        for widget in sm.widgets:
            widget.left += round(random())
            widget.top += round(random())
        sm.refresh()
        time.sleep(.2)

    sm.erase()
    sm.widgets.clear()

    resize_test = sm.new_widget(12, 12, 12, 12, default_color=sm.color(2))
    for i in range(10, 0, -1):
        resize_test[1:-1, 1:-1] = "\n".join("Resize me!" for _ in range(i))
        resize_test.border(color=sm.color(3))
        sm.refresh()
        time.sleep(.2)
        resize_test.height -= 1
