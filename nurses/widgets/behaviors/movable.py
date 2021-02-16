from ... import UP, DOWN, LEFT, RIGHT, UP_2, DOWN_2, LEFT_2, RIGHT_2


class Movable:
    move_up = UP
    move_up_alt = UP_2
    move_down = DOWN
    move_down_alt = DOWN_2
    move_left = LEFT
    move_left_alt = LEFT_2
    move_right = RIGHT
    move_right_alt = RIGHT_2

    lr_step = 1
    ud_step = 1

    wrap_height = None
    wrap_width = None

    bounded = False

    def on_press(self, key):
        top, left = self.top, self.left
        height, width = self.height, self.width
        bounded = self.bounded

        if key == self.move_up or key == self.move_up_alt:
            if not bounded or top > 0:
                self.top -= self.ud_step
        elif key == self.move_down or key == self.move_down_alt:
            if not bounded or top + height < self.parent.height:
                self.top += self.ud_step
        elif key == self.move_left or key == self.move_left_alt:
            if not bounded or left > 0:
                self.left -= self.lr_step
        elif key == self.move_right or key == self.move_right_alt:
            if not bounded or left + width < self.parent.width:
                self.left += self.lr_step
        else:
            return super().on_press(key)

        if self.wrap_height:
            self.top %= self.wrap_height
        if self.wrap_width:
            self.left %= self.wrap_width
        return True