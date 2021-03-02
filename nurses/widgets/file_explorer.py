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

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

        self.close_explorer()  # Should be before super call so that self.root is None and root.remove_widget doesn't error
        super().__init__(*args, **kwargs)

    def open_explorer(self):
        if self.root is not None:
            self.root.add_widget(self)

        self.is_open = True

    def close_explorer(self):
        self._current_path = Path("")

        if self.root is not None:
            self.root.remove_widget(self)

        self.is_open = False

    def refresh(self):
        if not self.is_open:
            return

        border_offset = int(self.has_border)
        current_directory = self._get_directory()

    def _get_directory(self):
        directories = []
        files = []
        for child in self._current_path.iterdir():
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
