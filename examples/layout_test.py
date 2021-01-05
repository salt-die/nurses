from nurses import ScreenManager, load_string

with ScreenManager() as sm:
    # Define a widget layout with a TAML-like string
    # load_string will return a dictionary of named widgets
    widgets = load_string("""
    HSplit(3) as top
        ArrayWin(color=sm.colors.YELLOW_ON_BLACK, border="curved", border_color=sm.colors.CYAN_ON_BLACK) as title
        HSplit(-3)
            VSplit(.5)
                ArrayWin(color=sm.colors.RED_ON_BLACK, border="heavy", border_color=sm.colors.GREEN_ON_BLACK) as left
                ArrayWin() as right
            ArrayWin(border="light", border_color=sm.colors.GREEN_ON_BLACK)
    """)
    globals().update(widgets)
    sm.root.add_widget(top)

    title[0, :5] = "Title"

    right.colors[:] = right.color = sm.colors.BLUE_ON_BLACK
    right.border("double", sm.colors.MAGENTA_ON_BLACK)

    async def scroll_up():
        async for i in sm.aiter(range(50), delay=.2):
            left.scroll()
            left[-1, :12] = f"Scroll up {i:02}"

    async def scroll_down():
        async for i in sm.aiter(range(33), delay=.3):
            right.scroll(-1)
            right[0, :14] = f"Scroll down {i:02}"

    sm.schedule(sm.root.refresh, delay=.1, n=100)
    sm.schedule(title.roll, delay=.1, n=100)
    sm.run(scroll_up(), scroll_down())
