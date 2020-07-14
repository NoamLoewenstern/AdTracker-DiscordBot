

class CAMPAIGNS:
    BASE_URL = 'https://api.mgid.com/v1'
    LIST = '/goodhits/clients/{client_id}/campaigns'
    STATS_DAILY_DETAILED = '/goodhits/campaigns/{campaign_id}/statistics'
    STATS_DAILY = '/goodhits/clients/{client_id}/campaigns-stat'


class TOKEN:
    GET_CURRENT = '/auth/token'


class WIDGETS:
    PAUSE = '/goodhits/clients/{{client_id}}/campaigns/{campaign_id}'
    RESUME = '/goodhits/clients/{{client_id}}/campaigns/{campaign_id}'
    LIST = '/goodhits/campaigns/{campaign_id}/quality-analysis'
