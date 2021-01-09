import time

from . import Widget


ZERO = (
    " _ \n"
    "| |\n"
    "|_|"
)

ONE = (
    "   \n"
    "  |\n"
    "  |"
)

TWO = (
    " _ \n"
    " _|\n"
    "|_ "
)

THREE = (
    " _ \n"
    " _|\n"
    " _|"
)

FOUR = (
    "   \n"
    "|_|\n"
    "  |"
)

FIVE = (
    " _ \n"
    "|_ \n"
    " _|"
)

SIX = (
    " _ \n"
    "|_ \n"
    "|_|"
)

SEVEN = (
    " _ \n"
    "  |\n"
    "  |"
)

EIGHT = (
    " _ \n"
    "|_|\n"
    "|_|"
)

NINE = (
    " _ \n"
    "|_|\n"
    " _|"
)

COLON = (
    "   \n"
    " . \n"
    " . "
)

DIGITS = ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE

def format(n):
    return DIGITS[n // 10], DIGITS[n % 10]

def digital_time():
    hours, minutes, seconds = map(format, time.localtime()[3:6])
    return *hours, COLON, *minutes, COLON, *seconds

class DigitalClock(Widget):
    def __init__(self, top, left, *args, **kwargs):
        super().__init__(top, left, 3, 24)

    def refresh(self):
        for x, digit in enumerate(digital_time()):
            for y, line in enumerate(digit.splitlines()):
                self.window.addstr(y, x * 3, line)
