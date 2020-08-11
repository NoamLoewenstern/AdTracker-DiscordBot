import json
import re
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from config import (DEFAULT_ALL_CAMPAIGNS_ALIAS, DEFAULT_OUTPUT_FORMAT,
                    DEFAULT_TIME_INTERVAL)
from constants import Platforms
from errors import InvalidCommandError
from logger import logger
from services import MGid, Thrive, ZeroPark

from .. import patterns as re_patterns


class Commands(str, Enum):
    list_campaigns = 'list'
    stats_campaign = 'stats'
    campaign_bot_traffic = 'bot-traffic'
    # list_sources = 'sources'
    spent_campaign = 'spent'
    widgets_top = 'widgets-top'
    widgets_stats = 'widgets-stats'
    widgets_high_cpa = 'widgets-high-cpa'
    widgets_low_cpa = 'widgets-low-cpa'
    widgets_kill_longtail = 'widgets-kill-longtail'
    widgets_turn_on_all = 'widgets-turn-on-all'
    widget_kill_bot_traffic = 'widgets-kill-bot'


COMMANDS_PATTERNS = [
    re_patterns.Commands.LIST_CAMPAIGNS,
    re_patterns.Commands.CAMPAIGN_STATS,
    re_patterns.Commands.BOT_TRAFFIC,
    # re_patterns.Commands.LIST_SORCES,
    re_patterns.Commands.SPENT_CAMPAIGN,
    re_patterns.Commands.WIDGETS_STATS,
    re_patterns.Commands.WIDGETS_TOP,
    re_patterns.Commands.WIDGETS_HIGH_CPA,
    re_patterns.Commands.WIDGETS_LOW_CPA,
    re_patterns.Commands.WIDGETS_KILL_LONGTAIL,
    re_patterns.Commands.WIDGETS_TURN_ON_ALL,
    re_patterns.Commands.WIDGETS_KILL_BOT_TRAFFIC,
]


class CommandParser:
    def __init__(self, mgid: MGid, zeropark: ZeroPark, thrive: Thrive):
        self.mgid = mgid
        self.zeropark = zeropark
        self.thrive = thrive

    def get_platform_handler(self, platform: Union[Platforms],
                             command: Commands):
        method_factory = {
            Platforms.MGID: {
                Commands.list_campaigns: self.mgid.list_campaigns,
                Commands.stats_campaign: self.mgid.stats_campaign,
                Commands.spent_campaign: self.mgid.spent_campaign,
                Commands.campaign_bot_traffic: self.mgid.campaign_bot_traffic,
                Commands.widgets_stats: self.mgid.widgets_stats,
                Commands.widgets_top: self.mgid.widgets_top,
                Commands.widgets_high_cpa: self.mgid.widgets_high_cpa,
                Commands.widgets_low_cpa: self.mgid.widgets_low_cpa,
                Commands.widgets_kill_longtail: self.mgid.widgets_kill_longtail,
                Commands.widgets_turn_on_all: self.mgid.widgets_turn_on_all,
                Commands.widget_kill_bot_traffic: self.mgid.widget_kill_bot_traffic,
            },
            Platforms.ZEROPARK: {
                Commands.list_campaigns: self.zeropark.list_campaigns,
                Commands.stats_campaign: self.zeropark.stats_campaign,
                Commands.spent_campaign: self.zeropark.spent_campaign,
                # Commands.campaign_bot_traffic: self.zeropark.campaign_bot_traffic,
                Commands.widgets_stats: self.zeropark.widgets_stats,
                Commands.widgets_top: self.zeropark.widgets_top,
                Commands.widgets_high_cpa: self.zeropark.widgets_high_cpa,
                Commands.widgets_low_cpa: self.zeropark.widgets_low_cpa,
                Commands.widgets_kill_longtail: self.zeropark.widgets_kill_longtail,
                Commands.widgets_turn_on_all: self.zeropark.widgets_turn_on_all,
                # Commands.widget_kill_bot_traffic: self.zeropark.widget_kill_bot_traffic,
            },
            Platforms.THRIVE: {
                Commands.list_campaigns: self.thrive.list_campaigns,
                # Commands.list_sources: self.thrive.list_sources,
                Commands.stats_campaign: self.thrive.stats_campaigns,
            },
        }
        method_factory[Platforms.MG] = method_factory[Platforms.MGID]
        method_factory[Platforms.ZP] = method_factory[Platforms.ZEROPARK]
        method_factory[Platforms.TRACKER] = method_factory[Platforms.THRIVE]
        return method_factory[platform][command]

    def parse_command(self, message: str) -> Tuple[Callable, Dict[str, Union[str, List[str]]]]:
        command_args = {}
        for pattern in COMMANDS_PATTERNS:
            match = pattern.match(message.lower())
            if match:
                break
        else:
            raise InvalidCommandError(command=message)

        group_dict = match.groupdict()
        command_args['command'] = group_dict['cmd']
        command_args['platform'] = group_dict['platform']
        command_args['output_format'] = self.get_output_format_from_command(message)
        # if (extra_query_args := self.get_extra_query_args_from_command(message)):
        #     command_args['extra_query_args'] = extra_query_args
        if (fields := self.get_fields_from_command(message)):
            command_args['fields'] = fields
        for optional_arg in [
            'threshold',
            'filter_limit',
        ]:
            if optional_arg in group_dict:
                command_args[optional_arg] = group_dict[optional_arg]

        # logger.debug(f"msg: {message} | matched: {match.re.pattern} | "
        #               f"platform: {command_args['platform']}")

        # params with default value
        for group_name, default_value in [
            ('campaign_id', None),
            ('time_interval', DEFAULT_TIME_INTERVAL),
            ('widget_id', None),
        ]:
            command_args[group_name] = group_dict.get(group_name) or default_value
        # if passed 'all' for campaign_id -> for all campaigns
        if (command_args.get('campaign_id') or '').lower() == DEFAULT_ALL_CAMPAIGNS_ALIAS:
            command_args['campaign_id'] = None
        if (command_args.get('widget_id') or '').lower() == DEFAULT_ALL_CAMPAIGNS_ALIAS:
            command_args['widget_id'] = None
        # optional flags:
        for pattern in [
            re_patterns.Flags.DATE_RANGE,
            re_patterns.Flags.TIME_RANGE,
            re_patterns.Flags.FILTER_LIMIT,
            re_patterns.Flags.IGNORE_ERRORS,
            re_patterns.Flags.FIELDS_OPTIONS,
        ]:
            if (match := pattern.search(message)):
                arg_name, value = list(match.groupdict().items())[0]
                command_args[arg_name] = value

        command_handler = self.get_platform_handler(command_args['platform'], command_args['command'])
        return command_handler, command_args

    def get_fields_from_command(self, command) -> Optional[List[str]]:
        if not (match := re_patterns.Flags.FILTER_FIELDS.search(command)):
            return None
        match_fields = match.group('fields')
        fields = match_fields.strip(',').split(',')
        return fields

    def get_output_format_from_command(self, command):
        match = re_patterns.Flags.OUTPUT_FORMAT.search(command)
        if not match:
            return DEFAULT_OUTPUT_FORMAT
        output_format = match.group('output_format')
        return output_format

    def get_extra_query_args_from_command(self, command):
        # TODO: implement adding extra args to command
        return None
