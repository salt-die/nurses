"""
details for future implementation:

similar to Textbox, will need to delay import the default selected color

should open/closed version of the menu be stored on separate windows? alternatively we could just resize/rewrite a single window
"""
from . import Widget


class Menu(Widget):
    """
    Notes
    -----
    `items` should be an iterable of pairs ("menu entry", callback)
    """
    move_up = 259  # Up-arrow
    move_down = 258  # Down-arrow
    select_key = 10  # Enter
    open_close_key = None  # Alt + first letter of menu name?

    wrap = False

    selected_color = None

    def __init__(self, top, left, *items, **kwargs):
        raise NotImplementedError
        self._items = dict(items)
        super().__init__(top, left, len(self._items), max(map(len, self._items) + 2, **kwargs))
