class Movable:
    MOVE_UP = 259  # Up-arrow
    MOVE_DOWN = 258  # Down-arrow
    MOVE_LEFT = 260  # Left-arrow
    MOVE_RIGHT = 261  # Right-arrow

    LR_STEP = 1
    UD_STEP = 1

    def __init__(self, *args, bounded=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.bounded = bounded

    def on_press(self, key):
        top, left = self.top, self.left
        height, width = self.height, self.width
        bounded = self.bounded

        if key == self.MOVE_UP:
            if not bounded or top > 0:
                self.top -= self.UD_STEP
        elif key == self.MOVE_DOWN:
            if not bounded or top + height < self.parent.height:
                self.top += self.UD_STEP
        elif key == self.MOVE_LEFT:
            if not bounded or left > 0:
                self.left -= self.LR_STEP
        elif key == self.MOVE_RIGHT:
            if not bounded or left + width < self.parent.width:
                self.left += self.LR_STEP
        else:
            return super().on_press(key)

        return True