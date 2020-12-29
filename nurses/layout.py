from .screen_manager import ScreenManager


class LayoutBase:
    def __init__(self):
        self.panels = [None, None]
        self.top = 0
        self.left = 0
        self.height, self.width = ScreenManager().screen.getmaxyx()

    def __getitem__(self, key):
        return self.panels[key]

    @property
    def top(self):
        return self._top

    @top.setter
    def top(self, value):
        self._top = value
        self.reset()

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value
        self.reset()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.reset()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self.reset()

    def reset(self):
        for i, item in enumerate(self.panels):
            if item:
                self[i] = item


class HSplit(LayoutBase):
    def __init__(self, row):
        super().__init__()
        self.row = round(row * self.height) if isinstance(row, float) else row

    def __setitem__(self, key, item):
        self.panels[key] = item
        item.width = self.width
        item.left = self.left

        if key == 0:
            item.height = self.row
            item.top = self.top
        elif key == 1:
            item.height = self.height - self.row
            item.top = self.top + self.row


class VSplit(LayoutBase):
    def __init__(self, col):
        super().__init__()
        self.col = round(col * self.width) if isinstance(col, float) else col

    def __setitem__(self, key, item):
        self.panels[key] = item
        item.height = self.height
        item.top = self.top

        if key == 0:
            item.width = self.col
            item.left = self.left
        elif key == 1:
            item.width = self.width - self.col
            item.left = self.left + self.col
