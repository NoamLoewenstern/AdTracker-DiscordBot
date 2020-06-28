
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator, Field


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
