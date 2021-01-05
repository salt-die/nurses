from collections import ChainMap
from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter

from .widget import Widget
from .screen_manager import ScreenManager


GRAMMAR = r"""
    ?start: _NL* python

    python: PYTHON ("as" CNAME)? _NL [_INDENT python+ _DEDENT] -> eval_python

    %import common.CNAME
    %import common.WS_INLINE
    %import common.SH_COMMENT
    NAME: CNAME ("." CNAME)*
    PYTHON: NAME "(" /.*/ ")"

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
        self.locals = ChainMap(Widget.types, Widget.types["Layout"].layouts, {"sm": ScreenManager()})

    def eval_python(self, args):
        obj, *rest = args
        obj = eval(str(obj), globals(), self.locals)
        if rest:
            if isinstance(rest[0], str):
                self.widgets[str(rest.pop(0))] = obj
            for child in rest:
                obj.add_widget(child)
        return obj

def load_string(build_string):
    """
    Returns dict of widgets whose positions and dimensions are set by the layouts in the TAML-like build string.

    See Also
    --------
    /examples/layout_test.py

    Notes
    -----
    Indentation indicates a widget or layout belongs to an outer Layout.
    Each line is expected to be valid python for a Layout or a Widget (possibly followed by `as NAME`,
    where NAME is the name of the widget in the returned dict).

    Examples
    --------
    >>> load_string(\"\"\"
    HSplit(3)
        ArrayWin() as title
        HSplit(-3)
            VSplit(.5)
                ArrayWin() as left
                ArrayWin() as right
            ArrayWin() as bottom
    \"\"\")

    This would return a dictionary of widgets with keys ("title", "left", "right", "bottom").
    The widgets positions and dimensions would be similar to:

    +-----------------+
    | title           |
    +-----------------+
    | left   | right  |
    |        |        |
    |        |        |
    +-----------------+
    | bottom          |
    +-----------------+
    """
    # Alternatively, we could cache the builder and parser and just reset the builder's widgets for each new call to `load_string`
    builder = LayoutBuilder()
    parser = Lark(GRAMMAR, parser='lalr', postlex=LayoutIndenter(), transformer=builder)
    layout = parser.parse(dedent(build_string))
    layout.update()
    return builder.widgets
