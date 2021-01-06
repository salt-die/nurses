class Singleton(type):
    """There can be only one...
    """
    instances = { }

    def __call__(cls):
        instances = Singleton.instances
        if cls not in instances:
            instances[cls] = super().__call__()
        return instances[cls]