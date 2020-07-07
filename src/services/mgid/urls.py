

class CAMPAIGNS:
    BASE_URL = 'https://api.mgid.com/v1'
    LIST = '/goodhits/clients/{client_id}/campaigns'
    STATS_DAILY_DETAILED = '/goodhits/campaigns/{campaign_id}/statistics'
    STATS_DAILY = '/goodhits/clients/{client_id}/campaigns-stat'
    WIDGETS_STATS = '/goodhits/campaigns/{campaign_id}/quality-analysis'

class Token:
    GET_CURRENT = '/auth/token'
