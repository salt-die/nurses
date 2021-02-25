from random import random

from nurses import ScreenManager, colors


with ScreenManager() as sm:
    blue_to_purple = colors.gradient(20, (0, 255, 255), (103, 15, 215), "blue_to_purple")
    chart = sm.root.new_widget(create_with="Chart", maxlen=200, gradient=blue_to_purple, size_hint=(.5, .5), y_label=5)

    def update():
        chart.update(random() * 50)
        sm.root.refresh()

    sm.schedule(update, delay=.1)
    sm.run()
