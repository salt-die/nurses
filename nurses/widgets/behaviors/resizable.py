from ... import UP, DOWN, LEFT, RIGHT


class Resizable:
    shrink_vertical = UP
    expand_vertical = DOWN
    shrink_horizontal = LEFT
    expand_horizontal = RIGHT

    def on_press(self, key):
        if key == self.shrink_vertical:
            self.height -= 1
        elif key == self.expand_vertical:
            self.height += 1
        elif key == self.shrink_horizontal:
            self.width -= 1
        elif key == self.expand_horizontal:
            self.width += 1
        else:
            return super().on_press(key)

        return True