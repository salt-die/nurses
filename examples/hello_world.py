from nurses import ScreenManager, colors

with ScreenManager() as sm:
    widget = sm.root.new_widget(5, 25, 3, 15, color=colors.YELLOW_ON_BLACK, create_with="ArrayWin")
    widget[0, :13] = "Hello, World!"

    # Here we demonstrate how to use numpy indexing to simplify animating text marching around a border.
    def marching_border():
        # Move each edge clockwise then place the 3 values that got overwritten.
        tr, bl, br = widget[0, -1], widget[-1, 0], widget[-1, -1]
        b = widget.buffer
        b[0, 1:] = widget[0, :-1]
        b[1:, -1] = widget[:-1, -1]
        b[-1, :-1] = widget[-1, 1:]
        b[:-1, 0] = widget[1:, 0]
        b[ 1, -1] = tr
        b[-1, -2] = br
        b[-2,  0] = bl
        widget.push()
        sm.root.refresh()

    sm.schedule(marching_border, delay=.1, n=120)
    sm.run()
