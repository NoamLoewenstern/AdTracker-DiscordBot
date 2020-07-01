from pydantic import BaseModel


class BaseModelSubscriptable(BaseModel):
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, item):
        return hasattr(self, item)


BaseModel = BaseModelSubscriptable
