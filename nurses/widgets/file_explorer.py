from pathlib import Path

from . import ArrayPad
from .. import UP, UP_2, DOWN, DOWN_2, ENTER, PGUP, PGDN


class FileExplorer(ArrayPad):
    move_up = UP
    move_up_alt = UP_2
    move_down = DOWN
    move_down_alt = DOWN_2
    select_key = ENTER
    page_up = PGUP
    page_down = PGDN
    default_directory = Path.home()
    selected_color = None

    def __init__(self, *args, **kwargs):
        self.close_explorer()  # Should be before super call so that self.root is None and root.remove_widget doesn't error
        super().__init__(*args, **kwargs)

        if isinstance(self.default_directory, str):
            self.default_directory = Path(self.default_directory)

    def open_explorer(self):
        self.file = None
        self.current_directory = self._get_directory()
        self.selection = 1
        self.is_open = True
        self.min_row = 0

        if self.root is not None:
            self.root.add_widget(self)
            self.root.refresh()

    def close_explorer(self):
        if self.root is not None:
            self.root.remove_widget(self)

        self._current_path = self.default_directory
        self.is_open = False

    def update_geometry(self):
        if self.root is None:
            return

        if self.selected_color is None:
            from .. import colors
            self.selected_color = colors.BLACK_ON_WHITE

        super().update_geometry()
        self.pad[0, :2] = "."

    def refresh(self):
        if not self.is_open:
            return

        directory = self.current_directory
        if (need_rows := len(directory) + 1 - self.rows) > 0:
            self.rows += need_rows

        if (need_cols := max(len(str(path)) for path in directory) - self.cols) > 0:
            self.cols += need_cols

        self[1:] = " "
        for i, path in enumerate(directory, start=1):
            self[i, :len(path.name)] = path.name

        self.pad_colors[:] = self.color
        self.pad_colors[self.selection] = self.selected_color

        super().refresh()

    def _get_directory(self):
        directories = []
        files = []
        for child in self._current_path.iterdir():
            if child.name.startswith("."):  # Skip hidden files / folders
                continue

            if child.is_dir():
                directories.append(child)
            else:
                files.append(child)

        directories.sort(key=lambda path: path.name)
        files.sort(key=lambda path: path.name)

        return directories + files

    def on_press(self, key):
        selection = self.selection
        directory = self.current_directory
        selected_path = directory[selection - 1]

        if key == self.select_key:
            if selection == 0:
                self._current_path = self._current_path.parent
                self.current_directory = self._get_directory()
            elif selected_path.is_dir():
                self._current_path = selected_path
                self.current_directory = self._get_directory()
            else:
                self.file = selected_path
                self.close_explorer()

        elif key == self.move_up or key == self.move_up_alt:
            self.selection = max(0, selection - 1)
            if self.selection < self.min_row:
                self.min_row -= 1

        elif key == self.move_down or key == self.move_down_alt:
            self.selection = min(len(directory), selection + 1)
            if self.selection - self.min_row == len(self.buffer[:, 0]):
                self.min_row += 1

        else:
            return super().on_press(key)

        self.root.refresh()
        return True
