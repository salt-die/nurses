"""
Credit for ascii art logo to Matthew Barber (https://ascii.matthewbarber.io/art/python/)

Directions:
    'q' to quit
    'r' to reset
    arrow-keys to move
    space to poke
"""
from math import hypot
from pathlib import Path

from nurses import ScreenManager
from nurses.widget import Widget
import numpy as np

UP, RIGHT, DOWN, LEFT = 259, 261, 258, 260
SPACE, RESET = 32, 114
POKE_POWER = 1  # Increase this for more powerful pokes
MAX_VELOCITY = 4
FRICTION = .97
HEIGHT, WIDTH = 27, 56
PARTICLE_DELAY, REFRESH_DELAY = .01, .02


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
        return True


class Pokable(Widget):
    def __init__(self, *args, cursor, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor = cursor
        self.vy = self.vx = 0  # velocity
        self.y = self.sy = self.top
        self.x = self.sx = self.left
        sm.schedule_callback(self.step, PARTICLE_DELAY)

    def on_press(self, key):
        if key == SPACE:
            self.poke()
        elif key == RESET:
            sm.run_soon(self.reset())

    def poke(self):
        dy = self.y - self.cursor.top
        dx = self.x - self.cursor.left
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

    async def reset(self):
        self.vy = self.vx = 0
        for i in range(1, 101):
            a = i / 100
            b = 1 - a
            self.y = a * self.sy + b * self.y
            self.x = a * self.sx + b * self.x
            self.top = round(self.y)
            self.left = round(self.x)
            if self.top == self.sy and self.left == self.sx:
                return
            await sm.sleep(PARTICLE_DELAY)


if __name__ == "__main__":
    with open(Path(__file__).parent / "python_logo.txt") as f:
        logo = f.read()

    logo = np.array([list(line + (WIDTH - len(line)) * " ") for line in logo.splitlines()])

    with ScreenManager() as sm:
        cursor = sm.new_widget(0, 0, 1, 1, create_with=Cursor)
        cursor[:] = "█"

        # Setup the "particles"
        colors = np.full((HEIGHT, WIDTH), sm.colors.BLUE_ON_BLACK)
        colors[-7:] = sm.colors.YELLOW_ON_BLACK
        colors[-13: -7, -41:] = sm.colors.YELLOW_ON_BLACK
        colors[-14, -17:] = sm.colors.YELLOW_ON_BLACK
        colors[-20: -14, -15:] = sm.colors.YELLOW_ON_BLACK
        it = np.nditer((logo, colors), ["multi_index"])
        for char, color in it:
            y, x = it.multi_index
            if char != " ":
                particle = sm.new_widget(y, x, 1, 1, color=color, cursor=cursor, create_with=Pokable)
                particle[:] = str(char)

        sm.top(cursor)
        sm.schedule_callback(sm.refresh, REFRESH_DELAY)
        sm.run()
