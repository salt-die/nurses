from nurses import ScreenManager

with ScreenManager() as sm:
    # Define some new colors:
    sm.colors.PURPLE = 103, 15, 215
    sm.colors.FUCHSIA = 181, 52, 78
    sm.colors.ORANGE = 224, 132, 33
    sm.colors.TEAL = 17, 163, 112

    HEIGHT, WIDTH = 10, 11
    widget = sm.new_widget(10, 10, HEIGHT, WIDTH)
    widget.colors[0::4] = sm.colors.PURPLE_ON_BLACK
    widget.colors[1::4] = sm.colors.FUCHSIA_ON_YELLOW
    widget.colors[2::4] = sm.colors.ORANGE_ON_GREEN
    widget.colors[3::4] = sm.colors.TEAL_ON_WHITE
    widget[:] = "Color Test!"

    async def roll_and_scroll():
        async for _ in sm.delayed(range(WIDTH), .2):
            widget.roll()

        async for _ in sm.delayed(range(HEIGHT), .2):
            widget.scroll()

    sm.run(roll_and_scroll())
