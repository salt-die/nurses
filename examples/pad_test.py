from nurses import ScreenManager, colors
from nurses.widgets import ArrayPad
from nurses.widgets.behaviors import Scrollable

class ScrollingPad(ArrayPad, Scrollable):
    ...

with ScreenManager() as sm:
    scroll_pad = sm.root.new_widget(
        create_with=ScrollingPad, rows=200, cols=200, size_hint=(1.0, 1.0),
        right_scrollbar=True, bottom_scrollbar=True, bar_color=colors.BLUE_ON_WHITE
    )

    for i, color in enumerate(colors.gradient(200, (0, 0, 255), (255, 255, 255), "blue_to_white")):
        scroll_pad[i, :] = f'{f"{i:03}":>10}' * 20
        scroll_pad.pad_colors[i] = color

    sm.schedule(sm.root.refresh)
    sm.run()
