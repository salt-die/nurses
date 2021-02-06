from nurses import ScreenManager, load_string

with ScreenManager() as sm:
    widgets = load_string("""
    Grid(2, 2)
        Stack()
            ArrayWin(border_style="light") as a
            ArrayWin(border_style="light") as b
        Stack(vertical=False)
            ArrayWin(border_style="light") as c
            ArrayWin(border_style="light") as d
        AnalogClock()
        AnalogClock()
    """)

    for i, widget in enumerate(widgets.values(), start=1):
        widget[0, :10] = "Testing..."
        sm.schedule(widget.roll, delay=i / 10, n=100 // i)

    sm.schedule(sm.root.refresh, delay=.1, n=100)
    sm.run()
