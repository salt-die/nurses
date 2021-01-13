from collections import defaultdict

NO_DEFAULT = object()


class Observable:
    """
    :class: Observables are simple properties that one can bind methods to.

    Notes
    -----
    We store method names instead of methods themselves.  This so we can dynamically patch methods on widgets and the new
    method will be called.  This is relevant in ArrayWin.__init__ for example, when we need to temporarily disable `_resize`.
    """
    def __init__(self, default=NO_DEFAULT):
        self.default = default
        self.methods = defaultdict(dict)
        self.callbacks = { }

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        self.dispatch(instance)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if self.name in instance.__dict__:
            return instance.__dict__[self.name]

        if self.default is not NO_DEFAULT:
            return self.default

        return self

    def dispatch(self, instance):
        # Build list of dispatches from _mro_ if it doesn't exist
        name = type(instance).__name__
        if name not in self.callbacks:
            d = { }
            for base in reversed(type(instance).__mro__):
                d.update(self.methods.get(base.__name__, { }))
            self.callbacks[name] = list(d)

        for callback in self.callbacks[name]:
            getattr(instance, callback)()

    def bind(self, class_name, method_name):
        self.methods[class_name][method_name] = None
