from . import Widget
from . import Menu
from .. import LEFT, RIGHT, ENTER


class Menubar(Widget):
    move_left = LEFT
    move_right = RIGHT
    select_key = ENTER

    selected_color = None

    def __init__(self, row, **kwargs):
        raise NotImplementedError