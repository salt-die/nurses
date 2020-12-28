from random import random, choice
from nurses import ScreenManager

sm = ScreenManager()

async def random_walk():
    for _ in range(30):
        for widget in sm.group("moving"):
            widget.left += round(random())
            widget.top += round(random())
        sm.top(choice(sm.group("moving")))  # Randomly place a widget on top
        sm.refresh()
        await sm.sleep(.5)

async def roll():
    for _ in range(150):
        for widget in sm.group("moving"):
            widget.roll()
        sm.refresh()
        await sm.sleep(.1)

async def resize():
    for _ in range(15):
        resize_widget.width -= 1
        sm.refresh()
        await sm.sleep(1)

async def scroll():
    for i in range(15):
        scroll_widget.scroll()
        scroll_widget.colors[-1] = sm.colors.BLUE_ON_BLACK
        scroll_widget[-1] = f"New Text{i:02}"
        sm.refresh()
        await sm.sleep(1)

# Define a new color
sm.colors.PURPLE = 103, 15, 215
# Create some widgets
for i in range(5):
    widget = sm.new_widget(i * 5, 0, 4, 15, group="moving")
    widget.border(color=sm.colors.PURPLE_ON_BLACK)
    widget[:] = "Hello, World!\nI'm a widget!"
    widget.colors[0] = sm.colors.RED_ON_BLACK

resize_widget = sm.new_widget(9, 40, 12, 18, default_color=sm.colors.YELLOW_ON_BLACK)
resize_widget.border("curved", sm.colors.RED_ON_BLACK)
resize_widget[:] = "Resize me!"
resize_widget.colors[:, ::2] = sm.colors.BLACK_ON_YELLOW

scroll_widget = sm.new_widget(9, 60, 18, 12)
scroll_widget.border("double", sm.colors.CYAN_ON_BLACK)
scroll_widget[:] = "Scroll me!"

with sm:  # alternatively, manually close with sm.close()
    sm.run_soon(random_walk(), roll(), resize(), scroll())
    sm.run()
