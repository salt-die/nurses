from .screen_manager import ScreenManager, _convert


# TODO: Add minimum size arguments to layouts
class Layout:
    def __init__(self):
        self.panels = [None, None]
        self.top = self.left = 0
        self.height, self.width = ScreenManager().screen.getmaxyx()


class HSplit(Layout):
    def __init__(self, row):
        super().__init__()
        self.row = row

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
            elif i == 1:
                item.height = self.height - row
                item.top = self.top + row

            if isinstance(item, Layout):
                item.update()


class VSplit(Layout):
    def __init__(self, col):
        super().__init__()
        self.col = col

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
            elif i == 1:
                item.width = self.width - col
                item.left = self.left + col

            if isinstance(item, Layout):
                item.update()
