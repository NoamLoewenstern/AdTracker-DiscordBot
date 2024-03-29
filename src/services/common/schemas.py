import re
from typing import Any, List, Type

from errors import PydanticParseObjError
from pydantic import BaseModel


class BaseModelSubscriptable(BaseModel):
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __delitem__(self, key):
        return self.__delattr__(key)

    def __contains__(self, item):
        return hasattr(self, item)

    @classmethod
    def parse_obj(cls: BaseModel, obj: Any) -> BaseModel:
        try:
            return super(BaseModelSubscriptable, cls).parse_obj(obj)
        except Exception as e:
            raise PydanticParseObjError(data=str(e))

    @classmethod
    def fields_list(cls) -> List[str]:
        from services.common.utils import extract_fields_from_class
        return extract_fields_from_class(cls)


BaseModel = BaseModelSubscriptable
