from nurses import ScreenManager

sm = ScreenManager()

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
widget[:] = "\n".join("Color Test!" for _ in range(HEIGHT))

async def roll_and_scroll():
    for _ in range(WIDTH):
        sm.refresh()
        widget.roll()
        await sm.sleep(.2)

    for _ in range(HEIGHT):
        sm.refresh()
        widget.scroll()
        await sm.sleep(.2)

sm.run_soon(roll_and_scroll())
sm.run()
sm.close()
