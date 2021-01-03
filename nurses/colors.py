# TODO: Reset colors in ScreenManager.close
from collections import defaultdict
import curses
from itertools import count
import re

DEFAULT_COLORS = "BLACK", "BLUE", "GREEN", "CYAN", "RED", "MAGENTA", "YELLOW", "WHITE"
DEFAULT_RGBS = (
    (  0,   0,   0),
    (  0,   0, 255),
    (  0, 255,   0),
    (  0, 255, 255),
    (255,   0,   0),
    (255,   0, 255),
    (255, 255,   0),
    (255, 255, 255),
)
COLOR_PAIR_RE = re.compile(r"([A-Z_]+)_ON_([A-Z_]+)")
COLOR_RE = re.compile(r"[A-Z_]+")
INIT_COLOR_START = 16  # Colors 1 - 15 can't be changed on windows. This might be need to be changed for other systems.

def _scale(components):
    """This scales rgb values in the range 0-255 to be in the range 0-1000.
    """
    return (round(component / 255 * 1000) for component in components)


class ColorManager:
    """
    :class: ColorManager manages curses color inits and color pair inits for nurses. There are two ways to get a
    curses color pair from this class.  The simplest way is to first define a color alias with
    `cm.COLOR = r, g, b' where `COLOR` can be any name consisting of capital letters and underscores and r, g, b
    are the color components between 0 - 255. Once aliases are defined one can retrieve a color pair by name:
    `cm.FOREGROUND_ON_BACKGROUND`.

    An alternative way to get a curses color pair is the `pair` method. `cm.pair(fr, fg, fb, br, bg, bb)`
    returns the color pair whose foreground components are `fr, fg, fb` and whose background components are
    `br, bg, bb`.

    Notes
    -----
    The names BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE are already defined and can't be redefined.

    Curses allows redefining an already defined color pair which will immediately change the colors of anything on
    screen using that color pair.  While one can redefine aliases with :class: ColorManager, there's currently
    no support for redefining a color pair.
    """
    def __init__(self):
        self._names_to_rgb = dict(zip(DEFAULT_COLORS, DEFAULT_RGBS))
        self._rgb_to_curses = defaultdict(count(INIT_COLOR_START).__next__, zip(DEFAULT_RGBS, count()))
        self._pair_to_curses = defaultdict(count(1).__next__, {(DEFAULT_RGBS[-1], DEFAULT_RGBS[0]): 0})

    def pair(self, fr, fg, fb, br, bg, bb):
        """
        Return a curses color pair whose foreground components are `fr, fg, fb` and whose
        background components are `br, bg, bb`.
        """
        pair = fore, back = (fr, fg, fb), (br, bg, bb)
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
        """Fetch the color pair (FOREGROUND, BACKGROUND) with attribute FOREGROUN_ON_BACKGROUND.
        """
        if not (match := COLOR_PAIR_RE.fullmatch(color_pair)):
            return super().__getattr__(color_pair)

        names = self._names_to_rgb
        fore, back = match.groups()
        if fore not in names:
            raise ValueError(f"{fore} not defined")
        if back not in names:
            raise ValueError(f"{back} not defined")

        return self.pair(*names[fore], *names[back])

    def __setattr__(self, color, rgb):
        """Assign `color` to `rgb`.
        """
        if not COLOR_RE.fullmatch(color):
            return super().__setattr__(color, rgb)

        if color in DEFAULT_COLORS:
            raise ValueError(f"can't redefine {color}")

        if any(component < 0 or component > 255 for component in rgb):
            raise ValueError(f"invalid components {rgb}")

        self._names_to_rgb[color] = rgb
