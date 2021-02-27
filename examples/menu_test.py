from nurses import ScreenManager, colors


with ScreenManager() as sm:

    menu = (
        ("1st Entry", lambda: print("1st Entry Selected")),
        ("2nd Entry", lambda: print("2nd Entry Selected")),
        ("3rd Entry", lambda: print("3rd Entry Selected")),
    )

    sm.root.new_widget(
        ("Menu1", menu),
        ("Menu2", menu),
        ("Menu3", menu),
        color=colors.BLACK_ON_WHITE,
        selected_color=colors.WHITE_ON_BLACK,
        create_with="Menubar",
    )

    sm.schedule(sm.root.refresh)
    sm.run()
