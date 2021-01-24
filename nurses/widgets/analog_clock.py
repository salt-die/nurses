import time
from math import pi, e

from . import Widget

TAU = 2 * pi

def sgn(n):
    return 1 if n >= 0 else -1

def safe_div(n):
    return abs(1 / n) if n != 0 else 1000


class AnalogClock(Widget):
    """
    An analog clock.

    Notes
    -----
    :class: AnalogClock's height will be `2 * radius + 1` and it's width will be `4 * radius + 1`
    """

    boundary = True
    boundary_color = None
    boundary_character = "'"
    boundary_thickness = .1
    boundary_resolution = 100


    ticks = True
    tick_color = None
    tick_character = "#"
    short_tick_length = .05
    long_tick_length = .1

    hours = True
    hours_color = None
    hours_character = "%"
    hours_length = .4

    minutes = True
    minutes_color = None
    minutes_character = "!"
    minutes_length = .65

    seconds = True
    seconds_color = None
    seconds_character = ":"
    seconds_length = .65

    def __init__(self, *args, height_hint=1.0, **kwargs):
        super().__init__(*args, size_hint=(height_hint, None), **kwargs)

    def line_segment(self, angle, start, stop, character, color=None):
        """
        Draw a segment of the radius of the clock.

        Parameters
        ----------
        angle:
            Angle of the segment in radians. An angle of 0 corresponds to 12 o' clock. (angles are rotated by `3 * pi / 2`)

        start, stop:
            Between 0 and 1, a percentage of the radius
        """
        if color is None:
            color = self.color

        radius = self.height / 2 - 1
        start *= radius
        stop *= radius

        angle = e ** ((angle - pi / 2) * 1j)

        delta = complex(safe_div(angle.real), safe_div(angle.imag))
        step = complex(sgn(angle.real), sgn(angle.imag))
        side_dis = 0j

        pos = center = radius * (2 + 1j)

        while True:
            dif = pos - center
            length = (dif.real**2 / 4 + dif.imag**2)**.5  # `/ 4`: We actually draw an ellipse twice as wide as it is tall so it looks circular on screen.
            if stop < length:
                break

            if side_dis.real < side_dis.imag:
                side_dis += delta.real
                pos += step.real
            else:
                side_dis += delta.imag * 1j
                pos += step.imag * 1j

            if start <= length:
                self.window.addstr(round(pos.imag), round(pos.real), character, color)

    def refresh(self):
        self.window.erase()

        if self.boundary:
            for theta in range(self.boundary_resolution):
                self.line_segment(
                    theta * TAU / self.boundary_resolution,
                    1 - self.boundary_thickness,
                    1,
                    self.boundary_character,
                    self.boundary_color or self.color,
                )

        if self.ticks:
            # Long ticks
            for theta in range(0, 24, 2):
                self.line_segment(
                    theta * TAU / 24,
                    1 - self.long_tick_length,
                    1,
                    self.tick_character,
                    self.tick_color or self.color,
                )

            # Short ticks
            for theta in range(1, 24, 2):
                self.line_segment(
                    theta * TAU / 24,
                    1 - self.short_tick_length,
                    1,
                    self.tick_character,
                    self.tick_color or self.color,
                )

        hours, minutes, seconds = time.localtime()[3:6]

        if self.hours:
            self.line_segment(
                TAU * ((hours + minutes / 60) % 12) / 12,
                0,
                self.hours_length,
                self.hours_character,
                self.hours_color or self.color,
            )

        if self.minutes:
            self.line_segment(
                TAU * minutes / 60,
                0,
                self.minutes_length,
                self.minutes_character,
                self.minutes_color or self.color,
            )

        if self.seconds:
            self.line_segment(
                TAU * seconds / 60,
                0,
                self.seconds_length,
                self.seconds_character,
                self.seconds_color or self.color,
            )

        super().refresh()
