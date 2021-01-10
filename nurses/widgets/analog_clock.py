import time
from math import pi, e

from . import Widget

TAU = 2 * pi
RESOLUTION = 100

def sgn(n):
    return 1 if n >= 0 else -1

def safe_div(n):
    return abs(1 / n) if n != 0 else 1000


class AnalogClock(Widget):
    boundary_color = None
    boundary_character = "."
    boundary_thickness = .1

    ticks = True
    tick_color = None
    tick_character = "#"
    short_tick_length = .1
    long_tick_length = .15

    hour_color = None
    hour_character = "%"
    hour_length = .4

    minute_color = None
    minute_character = "!"
    minute_length = .65

    seconds_color = None
    seconds_character = ":"
    seconds_length = .65

    def __init__(self, top, left, radius, *args, **kwargs):
        super().__init__(top, left, 2 * radius + 1, 2 * radius + 1, *args, **kwargs)
        self.radius = radius

    def line_segment(self, angle, start, stop, character, color=None):
        """
        Draw a segment of the radius of the clock.

        Parameters
        ----------
        angle:
            Angle of the segment in radians. An angle of 0 corresponds to 12 o' clock. (angles are rotated by `3 * pi / 2`)

        start, stop:
            Between 0 and 1, a percentage of max_radius
        """
        if color is None:
            color = self.color

        start *= self.radius
        stop *= self.radius

        angle = e ** ((angle - pi / 2) * 1j)

        delta = complex(safe_div(angle.real), safe_div(angle.imag))
        step = complex(sgn(angle.real), sgn(angle.imag))
        side_dis = 0j

        pos = center = self.radius * (1 + 1j)

        while (length := abs(pos - center)) < stop:
            if side_dis.real < side_dis.imag:
                side_dis += delta.real
                pos += step.real
            else:
                side_dis += delta.imag * 1j
                pos += step.imag * 1j

            if start <= length:
                self.window.addstr(round(pos.imag), round(pos.real), character, color)

    def draw_face(self):
        # Boundary
        for theta in range(RESOLUTION):
            self.line_segment(
                theta * TAU / RESOLUTION,
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

    def draw_hands(self):
        hours, minutes, seconds = time.localtime()[3:6]
        self.line_segment(
            TAU * ((hours + minutes / 60) % 12) / 12,
            0,
            self.hour_length,
            self.hour_character,
            self.hour_color or self.color,
        )
        self.line_segment(
            TAU * minutes / 60,
            0,
            self.minute_length,
            self.minute_character,
            self.minute_color or self.color,
        )
        self.line_segment(
            TAU * seconds / 60,
            0,
            self.seconds_length,
            self.seconds_character,
            self.seconds_color or self.color,
        )

    def refresh(self):
        self.window.erase()
        self.draw_face()
        self.draw_hands()
