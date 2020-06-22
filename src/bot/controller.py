import logging
from typing import Optional

from extensions import mgid, zeropark

from . import patterns

MGID = 'mgid'
ZEROPARK = 'zeropark'


class MessageHandler:
    pattern_commands = {
        'list_campaigns': {
            'pattern': patterns.LIST_CAMPAIGNS,
            MGID: mgid.list_campaigns,
            ZEROPARK: zeropark.list_campaigns,
        },
    }

    def handle_message(self, content: str, extra_args: Optional[dict] = None):
        for cmd, value in self.pattern_commands.items():
            if (match := value['pattern'].match(content)):
                platform = match.group('platform')
                logging.info(f"msg: {content} | matched: {value['pattern']} | platform: {platform}")
                resp = value[platform](extra_args)
                logging.info(f"reponse: {resp}")
                return resp
