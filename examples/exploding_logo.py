"""
Credit for ascii art logo to Matthew Barber (https://ascii.matthewbarber.io/art/python/)

Directions:
    'q' to quit
    'r' to reset
    arrow-keys to move
    space to poke
"""
import curses
from math import hypot, pi, sin
from pathlib import Path

import numpy as np
from nurses import ScreenManager
from nurses.widget import Widget
from nurses.scheduler import next_task

UP, RIGHT, DOWN, LEFT, SPACE, RESET = 259, 261, 258, 260, 32, 114  # Keybindings
POKE_POWER = 2  # Increase this for more powerful pokes
MAX_VELOCITY = 4  # Limits how fast particles can travel.
FRICTION = .97  # Friction decreases the closer this value is to `1`.
HEIGHT, WIDTH = 27, 56  # Size of the Python logo, found through inspection.
COLORS = 20  # Number of different rainbow colors -- If this changes the start color of the logo will also change.
FAST_DIVISION = tuple(i / 100 for i in range(1, 101))  # Used when lerping in Particle.reset

def rainbow_rgbs(n=COLORS):
    """This creates the rgb-tuples that make up the rainbow gradient.  It's what I refer to as the "lolcat"-function.
    """
    offsets = 0, 2 * pi / 3, 4 * pi / 3
    for i in range(n):
        yield tuple(int(sin(2 * pi / n * i + offset) * 127 + 128) for offset in offsets)


class Cursor(Widget):
    def on_press(self, key):
        if key == UP:
            self.top -= 2
        elif key == LEFT:
            self.left -= 4
        elif key == DOWN:
            self.top += 2
        elif key == RIGHT:
            self.left += 4
        else:
            return None

        self.top %= HEIGHT + 1
        self.left %= WIDTH + 1
        return True


class Particle:
    """This class fits the Widget api without inheriting from Widget: we don't need numpy array buffers for single character windows!
    """
    # We create a lot of particles, if we can get any speed up from this, we'll take it!
    __slots__ = "height", "width", "top", "left",  "start", "pos", "vel", "current_color", "character", "cursor", "window", "is_transparent"

    def __init__(self, top, left, cursor, current_color, character):
        self.height = self.width = 1

        self.top = top
        self.left = left

        self.start = self.pos = complex(top, left)

        self.vel = 0j # velocity

        self.current_color = current_color
        self.character = character

        self.cursor = cursor
        self.window = curses.newwin(1, 2)
        self.window.addstr(0, 0, self.character, sm.colors.palette["rainbow"][int(self.current_color)])

        self.is_transparent = False  # Needed to convince ScreenManager we're a Widget
        sm.schedule(self.step)

    def on_press(self, key):
        if key == SPACE:
            self.poke()
        elif key == RESET:
            sm.run_soon(self.reset())

    def poke(self):
        dyx = self.pos - complex(self.cursor.top - 1, self.cursor.left - 1)
        if dyx != 0:
            self.vel += POKE_POWER / (dyx.real**2 + dyx.imag**2) * dyx

    def step(self):
        if self.vel == 0:
            return

        if (mag := abs(self.vel)) > MAX_VELOCITY:
            self.vel *= MAX_VELOCITY / mag

        self.pos += self.vel

        if not 0 <= self.pos.real <= HEIGHT:
            self.vel = -self.vel.conjugate()
            self.pos += self.vel.real

        if not 0 <= self.pos.imag <= WIDTH:
            self.vel = self.vel.conjugate()
            self.pos += self.vel.imag

        self.top = round(self.pos.real)
        self.left = round(self.pos.imag)
        self.vel *= FRICTION

        self.current_color = (self.current_color + min(mag, MAX_VELOCITY)) % COLORS
        self.window.addstr(0, 0, self.character, sm.colors.palette["rainbow"][int(self.current_color)])

    async def reset(self):
        self.vel = 0j
        for a in FAST_DIVISION:
            self.pos = a * self.start + (1 - a) * self.pos
            self.top = round(self.pos.real)
            self.left = round(self.pos.imag)
            if self.top == self.start.real and self.left == self.start.imag:
                return
            await next_task()


if __name__ == "__main__":
    with open(Path(__file__).parent / "python_logo.txt") as f:
        logo = f.read()

    logo = np.array([list(line + (WIDTH - len(line)) * " ") for line in logo.splitlines()])
    colors = np.full((HEIGHT, WIDTH), 13)
    colors[-7:] = colors[-13: -7, -41:] = colors[-14, -17:] = colors[-20: -14, -15:] = 2

    with ScreenManager() as sm:
        for rgb in rainbow_rgbs():
            sm.colors.pair(rgb, sm.colors._names_to_rgb["BLACK"], palette="rainbow")

        cursor = sm.new_widget(0, 0, 3, 3, transparent=True, create_with=Cursor)
        cursor[(0, -1), 1] = "|"
        cursor[1] = "-+-"

        # Setup the "particles"
        it = np.nditer((logo, colors), ["multi_index"])
        for char, color in it:
            y, x = it.multi_index
            if char != " ":
                particle = sm.add_widget(Particle(y, x, character=str(char), current_color=color, cursor=cursor))

        sm.top(cursor)
        sm.schedule(sm.refresh)
        sm.run()
