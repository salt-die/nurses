from itertools import cycle

from nurses import ScreenManager, colors
from nurses.widgets import TextPad

with ScreenManager() as sm:
    tp = sm.root.new_widget(0, 0, 30, 50, border_style="curved", word_wrap=True, create_with=TextPad)
    rainbow = cycle(colors.rainbow_gradient())
    blue_green = colors.gradient(40, (0, 0, 255), (0, 255, 0), "blue_green")
    blue_green = cycle(blue_green + blue_green[::-1])
    red_blue = colors.pair_gradient(20, ((0, 0, 0), (255, 0, 0)), ((0, 0, 0), (0, 0, 255)), "red_blue")
    red_blue = cycle(red_blue + red_blue[::-1])

    c = tp._colors
    for i in range(30):
        c[i, 0] = next(blue_green)
    for i in range(50):
        c[29, i] = next(blue_green)
    for i in reversed(range(30)):
        c[i, -1] = next(blue_green)
    for i in reversed(range(50)):
        c[0, i] = next(blue_green)

    def crazy_colors():
        tr, bl, br = c[0, -1], c[-1, 0], c[-1, -1]
        c[0, 1:] = c[0, :-1]
        c[1:, -1] = c[:-1, -1]
        c[-1, :-1] = c[-1, 1:]
        c[:-1, 0] = c[1:, 0]
        c[ 1, -1] = tr
        c[-1, -2] = br
        c[-2,  0] = bl

        old = tp.color
        tp.color = next(rainbow)
        tp.pad_colors[tp.pad_colors == old] = tp.color

        tp.cursor_color = next(red_blue)

    tp.text = """’Twas brillig, and the slithy toves
      Did gyre and gimble in the wabe:
All mimsy were the borogoves,
      And the mome raths outgrabe.

“Beware the Jabberwock, my son!
      The jaws that bite, the claws that catch!
Beware the Jubjub bird, and shun
      The frumious Bandersnatch!"""

    sm.schedule(crazy_colors, delay=.1)
    sm.schedule(sm.root.refresh)
    sm.run()

    print(tp.text)