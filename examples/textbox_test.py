from nurses import ScreenManager
from nurses.widgets import Textbox


with ScreenManager() as sm:
    tb = sm.root.new_widget(0, 0, 20, border="curved", create_with=Textbox)

    async def print_result():
        print(await tb.gather())

    sm.run(print_result())
