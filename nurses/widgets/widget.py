from collections import defaultdict
import curses

from .. import screen_manager as sm  # Avoiding circular import.


class Widget:
    types = { }  # Registry of subclasses of Widget

    def __init_subclass__(cls):
        Widget.types[cls.__name__] = cls

        if not cls.on_press.__doc__:
            cls.on_press.__doc__ = Widget.on_press.__doc__

    def __init__(self,
        top=0, left=0, height=None, width=None, *,
        parent=None, transparent=False, window=None, **kwargs
    ):
        self.parent = parent
        self.children = [ ]
        self.group = defaultdict(list)

        if window:
            h, w = window.getmaxyx()
        elif parent:
            h, w = parent.height, parent.width
        else:
            h, w = sm.ScreenManager().screen.getmaxyx()
            w -= 1

        convert = self.convert
        self.top    = convert( top, h)
        self.left   = convert(left, w)
        self.height = convert(height or h, h)
        self.width  = convert(width or w, w)

        # Curses will return ERR if creating a window wider or taller than our screen.
        # We can get around this by creating a tiny window and then resizing to be as large as we'd like.
        # We may use pads in the future instead.
        # TODO: Test this hack on linux.
        self.window = window or curses.newwin(1, 1)
        self.window.resize(self.height, self.width + 1)

        self.is_transparent = transparent

    def add_widget(self, widget):
        self.children.append(widget)
        widget.parent = self

    def new_widget(self, *args, group=None, create_with=None, **kwargs):
        """
        Create a new widget and append to widget stack.  Can group widgets if providing a hashable group.
        To create a new subclassed widget use `create_with=MyWidget` or `create_with="MyWidget"` (pass the class or the class' name).
        """
        if create_with is None:
            create_with = Widget
        elif isinstance(create_with, str):
            create_with = Widget.types[create_with]

        widget = create_with(*args, parent=self, **kwargs)

        self.add_widget(widget)
        if group is not None:
            self.group[group].append(widget)

        return widget

    def on_top(self, widget):
        """Given a widget or an index of a widget, widget is moved to top of widget stack (so it is drawn last).
        """
        widgets = self.children
        if isinstance(widget, int):
            widgets.append(widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.append(widget)

    def on_bottom(self, widget):
        """Given a widget or an index of a widget, widget is moved to bottom of widget stack (so it is drawn first).
        """
        widgets = self.children
        if isinstance(widget, int):
            widgets.insert(0, widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.insert(0, widget)

    @property
    def overlay(self):
        return self.window.overlay if self.is_transparent else self.window.overwrite

    def refresh(self):
        """Redraw children's windows.
        """
        # Notably, we don't use curses.panels as they aren't available for windows-curses...
        # ...upside is we don't error when moving a widget off-screen.

        if self.parent is None:
            self.window.erase()

        h, w = self.height, self.width
        for widget in self.children:
            widget.refresh()
            y, x = widget.top, widget.left
            src_t, des_t = (-y, 0) if y < 0 else (0, y)
            src_l, des_l = (-x, 0) if x < 0 else (0, x)
            des_h = min(h - 1, des_t + widget.height)
            des_w = min(w - 1, des_l + widget.width - 1)  # -1 compensates for the extra width of widget's window

            widget.overlay(self.window, src_t, src_l, des_t, des_l, des_h, des_w)

        if self.parent is None:
            self.window.refresh()

    @staticmethod
    def convert(pos, bounds):
        """Utility function that converts a fractional or negative position to an absolute one.
        """
        if isinstance(pos, float):
            pos = round(pos * bounds)
        return pos + bounds if pos < 0 else pos

    def dispatch(self, key):
        for widget in reversed(self.children):
            if widget.on_press(key) or widget.dispatch(key):
                return True

    def on_press(self, key):
        """
        Called when a key is pressed and no widgets above this widget have handled the press.
        A press is handled when a widget's `on_press` method returns True.
        """
        try:
            return super().on_press(key)
        except AttributeError:
            pass
