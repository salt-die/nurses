from .layout import Layout


class Stack(Layout):
    def __init__(self, count, *, size=None, size_hint=(None, None), vertical=False, horizontal=False, min_height=1):
        super().__init__()
