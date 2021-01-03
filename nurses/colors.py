from collections import defaultdict
import curses
from itertools import count, product
import re

DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
DEFAULT_RGBS = tuple(product((-1, -2), repeat=3))  # Default colors are set by the terminal and could be anything; these tuples are just placeholders.
COLOR_RE = re.compile(r"[A-Z_]+")
COLOR_PAIR_RE = re.compile(r"([A-Z_]+)_ON_([A-Z_]+)")
INIT_COLOR_START = 16  # Colors 1 - 15 can't be changed on windows. This might be need to be changed for other systems.

def _scale(components):
    """This scales rgb values in the range 0-255 to be in the range 0-1000.
    """
    return (round(component / 255 * 1000) for component in components)


class _RGB:
    """
    This utility class will return the rgb values of colors or color pairs by name using __getattr__.
    It's mostly to be used to simplify redefining colors or color pairs.

    Examples
    --------
    >>> sm.colors.redefine_color(sm.colors.rgb.ORANGE, sm.colors.rgb.BLUE)
    """
    def __init__(self, names):
        self.names = names

    def __getattr__(self, alias):
        names = self.names

        if match := COLOR_PAIR_RE.fullmatch(alias):
            fore, back = match.groups()
            return names[fore], names[back]

        if COLOR_RE.fullmatch(alias):
            return names[alias]

        return super().__getattr__(alias)


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
        self.rgb = _RGB(self._names_to_rgb)

    def pair(self, fore, back):
        """Return a curses color pair from a pair of rgb-tuples.
        """
        pair = fore, back
        rgbs = self._rgb_to_curses
        pairs = self._pair_to_curses

        if fore not in rgbs:
            curses.init_color(rgbs[fore], *_scale(fore))
        if back not in rgbs:
            curses.init_color(rgbs[back], *_scale(back))

        if pair not in pairs:
            curses.init_pair(pairs[pair], rgbs[fore], rgbs[back])

        return curses.color_pair(pairs[pair])

    def __getattr__(self, color_pair):
        """Fetch the color pair (FOREGROUND, BACKGROUND) with attribute FOREGROUND_ON_BACKGROUND.
        """
        if not (match := COLOR_PAIR_RE.fullmatch(color_pair)):
            return super().__getattr__(color_pair)

        names = self._names_to_rgb
        fore, back = match.groups()
        if fore not in names:
            raise ValueError(f"{fore} not defined")
        if back not in names:
            raise ValueError(f"{back} not defined")

        return self.pair(names[fore], names[back])

    def __setattr__(self, color, rgb):
        """Assign `color` to `rgb`.
        """
        if not COLOR_RE.fullmatch(color):
            return super().__setattr__(color, rgb)

        if color in DEFAULT_COLORS:
            raise ValueError(f"can't redefine {color}")

        if any(component < 0 or component > 255 for component in rgb):
            raise ValueError(f"invalid components {rgb}")

        names = self._names_to_rgb
        if color in names and names[color] in self._rgb_to_curses:
            self.redefine_color(names[color], rgb)
        names[color] = rgb

    def redefine_color(self, old, new):
        """The color `old` is everywhere replaced with `new`.  Change is immediate without a screen refresh.
        """
        rgbs = self._rgb_to_curses

        rgbs[new] = rgbs.pop(old)
        curses.init_color(rgbs[new], *_scale(new))

    def redefine_color_pair(self, old, new):
        """The color pair `old` is everywhere replaced with `new`. Screen needs refresh to see changes.
        """
        rgbs = self._rgb_to_curses
        pairs = self._pair_to_curses

        pairs[new] = pairs.pop(old)
        curses.init_pair(pairs[new], rgbs[new[0]], rgbs[new[1]])
