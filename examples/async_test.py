from random import random, choice
from nurses import ScreenManager

with ScreenManager() as sm:
    sm.colors.PURPLE = 103, 15, 215  # Define a new color

    for i in range(5):
        widget = sm.new_widget(i * 5, 0, 4, 15, group="moving")
        widget.border(color=sm.colors.PURPLE_ON_BLACK)  # Color pair will be initialized automatically if it doesn't exist.
        widget[:] = "Hello, World!\nI'm a widget!"
        widget.colors[0] = sm.colors.RED_ON_BLACK

    resize_widget = sm.new_widget(9, 40, 12, 18, default_color=sm.colors.YELLOW_ON_BLACK)
    resize_widget.border("curved", sm.colors.RED_ON_BLACK)
    resize_widget[:] = "Resize me!"
    resize_widget.colors[:, ::2] = sm.colors.BLACK_ON_YELLOW

    scroll_widget = sm.new_widget(9, 60, 18, 12)
    scroll_widget.border("double", sm.colors.CYAN_ON_BLACK)
    scroll_widget[:] = "Scroll me!"

    async def random_walk():
        async for _ in sm.delayed(range(30), .5):
            for widget in sm.group("moving"):
                widget.left += round(random())
                widget.top += round(random())
            sm.top(choice(sm.group("moving")))

    async def roll():
        async for _ in sm.delayed(range(150), .1):
            for widget in sm.group("moving"):
                widget.roll()

    async def resize():
        async for _ in sm.delayed(range(15), 1):
            resize_widget.width -= 1

    async def scroll():
        async for i in sm.delayed(range(15), 1):
            scroll_widget.scroll()
            scroll_widget.colors[-1] = sm.colors.BLUE_ON_BLACK
            scroll_widget[-1] = f"New Text{i:02}"

    sm.run(random_walk(), roll(), resize(), scroll())
