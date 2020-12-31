from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter
from .layout import HSplit, VSplit
from .screen_manager import ScreenManager

# TODO: Add optional arguments to widgets and hsplit in the grammar
# TODO: Convert optional arguments automatically to int/float based on signature of layout or widget (probably through typehints)
# TODO: Layout tokens should be auto-generateed from .layout.Layout.layouts
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

    @classmethod
    def add_hsplit(cls, args):
        return cls.add_split(HSplit, args)

    @classmethod
    def add_vsplit(cls, args):
        return cls.add_split(VSplit, args)

    @staticmethod
    def add_split(split, args):
        line, panel_1, panel_2 = args

        line = float(line) if '.' in line else int(line)
        layout = split(line)
        layout.panels = [panel_1, panel_2]
        return layout

    def new_widget(self, args):
        widget = str(args[0])
        self.widgets[widget] = ScreenManager().new_widget()
        return self.widgets[widget]


def load_string(build_string):
    # Alternatively, we could cache the builder and parser and just reset the builder's widgets for each new call to `load_string`
    builder = LayoutBuilder()
    parser = Lark(grammar, parser='lalr', postlex=LayoutIndenter(), transformer=builder)
    layout = parser.parse(dedent(build_string))
    layout.update()
    return builder.widgets
