import json
import logging
import re
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from config import DEFAULT_OUTPUT_FORMAT, DEFAULT_TIME_INTERVAL
from constants import Platforms
from errors import InvalidCommand
from extensions import mgid, thrive, zeropark

from .. import patterns as re_patterns
from .utils import convert_resp_to_raw_string


class Commands(str, Enum):
    list_campaigns = 'list'
    stats_campaign = 'stats'
    bot_traffic = 'bot-traffic'
    list_sources = 'sources'
    spent_campaign = 'spent'
    top_widgets = 'top-widgets'
    high_cpa_widgets = 'high-cpa-widgets'


COMMANDS_PATTERNS = [
    re_patterns.LIST_CAMPAIGNS,
    re_patterns.CAMPAIGN_STATS,
    re_patterns.BOT_TRAFFIC,
    re_patterns.LIST_SORCES,
    re_patterns.SPENT_CAMPAIGN,
    re_patterns.TOP_WIDGETS,
    re_patterns.HIGH_CPA_WIDGETS,
]

class CommandParser:

    @classmethod
    def platform_method_factory(cls, platform: Union[Platforms],
                                command: Union['list', 'stats', 'bot-traffic']):
        # TODO change this -> to actual functions
        method_factory = {
            Platforms.MGID: {
                Commands.list_campaigns: mgid.list_campaigns,
                Commands.stats_campaign: mgid.stats_campaign,
                Commands.spent_campaign: mgid.spent_campaign,
                Commands.bot_traffic: mgid.bot_traffic,
                Commands.top_widgets: mgid.top_widgets,
                Commands.high_cpa_widgets: mgid.high_cpa_widgets,
            },
            Platforms.ZEROPARK: {
                Commands.list_campaigns: zeropark.list_campaigns,
                Commands.stats_campaign: zeropark.stats_campaign,
                Commands.spent_campaign: zeropark.spent_campaign,
                Commands.bot_traffic: zeropark.bot_traffic,
                Commands.top_widgets: zeropark.top_widgets,
                Commands.high_cpa_widgets: zeropark.high_cpa_widgets,
            },
            Platforms.THRIVE: {
                Commands.list_campaigns: thrive.list_campaigns,
                Commands.list_sources: thrive.list_sources,
                Commands.stats_campaign: thrive.stats_campaigns,
            },
        }
        return method_factory[platform][command]

    @classmethod
    def parse_command(cls, message: str) -> Tuple[Callable, Dict[str, Union[str, List[str]]]]:
        command_args = {}
        for pattern in COMMANDS_PATTERNS:
            match = pattern.match(message.lower())
            if match:
                break
        else:
            raise InvalidCommand(command=message)

        group_dict = match.groupdict()
        command_args['command'] = group_dict['cmd']
        command_args['platform'] = group_dict['platform']
        command_args['output_format'] = cls.get_output_format_from_command(message)
        # if (extra_query_args := cls.get_extra_query_args_from_command(message)):
        #     command_args['extra_query_args'] = extra_query_args
        if (fields := cls.get_fields_from_command(message)):
            command_args['fields'] = fields
        if 'threshold' in group_dict:
            command_args['threshold'] = group_dict['threshold']

        # logging.debug(f"msg: {message} | matched: {match.re.pattern} | "
        #               f"platform: {command_args['platform']}")

        # params with default value
        for group_name, default_value in [
            ('campaign_id', None),
            ('time_interval', DEFAULT_TIME_INTERVAL),
            ('filter_limit', '5'),
        ]:
            if (group_value := match.groupdict().get(group_name) or default_value):
                command_args[group_name] = group_value

        # optional flags:
        for pattern in [
            re_patterns.DATE_RANGE_FLAG,
            re_patterns.TIME_RANGE_FLAG,
            re_patterns.FLAG_LIMIT,
        ]:
            if (match := pattern.search(message)):
                arg_name, value = list(match.groupdict().items())[0]
                command_args[arg_name] = value

        # if match.re is re_patterns.LIST_CAMPAIGNS:
        #     pass
        # if match.re is re_patterns.CAMPAIGN_STATS:
        #     command_args['campaign_id'] = match.group('campaign_id')
        #     command_args['time_interval'] = match.group('time_interval') or DEFAULT_TIME_INTERVAL
        # if match.re is re_patterns.BOT_TRAFFIC:
        #     command_args['campaign_id'] = match.group('campaign_id')
        #     command_args['time_interval'] = match.group('time_interval') or DEFAULT_TIME_INTERVAL
        # if match.re is re_patterns.SPENT_CAMPAIGN:
        #     command_args['campaign_id'] = match.group('campaign_id')
        #     command_args['time_interval'] = match.group('time_interval') or DEFAULT_TIME_INTERVAL

        command_handler = cls.platform_method_factory(command_args['platform'], command_args['command'])
        return command_handler, command_args

    @classmethod
    def get_fields_from_command(cls, command) -> Optional[List[str]]:
        if not (match := re_patterns.FILTER_FIELDS.search(command)):
            return None
        match_fields = match.group('fields')
        fields = match_fields.strip(',').split(',')
        return fields

    @classmethod
    def get_output_format_from_command(cls, command):
        match = re_patterns.OUTPUT_FORMAT.search(command)
        if not match:
            return DEFAULT_OUTPUT_FORMAT
        output_format = match.group('output_format')
        return output_format

    @classmethod
    def get_extra_query_args_from_command(cls, command):
        # TODO: implement adding extra args to command
        return None
