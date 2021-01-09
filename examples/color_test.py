from itertools import cycle

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

    rainbow = cycle(colors.rainbow_gradient(20))  # Create a rainbow gradient with 20 colors
    purp_to_teal = cycle(colors.gradient(20, (103, 15, 215), (17, 163, 112), "purple_to_teal"))

    def update():
        widget.colors[:, :5] = next(rainbow)
        widget.colors[:, 5:] = next(purp_to_teal)
        widget.push()
        sm.root.refresh()

    sm.schedule(update, delay=.1)
    sm.run()

print(colors)