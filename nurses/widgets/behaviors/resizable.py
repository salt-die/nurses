class Resizable:
    shrink_vertical = 259  # Up-arrow
    expand_vertical = 258  # Down-arrow
    shrink_horizontal = 260  # Left-arrow
    expand_horizontal = 261  # Right-arrow

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