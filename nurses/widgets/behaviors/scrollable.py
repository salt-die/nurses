from ... import UP, DOWN, LEFT, RIGHT, UP_2, DOWN_2, LEFT_2, RIGHT_2, PGUP, PGDN


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
    page_up = PGUP
    page_down = PGDN

    def on_press(self, key):
        border_width = self.has_border * 2
        height_offset = self.top_scrollbar + self.bottom_scrollbar
        page = self.buffer.shape[0] - 1 - height_offset
        min_row, min_col = self.min_row, self.min_col
        max_min_row = self.rows - (self.height - height_offset - border_width)

        if key == self.scroll_up or key == self.scroll_up_alt:
            self.min_row = max(0, min_row - 1)
        elif key == self.scroll_down or key == self.scroll_down_alt:
            self.min_row = min(max_min_row, min_row + 1)
        elif key == self.scroll_left or key == self.scroll_left_alt:
            self.min_col = max(0, min_col - 1)
        elif key == self.scroll_right or key == self.scroll_right_alt:
            self.min_col = min(self.cols - (self.width - self.left_scrollbar - self.right_scrollbar - border_width), min_col + 1)
        elif key == PGUP:
            self.min_row = max(0, min_row - page)
        elif key == PGDN:
            self.min_row = min(max_min_row, min_row + page)
        else:
            return super().on_press(key)

        return True
