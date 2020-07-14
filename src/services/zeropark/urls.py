

class CAMPAIGNS:
    BASE_URL = 'https://panel.zeropark.com/api'
    STATS = '/stats/campaign/all'
    LIST_WIDGETS = '/stats/campaign/{campaign_id}/targets'


class WIDGETS:
    PAUSE = '/campaign/{campaign_id}/targets/pause'
    RESUME = '/campaign/{campaign_id}/targets/resume'
    LIST = '/stats/campaign/{campaign_id}/targets'
