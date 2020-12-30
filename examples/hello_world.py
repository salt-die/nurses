from nurses import ScreenManager

with ScreenManager() as sm:
    async def marching_border():
        # Here we demonstrate how to use numpy indexing to simplify animating text marching around a border.
        widget = sm.new_widget(5, 25, 3, 15, sm.colors.YELLOW_ON_BLACK)
        widget[0, :13] = "Hello, World!"

        async for _ in sm.delayed(range(120), .1):
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

    sm.run(marching_border())
