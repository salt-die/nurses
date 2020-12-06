import time
from nurses import ScreenManager
import numpy as np

with ScreenManager() as sm:
    my_widget = sm.new_widget(5, 5, 4, 15)
    my_widget[1:3, 1:14] = "Hello, World!\nI'm a widget!"
    my_widget.colors[1:3, 5:-5] = sm.color(3)
    my_widget.border("curved", sm.color(2))

    for i in range(30):
        my_widget.ul = i, i
        my_widget.buffer = np.roll(my_widget.buffer, (1, 0), (1, 0))  # Applying numpy functions to the buffer for fun effects
        my_widget.refresh()
        time.sleep(.2)
