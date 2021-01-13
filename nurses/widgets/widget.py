from collections import ChainMap, defaultdict
import curses

from .. import managers  # Avoiding circular import.
from ..observable import Observable


_attr_to_callbacks = defaultdict(list)
def bind_to(*attrs):
    """Decorator that binds a method to attributes.
    """
    def decorator(func):
        for attr in attrs:
            _attr_to_callbacks[attr].append(func.__name__)
        return func
    return decorator


class WidgetMeta(type):
    def __prepare__(name, bases):
        _attr_to_callbacks.clear()
        return ChainMap({ }, {"bind_to": bind_to})

    def __new__(meta, name, bases, methods):
        methods = methods.maps[0]

        # Any attributes that are bound to callbacks but aren't properties
        # are made into properties.
        for attr, callbacks in _attr_to_callbacks.items():
            if attr not in methods:
                for base in bases:
                    if attr in base.__dict__:
                        if not isinstance(base.__dict__[attr], Observable):
                            # The attribute isn't bindable, so we make a bindable version in the class dict.
                            # We probably don't want to touch base.__dict__
                            prop = methods[attr] = Observable(base.__dict__[attr])
                        else:
                            prop = base.__dict__[attr]
                        break
                else:
                    # Attribute doesn't exist, so create it.
                    prop = methods[attr] = Observable()
            elif not isinstance(methods[attr], Observable):
                # The attribute isn't bindable, replace it with an Observable
                prop = methods[attr] = Observable(methods[attr])
            else:
                prop = methods[attr]

            for callback in callbacks:
                prop.bind(name, callback)

        _attr_to_callbacks.clear()

        return super().__new__(meta, name, bases, methods)


class Widget(metaclass=WidgetMeta):
    types = { }  # Registry of subclasses of Widget

    def __init_subclass__(cls):
        Widget.types[cls.__name__] = cls

        if not cls.on_press.__doc__:
            cls.on_press.__doc__ = Widget.on_press.__doc__

    def __init__(self, *args, pos_hint=None, size_hint=None, color=None, parent=None, transparent=False, **kwargs):
        self.parent = parent
        self.children = [ ]
        self.group = defaultdict(list)

        ###  vvv NEEDS TO BE MOVE TO UPDATE vvv
        if parent:
            h, w = parent.height, parent.width
        else:
            h, w = managers.ScreenManager().screen.getmaxyx()  # <- this can be removed altogether if we defer update until widget has a parent
            w -= 1

        top, left, height, width, *rest = args + (None, None) if len(args) == 2 else args or (0, 0, None, None)

        if pos_hint is not None:
            top, left = map(self.convert, pos_hint, (h, w))
        if size_hint is not None:
            height, width = map(self.convert, size_hint, (h, w))

        self.top = top
        self.left = left
        self.height = height or h
        self.width  = width or w

        self.window = curses.newwin(self.height, self.width + 1)
        ### ^^^ NEEDS TO BE MOVED TO UPDATE ^^^
        self.update_color(color or curses.color_pair(0))

        self.is_transparent = transparent

        for attr in tuple(kwargs):
            if hasattr(self, attr):
                setattr(self, attr, kwargs.pop(attr))

        super().__init__(*rest, **kwargs)

    def update(self):
        """Set or reset the widget's geometry based on size or pos hints if they exist.
        """
        if self.parent is None:
            return

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root

    def walk(self, start=None):
        if start is None:
            start = self.root

        for child in start.children:
            yield from self.walk(child)
        yield start

    @property
    def is_in_front(self):
        return self.parent and self.parent.children[-1] is self

    @property
    def is_in_back(self):
        return self.parent and self.parent.children[0] is self

    def pull_to_front(self, widget):
        """Given a widget or an index of a widget, widget is moved to top of widget stack (so it is drawn last).
        """
        widgets = self.children
        if isinstance(widget, int):
            widgets.append(widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.append(widget)

    def push_to_back(self, widget):
        """Given a widget or an index of a widget, widget is moved to bottom of widget stack (so it is drawn first).
        """
        widgets = self.children
        if isinstance(widget, int):
            widgets.insert(0, widgets.pop(widget))
        else:
            widgets.remove(widget)
            widgets.insert(0, widget)

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

    @property
    def overlay(self):
        return self.window.overlay if self.is_transparent else self.window.overwrite

    def refresh(self):
        """Redraw children's windows.
        """
        # Notably, we don't use curses.panels as they aren't available for windows-curses...
        # ...upside is we don't error when moving a widget off-screen.
        h, w = self.height, self.width
        for widget in self.children:
            widget.refresh()
            y, x = widget.top, widget.left
            src_t, des_t = (-y, 0) if y < 0 else (0, y)
            src_l, des_l = (-x, 0) if x < 0 else (0, x)
            des_h = min(h - 1, des_t + widget.height)
            des_w = min(w - 1, des_l + widget.width - 1)  # -1 compensates for the extra width of widget's window

            widget.overlay(self.window, src_t, src_l, des_t, des_l, des_h, des_w)

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

    def update_color(self, color):
        self.color = color
        self.window.attrset(color)
