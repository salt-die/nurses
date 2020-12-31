from collections import ChainMap
from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter
from .layout import Layout
from .widget import Widget
from .screen_manager import ScreenManager


grammar = r"""
    ?start: _NL* python

    python: PYTHON _NL [_INDENT (widget | python)+ _DEDENT] -> eval_python
    widget: (NAME | PYTHON "as" NAME) _NL -> add_widget

    %import common.CNAME
    %import common.WS_INLINE
    %import common.SH_COMMENT
    NAME: CNAME ("." CNAME)*
    PYTHON: (NAME | "new_widget") "(" /.*/ ")"

    %declare _INDENT _DEDENT
    %ignore WS_INLINE
    %ignore _NL* SH_COMMENT

    _NL: /(\r?\n[\t ]*)+/
"""


class LayoutIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8


class LayoutBuilder(Transformer):
    def __init__(self):
        self.widgets = {}
        self._locals = ChainMap(Layout.layouts, Widget.types, {"sm": ScreenManager(), "new_widget": ScreenManager().new_widget})

    def eval_python(self, args):
        obj = eval(str(args[0]), globals(), self._locals)
        if isinstance(obj, Layout):
            obj.panels = args[1:]
        return obj

    def add_widget(self, args):
        name = str(args[-1])
        self.widgets[name] = ScreenManager().new_widget() if len(args) == 1 else self.eval_python(args)
        return self.widgets[name]


def load_string(build_string):
    # Alternatively, we could cache the builder and parser and just reset the builder's widgets for each new call to `load_string`
    builder = LayoutBuilder()
    parser = Lark(grammar, parser='lalr', postlex=LayoutIndenter(), transformer=builder)
    layout = parser.parse(dedent(build_string))
    layout.update()
    return builder.widgets
