import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from utils import DictForcedStringKeys

from ..thrive import Thrive
from .common_service import CommonService
from .utils import get_thrive_id_from_camp


class PlatformService(CommonService):
    def __init__(self, thrive: Thrive, *args, **kargs):
        super().__init__(*args, **kargs)
        self.thrive = thrive
        self.thrive.platforms.append(self)
        self._campaigns: Dict[str, Any] = None

    @property
    def campaigns(self):
        # implement in child-classes
        return self._campaigns

    @campaigns.setter
    def campaigns(self, d: dict):
        self._campaigns = DictForcedStringKeys(d)

    def _update_campaigns(self, campaigns: List[BaseModel]):
        if self._campaigns is None:
            self._campaigns = DictForcedStringKeys()
        self._campaigns.update({campaign['id']: campaign for campaign in campaigns})
        return self._campaigns

    def get_thrive_id(self, campaign: Union[BaseModel, Dict[Union['id', 'name'], Union[str, int]]],
                      raise_=not os.getenv('DEBUG')) -> Optional[str]:
        return get_thrive_id_from_camp(campaign=campaign,
                                       raise_=raise_,
                                       platform=type(self).__name__)

    def _merge_thrive_stats(self,
                            stats: List[Dict],
                            thrive_results: List[Dict],
                            MergedStatsModel: BaseModel,
                            ) -> List[BaseModel]:
        merged = []
        for stat in stats:
            for thrive_result in thrive_results:
                if self.get_thrive_id(stat) == str(thrive_result['id']):
                    merged_dict = {**thrive_result, **stat.dict()}
                    merged.append(MergedStatsModel(**merged_dict))
                    # logging.debug(f"\tMERGED stats: {stat}")
        return merged
