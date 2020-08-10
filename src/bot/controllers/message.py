import json
import logging
from typing import Tuple, Union

from bot.patterns import ignore_errors_keyname
from errors import ErrorList, InternalError
from extensions import OutputFormatTypes, mgid, thrive, zeropark

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

    def handle_message(self, content: str, format_output: bool = True) -> Tuple[Union[list, dict, str]]:

        command_handler, command_args = self.command_parser.parse_command(content)
        resp = command_handler(**command_args)
        error_resp: ErrorList = ErrorList()
        if isinstance(resp, tuple):
            if len(resp) != 2:
                raise InternalError(type='Unknown Internal Error, Check Error Logs.')
            resp, error_resp = resp
            if not isinstance(error_resp, ErrorList):
                internal_error = InternalError(
                    type='Internal Warning, Should return Errors in ErrorList type.')
                logging.warning(str(internal_error))
        if ignore_errors_keyname in command_args:
            error_resp.clear()
        if format_output:
            resp = self.format_response(resp, format_type=command_args['output_format'])
            error_resp = self.format_response(error_resp, format_type=command_args['output_format'])

        return resp, error_resp, command_args['output_format']

    def get_output_format_type(self, msg: str):
        if not (match := patterns.OUTPUT_FORMAT.search(msg)):
            return self.output_format_types['default']()

    @staticmethod
    def format_response(resp: Union[list, dict, str],
                        format_type: OutputFormatTypes = 'list') -> str:

        if not getattr(OutputFormatTypes, format_type):
            # default will be list
            format_type = 'list'
        # if format_type != OutputFormatTypes.str:
        # TODO: implement other formats to. # not requested for other formats
        new_resp = convert_resp_to_raw_string(resp)
        return new_resp
