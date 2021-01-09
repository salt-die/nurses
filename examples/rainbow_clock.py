from nurses import colors, ScreenManager

from nurses.widgets.behaviors import Movable
from nurses.widgets import DigitalClock


class MovableClock(DigitalClock, Movable):
    ...


with ScreenManager() as sm:
    widget = sm.root.new_widget(0, 0, create_with=MovableClock)

    rainbow = colors.rainbow_gradient(20)

    async def rainbow_time():
        i = 0
        while True:
            widget.update_color(rainbow[i])
            i = (i + 1) % 20
            sm.root.refresh()
            await sm.sleep(.1)

    sm.run(rainbow_time())
