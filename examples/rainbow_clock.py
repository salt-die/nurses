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


class ClockHolder(ArrayWin, Movable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_widget(MovingClock(1, 1))
        self.border("curved", colors.BLUE_ON_BLACK)


with ScreenManager() as sm:
    widget = sm.root.new_widget(0, 0, 15, 40, create_with=ClockHolder)

    rainbow = colors.rainbow_gradient(20)

    async def rainbow_time():
        i = 0
        while True:
            widget.children[0].update_color(rainbow[i])
            i = (i + 1) % 20
            sm.root.refresh()
            await sm.sleep(.1)

    sm.run(rainbow_time())
