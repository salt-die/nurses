from pathlib import Path

from . import Widget
from .. import UP, UP_2, DOWN, DOWN_2, ENTER, PGUP, PGDN


class FileExplorer(Widget):
    move_up = UP
    move_up_alt = UP_2
    move_down = DOWN
    move_down_alt = DOWN_2
    select_key = ENTER
    page_up = PGUP
    page_down = PGDN

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
        ...

    def open_explorer(self):
        ...

    def close_explorer(self):
        ...

    def refresh(self):
        ...
