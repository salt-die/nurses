from nurses import ScreenManager, colors, load_string

with ScreenManager() as sm:
    widgets = load_string("""
    Grid(2, 2)
        Stack()
            ArrayWin(border="light") as tl_top
            ArrayWin(border="light") as tl_bottom
        Stack(vertical=False)
            ArrayWin(border="light") as tr_left
            ArrayWin(border="light") as tr_right
        AnalogClock()
        AnalogClock()
    """)

    for i, widget in enumerate(widgets.values(), start=1):
        widget[0, :10] = "Testing..."
        sm.schedule(widget.roll, delay=i / 10, n=100 // i)

    sm.schedule(sm.root.refresh, delay=.1, n=100)
    sm.run()
