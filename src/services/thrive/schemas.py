from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CampaignNameID(BaseModel):
    id: int = Field(alias='campId')
    campId: int
    name: str
    cpc: float = None
    cpaMode: Union[bool, int] = None
    source: Optional[int] = None


class CampaignGETResponse(BaseModel):
    error: bool
    data: List[CampaignNameID]


class SourceVariableValue(BaseModel):
    param: str
    holder: str
    name: str


class SourcePostback(BaseModel):
    type: int
    code: str


class SourceBase(BaseModel):
    id: int = Field(alias='sourceId')
    sourceId: int
    name: str


class SourceCache(SourceBase):
    camps: List[CampaignNameID]
    campCount: int


class Source(SourceCache):
    abbr: str
    postbacks: List[SourcePostback]
    variables: Dict[str, SourceVariableValue]


class SourceGETResponse(BaseModel):
    data: List[Source]
