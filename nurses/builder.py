from lark import Lark, Transformer
from lark.indenter import Indenter
from .layout import HSplit, VSplit
from .screen_manager import ScreenManager

grammar = r"""
    ?start: _NL* (hsplit | vsplit)

    hsplit: "HSplit" NUMBER _NL [_INDENT (widget | hsplit | vsplit) (widget | hsplit | vsplit) _DEDENT] -> add_hsplit
    vsplit: "VSplit" NUMBER _NL [_INDENT (widget | hsplit | vsplit) (widget | hsplit | vsplit) _DEDENT] -> add_vsplit
    widget: NAME _NL -> new_widget

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %declare _INDENT _DEDENT
    %ignore WS_INLINE

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
        self.sm = ScreenManager()

    def add_hsplit(self, args):
        row, _0, _1 = args
        h = HSplit(int(row) if row.isdigit() else float(row))
        h[0] = _0
        h[1] = _1
        return h

    def add_vsplit(self, args):
        col, _0, _1 = args
        v = VSplit(int(col) if col.isdigit() else float(col))
        v[0] = _0
        v[1] = _1
        return v

    def new_widget(self, args):
        self.widgets[str(args[0])] = w = self.sm.new_widget()
        return w

def load_string(layout):
    builder = LayoutBuilder()
    Lark(grammar, parser='lalr', postlex=LayoutIndenter(), transformer=builder).parse(layout)
    return builder.widgets
