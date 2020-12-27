# TODO: Reset colors after screen_manager closes
from collections import defaultdict
import curses
from itertools import count
import re

DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
COLOR_RE = re.compile(r"([A-Z]+)_(?:ON_)?([A-Z]+)")
SET_COLOR = re.compile(r"[A-Z]+")
INIT_COLOR_START = 64  # May need to be lowered on terminals with too few colors.  Recommend at least 16, as these colors can't be changed on windows.

class ColorDict(dict):
    """A dict that automatically initializes missing color pairs."""
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
        """Fetch the color pair (COLOR1, COLOR2) with attribute COLOR1_ON_COLOR2 or COLOR1_COLOR2."""
        if match := COLOR_RE.fullmatch(attr):
            for color in match.groups():
                if color not in self._colors:
                    raise ValueError(f"{color} not defined")

            return curses.color_pair(self[match.groups()])

        return super().__getattr__(attr)

    def __setattr__(self, attr, rgb):
        """Initialize a new color `attr` or re-define an old color to rgb"""
        if not SET_COLOR.fullmatch(attr):
            return super().__setattr__(attr, rgb)

        if attr in DEFAULT_COLORS:
            raise ValueError(f"Can't redefine {attr}")

        if any(not (0 <= component <= 256) for component in rgb):
            raise ValueError("RGB components must be between 0 and 256")

        curses.init_color(self._colors[attr], *(round(component / 256 * 1000) for component in rgb))
