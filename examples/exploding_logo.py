"""
Credit for ascii art logo to Matthew Barber (https://ascii.matthewbarber.io/art/python/)

Directions:
    'q' to quit
    'r' to reset
    arrow-keys to move
    space to poke
"""
import numpy as np
from nurses import ScreenManager, colors, Widget
from nurses.widgets.behaviors import Movable


LOGO = """
                   _.gj8888888lkoz.,_
                d888888888888888888888b,
               j88P""V8888888888888888888
               888    8888888888888888888
               888baed8888888888888888888
               88888888888888888888888888
                            8888888888888
    ,ad8888888888888888888888888888888888  888888be,
   d8888888888888888888888888888888888888  888888888b,
  d88888888888888888888888888888888888888  8888888888b,
 j888888888888888888888888888888888888888  88888888888p,
j888888888888888888888888888888888888888'  8888888888888
8888888888888888888888888888888888888^"   ,8888888888888
88888888888888^'                        .d88888888888888
8888888888888"   .a8888888888888888888888888888888888888
8888888888888  ,888888888888888888888888888888888888888^
^888888888888  888888888888888888888888888888888888888^
 V88888888888  88888888888888888888888888888888888888Y
  V8888888888  8888888888888888888888888888888888888Y
   `"^8888888  8888888888888888888888888888888888^"'
               8888888888888
               88888888888888888888888888
               8888888888888888888P""V888
               8888888888888888888    888
               8888888888888888888baed88V
                `^888888888888888888888^
                  `'"^^V888888888V^^'
"""
SPACE, RESET = 32, 114  # Keybindings
POKE_POWER = 2          # Increase this for more powerful pokes
MAX_VELOCITY = 10       # Limits how fast particles can travel.
FRICTION = .97          # Friction decreases the closer this value is to `1`.
HEIGHT, WIDTH = 28, 56  # Size of the Python logo
COLORS = 20             # Number of different rainbow colors
BLUE, YELLOW = round(13/20 * COLORS), round(1/10 * COLORS)
COLOR_LERP = 4          # Increase to speed up return to start color on reset
COLOR_CHANGE = 5        # The higher this is the faster colors will change due to velocity
FAST_DIVISION = tuple(i / 100 for i in range(1, 101))  # Used when lerping in Particle.reset


class Cursor(Widget, Movable):
    ud_step = 2
    lr_step = 4
    wrap_height = HEIGHT + 1
    wrap_width = WIDTH + 1


class Particle(Widget):
    # We create a lot of particles, if we can get any speed up from this, we'll take it!
    __slots__ = "start", "pos", "vel", "start_color", "color"

    def __init__(self, top, left, color, character, **kwargs):
        super().__init__(top, left, 1, 1, color=color)
        self.start = self.pos = complex(top, left)

        self.vel = 0j # velocity

        self.start_color = color
        self.character = character

        sm.schedule(self.step)

    def update_geometry(self):
        if self.parent is None:
            return

        super().update_geometry()
        self.window.addstr(0, 0, self.character, colors.palette["rainbow"][self.color])

    def on_press(self, key):
        if key == SPACE:
            self.poke()
        elif key == RESET:
            sm.run_soon(self.reset())

    def poke(self):
        dyx = self.pos - complex(cursor.top - 1, cursor.left - 1)
        if dyx != 0:
            self.vel += POKE_POWER / (dyx.real**2 + dyx.imag**2) * dyx

    def step(self):
        if self.vel == 0:
            return

        if (mag := abs(self.vel)) > MAX_VELOCITY:
            self.vel *= MAX_VELOCITY / mag

        self.pos += self.vel

        # These two conditionals will cause particles to bounce off the edges
        if not 0 <= self.pos.real <= HEIGHT:
            self.vel = -self.vel.conjugate()
            self.pos += 2 * self.vel.real

        if not 0 <= self.pos.imag <= WIDTH:
            self.vel = self.vel.conjugate()
            self.pos += 2j * self.vel.imag

        self.top = round(self.pos.real)
        self.left = round(self.pos.imag)
        self.vel *= FRICTION

        self.color = (self.color + min(mag, MAX_VELOCITY) * COLOR_CHANGE) % COLORS

    async def reset(self):
        self.vel = 0j
        async for a in sm.aiter(FAST_DIVISION):
            self.pos = a * self.start + (1 - a) * self.pos
            self.color = COLOR_LERP * a * self.start_color + (1 - COLOR_LERP * a) * self.color
            self.top = round(self.pos.real)
            self.left = round(self.pos.imag)
            if self.top == self.start.real and self.left == self.start.imag and self.start_color == int(self.color):
                return

    def refresh(self):
        self.window.chgat(0, 0, colors.palette["rainbow"][int(self.color)])


with ScreenManager() as sm:
    colors.rainbow_gradient(COLORS)

    # Starting colors of LOGO:
    c = np.full((HEIGHT, WIDTH), BLUE)
    c[-7:] = c[-13: -7, -41:] = c[-14, -17:] = c[-20: -14, -15:] = YELLOW

    # Create a Particle for each non-space character in the logo
    for y, row in enumerate(LOGO.splitlines()):
        for x, char in enumerate(row):
            if char != " ":
                sm.root.add_widget(Particle(y, x, character=char, color=c[y, x]))

    cursor = sm.root.new_widget(0, 0, 3, 3, transparent=True, create_with=Cursor)
    cursor.window.addstr(0, 0, " | \n-+-\n | ")

    sm.schedule(sm.root.refresh)
    sm.run()
