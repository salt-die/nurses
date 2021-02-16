from ... import UP, DOWN, LEFT, RIGHT, UP_2, DOWN_2, LEFT_2, RIGHT_2


class Resizable:
    shrink_vertical = UP
    shrink_vertical_alt = UP_2
    expand_vertical = DOWN
    expand_vertical_alt = DOWN_2
    shrink_horizontal = LEFT
    shrink_horizontal_alt = LEFT_2
    expand_horizontal = RIGHT
    expand_horizontal_alt = RIGHT_2

    def on_press(self, key):
        if key == self.shrink_vertical or key == self.shrink_vertical_alt:
            self.height -= 1
        elif key == self.expand_vertical or key == self.expand_vertical_alt:
            self.height += 1
        elif key == self.shrink_horizontal or key == self.shrink_horizontal_alt:
            self.width -= 1
        elif key == self.expand_horizontal or key == self.expand_horizontal_alt:
            self.width += 1
        else:
            return super().on_press(key)

        return True