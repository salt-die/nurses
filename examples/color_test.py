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
    widget.colors[2::4] = sm.colors.ORANGE_ON_GREEN
    widget.colors[3::4] = sm.colors.TEAL_ON_WHITE
    widget[:] = "Color Test!"

    sm.refresh()
    sm.pause()

    sm.colors.PURPLE = 255, 50, 100 # Note that `sm.colors.redefine_color(sm.colors.rgb.PURPLE, (255, 50, 100))` is similar,
                                    # but doesn't redefine the alias so that new color pairs using PURPLE would still use the old value `(103, 15, 215)`.
    sm.pause()

    rgb = sm.colors.rgb
    sm.colors.redefine_color_pair(rgb.ORANGE_ON_GREEN, rgb.TEAL_ON_BLACK)  # The first color pair must exist.
    sm.refresh()
    sm.pause()
