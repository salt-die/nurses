from nurses import ScreenManager, load_string

with ScreenManager() as sm:
    # Define a widget layout with a toml-like string
    # load_string will return a dictionary of the widgets, names taken from the string
    widgets = load_string("""
    HSplit 3
        title
        HSplit -3
            VSplit .5
                left
                right
            bottom
    """)

    title = widgets["title"]
    title.border("curved", sm.colors.CYAN_ON_BLACK)
    title[0, :5] = "Title"
    title.colors[:] = sm.colors.YELLOW_ON_BLACK

    left = widgets["left"]
    left.border("heavy", sm.colors.GREEN_ON_BLACK)

    right = widgets["right"]
    right.border("double", sm.colors.MAGENTA_ON_BLACK)

    bottom = widgets["bottom"]
    bottom.border("light", sm.colors.GREEN_ON_BLACK)

    async def roll_title():
        async for _ in sm.delayed(range(100), .1):
            title.roll()

    async def scroll_up():
        async for i in sm.delayed(range(50), .2):
            left.scroll()
            left.colors[-1] = sm.colors.RED_ON_BLACK
            left[-1, :12] = f"Scroll up {i:02}"

    async def scroll_down():
        async for i in sm.delayed(range(33), .3):
            right.roll(-1, vertical=True)
            right.colors[0] = sm.colors.BLUE_ON_BLACK
            right[0, :14] = f"Scroll down {i:02}"

    sm.run(roll_title(), scroll_up(), scroll_down())
