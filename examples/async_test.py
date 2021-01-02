from random import random, choice
from nurses import ScreenManager

with ScreenManager() as sm:
    sm.colors.PURPLE = 103, 15, 215  # Define a new color

    for i in range(5):
        widget = sm.new_widget(i * 5, 0, 4, 15, group="moving", border="light", border_color=sm.colors.PURPLE_ON_BLACK)
        widget.colors[0] = sm.colors.RED_ON_BLACK
        widget[:] = "Hello, World!\nI'm a widget!"

    resize_widget = sm.new_widget(9, 40, 12, 18, sm.colors.BLACK_ON_YELLOW, border="curved", border_color=sm.colors.RED_ON_BLACK)
    resize_widget.colors[:, ::2] = sm.colors.YELLOW_ON_BLACK
    resize_widget[:] = "Resize me!"

    scroll_widget = sm.new_widget(9, 60, 18, 12, border="double", border_color=sm.colors.CYAN_ON_BLACK)
    scroll_widget[:] = "Scroll me!"
    scroll_widget.color = sm.colors.BLUE_ON_BLACK

    def random_walk():
        for widget in sm.group("moving"):
            widget.left += round(random())
            widget.top += round(random())
        sm.top(choice(sm.group("moving")))

    def resize():
        resize_widget.width -= 1

    async def scroll():
        async for i in sm.delayed(range(15), 1):
            scroll_widget.scroll()
            scroll_widget[-1] = f"New Text{i:02}"

    sm.schedule(random_walk, delay=.5, n=30)
    for widget in sm.group("moving"):
        sm.schedule(widget.roll, delay=.1, n=150)
    sm.schedule(resize, delay=1, n=15)
    sm.schedule(sm.refresh, delay=.1, n=150)
    sm.run(scroll())
