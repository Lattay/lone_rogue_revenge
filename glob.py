def register_singleton(cls):
    class Singleton(cls):
        _uniq = None

        def __new__(class_):
            if class_._uniq is None:
                class_._uniq = cls.__new__(Singleton)
            return class_._uniq
    return Singleton()


@register_singleton
class globs:
    def __init__(self):
        self._forum = {}

    def clear(self):
        self._forum = {}

    def register(self, name, obj):
        self._forum[name] = obj

    def __getattr__(self, name):
        if name in self._forum:
            return self._forum[name]
        else:
            return self.__getattribute__(name)

    def __setattr__(self, name, val):
        if name == "_forum":
            super().__setattr__(name, val)
        self._forum[name] = val
