import logging
import os
import re
from typing import Dict, Optional, Union

from errors import InvalidPlatormCampaignName


def get_thrive_id_from_camp(campaign: Dict[Union['id', 'name'], Union[str, int]],
                            raise_=not os.getenv('DEBUG'),
                            platform='') -> Optional[int]:
    if not (match := re.match(r'(?P<thrive_camp_id>\d+) ', campaign['name'])):
        err_msg = f"Campaign {campaign['id']} Named '{campaign['name']}' Doesn't Contain THRIVE Camp-ID."
        if raise_:
            raise InvalidPlatormCampaignName(
                platform=platform,
                data=err_msg)
        logging.error(f'[!] {err_msg}')
        return None
    return match.group('thrive_camp_id')
