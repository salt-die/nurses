from pathlib import Path

from . import ArrayPad
from .behaviors import Scrollable
from .. import UP, UP_2, DOWN, DOWN_2, ENTER, PGUP, PGDN


class FileExplorer(ArrayPad, Scrollable):
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
        raise NotImplementedError

        self.close_explorer()  # Should be before super call so that self.root is None and root.remove_widget doesn't error
        super().__init__(*args, **kwargs)

        if isinstance(self.default_directory, str):
            self.default_directory = Path(self.default_directory)

        self.pad[0, :2] = ".."

    def open_explorer(self):
        if self.root is not None:
            self.root.add_widget(self)

        self.current_directory = self._get_directory()
        self.selection = 1
        self.is_open = True

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
        files.sort(lambda path: path.name)

        return directories + files

    def on_press(self, key):
        if key == self.select_key:
            ...

        return super().on_press(key)
