# TODO: Find a way to init widgets with more options in the build string
from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter
from .layout import HSplit, VSplit
from .screen_manager import ScreenManager

grammar = r"""
    ?start: _NL* (hsplit | vsplit)

    hsplit: "HSplit" SIGNED_NUMBER _NL [_INDENT (widget | hsplit | vsplit) (widget | hsplit | vsplit) _DEDENT] -> add_hsplit
    vsplit: "VSplit" SIGNED_NUMBER _NL [_INDENT (widget | hsplit | vsplit) (widget | hsplit | vsplit) _DEDENT] -> add_vsplit
    widget: NAME _NL -> new_widget

    %import common.CNAME -> NAME
    %import common.SIGNED_NUMBER
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
        row, top, bottom = args
        try:
            row = int(row)
        except ValueError:
            row = float(row)
        h = HSplit(row)
        h.panels = [top, bottom]
        return h

    def add_vsplit(self, args):
        col, left, right = args
        try:
            col = int(col)
        except ValueError:
            col = float(col)
        v = VSplit(col)
        v.panels = [left, right]
        return v

    def new_widget(self, args):
        self.widgets[str(args[0])] = w = self.sm.new_widget()
        return w


def load_string(layout_string):
    builder = LayoutBuilder()
    parser = Lark(grammar, parser='lalr', postlex=LayoutIndenter(), transformer=builder)
    parser.parse(dedent(layout_string)).update()
    return builder.widgets
