from nurses import ScreenManager, load_string

with ScreenManager() as sm:
    # Define a widget layout with a TAML-like string
    # load_string will return a dictionary of named widgets
    widgets = load_string("""
    HSplit(3)
        # valid python creates widget, `as NAME` will name the widget
        # `sm` refers to ScreenManager()
        sm.new_widget(color=sm.colors.YELLOW_ON_BLACK, border="curved", border_color=sm.colors.CYAN_ON_BLACK) as title
        HSplit(-3)
            VSplit(.5)
                # can just use `new_widget` without the preceding "sm."
                new_widget(color=sm.colors.RED_ON_BLACK, border="heavy", border_color=sm.colors.GREEN_ON_BLACK) as left
                right  # can create a default widget with just a name
            # names aren't necessary, widgets will be omitted from the returned dictionary
            new_widget(border="light", border_color=sm.colors.GREEN_ON_BLACK)
    """)
    globals().update(widgets)  # add widgets to this namespace
    right.colors[:] = right.color = sm.colors.BLUE_ON_BLACK
    right.border("double", sm.colors.MAGENTA_ON_BLACK)

    async def roll_title():
        title[0, :5] = "Title"
        async for _ in sm.delayed(range(100), .1):
            title.roll()

    async def scroll_up():
        async for i in sm.delayed(range(50), .2):
            left.scroll()
            left[-1, :12] = f"Scroll up {i:02}"

    async def scroll_down():
        async for i in sm.delayed(range(33), .3):
            right.scroll(-1)
            right[0, :14] = f"Scroll down {i:02}"

    sm.run(roll_title(), scroll_up(), scroll_down())
