from collections import defaultdict
import curses
from itertools import count, product
import re

DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
DEFAULT_RGBS = tuple(product((-1, -2), repeat=3))  # Default colors are set by the terminal and could be anything; these tuples are just placeholders.
COLOR_RE = re.compile(r"[A-Z_]+")
COLOR_PAIR_RE = re.compile(r"([A-Z_]+)_ON_([A-Z_]+)")
INIT_COLOR_START = 16  # Colors 0 - 15 can't be changed on windows. This might be need to be changed for other systems.

def _scale(components):
    """This scales rgb values in the range 0-255 to be in the range 0-1000.
    """
    return (round(component / 255 * 1000) for component in components)


class _ColorManager:
    """
    :class: _ColorManager manages curses color inits and color pair inits for nurses. There are two ways to get a
    curses color pair from this class.  The simplest way is to first define a color alias with
    `cm.COLOR = r, g, b' where `COLOR` can be any name consisting of capital letters and underscores and r, g, b
    are the color components between 0 - 255. Once aliases are defined one can retrieve a color pair by name:
    `cm.FOREGROUND_ON_BACKGROUND`.

    An alternative way to get a curses color pair is the `pair` method which expects a pair of rgb 3-tuples.

    Notes
    -----
    The names BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE are already defined and can't be redefined.
    These are your terminal default colors, don't necessarily correspond to black, blue, green, etc.
    """
    def __init__(self):
        self._names_to_rgb = dict(zip(DEFAULT_COLORS, DEFAULT_RGBS))
        self._rgb_to_curses = defaultdict(count(INIT_COLOR_START).__next__, zip(DEFAULT_RGBS, count()))
        self._pair_to_curses = defaultdict(count(1).__next__, {(DEFAULT_RGBS[-1], DEFAULT_RGBS[0]): 0})

    def color(self, rgb):
        """Return a curses color number from a rgb-tuple.
        """
        rgbs = self._rgb_to_curses
        if rgb not in rgbs:
            curses.init_color(rgbs[rgb], *_scale(rgb))
        return rgbs[rgb]

    def pair(self, fore, back):
        """Return a curses color pair from a pair of rgb-tuples.
        """
        pair = fore, back
        color = self.color
        pairs = self._pair_to_curses

        if pair not in pairs:
            curses.init_pair(pairs[pair], color(fore), color(back))
        return curses.color_pair(pairs[pair])

    def __getattr__(self, attr):
        """Fetch the color pair (FOREGROUND, BACKGROUND) with attribute FOREGROUND_ON_BACKGROUND.
        """
        names = self._names_to_rgb

        if match := COLOR_PAIR_RE.fullmatch(attr):
            fore, back = match.groups()
            if fore not in names:
                raise ValueError(f"{fore} not defined")
            if back not in names:
                raise ValueError(f"{back} not defined")

            return self.pair(names[fore], names[back])

        return super().__getattr__(attr)

    def __setattr__(self, color, rgb):
        """Assign the alias `color` to `rgb`.
        """
        if not COLOR_RE.fullmatch(color):
            return super().__setattr__(color, rgb)

        if color in DEFAULT_COLORS:
            raise ValueError(f"can't redefine {color}")

        if any(component < 0 or component > 255 for component in rgb):
            raise ValueError(f"invalid components {rgb}")

        self._names_to_rgb[color] = rgb
