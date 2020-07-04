from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import Field

from errors import InvalidPlatormCampaignName
from services.thrive.schemas import CampaignExtendedInfoStats

from ..common.common_service import TargetType
from ..common.platform import get_thrive_id_from_camp
from ..common.schemas import BaseModel


class CampaignBaseData(BaseModel):
    id: int = Field(None, alias='campaignId')
    campaignId: int = None
    name: str = None

    @property
    def target_type(self) -> str:
        for target_type in [
            TargetType.DESKTOP,
            TargetType.MOBILE,
        ]:
            if target_type in self.name:
                return target_type.value
        return TargetType.BOTH.value

    @property
    def thrive_id(self):
        return get_thrive_id_from_camp({'id': self.id, 'name': self.name})

    def dict(self, *args, **kwargs):
        return {**super().dict(*args, **kwargs),
                'target_type': self.target_type,
                'thrive_id': self.thrive_id}


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
    clicks: int
    wages: int


class Filter(BaseModel):
    filterType: str


class WidgetsFilterUid(Filter):
    widgets: Dict[str, str] = None


class IPsFilter(Filter):
    ips: List[str]


class DomainsFilter(Filter):
    domainsNames: List[str]


class CampaignStatus(BaseModel):
    id: int
    name: str
    reason: str


class CampaignData(CampaignBaseData):
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


class CampaignStat(CampaignBaseData):
    id: int = Field(alias='campaignId')
    campaignId: int
    imps: int
    clicks: int
    platform_clicks: int = Field(alias='clicks')
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


class MergedWithThriveStats(CampaignStat):
    # thrive stat data:
    thrive_clicks: int = None
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
