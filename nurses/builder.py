from collections import ChainMap
from textwrap import dedent

from lark import Lark, Transformer
from lark.indenter import Indenter
from .layout import Layout
from .widget import Widget
from .screen_manager import ScreenManager


GRAMMAR = r"""
    ?start: _NL* python

    python: PYTHON _NL [_INDENT (widget | python)+ _DEDENT] -> eval_python
    widget: (NAME | PYTHON "as" NAME) _NL -> add_widget

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
    """
    Returns dict of widgets whose positions and dimensions are set by the layouts in the TAML-like build string.

    See Also
    --------
    /examples/layout_test.py

    Notes
    -----
    Indentation indicates a widget or layout belongs to an outer Layout.
    Each line is expected to be valid python for a Layout or a Widget (possibly followed by `as NAME`,
    where NAME is the name of the widget in the returned dict) or a name for a new widget.
    `ScreenManager()` is given the alias `sm`. `sm.new_widget` can be shortened to just `new_widget`.

    Examples
    --------
    >>> load_string(\"\"\"
    HSplit(3)
        title
        HSplit(-3)
            VSplit(.5)
                left
                right
            bottom
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
