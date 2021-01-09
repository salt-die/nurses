from itertools import cycle

from nurses import colors, ScreenManager
from nurses.widgets import ArrayWin, DigitalClock
from nurses.widgets.behaviors import Movable


VELOCITY = .5


class MovingClock(DigitalClock):
    def __init__(self, top, left, *args, **kwargs):
        super().__init__(top, left, *args, **kwargs)

        self.pos = complex(top, left)
        self.vel = 1 + 1j
        self.vel *= VELOCITY / abs(self.vel)  # Normalize

        sm.schedule(self.update, delay=.1)

    def update(self):
        self.pos += self.vel

        if not 1 <= self.pos.real <= self.parent.height - self.height - 1:
            self.vel = -self.vel.conjugate()
            self.pos += 2 * self.vel.real

        if not 1 <= self.pos.imag <= self.parent.width - self.width - 1:
            self.vel = self.vel.conjugate()
            self.pos += 2j * self.vel.imag

        self.top = round(self.pos.real)
        self.left = round(self.pos.imag)

        self.update_color(next(rainbow))
        sm.root.refresh()


class ClockHolder(ArrayWin, Movable):
    ...


with ScreenManager() as sm:
    rainbow = cycle(colors.rainbow_gradient(20))

    outer = ClockHolder(0, 0, 15, 40, border="curved", border_color=colors.BLUE_ON_BLACK)
    outer.add_widget(MovingClock(1, 1))

    sm.root.add_widget(outer)
    sm.run()
