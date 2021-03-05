from nurses import ScreenManager, colors
from nurses.widgets import FileExplorer, Menubar, TextPad


with ScreenManager() as sm:
    fe = sm.root.new_widget(size_hint=(.5, .5), pos_hint=(.5, .5), border_style="light", create_with="FileExplorer")

    async def get_file():
        ...

    file = (
        ("Open...", lambda: ...),
        ("Save", lambda: ...),
        ("Save As...", lambda: ...),
    )

    edit = (

    )