from nurses import ScreenManager, colors

NOT_IMPLEMENTED = lambda: None


with ScreenManager() as sm:
    fe = sm.root.new_widget(size_hint=(.5, .5), pos_hint=(.25, .25), border_style="light", create_with="FileExplorer")
    fe.close_explorer()
    de = sm.root.new_widget(size_hint=(.5, .5), pos_hint=(.25, .25), border_style="light", create_with="DirExplorer")
    de.close_explorer()

    tp = sm.root.new_widget(1, 0, size_hint=(None, 1.0), create_with="TextPad")
    tp.getter("height", lambda: sm.root.height - 1)
    tp._resize()

    async def open_file():
        fe.open_explorer()
        while fe.file is None:
            await sm.next_task()

        with open(fe.file) as f:
            tp.text = f.read()

    # Menus for menu bar:
    file = (
        ("Open...", lambda: sm.run_soon(open_file())),
        ("Save", NOT_IMPLEMENTED),
        ("Save As...", NOT_IMPLEMENTED),
    )

    edit = (
        ("Cut", NOT_IMPLEMENTED),
        ("Copy", NOT_IMPLEMENTED),
        ("Paste", NOT_IMPLEMENTED),
    )

    menubar = sm.root.new_widget(
        ("File", file),
        ("Edit", edit),
        color=colors.BLACK_ON_WHITE,
        selected_color=colors.WHITE_ON_BLACK,
        border_style="curved",
        create_with="Menubar"
    )

    sm.schedule(sm.root.refresh)
    sm.run()
