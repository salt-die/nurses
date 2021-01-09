from collections import defaultdict
import curses
from itertools import count, product, repeat
from math import pi, sin
import re
from warnings import warn

from .meta import Singleton


DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
DEFAULT_RGBS = tuple(product((-1, -2), repeat=3))  # Default colors are set by the terminal and could be anything; these tuples are just placeholders.
COLOR_RE = re.compile(r"[A-Z_]+")
COLOR_PAIR_RE = re.compile(r"([A-Z_]+)_ON_([A-Z_]+)")
INIT_COLOR_START = 16  # Colors 0 - 15 are already init on windows terminal and can't be re-init

def lerp(start, end, percent):
    """Linear interpolation between `start` and `end`.
    """
    return percent * end + (1 - percent) * start

def scale(components):
    """This scales rgb values in the range 0-255 to be in the range 0-1000.
    """
    return (round(component / 255 * 1000) for component in components)


class ColorManager(metaclass=Singleton):
    """
    :class: ColorManager manages curses color inits and color pair inits for nurses. There are two ways to get a
    curses color pair from this class.  The simplest way is to first define a color alias with
    `colors.COLOR = r, g, b' where `COLOR` can be any name consisting of capital letters and underscores and r, g, b
    are the color components between 0 - 255, then once aliases are defined one can retrieve a color pair by name:
    `colors.FOREGROUND_ON_BACKGROUND`.

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
        self.palette = defaultdict(list)

    def rainbow_gradient(self, n=20, background="BLACK", palette="rainbow"):
        """
        Returns an `n` color rainbow gradient.

        Other Parameters
        ----------
        background: optional
            The background color for the gradient. Can be a string ("COLOR_NAME") or rgb-tuple. (the default is "BLACK")

        palette: optional
            Save the gradient to a list in the palette dictionary with the given name. (the default is "rainbow")
            If the palette already exists the user is warned and the existing palette is cleared.
        """
        if self.palette[palette]:
            warn(f"{palette} already exists; clearing")
            self.palette[palette].clear()

        back = getattr(self, background) if isinstance(background, str) else self.color(background)

        offsets = 0, 2 * pi / 3, 4 * pi / 3

        for i in range(n):
            self.pair(tuple(int(sin(2 * pi / n * i + offset) * 127 + 128) for offset in offsets), back, palette)

        return self.palette[palette]

    def pair_gradient(self, n, start_pair, end_pair, palette):
        """
        Create a gradient from `start_pair` to `end_pair` with `n` colors.  `n` should greater or equal to 2.
        The color pairs are appended to`self.palette[palette]`.  Returns `self.palette[palette]`.
        """
        self.pair(*start_pair, palette)

        for i in range(n - 2):
            percent = (i + 1) / (n - 1)
            fore = tuple(map(lerp, start_pair[0], end_pair[0], repeat(percent)))
            back = tuple(map(lerp, start_pair[1], end_pair[1], repeat(percent)))
            self.pair(fore, back, palette)

        self.pair(*end_pair, palette)
        return self.palette[palette]

    def gradient(self, n, start_color, end_color, palette, background="BLACK"):
        """
        Create a gradient of `n` color pairs from `start_color` to `end_color` with a given background color.
        The color pairs are appended to`self.palette[palette]`.  Returns `self.palette[palette]`.

        Other Parameters
        ----------
        background: optional
            The background color for the gradient. Can be a string ("COLOR_NAME") or rgb-tuple. (the default is "BLACK")
        """
        back = getattr(self, background) if isinstance(background, str) else self.color(background)
        return self.pair_gradient(n, (start_color, back), (end_color, back), palette)

    def color(self, rgb):
        rgbs = self._rgb_to_curses

        if rgb not in rgbs:
            curses.init_color(rgbs[rgb], *scale(rgb))

        return rgbs[rgb]

    def pair(self, fore, back, palette=None):
        """
        Return a curses color pair from a pair of rgb-tuples. If `palette` is provided, the color
        pair will be appended to `self.palette[palette]`.  This can simplify creating color gradients.
        """
        pair = fore, back
        pairs = self._pair_to_curses
        color = self.color

        if pair not in pairs:
            curses.init_pair(pairs[pair], color(fore), color(back))

        color_pair = curses.color_pair(pairs[pair])

        if palette is not None:
            self.palette[palette].append(color_pair)

        return color_pair

    def __getattr__(self, attr):
        """
        Fetch the color pair (FOREGROUND, BACKGROUND) with attribute FOREGROUND_ON_BACKGROUND.
        Alternatively, if called with just a single color, return the color's rgb-tuple.
        """
        names = self._names_to_rgb

        if match := COLOR_PAIR_RE.fullmatch(attr):
            fore, back = match.groups()
            if fore not in names:
                raise ValueError(f"{fore} not defined")
            if back not in names:
                raise ValueError(f"{back} not defined")

            return self.pair(names[fore], names[back])

        if COLOR_RE.fullmatch(attr):
            return names[attr]

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

    def __str__(self):
        return f"Current aliases: {', '.join(self._names_to_rgb) or 'None'}\nCurrent palettes: {', '.join(self.palette) or 'None'}"