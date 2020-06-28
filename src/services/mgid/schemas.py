
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class TrackingOptions(BaseModel):
    utm_campaign: str
    utm_source: str
    utm_medium: str
    utm_custom: str


class LimitsFilter(BaseModel):
    limitType: str
    dailyLimit: int
    overallLimit: int
    splitDailyLimitEvenly: int


class CampaignStatistics(BaseModel):
    click: int
    wages: int


class Filter(BaseModel):
    filterType: str


class WidgetsFilterUid(Filter):
    widgets: List[str]


class IPsFilter(Filter):
    ips: List[str]


class DomainsFilter(Filter):
    domainsNames: List[str]


class CampaignStatus(BaseModel):
    id: int
    name: str
    reason: str


class CampaignData(BaseModel):
    id: int = None
    name: str = None
    language: int = None
    status: CampaignStatus = None
    domainsFilter: DomainsFilter = None
    ipsFilter: IPsFilter = None
    widgetsFilterUid: WidgetsFilterUid = None
    limitsFilter: LimitsFilter = None
    trackingOptions: TrackingOptions = None
    targets: Dict[str, str] = None
    languageTargeting: List[str] = None
    whenAdd: str = None
    campaignType: str = None


class CampaignGETResponse(BaseModel):
    __root__: Dict[str, CampaignData]


class AcceptedClick(BaseModel):
    time = str
    ip = str
    teaserId = int
    sourceId = int
    informerUid = int
    country = str
    region = str
    price = float


class CampaignStatDayDetailsSummary(BaseModel):
    numberOfClicks: int
    numberOfAcceptedClicks: int
    fundsEarned: float
    numberOfRejectedClicks: int
    numberOfShows: int
    # acceptedClicks: List[AcceptedClick]


class CampaignStatDayDetailsStatistics(BaseModel):
    summary: CampaignStatDayDetailsSummary


class CampaignStatDayDetailsGETResponse(BaseModel):
    id = int
    statistics: CampaignStatDayDetailsStatistics


class CampaignStat(BaseModel):
    id: int = Field(alias='campaignId')
    campaignId: int
    imps: int
    clicks: int
    spent: float
    avcpc: float
    interest: float = None
    interestCost: float = None
    decision: float = None
    decisionCost: float = None
    buying: float
    buyingCost: float
    revenue: float
    epc: float
    profit: float


class StatsAllCampaignGETResponse(BaseModel):
    dateInterval: str
    campaigns_stat: Dict[str, CampaignStat] = Field(alias='campaigns-stat')
