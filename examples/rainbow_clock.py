from nurses import colors, ScreenManager

from nurses.widgets.behaviors import Movable
from nurses.widgets import DigitalClock


class MovableClock(DigitalClock, Movable):
    ...

with ScreenManager() as sm:
    sm.root.add_widget(MovableClock(0, 0))

    colors.rainbow_gradient(20)

    async def rainbow_time():
        i = 0
        while True:
            sm.root.children[0].update_color(colors.palette["rainbow"][i])
            i = (i + 1) % 20
            sm.root.refresh()
            await sm.sleep(.1)

    sm.run(rainbow_time())
