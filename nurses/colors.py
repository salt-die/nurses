"""To define a new color just assign the rgb values (each value being 0 - 255) directly to the color name (let sm be the ScreenManager):
        ```py
        sm.colors.PURPLE = 103, 15, 215
        ```
    ::Warning:: ColorDict expects color names to match the regex r"[A-Z]+" (i.e., capital letters only).

    To get some color pair just ask for the colors by name, like so:
        ```py
        sm.colors.PURPLE_ON_BLACK
        ```
    If the color pair isn't defined, ColorDict will initialize it as long as each of the colors are defined.
    Note the colors BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE are already defined.

    ::Warning:: Though ColorDict subclasses dict, using the __getitem__ interface could cause errors (bypasses checks in __getattr__).
"""
# TODO: Some program may want a large number of colors, and referring to colors by name may not be convenient in such cases.
#       Considering adding a way to refer to colors by their hex color code, something like: `sm.colors.H335551`
#       Alternatively, add a method to grab a color-pair directy from RGB values: `sm.colors.rgb(103, 15, 215, 0, 0, 0)` (PURPLE_ON_BLACK)
# TODO: Reset colors in ScreenManager.close
from collections import defaultdict
import curses
from itertools import count
import re

DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
COLOR_RE = re.compile(r"([A-Z]+)_(?:ON_)?([A-Z]+)")
SET_COLOR = re.compile(r"[A-Z]+")
INIT_COLOR_START = 64  # May need to be lowered on terminals with too few colors.  Recommend at least 16, as the colors 1 - 15 can't be changed on windows.

class ColorDict(dict):
    """
    A dict that automatically initializes colors or missing color pairs.

    Notes
    -----
    The colors BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE are defined by default.

    Examples
    --------
    >>> sm.colors.PURPLE = 103, 15, 215

    This will define a new color `PURPLE`

    >>> sm.colors.PURPLE_ON_BLACK

    This will return a curses color_pair; both colors must already be define.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["WHITE", "BLACK"] = 0  # Default color pair.
        self._pair_count = count(1)
        self._colors = defaultdict(count(INIT_COLOR_START).__next__, zip(DEFAULT_COLORS, count()))

    def __missing__(self, key):
        colors = self._colors
        pair_number = next(self._pair_count)

        curses.init_pair(pair_number, colors[key[0]], colors[key[1]])

        self[key] = pair_number
        return self[key]

    def __getattr__(self, attr):
        """Fetch the color pair (FORE, BACK) with attribute FORE_ON_BACK or FORE_BACK.
        """
        if not (match := COLOR_RE.fullmatch(attr)):
            return super().__getattr__(attr)

        fore, back = match.groups()
        if (fore_not_in := fore not in self._colors) or back not in self._colors:
            raise ValueError(f"{fore if fore_not_in else back} not defined")

        return curses.color_pair(self[fore, back])


    def __setattr__(self, attr, rgb):
        """Initialize a new color `attr` or re-define an old color to rgb.
        """
        if not SET_COLOR.fullmatch(attr):
            return super().__setattr__(attr, rgb)

        if attr in DEFAULT_COLORS:
            raise ValueError(f"Can't redefine {attr}")

        if any(not (0 <= component <= 256) for component in rgb):
            raise ValueError("RGB components must be between 0 and 256")

        curses.init_color(self._colors[attr], *(round(component / 256 * 1000) for component in rgb))
