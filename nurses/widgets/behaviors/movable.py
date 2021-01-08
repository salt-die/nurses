class Movable:
    move_up = 259  # Up-arrow
    move_down = 258  # Down-arrow
    move_left = 260  # Left-arrow
    move_right = 261  # Right-arrow

    lr_step = 1
    ud_step = 1

    wrap_height = None
    wrap_width = None

    bounded = False

    def on_press(self, key):
        top, left = self.top, self.left
        height, width = self.height, self.width
        bounded = self.bounded

        if key == self.move_up:
            if not bounded or top > 0:
                self.top -= self.ud_step
        elif key == self.move_down:
            if not bounded or top + height < self.parent.height:
                self.top += self.ud_step
        elif key == self.move_left:
            if not bounded or left > 0:
                self.left -= self.lr_step
        elif key == self.move_right:
            if not bounded or left + width < self.parent.width:
                self.left += self.lr_step
        else:
            return super().on_press(key)

        if self.wrap_height:
            self.top %= self.wrap_height
        if self.wrap_width:
            self.left %= self.wrap_width
        return True