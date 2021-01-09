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

    colors.rainbow_gradient(20)  # Create a rainbow gradient with 20 colors
    colors.gradient(20, (103, 15, 215), (17, 163, 112), "purple to teal")

    async def rainbow():
        async for i in sm.aiter(range(200), delay=.1):
            widget.colors[:, :5] = colors.palette["rainbow"][i % 20]
            widget.colors[:, 5:] = colors.palette["purple to teal"][i % 20]
            widget.push()
            sm.root.refresh()

    sm.run(rainbow())

print(colors)