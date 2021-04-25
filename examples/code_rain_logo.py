"""
Credit for ascii art logo to Matthew Barber (https://ascii.matthewbarber.io/art/python/)
"""
import numpy as np
from nurses import ScreenManager, colors
from nurses.widgets import ArrayWin

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
HEIGHT, WIDTH = 28, 56  # Dimensions of LOGO
CODE_RAIN_HEIGHT = 8    # The height of the trail of the code rain + 1,  this should be divisble by 2
LAST_RAINFALL = 25      # Number of seconds until the last rain drops.
TIME_PER_ROW = .2       # Time rain spends on each row.
MATRIX_KANJI = list('ﾆﾍ7ﾒﾜﾊﾑﾇｵ2ZI508')


class CodeRain(ArrayWin):
    drops_falling= 0

    def __init__(self, y, x, character, gradient, delay):
        super().__init__(-CODE_RAIN_HEIGHT, x, CODE_RAIN_HEIGHT, 1, transparent=True)
        self._buffer = np.full((CODE_RAIN_HEIGHT, 1), " ")
        self._colors = np.array(BLACKGREEN)[:, np.newaxis]

        self.target_row = y
        self.character = character
        self.gradient = gradient
        self.delay = delay

        CodeRain.drops_falling += 1

        self._char_task = sm.new_task(self.new_char())
        sm.run_soon(self.fall())

    async def fall(self):
        await sm.sleep(self.delay)
        sm.root.pull_to_front(self)
        for _ in range(self.target_row + 1):
            self.buffer[:-1] = self.buffer[1:]
            self.top += 1
            await sm.sleep(TIME_PER_ROW)

        # Fade to trail to black
        for i in range(CODE_RAIN_HEIGHT - 1):
            self.colors[1: -1] = self.colors[: -2]
            self.buffer[i] = " "
            await sm.sleep(TIME_PER_ROW)

        CodeRain.drops_falling -= 1

    async def new_char(self):
        while True:
            self.buffer[-1] = np.random.choice(MATRIX_KANJI)
            await sm.next_task()

    async def fade(self):
        for color in self.gradient:
            self.colors[-1] = color
            await sm.next_task()

        await sm.sleep(self.delay / 9)
        self._char_task.cancel()
        self.buffer[-1] = self.character

async def fade_when_done():
    while CodeRain.drops_falling:
        await sm.sleep(TIME_PER_ROW)

    for drop in sm.root.children:
        sm.run_soon(drop.fade())


with ScreenManager() as sm:
    BLACK = colors.gradient(CODE_RAIN_HEIGHT // 2, (0, 0, 0), (0, 255, 0), 'black_to_green')
    GREEN = colors.gradient(CODE_RAIN_HEIGHT // 2, (0, 255, 0), (255, 255, 255), 'green_to_white')
    BLACKGREEN = BLACK + GREEN
    BLUE = colors.gradient(25, (255, 255, 255), (48, 105, 152), 'white_to_blue')
    YELLOW = colors.gradient(25, (255, 255, 255), (255, 212, 59), 'white_to_yellow')

    # Ending colors of logo:  Blue: True, Yellow: False
    c = np.ones((HEIGHT, WIDTH), dtype=bool)
    c[-7:] = c[-13: -7, -41:] = c[-14, -17:] = c[-20: -14, -15:] = False

    # Exponential distribution of starting times for the rain drops.
    random = np.random.exponential(1, (HEIGHT, WIDTH))
    random = random - random.min()
    random /= random.max()
    start_times = np.sort((1 - random) * LAST_RAINFALL, axis=0)[::-1]

    # Create a CodeRain for each non-space character in the logo
    for y, row in enumerate(LOGO.splitlines()):
        for x, char in enumerate(row):
            if char != " ":
                sm.root.add_widget(CodeRain(y, x, character=char, gradient=BLUE if c[y, x] else YELLOW, delay=start_times[y, x]))

    sm.run_soon(fade_when_done())
    sm.schedule(sm.root.refresh)
    sm.run()
