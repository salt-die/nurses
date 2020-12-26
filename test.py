from random import random, choice

from nurses import ScreenManager

sm = ScreenManager()

async def random_walk():
    for _ in range(30):
        for widget in sm.widgets:
            widget.left += round(random())
            widget.top += round(random())
        sm.refresh()
        await sm.sleep(.5)

async def roll():
    for _ in range(150):
        for widget in sm.widgets:
            widget.roll()
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