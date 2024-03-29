from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from config import RUNNING_ON_SERVER
from constants import DEBUG
from errors import CampaignNameMissingTrackerIDError, ErrorList
from pydantic import BaseModel

from utils import merge_objs

from ..thrive import Thrive
from .common_service import CommonService
from .utils import CampaignIDsDict, get_thrive_id_from_camp


class PlatformService(CommonService):
    def __init__(self, thrive: Thrive,
                 platform: str = '',
                 email: str = '',
                 password: str = '',
                 *args, **kargs):
        super().__init__(*args, **kargs)
        self.thrive = thrive
        self.thrive.platforms.append(self)
        self._campaigns: Dict[str, Any] = None
        self.platform = platform
        self.email = email
        self.password = password

    @property
    def campaigns(self):
        # implement in child-classes
        return self._campaigns

    @campaigns.setter
    def campaigns(self, d: dict):
        self._campaigns = CampaignIDsDict(d, platform=self.platform)

    def _update_campaigns(self, campaigns: List[BaseModel]):
        if self._campaigns is None:
            self._campaigns = CampaignIDsDict(platform=self.platform)
        self._campaigns.update({campaign['id']: campaign for campaign in campaigns})
        return self._campaigns

    def get_thrive_id(self, campaign: Union[BaseModel, Dict[Literal['id', 'name'], Union[str, int]]],
                      raise_=not RUNNING_ON_SERVER) -> Optional[str]:
        thrive_id = get_thrive_id_from_camp(campaign=campaign,
                                            raise_=raise_,
                                            platform=type(self).__name__)
        if thrive_id not in self.thrive.campaigns:
            raise CampaignNameMissingTrackerIDError(id=thrive_id,
                                                    name=campaign['name'],
                                                    platform=self.platform)
        return thrive_id

    def _merge_thrive_stats(self,
                            stats: List[Dict],
                            thrive_results: List[Dict],
                            MergedStatsModel: BaseModel,
                            raise_=not RUNNING_ON_SERVER,
                            ) -> Tuple[List[BaseModel], ErrorList]:
        merged = []
        error_stats = ErrorList()
        if len(thrive_results) == 1 and not thrive_results[0]:
            return stats, error_stats
        for stat in stats:
            try:
                stat_thrive_id = self.get_thrive_id(stat, raise_=raise_)
            except CampaignNameMissingTrackerIDError as e:
                error_stats.append(e.dict())
                continue
            for thrive_result in thrive_results:
                if not thrive_result:
                    continue
                if stat_thrive_id == str(thrive_result['id']):
                    if isinstance(stat, BaseModel):
                        stat = stat.dict()
                    merged_dict = {**thrive_result, **stat}
                    merged.append(MergedStatsModel.parse_obj(merged_dict))
                    break
        return merged, error_stats

    def _merge_and_update_list_objects(self,
                                       list_objects_1: Union[Dict, List[Dict]],
                                       list_objects_2: Union[Dict, List[Dict]],
                                       /,
                                       key='id',
                                       just_common=False,
                                       ) -> List[Dict]:
        if isinstance(list_objects_1, list):
            # 'key' in obj-dict will be the keys in the new dict (to allow merging object-dict)
            dict_1 = {obj[key]: obj for obj in list_objects_1}
            dict_2 = {obj[key]: obj for obj in list_objects_2}
        elif isinstance(list_objects_1, dict):
            dict_1 = list_objects_1
            dict_2 = list_objects_2
        else:
            raise ValueError("Must Pass Type Dict | List[Dict]. Passed " + str(type(list_objects_1)))

        set_d1_keys = set(dict_1)
        set_d2_keys = set(dict_2)
        if set_d1_keys == set_d2_keys:
            return [merge_objs(dict_1[key], dict_2[key]) for key in set_d1_keys]

        unique_keys_1 = set_d1_keys - set_d2_keys
        unique_keys_2 = set_d2_keys - set_d1_keys
        common_keys = set_d2_keys & set_d1_keys
        merged_list = [merge_objs(dict_1[key], dict_2[key]) for key in common_keys]
        if just_common:
            return merged_list
        # Adds the objects which have UNIQUE 'key' from each list of objects.
        merged_list.extend(dict_1[key] for key in unique_keys_1)
        merged_list.extend(dict_2[key] for key in unique_keys_2)
        return merged_list
