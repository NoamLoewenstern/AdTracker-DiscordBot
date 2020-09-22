import re
from typing import Callable, List, Optional, Union

from pydantic import Field, validator

from ..common.common_service import TargetType
from ..common.platform import get_thrive_id_from_camp
from ..common.schemas import BaseModel


class CampaignBaseData(BaseModel):
    id: str
    name: str

    @property
    def target_type(self) -> str:
        for _target_type in [
            TargetType.DESKTOP,
            TargetType.MOB,
            TargetType.MOBILE,
        ]:
            if re.search(f'(?<!\\w){_target_type}(?!\\w)', self.name, re.IGNORECASE):
                return _target_type.value
        return TargetType.BOTH.value

    @property
    def thrive_id(self):
        return get_thrive_id_from_camp({'id': self.id, 'name': self.name}, platform='zeropark', raise_=False)

    def dict(self, *args, **kwargs):
        return {**super().dict(*args, **kwargs),
                'target_type': self.target_type,
                'thrive_id': self.thrive_id}


class Budget(BaseModel):
    type: str = None
    amount: int = None


class State(BaseModel):
    state: str
    actions: List[Union["EDIT", "PAUSE", "CHANGE_BID", "DUPLICATE", "DELETE"]]


class Details(CampaignBaseData):
    # details:
    geo: str = None
    type: str = None
    trafficSourceType: List[str] = None
    url: str = None
    totalBudget: Budget = None
    dailyBudget: Budget = None
    bid: float = None
    state: State = None
    optimisation: str = None
    demographicTargeting: bool = None
    privateDeal: bool = None


class Stats(BaseModel):
    spent: float
    payout: int
    redirects: int
    conversions: int
    clicks: int = 0
    platform_clicks: int = Field(0, alias='clicks')
    averageBid: float = None
    availableVisits: int = None
    returnOfInvestment: float = None
    winRatio: float = None
    ecpa: float = None

    @validator('ecpa')
    def prevent_none(cls, v):
        if v is None:
            return 0


class CampaignElement(BaseModel):
    details: Details
    stats: Stats
    trackingConversions: bool = None
    currentConversionCappingConversions: bool = None


class Summary(Stats):
    impressions: int = None


class CampaignStatsResponse(BaseModel):
    page: int = None
    total: int = None
    limit: int = None
    summary: Summary = None
    elements: List[CampaignElement] = None


class ExtendedStats(Details):
    # includes: Details
    # includes: Stats Data:
    spent: float
    payout: float
    redirects: int
    conversions: int
    clicks: int = 0
    platform_clicks: int = Field(0, alias='clicks')
    averageBid: float = None
    availableVisits: int = None
    returnOfInvestment: float = None
    winRatio: float = None
    ecpa: float = None

    @validator('ecpa')
    def prevent_none(cls, v):
        if v is None:
            return 0


class ListExtendedStats(BaseModel):
    __root__: List[ExtendedStats]


class MergedWithThriveStats(ExtendedStats):
    # thrive stat data:
    thrive_clicks: int = None
    platform_clicks: int = None
    cost: float
    conv: int
    ctr: float
    roi: float
    rev: float
    profit: float
    # non default fields for merge data with thrive
    imps: int = None
    cpc: float = None
    thru: int = None
    cvr: float = None
    # epc: float # platfrom contradiction
    # epa: float # platfrom contradiction
    # cpa: int # property

    @property
    def cpa(self) -> float:
        if self.conv == 0:
            return 0
        return self.cost / self.conv

    @property
    def revenue(self) -> float:
        return self.rev

    def dict(self, *args, **kwargs):
        return {
            **super().dict(*args, **kwargs),
            'cpa': self.cpa,
            'revenue': self.revenue,
        }


class TargetStats(BaseModel):
    spent: float
    payout: int
    aversageBid: float = None
    redirects: int
    conversions: int
    returnOfInvestment: float = None
    ecpa: float = None

    @validator('ecpa')
    def prevent_none(cls, v):
        if v is None:
            return 0


class BidPosition(BaseModel):
    topBid: float = None
    position: str = None


class TargetData(BaseModel):
    id: str
    target: str
    source: str
    sourceId: str
    trafficSourceType: str
    stats: TargetStats
    state: State
    bidPosition: BidPosition


class TargetStatsMergedData(TargetStats):
    id: str
    target: str
    source: str
    sourceId: str
    trafficSourceType: str
    state: State = None


class TargetStatsByCampaignResponse(BaseModel):
    page: int = None
    total: int = None
    limit: int = None
    summary: Summary = None
    elements: List[TargetData] = None
