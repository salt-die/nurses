from collections import ChainMap
from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter

from .managers import colors, ScreenManager
from .widgets import Widget


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
    def __init__(self, globals):
        self.widgets = {}
        self.globals = globals
        self.locals = ChainMap(Widget.types, Widget.types["Layout"].layouts, {"colors": colors})

    def eval_python(self, args):
        obj, *rest = args
        obj = eval(str(obj), self.globals, self.locals)
        if rest:
            if isinstance(rest[0], str):
                self.widgets[str(rest.pop(0))] = obj
            for child in rest:
                obj.add_widget(child)
        return obj


def load_string(build_string, globals={ }, *, root=True):
    """
    Returns dict of widgets whose positions and dimensions are set by the layouts in the TAML-like build string.
    `globals` is an optional dictionary that provides context to code executed in the build string.

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
    builder = LayoutBuilder(globals)
    parser = Lark(GRAMMAR, parser='lalr', postlex=LayoutIndenter(), transformer=builder)
    layout = parser.parse(dedent(build_string))
    layout.update()
    if root:
        ScreenManager().root.add_widget(layout)
    return builder.widgets
