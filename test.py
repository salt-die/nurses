from random import random, choice
import time

from nurses import ScreenManager as sm


DELAY = .2
def delayed(iter, delay=DELAY):
    for i in iter:
        sm.refresh()
        yield i
        time.sleep(delay)

def reset_sm_after(f):
    def wrapper():
        f()
        sm.erase()
        sm.widgets.clear()
    return wrapper

@reset_sm_after
def move_test():
    for i in range(5):
        widget = sm.new_widget(5 * i, 0, 4, 15)
        widget[1:-1, 1:-1] = "Hello, World!\nI'm a widget!"
        widget.colors[1:3, 5:-5] = sm.color(3)
        widget.border(choice(("light", "heavy", "double", "curved")), sm.color(2))

    for _ in delayed(range(30)):
        for widget in sm.widgets:
            widget.left += round(random())
            widget.top += round(random())

@reset_sm_after
def resize_test():
    wid = sm.new_widget(12, 12, 13, 12, default_color=sm.color(2))
    for i in delayed(range(10, 0, -1)):
        wid.height -= 1
        wid[1:-1, 1:-1] = "\n".join("Resize me!" for _ in range(i))
        wid.border(color=sm.color(3))

@reset_sm_after
def roll_test():
    wid = sm.new_widget(10, 30, 1, 11)
    wid[:] = "Rolling! :)"
    for _ in delayed(range(30)):
        wid.roll(vertical=False)

@reset_sm_after
def scroll_test():
    wid = sm.new_widget(10, 30, 10, 12)
    wid[:] = "\n".join("Scroll Test!" for _ in range(10))
    wid.colors[::2] = sm.color(2)
    wid.refresh()
    for _ in delayed(range(10)):
        wid.scroll()

move_test()
resize_test()
roll_test()
scroll_test()

sm.close()  # Alternatively, using ScreenManager as a context manager will call this method automatically.