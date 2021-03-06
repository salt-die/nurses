from random import random, choice
from nurses import ScreenManager, colors

with ScreenManager() as sm:
    colors.PURPLE = 103, 15, 215  # Define a new color

    for i in range(5):
        widget = sm.root.new_widget(i * 5, 0, 4, 15, create_with="ArrayWin", group="moving", border_style="light", border_color=colors.PURPLE_ON_BLACK)
        widget.colors[0] = colors.RED_ON_BLACK
        widget[:] = "Hello, World!\nI'm a widget!"

    resize_widget = sm.root.new_widget(9, 40, 12, 18, create_with="ArrayWin", color=colors.BLACK_ON_YELLOW, border_style="curved", border_color=colors.RED_ON_BLACK)
    resize_widget.colors[:, ::2] = colors.YELLOW_ON_BLACK
    resize_widget[:] = "Resize me!"

    scroll_widget = sm.root.new_widget(9, 60, 18, 12, create_with="ArrayWin", border_style="double", border_color=colors.CYAN_ON_BLACK)
    scroll_widget[:] = "Scroll me!"
    scroll_widget.color = colors.BLUE_ON_BLACK

    def random_walk():
        for widget in sm.root.group["moving"]:
            widget.left += round(random())
            widget.top += round(random())
        sm.root.pull_to_front(choice(sm.root.group["moving"]))

    def resize():
        resize_widget.width -= 1

    async def scroll():
        async for i in sm.aiter(range(15), delay=1):
            scroll_widget.scroll()
            scroll_widget[-1] = f"New Text{i:02}"

    sm.schedule(random_walk, delay=.5, n=30)
    for widget in sm.root.group["moving"]:
        sm.schedule(widget.roll, delay=.1, n=150)
    sm.schedule(resize, delay=1, n=15)
    sm.schedule(sm.root.refresh, delay=.1, n=150)
    sm.run(scroll())
