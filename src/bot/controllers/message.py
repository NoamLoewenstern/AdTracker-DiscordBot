import json
import logging
from typing import Union

from extensions import mgid, thrive, zeropark

from .. import patterns
from .command import CommandParser
from .utils import convert_resp_to_raw_string

DEFAULT_OUTPUT_FORMAT = 'list'


class MessageHandler:
    output_format_types = {
        'default': lambda: 'list',
        'json': lambda resp: format_response(resp),
    }

    def __init__(self):
        self.command_parser = CommandParser(mgid, zeropark, thrive)

    def handle_message(self, content: str):

        command_handler, command_args = self.command_parser.parse_command(content)
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
