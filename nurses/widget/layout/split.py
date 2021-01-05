from . import Layout

# One can exploit a symmetry in the update functions of HSplit and VSplit to write a single function
# for both, but it's less readable.  We've chosen the more verbose option:
class HSplit(Layout):
    """
    Split the screen horizontally at `row` from top or bottom of the screen (depending on the sign of `row`).
    If `row` is a float, it's taken to be percentage of the screen (i.e., HSplit(.33) will split the screen
    33% of the distance from top to bottom).

    No (direct) child's height will be less than `min_height` (default is 1, should be positive).
    """
    def __init__(self, row, min_height=1):
        super().__init__()
        self.row = row
        self.min_height = min_height

    def update(self):
        row = self.convert(self.row, self.height)
        min_height = self.convert(self.min_height, self.height)
        if row < min_height:
            row = min_height
        elif self.height - row < min_height:
            row = self.height - min_height

        for i, child in enumerate(self.children):
            if not child:
                continue

            child.width = self.width
            child.left = 0

            if i == 0:
                child.height = row
                child.top = 0
            else:
                child.height = self.height - row
                child.top = row

            if isinstance(child, Layout):
                child.update()


class VSplit(Layout):
    """
    Split the screen vertically at `col` from left or right of the screen (depending on the sign of `col`).
    If `col` is a float, it's taken to be percentage of the screen (i.e., VSplit(.33) will split the screen
    33% of the distance from left to right).

    No (direct) child's width will be less than `min_width` (default is 1, should be positive).
    """
    def __init__(self, col, min_width=1):
        super().__init__()
        self.col = col
        self.min_width = min_width

    def update(self):
        col = self.convert(self.col, self.width)
        min_width = self.convert(self.min_width, self.width)
        if col < min_width:
            col = min_width
        elif self.width - col < min_width:
            col = self.width - min_width

        for i, child in enumerate(self.children):
            if not child:
                continue

            child.height = self.height
            child.top = 0

            if i == 0:
                child.width = col
                child.left = 0
            else:
                child.width = self.width - col
                child.left = col

            if isinstance(child, Layout):
                child.update()
