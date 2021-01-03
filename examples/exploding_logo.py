"""
Credit for ascii art logo to Matthew Barber (https://ascii.matthewbarber.io/art/python/)

Directions:
    'q' to quit
    'r' to reset
    arrow-keys to move
    space to poke
"""
from math import hypot, pi, sin
from pathlib import Path

from nurses import ScreenManager
from nurses.widget import Widget
import numpy as np

UP, RIGHT, DOWN, LEFT = 259, 261, 258, 260
SPACE, RESET = 32, 114
POKE_POWER = 2  # Increase this for more powerful pokes
MAX_VELOCITY = 4
FRICTION = .97
HEIGHT, WIDTH = 27, 56
PARTICLE_DELAY = .01
COLORS = 20

def rainbow_rgbs(n=COLORS):
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


class Pokable(Widget):
    def __init__(self, *args, cursor, current_color, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.vy = self.vx = 0  # velocity
        self.y = self.sy = self.top
        self.x = self.sx = self.left
        self.current_color = current_color
        self.colors[:] = sm.colors.palette["rainbow"][current_color]
        sm.schedule(self.step, delay=PARTICLE_DELAY)

    def on_press(self, key):
        if key == SPACE:
            self.poke()
        elif key == RESET:
            sm.run_soon(self.reset())

    def poke(self):
        dy = self.y - self.cursor.top - 1
        dx = self.x - self.cursor.left - 1
        hyp = dx**2 + dy**2
        if not hyp:
            return
        power = POKE_POWER / hyp
        self.vx += power * dx
        self.vy += power * dy

    def step(self):
        vy, vx = self.vy, self.vx
        if (mag := hypot(vy, vx)) > MAX_VELOCITY:
            normal = MAX_VELOCITY / mag
            vx *= normal
            vy *= normal

        self.y += vy
        self.x += vx

        if not 0 <= self.y <= HEIGHT:
            vy *= -1
            self.y += vy
        if not 0 <= self.x <= WIDTH:
            vx *= -1
            self.x += vx

        self.top = round(self.y)
        self.left = round(self.x)
        self.vy = vy * FRICTION
        self.vx = vx * FRICTION

        self.current_color = (self.current_color + min(mag, MAX_VELOCITY)) % COLORS
        self.colors[:] = sm.colors.palette["rainbow"][int(self.current_color)]
        self.refresh()

    async def reset(self):
        self.vy = self.vx = 0
        async for i in sm.delayed(range(1, 101), PARTICLE_DELAY):
            a = i / 100
            b = 1 - a
            self.y = a * self.sy + b * self.y
            self.x = a * self.sx + b * self.x
            self.top = round(self.y)
            self.left = round(self.x)
            if self.top == self.sy and self.left == self.sx:
                return


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
                particle = sm.new_widget(y, x, 1, 1, current_color=color, cursor=cursor, create_with=Pokable)
                particle[:] = str(char)

        sm.top(cursor)
        sm.schedule(sm.refresh)
        sm.run()
