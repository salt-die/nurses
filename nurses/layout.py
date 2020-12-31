from .screen_manager import ScreenManager, _convert


# TODO: Add minimum size arguments to layouts (needs to be added to build string grammar as well)
class Layout:
    layouts = {}

    def __init_subclass__(cls):
        Layout.layouts[cls.__name__] = cls  # Register layouts
        cls.update.__doc__ = Layout.update.__doc__

    def __init__(self):
        self.top = self.left = 0
        self.height, self.width = ScreenManager().screen.getmaxyx()

    def update(self):
        """Set the widths/heights of sublayouts/contained widgets and call update on sublayouts."""
        raise NotImplementedError


# One can exploit a symmetry in the update functions of HSplit and VSplit to write a single function
# for both, but the function becomes much harder to read with setattr everywhere.  I prefer this:
class HSplit(Layout):
    def __init__(self, row):
        super().__init__()
        self.row = row
        self.panels = [None, None]

    def update(self):
        row = _convert(self.row, self.height)

        for i, item in enumerate(self.panels):
            if not item:
                continue

            item.width = self.width
            item.left = self.left

            if i == 0:
                item.height = row
                item.top = self.top
            else:
                item.height = self.height - row
                item.top = self.top + row

            if isinstance(item, Layout):
                item.update()


class VSplit(Layout):
    def __init__(self, col):
        super().__init__()
        self.col = col
        self.panels = [None, None]

    def update(self):
        col = _convert(self.col, self.width)

        for i, item in enumerate(self.panels):
            if not item:
                continue

            item.height = self.height
            item.top = self.top

            if i == 0:
                item.width = col
                item.left = self.left
            else:
                item.width = self.width - col
                item.left = self.left + col

            if isinstance(item, Layout):
                item.update()
