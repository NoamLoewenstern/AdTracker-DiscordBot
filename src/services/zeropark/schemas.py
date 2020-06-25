from typing import Callable, List, Optional, Union

from pydantic import BaseModel


class Budget(BaseModel):
    type: str = None
    amount: int = None


class State(BaseModel):
    state: str
    actions: List[Union["EDIT", "PAUSE", "CHANGE_BID", "DUPLICATE", "DELETE"]]


class Details(BaseModel):
    # details:
    id: str
    name: str
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
    averageBid: float = None
    redirects: int
    conversions: int
    availableVisits: int = None
    returnOfInvestment: float
    winRatio: float = None
    ecpa: float = None


class CampaignElement(BaseModel):
    details: Details
    stats: Stats
    trackingConversions: bool = None
    currentConversionCappingConversions: bool = None


class Summary(BaseModel):
    spent: float
    payout: float
    averageBid: float
    redirects: int
    clicks: int
    conversions: int
    impressions: int
    # clickThroughRate: float = None
    returnOfInvestment: float
    ecpa: float


class CampaignStatsResponse(BaseModel):
    page: int
    total: int
    limit: int
    summary: Summary
    elements: List[CampaignElement]
