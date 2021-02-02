from nurses import ScreenManager
from nurses.widgets.textbox import Textbox


with ScreenManager() as sm:
    tb = sm.root.new_widget(0, 0, 3, 20, border="light", create_with=Textbox)

    async def print_result():
        print(await tb.gather())

    sm.run_soon(print_result())
    sm.schedule(sm.root.refresh)
    sm.run()
