from ... import UP, DOWN, LEFT, RIGHT, UP_2, DOWN_2, LEFT_2, RIGHT_2


class Scrollable:
    """Warning:: Scrollable behavior for :class: ArrayPad only.
    """
    scroll_up = UP
    scroll_up_alt = UP_2
    scroll_down = DOWN
    scroll_down_alt = DOWN_2
    scroll_left = LEFT
    scroll_left_alt = LEFT_2
    scroll_right = RIGHT
    scroll_right_alt = RIGHT_2

    def on_press(self, key):
        border_width = self.has_border * 2

        if key == self.scroll_up or key == self.scroll_up_alt:
            self.min_row = max(0, self.min_row - 1)
        elif key == self.scroll_down or key == self.scroll_down_alt:
            self.min_row = min(self.rows - (self.height - self.top_scrollbar - self.bottom_scrollbar - border_width), self.min_row + 1)
        elif key == self.scroll_left or key == self.scroll_left_alt:
            self.min_col = max(0, self.min_col - 1)
        elif key == self.scroll_right or key == self.scroll_right_alt:
            self.min_col = min(self.cols - (self.width - self.left_scrollbar - self.right_scrollbar - border_width), self.min_col + 1)
        else:
            return super().on_press(key)

        return True
