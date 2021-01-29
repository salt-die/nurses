from itertools import cycle

from nurses import ScreenManager, colors

with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient(20))
    blue_to_yellow = colors.gradient(20, (0, 0, 255), (0, 255, 255), "blue_to_yellow")
    blue_to_yellow += blue_to_yellow[::-1]
    blue_to_yellow = cycle(blue_to_yellow)

    big_clock = sm.root.new_widget(0, 0, boundary=False, create_with="AnalogClock")

    small_clock = sm.root.new_widget(18, 15,  transparent=True, pos_hint=(-8, None), create_with="DigitalClock")
    small_clock.getter("left", lambda: big_clock.height - small_clock.width // 2 - 1)

    def update_color():
        big_clock.update_color(next(blue_to_yellow))
        small_clock.update_color(next(rainbow))

    sm.schedule(sm.root.refresh)
    sm.schedule(update_color, delay=.1)
    sm.run()
