from nurses import ScreenManager, load_string

with ScreenManager() as sm:
    widgets = load_string("""
    HSplit 3
        title
        VSplit .5
            left
            right
    """)

    async def roll_title():
        title = widgets["title"]
        title.border("curved", sm.colors.CYAN_ON_BLACK)
        title[0, :5] = "Title"
        title.colors[:] = sm.colors.YELLOW_ON_BLACK
        for _ in range(100):
            title.roll()
            sm.refresh()
            await sm.sleep(.1)

    async def scroll_up():
        left = widgets["left"]
        left.border("heavy", sm.colors.GREEN_ON_BLACK)
        for i in range(50):
            left.scroll()
            left.colors[-1] = sm.colors.RED_ON_BLACK
            left[-1, :12] = f"Scroll up {i:02}"
            sm.refresh()
            await sm.sleep(.2)

    async def scroll_down():
        right = widgets["right"]
        right.border("double", sm.colors.MAGENTA_ON_BLACK)
        for i in range(33):
            right.roll(-1, vertical=True)
            right.colors[0] = sm.colors.BLUE_ON_BLACK
            right[0, :14] = f"Scroll down {i:02}"
            sm.refresh()
            await sm.sleep(.3)

    sm.run(roll_title(), scroll_up(), scroll_down())
