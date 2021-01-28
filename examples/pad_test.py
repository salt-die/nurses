from nurses import ScreenManager, colors
from nurses.widgets import ArrayPad
from nurses.widgets.behaviors import Scrollable

class ScrollingPad(ArrayPad, Scrollable):
    ...

with ScreenManager() as sm:
    blue_to_white = colors.gradient(200, (0, 0, 255), (255, 255, 255), "blue_to_white")

    scroll_pad = sm.root.new_widget(create_with=ScrollingPad, rows=200, cols=200, size_hint=(1.0, 1.0))

    for i in range(200):
        scroll_pad[i, :] = f'{f"{i:03}":>10}' * 20
        scroll_pad.pad_colors[i] = blue_to_white[i]

    sm.schedule(sm.root.refresh)
    sm.run()
