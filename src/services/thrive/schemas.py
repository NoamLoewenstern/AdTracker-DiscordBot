from typing import Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CampaignBasicInfo(BaseModel):
    id: int = Field(alias='campId')
    campId: int
    name: str
    cpc: float = None
    cpaMode: Union[bool, int] = None


class CampaignNameID(CampaignBasicInfo):
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


class CampaignNameID(BaseModel):
    data: List[Source]


class TagArray(BaseModel):
    tagId: int
    name: str


class CloakingOptions(BaseModel):
    desktop: int
    mobile: int
    tablet: int


class CampaignGeneralInfo(CampaignBasicInfo):
    sourceId: int
    sourceName: str
    sourceAbbr: str
    typeId: int
    typeName: str
    rotTemplateId: int
    rotTemplateName: str = None
    rulesEnabled: int
    tagsArray: List[TagArray]
    tagsList: str
    startDateStr: str
    archived: int
    archiveDateStr: str
    customToken: str
    cloakingOpt: int
    cloakingOptions: CloakingOptions
    uri: str
    campIdHashQuery: str
    testClick: int
    testConv: int
    # sourceVariables
    # branches
    # aiData


class CampaignExtendedInfoStats(CampaignGeneralInfo):
    clicks: int
    cost: float
    cpc: float
    thru: int
    conv: int
    rev: float
    ctr: float
    profit: float
    roi: float
    epc: float
    cvr: float
    epa: float

    @property
    def cpa(self):
        if self.conv == 0:
            return 0
        return self.cost / self.conv

    def dict(self, *args, **kwargs):
        return {**super().dict(*args, **kwargs),
                'cpa': self.cpa}


class SideCarTimeData(BaseModel):
    start: int
    end: int
    from_: str
    to: str
    timezone: str

    class Config:
        fields = {
            'from_': 'from'
        }


class CampaignStats(BaseModel):
    data: List[CampaignExtendedInfoStats]
    sidecar: SideCarTimeData
