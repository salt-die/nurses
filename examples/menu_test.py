from nurses import ScreenManager, colors
from nurses.widgets import Menu, Menubar


class MyMenu(Menu):
    open_close_key = ord('`')


with ScreenManager() as sm:

    sm.root.add_widget(
        Menubar(
            MyMenu("Menu1",
                (
                    ("1st Entry", lambda: print("1st Entry Selected")),
                    ("2nd Entry", lambda: print("2nd Entry Selected")),
                    ("3rd Entry", lambda: print("3rd Entry Selected")),
                ),
            ),
            MyMenu("Menu2",
                (
                    ("1st Entry", lambda: print("1st Entry Selected")),
                    ("2nd Entry", lambda: print("2nd Entry Selected")),
                    ("3rd Entry", lambda: print("3rd Entry Selected")),
                ),
            ),
            MyMenu("Menu3",
                (
                    ("1st Entry", lambda: print("1st Entry Selected")),
                    ("2nd Entry", lambda: print("2nd Entry Selected")),
                    ("3rd Entry", lambda: print("3rd Entry Selected")),
                ),
            ),
            color=colors.BLACK_ON_WHITE,
            selected_color=colors.WHITE_ON_BLACK,
        )
    )

    sm.schedule(sm.root.refresh)
    sm.run()
