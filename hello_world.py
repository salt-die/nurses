from nurses import ScreenManager

with ScreenManager() as sm:
    sm.colors.PURPLE = 103, 15, 215

    async def hello():
        widget = sm.new_widget(5, 5, 3, 15, sm.colors.GREEN_ON_BLACK)
        widget.border("curved", sm.colors.PURPLE_ON_BLACK)
        widget[:] = "Hello, World!"

        for _ in range(60):
            widget.roll()
            sm.refresh()
            await sm.sleep(.2)

    async def scroll_border():
        # Here we demonstrate how to use numpy indexing to simplify animating text marching around a border.
        widget = sm.new_widget(5, 25, 3, 15, sm.colors.YELLOW_ON_BLACK)
        widget[0, :13] = "Hello, World!"

        for _ in range(120):
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
            widget.refresh()
            sm.refresh()
            await sm.sleep(.1)

    sm.run(hello(), scroll_border())
