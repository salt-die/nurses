from collections import defaultdict
import curses

from ..observable import Observable


BORDER_STYLES = {
    "light" : "┌┐│─└┘",
    "heavy" : "┏┓┃━┗┛",
    "double": "╔╗║═╚╝",
    "curved": "╭╮│─╰╯",
}

_attr_to_callbacks = defaultdict(list)
def bind_to(*attrs):
    """Decorator that binds a method to attributes.  Attributes in `attrs` that aren't Observable will be redefined as Observables.
    """
    def decorator(func):
        for attr in attrs:
            _attr_to_callbacks[attr].append(func.__name__)
        return func
    return decorator


class Observer(type):
    """
    Warning: Experimental meta-programming ahead.

    This metaclass will search for any attributes what were added to `_attr_to_callbacks` with the `bind_to`
    decorator in a Widget class definition.  If those attributes aren't `Observable` they will be redefined as
    Observable so that the decorated methods can be bound to the attributes.
    """
    def __prepare__(name, bases):
        _attr_to_callbacks.clear()
        return {"bind_to": bind_to}

    def __new__(meta, name, bases, methods):
        del methods["bind_to"]
        # Attributes bound to callbacks that aren't `Observable` are made so:
        for attr, callbacks in _attr_to_callbacks.items():
            if attr not in methods:
                for base in bases:
                    if attr in base.__dict__:
                        if not isinstance(base.__dict__[attr], Observable):
                            prop = methods[attr] = Observable(base.__dict__[attr])
                        else:
                            prop = base.__dict__[attr]
                        break
                else:
                    prop = methods[attr] = Observable()
            elif not isinstance(methods[attr], Observable):
                prop = methods[attr] = Observable(methods[attr])
            else:
                prop = methods[attr]

            for callback in callbacks:
                prop.bind(name, callback)

        _attr_to_callbacks.clear()
        return super().__new__(meta, name, bases, methods)


