from nurses import ScreenManager, colors
from nurses.widgets import ArrayPad
from nurses.widgets.behaviors import Scrollable

class ScrollingPad(ArrayPad, Scrollable):
    ...

with ScreenManager() as sm:
    scroll_pad = sm.root.new_widget(create_with=ScrollingPad, rows=200, cols=200)
    scroll_pad[::2] = "#"
    scroll_pad[:, ::2] = "#"
    scroll_pad.pad_colors[::2] = colors.BLACK_ON_YELLOW
    sm.schedule(sm.root.refresh)
    sm.run()
