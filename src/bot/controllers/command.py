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
    campaign_bot_traffic = 'bot-traffic'
    list_sources = 'sources'
    spent_campaign = 'spent'
    widgets_top = 'widgets-top'
    widgets_high_cpa = 'widgets-high-cpa'
    widgets_low_cpa = 'widgets-low-cpa'
    widgets_kill_longtail = 'widgets-kill-longtail'
    widgets_turn_on_all = 'widgets-turn-on-all'
    widget_kill_bot_traffic = 'widgets-kill-bot'


COMMANDS_PATTERNS = [
    re_patterns.Commands.LIST_CAMPAIGNS,
    re_patterns.Commands.CAMPAIGN_STATS,
    re_patterns.Commands.BOT_TRAFFIC,
    re_patterns.Commands.LIST_SORCES,
    re_patterns.Commands.SPENT_CAMPAIGN,
    re_patterns.Commands.WIDGETS_TOP,
    re_patterns.Commands.WIDGETS_HIGH_CPA,
    re_patterns.Commands.WIDGETS_LOW_CPA,
    re_patterns.Commands.WIDGETS_KILL_LONGTAIL,
    re_patterns.Commands.WIDGETS_TURN_ON_ALL,
    re_patterns.Commands.WIDGETS_KILL_BOT_TRAFFIC,
]

class CommandParser:

    @classmethod
    def platform_method_factory(cls, platform: Union[Platforms],
                                command: Commands):
        method_factory = {
            Platforms.MGID: {
                Commands.list_campaigns: mgid.list_campaigns,
                Commands.stats_campaign: mgid.stats_campaign,
                Commands.spent_campaign: mgid.spent_campaign,
                Commands.campaign_bot_traffic: mgid.campaign_bot_traffic,
                Commands.widgets_top: mgid.widgets_top,
                Commands.widgets_high_cpa: mgid.widgets_high_cpa,
                Commands.widgets_low_cpa: mgid.widgets_low_cpa,
                Commands.widgets_kill_longtail: mgid.widgets_kill_longtail,
                Commands.widgets_turn_on_all: mgid.widgets_turn_on_all,
                Commands.widget_kill_bot_traffic: mgid.widget_kill_bot_traffic,
            },
            Platforms.ZEROPARK: {
                Commands.list_campaigns: zeropark.list_campaigns,
                Commands.stats_campaign: zeropark.stats_campaign,
                Commands.spent_campaign: zeropark.spent_campaign,
                Commands.campaign_bot_traffic: zeropark.campaign_bot_traffic,
                Commands.widgets_top: zeropark.widgets_top,
                Commands.widgets_high_cpa: zeropark.widgets_high_cpa,
                Commands.widgets_low_cpa: zeropark.widgets_low_cpa,
                Commands.widgets_kill_longtail: zeropark.widgets_kill_longtail,
                Commands.widgets_turn_on_all: zeropark.widgets_turn_on_all,
                Commands.widget_kill_bot_traffic: zeropark.widget_kill_bot_traffic,
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
            re_patterns.Flags.DATE_RANGE,
            re_patterns.Flags.TIME_RANGE,
            re_patterns.Flags.FILTER_LIMIT,
        ]:
            if (match := pattern.search(message)):
                arg_name, value = list(match.groupdict().items())[0]
                command_args[arg_name] = value

        command_handler = cls.platform_method_factory(command_args['platform'], command_args['command'])
        return command_handler, command_args

    @classmethod
    def get_fields_from_command(cls, command) -> Optional[List[str]]:
        if not (match := re_patterns.Flags.FILTER_FIELDS.search(command)):
            return None
        match_fields = match.group('fields')
        fields = match_fields.strip(',').split(',')
        return fields

    @classmethod
    def get_output_format_from_command(cls, command):
        match = re_patterns.Flags.OUTPUT_FORMAT.search(command)
        if not match:
            return DEFAULT_OUTPUT_FORMAT
        output_format = match.group('output_format')
        return output_format

    @classmethod
    def get_extra_query_args_from_command(cls, command):
        # TODO: implement adding extra args to command
        return None
