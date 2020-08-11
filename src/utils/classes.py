from typing import Any, Callable, Union


class AbstractDictForcedKey(dict):
    def __init__(self, d=None, /, *, on_key_hook: Callable[[Union[int, str]], Any],
                 **kwargs):
        self.__on_key_hook = on_key_hook
        if d is not None:
            super().__init__(self.__convert_keys(d), **kwargs)

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
        new_d = {}
        for key, value in list(d.items()):
            new_d[self.__on_key_hook(key)] = value
        return new_d


class DictForcedStringKeys(AbstractDictForcedKey):
    def __init__(self, d=None, /, **kargs):
        super().__init__(d, on_key_hook=str, **kargs)
