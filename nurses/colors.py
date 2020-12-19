# TODO: Need color creation via curses.init_color support
import curses
from itertools import count
import re

COLOR_RE = re.compile(r"([A-Z]+)_(?:ON_)?([A-Z]+)")


class ColorDict(dict):
    """A dict that automatically initializes missing color pairs."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["WHITE", "BLACK"] = 0
        self._pair_count = count(1)

    def __missing__(self, key):
        pair_number = next(self._pair_count)

        curses.init_pair(pair_number, getattr(curses, f"COLOR_{key[0]}"), getattr(curses, f"COLOR_{key[1]}"))

        self[key] = pair_number
        return self[key]

    def __getattr__(self, attr):
        """Fetch the color pair (COLOR1, COLOR2) with attribute COLOR1_ON_COLOR2 or COLOR1_COLOR2."""
        if match := COLOR_RE.fullmatch(attr):
            return curses.color_pair(self[match.groups()])

        return super().__getattr__(attr)
