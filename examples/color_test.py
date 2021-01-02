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

    sm.schedule_callback(widget.roll, delay=.2, n=WIDTH)
    sm.schedule_callback(sm.refresh, delay=.2, n=WIDTH)
    sm.run()
    sm.schedule_callback(widget.scroll, delay=.2, n=HEIGHT)
    sm.schedule_callback(sm.refresh, delay=.2, n=WIDTH)
    sm.run()
