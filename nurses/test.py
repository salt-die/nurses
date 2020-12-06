import curses
import time
import screen

S = screen.run()
my_widget = S.new_widget((5, 5), 15, 3)

my_widget[1:14, 1] = "Hello, World!"
my_widget.colors[5:-5, 1] = curses.color_pair(3)
my_widget.border("curved", curses.color_pair(2))

for i in range(30):
    my_widget.ul = i, i
    my_widget.refresh()
    time.sleep(.5)