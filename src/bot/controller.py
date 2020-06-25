import logging
import re
from typing import Optional, Union
import json

from extensions import mgid, thrive, zeropark

from . import patterns

MGID = 'mgid'
ZEROPARK = 'zeropark'
THRIVE = 'thrive'


class MessageHandler:
    pattern_commands = {
        'list_campaigns': {
            'pattern': patterns.LIST_CAMPAIGNS,
            MGID: mgid.list_campaigns,
            ZEROPARK: zeropark.list_campaigns,
            THRIVE: thrive.list_campaigns,
        },
    }
    output_format_types = {
        'default': 'list',
        'json': lambda resp: format_response(resp),
    }

    def handle_message(self, content: str, extra_args: Optional[dict] = None):
        for cmd, value in self.pattern_commands.items():
            if (match := value['pattern'].match(content)):
                platform = match.group('platform')
                logging.debug(
                    f"msg: {content} | matched: {value['pattern']} | platform: {platform}")
                resp = value[platform](extra_args)
                logging.debug(f"reponse: {resp}")
                output_format_type = self.get_output_format_type(content)
                resp = self.format_response(resp, format_type=output_format_type)
                logging.debug(f"output-format: {output_format_type}\n{resp}")
                return resp

        return "Invalid Command"

    def get_output_format_type(self, msg: str):
        if not (match := patterns.OUTPUT_FORMAT.search(msg)):
            return self.output_format_types['default']

    @staticmethod
    def format_response(resp: Union[list, dict, str],
                        format_type: Union['list', 'json', 'csv', 'str'] = 'list'):
        def convert_dict_to_raw_string(resp: list):
            raw_resp = []
            for key, value in resp.items():
                raw_resp.append(f'{key}: {value}')
            return '\n'.join(raw_resp)

        def convert_resp_to_raw_string(resp):
            if isinstance(resp, str):
                resp = json.loads(resp)
            if isinstance(resp, dict):
                return convert_dict_to_raw_string(resp)
            if isinstance(resp, list):
                raw_resp = []
                for item in resp:
                    if isinstance(item, dict):
                        raw_resp.append(convert_dict_to_raw_string(item))
                    else:
                        raw_resp.append(str(item))
                return '\n'.join(raw_resp)

        if format_type not in ['list', 'json', 'csv', 'str']:
            format_type = 'list'
        if format_type == 'list':
            return convert_resp_to_raw_string(resp)
