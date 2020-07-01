from typing import Callable, List, Optional, Union

from ..common.schemas import BaseModel


class CampaignBaseData(BaseModel):
    id: str
    name: str


class Budget(BaseModel):
    type: str = None
    amount: int = None


class State(BaseModel):
    state: str
    actions: List[Union["EDIT", "PAUSE", "CHANGE_BID", "DUPLICATE", "DELETE"]]


class Details(CampaignBaseData):
    # details:
    geo: str
    type: str
    trafficSourceType: List[str]
    url: str
    totalBudget: Budget
    dailyBudget: Budget
    bid: float
    state: State
    optimisation: str
    demographicTargeting: bool
    privateDeal: bool


class Stats(BaseModel):
    spent: float
    payout: float
    redirects: int
    clicks: int = None
    conversions: int
    averageBid: float = None
    availableVisits: int = None
    returnOfInvestment: float = None
    winRatio: float = None
    ecpa: float = None


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


class ExtendedStats(Stats):
    # includes: Stats
    # includes: Details Data:
    id: str
    name: str
    geo: str
    type: str
    totalBudget: Budget
    dailyBudget: Budget
    bid: float
    state: State


class ListExtendedStats(BaseModel):
    __root__: List[ExtendedStats]
