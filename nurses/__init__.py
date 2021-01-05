from importlib import import_module
from pathlib import Path

from .screen_manager import ScreenManager
from .widget import Widget
from .widget.layout import Layout
from .builder import load_string

__all__ = "ScreenManager", "Widget", "Layout", "load_string"

def loader(path, base):
    """
    HERE BE DRAGONS.

    This utility function will load all modules in a given path. We do this to populate
    Widget.types with all subclassed widgets and to populate Layout.layouts with all
    subclassed layouts.
    """
    for f in path.iterdir():
        module_name = f.stem
        if module_name != "__init__":
            import_module("." + module_name, base)

loader(Path(__file__).parent / "widget", "nurses.widget")
loader(Path(__file__).parent / "widget" / "layout", "nurses.widget.layout")

del import_module
del Path
del loader