import numpy as np

from . import ArrayWin


class Pad(ArrayWin):
    """
    Pads are windows that can be larger than the screen.  They have an extra buffer, `pad`: rectangular slices of `pad`
    will be copied to the buffer and pushed to the screen.
    """

    def __init__(self, *args, rows, cols, **kwargs):
        super().__init__(*args, **kwargs)

        self.rows = rows
        self.cols = cols

        self.pad = np.full((rows, cols), " ")

    """
    Notes for implementation:

    Need to reimplement `__getitem__`, `__setitem__`, `push`

    Some attributes to keep track of which rectangular slice of `pad` we want to see.
    ```