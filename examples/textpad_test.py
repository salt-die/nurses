from nurses import ScreenManager
from nurses.widgets import TextPad

with ScreenManager() as sm:
    tp = sm.root.new_widget(0, 0, 30, 50, rows=50, cols=150, border_style="curved", create_with=TextPad)

    sm.schedule(sm.root.refresh)
    sm.run()

    print(tp.text)