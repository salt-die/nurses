from itertools import cycle

from nurses import ScreenManager, colors
from nurses.widgets import Textbox
from nurses.widgets.behaviors import Bouncing


class WalkingTextbox(Bouncing, Textbox):
    ...


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient())
    tb = sm.root.new_widget(0, 0, 20, border="curved", create_with=WalkingTextbox)

    def color_border():
        tb.border(style="curved", color=next(rainbow))

        tb._buffer[0, 1:7] = tuple("Input:")
        tb._colors[0, 1:7] = 0

        sm.root.refresh()

    tb.schedule_bounce()
    color_task = sm.schedule(color_border, delay=.1)

    async def print_result():
        print(await tb.gather())
        tb.bounce.cancel()
        color_task.cancel()

    sm.run(print_result())
