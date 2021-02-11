from nurses import ScreenManager
from nurses.widgets import Menu


class MyMenu(Menu):
    open_close_key = ord('`')


with ScreenManager() as sm:
    sm.root.add_widget(
        MyMenu(0, 0, "Menu",
            (
                ("1st Entry", lambda: print("1st Entry Selected")),
                ("2nd Entry", lambda: print("2nd Entry Selected")),
                ("3rd Entry", lambda: print("3rd Entry Selected")),
            ),
            border_style="curved",
        )
    )

    sm.schedule(sm.root.refresh)
    sm.run()
