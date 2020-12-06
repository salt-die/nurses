import time
from nurses import ScreenManager

with ScreenManager() as sm:
    my_widget = sm.new_widget((5, 5), 15, 3)
    my_widget[1:14, 1] = "Hello, World!"
    my_widget.colors[5:-5, 1] = sm.color(3)
    my_widget.border("curved", sm.color(2))

    for i in range(30):
        my_widget.ul = i, i
        my_widget.refresh()
        time.sleep(.2)