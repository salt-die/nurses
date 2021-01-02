from abc import ABC, abstractmethod

from .screen_manager import ScreenManager, _convert


class Layout(ABC):
    """
    Layouts are used to assign position and dimensions of contained widgets/sub-layouts.

    Once all widgets and sub-layouts have been added to `children` (and children's children),
    call `update` on the root layout to assign dimensions and positions to all children.
    """
    layouts = { }  # Registry of subclasses of Layout

    def __init_subclass__(cls):
        Layout.layouts[cls.__name__] = cls
        if not cls.update.__doc__:
            cls.update.__doc__ = Layout.update.__doc__

    def __init__(self):
        self.top = self.left = 0
        self.height, self.width = ScreenManager().screen.getmaxyx()

    @abstractmethod
    def update(self):
        """Set the positions and dimensions of sub-layouts and contained widgets, and call `update` on sub-layouts.
        """


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
        self.children = [None, None]

    def update(self):
        row = _convert(self.row, self.height)
        min_height = _convert(self.min_height, self.height)
        if row < min_height:
            row = min_height
        elif self.height - row < min_height:
            row = self.height - min_height

        for i, child in enumerate(self.children):
            if not child:
                continue

            child.width = self.width
            child.left = self.left

            if i == 0:
                child.height = row
                child.top = self.top
            else:
                child.height = self.height - row
                child.top = self.top + row

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
        self.children = [None, None]

    def update(self):
        col = _convert(self.col, self.width)
        min_width = _convert(self.min_width, self.width)
        if col < min_width:
            col = min_width
        elif self.width - col < min_width:
            col = self.width - min_width

        for i, child in enumerate(self.children):
            if not child:
                continue

            child.height = self.height
            child.top = self.top

            if i == 0:
                child.width = col
                child.left = self.left
            else:
                child.width = self.width - col
                child.left = self.left + col

            if isinstance(child, Layout):
                child.update()
