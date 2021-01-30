class Scrollable:
    """Warning:: Scrollable behavior for :class: ArrayPad only.
    """
    scroll_up = 259  # Up-arrow
    scroll_down = 258  # Down-arrow
    scroll_left = 260  # Left-arrow
    scroll_right = 261  # Right-arrow

    def on_press(self, key):
        if key == self.scroll_up:
            self.min_row = max(0, self.min_row - 1)
        elif key == self.scroll_down:
            self.min_row = min(self.rows - (self.height - self.top_scrollbar - self.bottom_scrollbar), self.min_row + 1)
        elif key == self.scroll_left:
            self.min_col = max(0, self.min_col - 1)
        elif key == self.scroll_right:
            self.min_col = min(self.cols - (self.width - self.left_scrollbar - self.right_scrollbar), self.min_col + 1)
        else:
            return super().on_press(key)

        return True
