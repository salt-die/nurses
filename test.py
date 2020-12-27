from random import random, choice

from nurses import ScreenManager

sm = ScreenManager()

async def random_walk():
    for _ in range(30):
        for widget in sm.widgets:
            widget.left += round(random())
            widget.top += round(random())
        sm.top(choice(sm.widgets))  # Randomly place a widget on top
        sm.refresh()
        await sm.sleep(.5)

async def roll():
    for _ in range(150):
        for widget in sm.widgets:
            widget.roll(roll_border=False)
        sm.refresh()
        await sm.sleep(.1)

# Define a new color
sm.colors.PURPLE = 103, 15, 215
# Create some widgets
for i in range(5):
    widget = sm.new_widget(i * 5, 0, 4, 15)
    widget.border(color=sm.colors.PURPLE_ON_BLACK)
    widget[1:-1, 1:-1] = "Hello, World!\nI'm a widget!"
    widget.colors[1, 1: -1] = sm.colors.RED_ON_BLACK

sm.run_soon(random_walk())
sm.run_soon(roll())
sm.run()


async def resize():
    sm.widgets.clear()
    widget = sm.new_widget(10, 10, 10, 10)
    widget[:] = "Resize me!"
    widget.colors[::2, ::2] = sm.colors.YELLOW_ON_BLACK
    widget.colors[1::2, 1::2] = sm.colors.BLACK_ON_YELLOW
    for _ in range(9):
        widget.height -= 1
        sm.refresh()
        await sm.sleep(.3)

sm.run_soon(resize())
sm.run()

sm.close()