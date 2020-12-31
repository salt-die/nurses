from math import hypot
from pathlib import Path

from nurses import ScreenManager
from nurses.widget import Widget
import numpy as np

N, E, S, W = 259, 261, 258, 260
SPACE, R = 32, 114
POKE_POWER = 100
MAX_VELOCITY = 4
FRICTION = .8
MAX_Y, MAX_X = 27, 56
PARTICLE_DELAY, REFRESH_DELAY = .01, .02


class Cursor(Widget):
    def on_press(self, key):
        if key == N:
            self.top -= 2
        elif key == W:
            self.left -= 4
        elif key == S:
            self.top += 2
        elif key == E:
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
        sm.run_soon(self.step())

    def on_press(self, key):
        if key == SPACE:
            self.poke()
        elif key == R:
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

    async def step(self):
        while True:
            vy, vx = self.vy, self.vx
            if (mag := hypot(vy, vx)) > MAX_VELOCITY:
                normal = MAX_VELOCITY / mag
                vx *= normal
                vy *= normal

            self.y += vy
            self.x += vx

            if not 0 <= self.y <= MAX_Y:
                vy *= -1
                self.y += vy
            if not 0 <= self.x <= MAX_X:
                vx *= -1
                self.x += vx

            self.top = round(self.y)
            self.left = round(self.x)
            self.vy = vy * FRICTION
            self.vx = vx * FRICTION

            await sm.sleep(PARTICLE_DELAY)

    async def reset(self):
        self.vy = self.vx = 0
        y_dis = 1 / 100 * (self.sy - self.y)
        x_dis = 1 / 100 * (self.sx - self.x)
        for i in range(100):
            self.y += y_dis
            self.x += x_dis
            self.top = round(self.y)
            self.left = round(self.x)
            await sm.sleep(PARTICLE_DELAY)


async def refresh_often():
    while True:
        sm.refresh()
        await sm.sleep(REFRESH_DELAY)


if __name__ == "__main__":
    with open(Path(__file__).parent / "python_logo.txt") as f:
        logo = f.read()

    logo = np.array([list(line + (MAX_X - len(line)) * " ") for line in logo.splitlines()])

    sm = ScreenManager()

    cursor = sm.new_widget(0, 0, 1, 1, create_with=Cursor)
    cursor[:] = "█"

    # Setup the "particles"
    colors = np.full((MAX_Y, MAX_X), sm.colors.BLUE_ON_BLACK)
    colors[-7:] = sm.colors.YELLOW_ON_BLACK
    colors[-13: -7, -41:] = sm.colors.YELLOW_ON_BLACK
    colors[-14, -17:] = sm.colors.YELLOW_ON_BLACK
    colors[-20: -14, -15:] = sm.colors.YELLOW_ON_BLACK
    it = np.nditer((logo, colors), ["multi_index"])
    for char, color in it:
        y, x = it.multi_index
        if char != " ":
            particle = sm.new_widget(y, x, 1, 1, color=color, cursor=cursor, group="particles", create_with=Pokable)
            particle[0, 0] = str(char)

    sm.top(cursor)
    sm.run(refresh_often())
    sm.close()
