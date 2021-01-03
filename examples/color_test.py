from math import sin, pi
import time
from nurses import ScreenManager

with ScreenManager() as sm:
    # Define some new colors:
    sm.colors.PURPLE = 103, 15, 215
    sm.colors.FUCHSIA = 181, 52, 78
    sm.colors.ORANGE = 224, 132, 33
    sm.colors.TEAL = 17, 163, 112

    widget = sm.new_widget(10, 10, 10, 11)
    widget.colors[0::4] = sm.colors.PURPLE_ON_BLACK
    widget.colors[1::4] = sm.colors.FUCHSIA_ON_YELLOW
    widget.colors[2::4] = sm.colors.ORANGE_ON_PURPLE
    widget.colors[3::4] = sm.colors.TEAL_ON_WHITE
    widget[:] = "Color Test!"

    sm.refresh()
    sm.pause()

    COLORS = 20
    def rainbow_rgbs(n=COLORS):
        offsets = 0, 2 * pi / 3, 4 * pi / 3
        for i in range(n):
            yield tuple(int(sin(2 * pi / n * i + offset) * 127 + 128) for offset in offsets)

    for rgb in rainbow_rgbs():
        sm.colors.pair(rgb, (0, 0, 0), palette="rainbow")

    async def rainbow():
        async for i in sm.delayed(range(200), .1):
            widget.colors[:] = sm.colors.palette["rainbow"][i % COLORS]
            widget.refresh()
            sm.refresh()

    sm.run(rainbow())