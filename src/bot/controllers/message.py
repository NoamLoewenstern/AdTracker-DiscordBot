import json
import logging
import re
from typing import Optional, Union

from errors import InvalidCommand
from extensions import mgid, thrive, zeropark

from .. import patterns
from .command import CommandParser
from .utils import convert_resp_to_raw_string

MGID = 'mgid'
ZEROPARK = 'zeropark'
THRIVE = 'thrive'
DEFAULT_OUTPUT_FORMAT = 'list'


class MessageHandler:
    def __init__(self):

        self.pattern_actions = [
            (patterns.LIST_CAMPAIGNS, lambda platform:
                self.command_handler.list_campaigns_factory(platform)),
            (patterns.CAMPAIGN_STATS, lambda platform:
                self.command_handler.campaign_stats_factory(platform)),
        ]
        self.output_format_types = {
            'default': lambda: 'list',
            'json': lambda resp: format_response(resp),
        }

    def handle_message(self, content: str):

        command_handler, command_args = CommandParser.parse_command(content)
        resp = command_handler(**command_args)
        # logging.debug(f"reponse: {resp}")
        resp = self.format_response(resp, format_type=command_args['output_format'])
        # logging.debug(f"output-format: {command_args['output_format']}\n{resp}")
        return resp, command_args['output_format']

        return "Invalid Command", 'str'

    def get_output_format_type(self, msg: str):
        if not (match := patterns.OUTPUT_FORMAT.search(msg)):
            return self.output_format_types['default']()

    @staticmethod
    def format_response(resp: Union[list, dict, str],
                        format_type: Union['str', 'list', 'json', 'csv'] = 'list'):

        if format_type not in ['list', 'json', 'csv', 'str']:
            # default will be list
            format_type = 'list'
        if format_type == 'list':
            # didn't implement other formats yet.
            return convert_resp_to_raw_string(resp)
