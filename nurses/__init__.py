from importlib import import_module
from pathlib import Path

from .screen_manager import ScreenManager
from .widgets import Widget
from .widgets.layouts import Layout
from .builder import load_string

__all__ = "ScreenManager", "Widget", "Layout", "load_string"

def _loader(path, base):
    """
    HERE BE DRAGONS.

    This utility function will load all modules in a given path. We do this to populate
    Widget.types with all subclassed widgets and to populate Layout.layouts with all
    subclassed layouts.
    """
    for f in path.iterdir():
        if not f.is_file() or f.suffix == ".py":
            if not (module_name := f.stem).startswith("__"):
                import_module("." + module_name, base)

_loader(Path(__file__).parent / "widgets", "nurses.widgets")
_loader(Path(__file__).parent / "widgets" / "layouts", "nurses.widgets.layouts")
