from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel


class ThriveResponse(BaseModel):
    error: bool
    data: list


class CampaignNameID(BaseModel):
    campId: int
    name: str
    cpc: float = None
    cpaMode: Union[bool, int] = None
    source: Optional[int] = None


class CampaignGETResponse(ThriveResponse):
    data: List[CampaignNameID]


class SourceVariableValue(BaseModel):
    param: str
    holder: str
    name: str


class SourcePostback(BaseModel):
    type: int
    code: str


class SourceBase(BaseModel):
    sourceId: int
    name: str


class SourceCache(SourceBase):
    camps: List[CampaignNameID]
    campCount: int


class Source(SourceCache):
    abbr: str
    postbacks: List[SourcePostback]
    variables: Dict[str, SourceVariableValue]


class SourceGETResponse(ThriveResponse):
    data: List[Source]
