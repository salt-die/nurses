class Bouncing:
    """After `schedule_bounce` is called widget will move according to its `vel` attribute, bouncing off its parent's boundaries.
    """

    vel = 1 + 1j
    delay = .3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos = complex(self.top, self. left)

    def schedule_bounce(self):
        from ... import ScreenManager
        self.bounce = ScreenManager().schedule(self._bounce, delay=self.delay)

    def _bounce(self):
        self.pos += self.vel

        offset = int(self.parent.has_border)
        h, w = self.parent.height - 2 * offset, self.parent.width - 2 * offset

        if not 0 <= self.pos.real <= h - self.height:
            self.vel = -self.vel.conjugate()
            self.pos += 2 * self.vel.real

        if not 0 <= self.pos.imag <= w - self.width:
            self.vel = self.vel.conjugate()
            self.pos += 2j * self.vel.imag

        self.top = round(self.pos.real)
        self.left = round(self.pos.imag)
