import json
import logging
import re
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Union

from config import DEFAULT_OUTPUT_FORMAT, DEFAULT_TIME_INTERVAL
from constants import Platforms
from errors import InvalidCommand
from extensions import mgid, thrive, zeropark

from .. import patterns
from .utils import convert_resp_to_raw_string


class Commands(str, Enum):
    list_campaigns = 'list_campaigns'
    campaign_stats = 'stats'
    bot_traffic = 'bot-traffic'
    list_sources = 'list_sources'


class CommandParser:
    COMMANDS_PATTERNS = [
        patterns.LIST_CAMPAIGNS,
        patterns.CAMPAIGN_STATS,
        patterns.BOT_TRAFFIC,
        patterns.LIST_SORCES,
    ]

    @classmethod
    def platform_method_factory(cls, platform: Union[Platforms],
                                command: Union['list', 'stats', 'bot-traffic']):
        command_factory = {
            'list': Commands.list_campaigns,
            'stats': Commands.campaign_stats,
            'bot-traffic': Commands.bot_traffic,
            'sources': Commands.list_sources,
        }
        # TODO change this -> to actual functions
        method_factory = {
            Platforms.MGID: {
                Commands.list_campaigns: mgid.list_campaigns,
                Commands.campaign_stats: mgid.stats_campaign,
            },
            Platforms.ZEROPARK: {
                Commands.list_campaigns: zeropark.list_campaigns,
            },
            Platforms.THRIVE: {
                Commands.list_campaigns: thrive.list_campaigns,
                Commands.list_sources: thrive.list_sources,
            },
        }
        return method_factory[platform][command_factory[command]]

    @classmethod
    def parse_command(cls, message: str) -> Tuple[Callable, Dict[str, Union[str, List[str]]]]:
        command_args = {}
        for pattern in cls.COMMANDS_PATTERNS:
            match = pattern.match(message.lower())
            if match:
                break
        else:
            raise InvalidCommand(command=message)

        command_args['command'] = match.group('cmd')
        command_args['platform'] = match.group('platform')
        command_args['output_format'] = cls.get_output_format_from_command(message)
        # if (extra_query_args := cls.get_extra_query_args_from_command(message)):
        #     command_args['extra_query_args'] = extra_query_args
        if (fields := cls.get_fields_from_command(message)):
            command_args['fields'] = fields

        logging.debug(
            f"msg: {message} | matched: {match.re.pattern} | platform: {command_args['platform']}")

        if match.re is patterns.LIST_CAMPAIGNS:
            pass
        if match.re is patterns.CAMPAIGN_STATS:
            command_args['campaign_id'] = match.group('campaign_id')
            command_args['time_interval'] = match.group('time_interval') or DEFAULT_TIME_INTERVAL
        if match.re is patterns.BOT_TRAFFIC:
            command_args['campaign_id'] = match.group('campaign_id')
            command_args['time_interval'] = match.group('time_interval') or DEFAULT_TIME_INTERVAL

        command_handler = cls.platform_method_factory(command_args['platform'], command_args['command'])
        return command_handler, command_args

    @classmethod
    def get_fields_from_command(cls, command) -> Optional[List[str]]:
        match = patterns.FILTER_FIELDS.search(command)
        if not match:
            return None
        match_fields = match.group('fields')
        fields = match_fields.strip(',').split(',')
        return fields

    @classmethod
    def get_output_format_from_command(cls, command):
        match = patterns.OUTPUT_FORMAT.search(command)
        if not match:
            return DEFAULT_OUTPUT_FORMAT
        output_format = match.group('output_format')
        return output_format

    @classmethod
    def get_extra_query_args_from_command(cls, command):
        # TODO: implement adding extra args to command
        return None
