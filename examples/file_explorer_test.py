from nurses import ScreenManager


with ScreenManager() as sm:
    fe = sm.root.new_widget(5, 5, 10, 20, border_style="light", create_with="FileExplorer")

    async def get_file():
        fe.open_explorer()
        while fe.file is None:
            await sm.next_task()

    sm.run(get_file())

print(fe.file.name)