class Widget(metaclass=Observer):
    """
    The base window for nurses.  A fancy wrapper around a curses window.

    Parameters
    ----------
    top, left, height, width: optional, positional only
        Upper and left-most coordinates of widget relative to parent, and dimensions of the widget.
        (the defaults are 0, 0, parent's max height, parent's max width)

    Other Parameters
    ----------------
    color: optional
       A curses color_pair, the default color of this widget. (the default is `curses.color_pair(0)`)

    pos_hint, size_hint: optional
        If a pos_hint or size_hint are given they will override any given pos or size arguments.  Hints are expected to be
        2-tuples of numbers or None.  Fractional arguments are interpreted as percentage of parent, and parent width or
        height will be added to negative arguments. (e.g., `size_hint=(.5, None)` means widget will be half as tall as parent
        and the width will come from the `width` arg.)

    transparent: optional
        If true, widget will overlay other widgets instead of overwrite them (whitespace will be "see-through"). (the default is `False`)

    Notes
    -----
    Coordinates are (y, x) (both a curses and a numpy convention) with y being vertical and increasing as you move down
    and x being horizontal and increasing as you move right.  Top-left corner is (0, 0)

    If some part of the widget moves out-of-bounds of the screen only the part that overlaps the screen will be drawn.

    Widget size is limited by screen size. (but ArrayPad isn't)
    """
    types = { }  # Registry of subclasses of Widget

    color = 0
    parent = None
    transparent = False
    border_style = None
    border_color = None
    pos_hint = None, None
    size_hint = None, None

    def __init_subclass__(cls):
        Widget.types[cls.__name__] = cls  # Register subclasses

        if not cls.on_press.__doc__:
            cls.on_press.__doc__ = Widget.on_press.__doc__

    def __init__(self, *args, **kwargs):
        self.children = [ ]
        self.group = defaultdict(list)
        self.window = None

        # Assign default values if len(args) < 4
        top, left, height, width, *rest = args + (None, None) if len(args) == 2 else args or (0, 0, None, None)

        self.top = top
        self.left = left
        self.height = height
        self.width = width

        for attr in tuple(kwargs):
            # This allows one to set class attributes with keyword-arguments. TODO: Document this.
            if hasattr(self, attr):
                setattr(self, attr, kwargs.pop(attr))

        super().__init__(*rest, **kwargs)

    __init__.__text_signature__ = (
        "($self, top=0, left=0, height=None, width=None, /, "
        "color=0, parent=None, transparent=False, border_style=None, border_color=None, "
        "pos_hint=(None, None), size_hint=(None, None), **kwargs)"
    )

    def getter(self, name, getter):
        """
        Replace an attribute lookup with a no-argument function call.

        ::Warning:: This modifies the class dictionary, replacing any non-Observable attribute with an Observable.
        """
        observable = getattr(type(self), name, None)
        if not isinstance(observable, Observable):
            setattr(type(self), name, observable := Observable(observable))

        observable.getters[self] = getter

    @bind_to("top")
    def _set_pos_hint_y(self):
        self.pos_hint = None, self.pos_hint[1]

    @bind_to("left")
    def _set_pos_hint_x(self):
        self.pos_hint = self.pos_hint[0], None

    @bind_to("height")
    def _set_size_hint_y(self):
        self.size_hint = None, self.size_hint[1]

    @bind_to("width")
    def _set_size_hint_x(self):
        self.size_hint = self.size_hint[0], None

    def update_geometry(self):
        """
        Set or reset the widget's geometry based on size or pos hints if they exist.

        Notes
        -----
        This should only be called by the widget's parent (usually when calling the parent's `add_widget` method).
        This will immediately return if there isn't a root widget, since screen size can't be determined yet.
        """
        if self.root is None:
            return

        border = int(self.parent.has_border)
        h, w = self.parent.height - 2 * border, self.parent.width - 2 * border

        top, left = self.pos_hint
        height, width = self.size_hint

        if top is not None:
            self.top = self.convert(top, h)
        if left is not None:
            self.left = self.convert(left, w)

        if height is not None:
            self.height = self.convert(height, h)
        if width is not None:
            self.width = self.convert(width, w)

        if self.height is None:
            self.height = h
        if self.width is None:
            self.width = w

        self.pos_hint = top, left
        self.size_hint = height, width

        if self.window is None:
            self.window = curses.newwin(self.height, self.width + 1)
            self.update_color(self.color)

            if self.has_border:
                self.border(self.border_style, self.border_color)

        for child in self.children:
            if child is not None:
                child.update_geometry()

    @bind_to("height", "width")
    def _resize(self):
        if self.window:
            self.window.resize(self.height, self.width + 1)

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def root(self):
        if self.parent is None:
            return None
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
        widget.update_geometry()

    def remove_widget(self, widget):
        self.children.remove(widget)

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
        return self.window.overlay if self.transparent else self.window.overwrite

    def refresh(self):
        """Redraw children's windows.
        """
        # Notably, we don't use curses.panels as they aren't available for windows-curses...
        # ...upside is we don't error when moving a widget off-screen.
        border = int(self.has_border)
        h, w = self.height, self.width
        for widget in self.children:
            if widget is None:
                continue

            widget.refresh()
            y, x = widget.top, widget.left
            src_t, des_t = (-y, border) if y < 0 else (0, y + border)
            src_l, des_l = (-x, border) if x < 0 else (0, x + border)
            des_h = min(h - 1, des_t + widget.height)
            des_w = min(w - 1, des_l + widget.width - 1)  # -1 compensates for the extra width of widget's window

            widget.overlay(self.window, src_t, src_l, des_t, des_l, des_h, des_w)

    @staticmethod
    def convert(value, bounds):
        """Utility function that converts a fractional or negative value to an absolute one.
        """
        if isinstance(value, float):
            value = int(value * bounds)
        return value + bounds if value < 0 else value

    @staticmethod
    def line(y1, x1, y2, x2):
        """Yields coordinates for a line from (y1, x1) to (y2, x2).
        """
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        if dy == 0:  # Horizontal
            gen = ((y1, x) for x in range(x1, x2 + 1))
        elif dx == 0: # Vertical
            gen = ((y, x1) for y in range(y1, y2 + 1))
        elif dy < dx:
            gen = Widget._line_low(y2, x2, y1, x1) if x1 > x2 else Widget._line_low(y1, x1, y2, x2)
        else:
            gen = Widget._line_high(y2, x2, y1, x1) if y1 > y2 else Widget._line_high(y1, x1, y2, x2)

        yield from gen

    @staticmethod
    def _line_low(y1, x1, y2, x2):
        dx = x2 - x1
        dy, yi = (2 * (y2 - y1), 1) if y2 >= y1 else (2 * (y1 - y2), -1)

        dif = dy - 2 * dx

        delta = dy - dx
        y = y1
        for x in range(x1, x2 + 1):
            yield y, x

            if delta > 0:
                y += yi
                delta += dif
            else:
                delta += dy

    @staticmethod
    def _line_high(y1, x1, y2, x2):
        dx, xi = (2 * (x2 - x1), 1) if x2 >= x1 else (2 * (x1 - x2), -1)
        dy = y2 - y1

        dif = dx - 2 * dy

        delta = dx - dy
        x = x1
        for y in range(y1, y2 + 1):
            yield y, x

            if delta > 0:
                x += xi
                delta += dif
            else:
                delta += dx

    @property
    def has_border(self):
        return bool(self.border_style)

    def border(self, style="light", color=None):
        """
        Draw a border on the edges of the widget.

        Parameters
        ----------
        style: optional
            The style of the border, can be one of `nurses.widget.BORDER_STYLES`. (the default is "light")

        color: optional
            The color of the border.  (the default is the widget's `color`)
        """
        # Curses windows already have a `border` method, but UnicodeEncodeErrors seem to happen when called with the
        # characters in BORDER_STYLES. So we add the border "by hand".
        self.border_style = style
        self.border_color = color

        window = self.window
        h, w = self.height - 1, self.width - 1
        ul, ur, v, hor, ll, lr = BORDER_STYLES[style]
        color = color or self.color

        window.addstr(0, 0, ul, color)
        window.addstr(0, w, ur, color)
        window.addstr(h, 0, ll, color)
        window.addstr(h, w, lr, color)

        for x in range(1, w):
            window.addstr(0, x, hor, color)
            window.addstr(h, x, hor, color)

        for y in range(1, h):
            window.addstr(y, 0, v, color)
            window.addstr(y, w, v, color)

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
