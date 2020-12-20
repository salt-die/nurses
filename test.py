from random import random, choice
import time

from nurses import ScreenManager

sm = ScreenManager()

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
        widget.colors[1:3, 5:-5] = sm.colors.BLUE_ON_BLACK
        widget.border(choice(("light", "heavy", "double", "curved")), sm.colors.RED_ON_BLACK)

    for _ in delayed(range(30)):
        for widget in sm.widgets:
            widget.left += round(random())
            widget.top += round(random())

@reset_sm_after
def resize_test():
    wid = sm.new_widget(12, 12, 13, 12, sm.colors.RED_ON_BLACK)
    for i in delayed(range(10, 0, -1)):
        wid.height -= 1
        wid[1:-1, 1:-1] = "\n".join("Resize me!" for _ in range(i))
        wid.border(color=sm.colors.BLUE_ON_BLACK)

@reset_sm_after
def roll_test():
    wid = sm.new_widget(10, 30, 1, 11, sm.colors.CYAN_ON_YELLOW)
    wid[:] = "Rolling! :)"
    for _ in delayed(range(30)):
        wid.roll()

@reset_sm_after
def scroll_test():
    wid = sm.new_widget(10, 30, 10, 12)
    sm.colors.PURPLE = 103, 15, 215
    wid.colors[::2] = sm.colors.PURPLE_ON_BLACK
    wid[:] = "\n".join("Scroll Test!" for _ in range(10))
    for _ in delayed(range(10)):
        wid.scroll()

with sm:  # Context manager will call sm.close after
    move_test()
    resize_test()
    roll_test()
    scroll_test()