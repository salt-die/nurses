from itertools import cycle

from nurses import ScreenManager, colors
from nurses.widgets import Textbox
from nurses.widgets.behaviors import Bouncing


class BouncingTextbox(Bouncing, Textbox):
    def refresh(self):
        self.border(style="curved", color=next(rainbow))
        self.window.addstr(0, 1, "Input:")
        super().refresh()


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient())

    tb = sm.root.new_widget(0, 0, 20, border="curved", create_with=BouncingTextbox)
    tb.schedule_bounce()

    refresh_task = sm.schedule(sm.root.refresh, delay=.1)

    async def print_result():
        print(await tb.gather())
        tb.bounce.cancel()
        refresh_task.cancel()

    sm.run(print_result())
