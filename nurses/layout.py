from .screen_manager import ScreenManager

# TODO: Add minimum size arguments to layouts
class Layout:
    def __init__(self):
        self.panels = [None, None]
        self.top = self.left = 0
        self.height, self.width = ScreenManager().screen.getmaxyx()


class HSplit(Layout):
    def __init__(self, row):
        super().__init__()
        self._row = row

    def update(self):
        row = self._row
        if isinstance(row, float):
            if row < 0:
                row += 1
            row = round(row * self.height)
        elif row < 0:
            row += self.height

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
        self._col = col

    def update(self):
        col = self._col
        if isinstance(col, float):
            if col < 0:
                col += 1
            col = round(col * self.width)
        elif col < 0:
            col += self.width

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
