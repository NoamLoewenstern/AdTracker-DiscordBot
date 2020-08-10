from typing import Any, Type

from pydantic import BaseModel

from errors import PydanticParseObjError


class BaseModelSubscriptable(BaseModel):
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, item):
        return hasattr(self, item)

    @classmethod
    def parse_obj(cls: Type['Model'], obj: Any) -> 'Model':
        try:
            return super(BaseModelSubscriptable, cls).parse_obj(obj)
        except Exception as e:
            raise PydanticParseObjError(data=str(e))


BaseModel = BaseModelSubscriptable
