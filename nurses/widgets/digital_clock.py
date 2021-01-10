import time

from . import Widget


ZERO = (
    " _ ",
    "| |",
    "|_|",
)

ONE = (
    "   ",
    "  |",
    "  |",
)

TWO = (
    " _ ",
    " _|",
    "|_ ",
)

THREE = (
    " _ ",
    " _|",
    " _|",
)

FOUR = (
    "   ",
    "|_|",
    "  |",
)

FIVE = (
    " _ ",
    "|_ ",
    " _|",
)

SIX = (
    " _ ",
    "|_ ",
    "|_|",
)

SEVEN = (
    " _ ",
    "  |",
    "  |",
)

EIGHT = (
    " _ ",
    "|_|",
    "|_|",
)

NINE = (
    " _ ",
    "|_|",
    " _|",
)

COLON = (
    "   ",
    " . ",
    " . ",
)

DIGITS = ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE

def format(n):
    return DIGITS[n // 10], DIGITS[n % 10]

def digital_time(twelve_hour=False):
    hours = time.localtime()[3]
    if twelve_hour:
        hours %= 12
    hours, minutes, seconds = map(format, (hours, *time.localtime()[4:6]))

    return *hours, COLON, *minutes, COLON, *seconds


class DigitalClock(Widget):
    """A digital clock widget.  Dimensions of this widget are (3, 24).
    """
    def __init__(self, top, left, *args, twelve_hour=False, **kwargs):
        super().__init__(top, left, 3, 24, *args, **kwargs)
        self.twelve_hour = twelve_hour

    def refresh(self):
        for x, digit in enumerate(digital_time(self.twelve_hour)):
            for y, line in enumerate(digit):
                self.window.addstr(y, x * 3, line)
