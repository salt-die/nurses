class Singleton(type):
    """There can be only one...
    """
    _instances = { }

    def __call__(cls):
        instances = cls._instances
        if cls not in instances:
            instances[cls] = super().__call__()
        return instances[cls]