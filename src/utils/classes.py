class DictForcedStringKeys(dict):
    def __init__(self, d=None):
        if d is not None:
            super().__init__(self.__convert_keys(d))

    def __getitem__(self, key):
        return super().__getitem__(str(key))

    def __setitem__(self, key, value):
        return super().__setitem__(str(key), value)

    def get(self, key, default):
        return super().get(str(key), default)

    def setdefault(self, key, default):
        return super().setdefault(str(key), default)

    def __contains__(self, key):
        return super().__contains__(str(key))

    def update(self, d):
        return super().update(self.__convert_keys(d))

    def __convert_keys(self, d: dict):
        for key, value in list(d.items()):
            d[str(key)] = value
        return d
