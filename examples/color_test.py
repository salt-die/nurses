from math import sin, pi

from nurses import ScreenManager, colors

with ScreenManager() as sm:
    # Define some new colors:
    colors.PURPLE = 103, 15, 215
    colors.FUCHSIA = 181, 52, 78
    colors.ORANGE = 224, 132, 33
    colors.TEAL = 17, 163, 112

    widget = sm.root.new_widget(10, 10, 10, 11, create_with="ArrayWin")
    widget.colors[0::4] = colors.PURPLE_ON_BLACK
    widget.colors[1::4] = colors.FUCHSIA_ON_YELLOW
    widget.colors[2::4] = colors.ORANGE_ON_PURPLE
    widget.colors[3::4] = colors.TEAL_ON_WHITE
    widget[:] = "Color Test!"

    sm.root.refresh()
    sm.pause()

    COLORS = 20
    def rainbow_rgbs(n=COLORS):
        offsets = 0, 2 * pi / 3, 4 * pi / 3
        for i in range(n):
            yield tuple(int(sin(2 * pi / n * i + offset) * 127 + 128) for offset in offsets)

    for rgb in rainbow_rgbs():
        colors.pair(rgb, (0, 0, 0), palette="rainbow")

    async def rainbow():
        async for i in sm.aiter(range(200), delay=.1):
            widget.colors[:] = colors.palette["rainbow"][i % COLORS]
            widget.push()
            sm.root.refresh()

    sm.run(rainbow())

print(colors)