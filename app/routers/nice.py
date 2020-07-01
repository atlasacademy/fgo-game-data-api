import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings
from ..data import nice, search
from ..data.common import Region
from ..data.enums import TRAIT_NAME
from ..data.gamedata import masters
from ..data.schemas.nice import (
    Language,
    NiceBaseFunctionReverse,
    NiceBuffReverse,
    NiceEquip,
    NiceItem,
    NiceMysticCode,
    NiceQuestPhase,
    NiceServant,
    NiceSkillReverse,
    NiceTdReverse,
)
from .deps import DetailMessage, EquipSearchQueryParams, ServantSearchQueryParams
from .utils import item_response, list_response, list_string


logger = logging.getLogger()
settings = Settings()


if settings.export_all_nice:  # pragma: no cover
    for region_ in (Region.NA, Region.JP):
        start_time = time.perf_counter()
        logger.info(f"Writing nice {region_} servant and equip data …")
        all_equip_data = [
            nice.get_nice_equip_model(region_, item_id)
            for item_id in masters[region_].mstSvtEquipCollectionNo.values()
        ]
        all_servant_data = [
            nice.get_nice_servant_model(region_, item_id)
            for item_id in masters[region_].mstSvtServantCollectionNo.values()
        ]
        all_item_data = [
            nice.get_nice_item(region_, item_id)
            for item_id in masters[region_].mstItemId
        ]
        all_mc_data = [
            nice.get_nice_mystic_code(region_, item_id)
            for item_id in masters[region_].mstEquipId
        ]
        with open(f"export/{region_}/nice_trait.json", "w", encoding="utf-8") as fp:
            json.dump(TRAIT_NAME, fp)
        with open(f"export/{region_}/nice_servant.json", "w", encoding="utf-8") as fp:
            fp.write(list_string(all_servant_data))
        with open(f"export/{region_}/nice_equip.json", "w", encoding="utf-8") as fp:
            fp.write(list_string(all_equip_data))
        with open(f"export/{region_}/nice_item.json", "w", encoding="utf-8") as fp:
            json.dump(all_item_data, fp, ensure_ascii=False)
        with open(
            f"export/{region_}/nice_mystic_code.json", "w", encoding="utf-8"
        ) as fp:
            json.dump(all_mc_data, fp, ensure_ascii=False)
        run_time = time.perf_counter() - start_time
        logger.info(f"Finished writing nice {region_} data in {run_time:.4f}s.")


responses: Dict[Union[str, int], Any] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


router = APIRouter()


nice_find_servant_extra = """
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
- **lore**: Add profile info to the response
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + nice_find_servant_extra,
    response_description="Servant Entity",
    response_model=List[NiceServant],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Optional[Language] = None,
    lore: bool = False,
):
    if search_param.hasSearchParams:
        matches = search.search_servant(search_param)
        return list_response(
            [
                nice.get_nice_servant_model(search_param.region, item, lore, lang)
                for item in matches
            ]
        )
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_servant_description = """Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field.

- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
- **lore**: Add profile info to the response
"""
pre_processed_data_links = """

Preprocessed data:
- [NA servant](/export/NA/nice_servant.json)
- [JP servant](/export/JP/nice_servant.json)
"""

if settings.documentation_all_nice:
    get_servant_description += pre_processed_data_links


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
    description=get_servant_description,
    responses=responses,
)
async def get_servant(
    region: Region, item_id: int, lang: Optional[Language] = None, lore: bool = False
):
    if item_id in masters[region].mstSvtServantCollectionNo:
        item_id = masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in masters[region].mstSvtServantCollectionNo.values():
        return item_response(nice.get_nice_servant_model(region, item_id, lore, lang))
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION,
    response_description="Equip Entity",
    response_model=List[NiceEquip],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    lore: bool = False,
):
    if search_param.hasSearchParams:
        matches = search.search_equip(search_param)
        return list_response(
            [
                nice.get_nice_equip_model(search_param.region, item, lore)
                for item in matches
            ]
        )
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_equip_description = """Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field.

- **lore**: Add profile info to the response
"""
pre_processed_equip_links = """

Preprocessed data:
- [NA CE](/export/NA/nice_equip.json)
- [JP CE](/export/JP/nice_equip.json)
"""

if settings.documentation_all_nice:
    get_equip_description += pre_processed_equip_links


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    response_description="CE Entity",
    response_model=NiceEquip,
    response_model_exclude_unset=True,
    description=get_equip_description,
    responses=responses,
)
async def get_equip(region: Region, item_id: int, lore: bool = False):
    if item_id in masters[region].mstSvtEquipCollectionNo:
        item_id = masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in masters[region].mstSvtEquipCollectionNo.values():
        return item_response(nice.get_nice_equip_model(region, item_id, lore))
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/svt/{item_id}",
    summary="Get svt data",
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_svt(region: Region, item_id: int, lore: bool = False):
    """
    Get svt info from ID

    Only use actual IDs for lookup. Does not convert from collectionNo.
    The endpoint is not limited to servants or equips ids.
    """
    if item_id in masters[region].mstSvtId:
        return item_response(nice.get_nice_servant_model(region, item_id, lore))
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


get_mc_description = "Get nice Mystic Code info from ID"
pre_processed_mc_links = """

Preprocessed data:
- [NA Mystic Code](/export/NA/nice_mystic_code.json)
- [JP Mystic Code](/export/JP/nice_mystic_code.json)
"""

if settings.documentation_all_nice:
    get_mc_description += pre_processed_mc_links


@router.get(
    "/{region}/MC/{item_id}",
    summary="Get Mystic Code data",
    response_description="Mystic Code entity",
    response_model=NiceMysticCode,
    response_model_exclude_unset=True,
    description=get_mc_description,
    responses=responses,
)
async def get_mystic_code(region: Region, item_id: int):
    if item_id in masters[region].mstEquipId:
        return nice.get_nice_mystic_code(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Mystic Code not found")


@router.get(
    "/{region}/skill/{item_id}",
    summary="Get skill data",
    response_description="Skill entity",
    response_model=NiceSkillReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_skill(
    region: Region, item_id: int, reverse: bool = False, lang: Optional[Language] = None
):
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    """
    if item_id in masters[region].mstSkillId:
        return item_response(nice.get_nice_skill_alone(region, item_id, reverse, lang))
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@router.get(
    "/{region}/NP/{item_id}",
    summary="Get NP data",
    response_description="NP entity",
    response_model=NiceTdReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_td(
    region: Region, item_id: int, reverse: bool = False, lang: Optional[Language] = None
):
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    """
    if item_id in masters[region].mstTreasureDeviceId:
        return item_response(nice.get_nice_td_alone(region, item_id, reverse, lang))
    else:
        raise HTTPException(status_code=404, detail="NP not found")


@router.get(
    "/{region}/function/{item_id}",
    summary="Get function data",
    response_description="Function entity",
    response_model=NiceBaseFunctionReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_function(
    region: Region, item_id: int, reverse: bool = False, lang: Optional[Language] = None
):
    """
    Get the function data from the given ID

    - **reverse**: Reverse lookup the skills that have this function
    and return the reversed skill objects.
    Will search recursively and return all entities in path: func -> skill -> servant.
    """
    if item_id in masters[region].mstFuncId:
        return item_response(nice.get_nice_func_alone(region, item_id, reverse, lang))
    else:
        raise HTTPException(status_code=404, detail="Function not found")


@router.get(
    "/{region}/buff/{item_id}",
    summary="Get buff data",
    response_description="Buff Entity",
    response_model=NiceBuffReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_buff(
    region: Region, item_id: int, reverse: bool = False, lang: Optional[Language] = None
):
    """
    Get the buff data from the given ID

    - **reverse**: Reverse lookup the functions that have this buff
    and return the reversed function objects.
    Will search recursively and return all entities in path: buff -> func -> skill -> servant.
    """
    if item_id in masters[region].mstBuffId:
        return item_response(nice.get_nice_buff_alone(region, item_id, reverse, lang))
    else:
        raise HTTPException(status_code=404, detail="Buff not found")


get_item_description = "Get nice item info from ID"
pre_processed_item_links = """

Preprocessed data:
- [NA Item](/export/NA/nice_item.json)
- [JP Item](/export/JP/nice_item.json)
"""

if settings.documentation_all_nice:
    get_item_description += pre_processed_item_links


@router.get(
    "/{region}/item/{item_id}",
    summary="Get Item data",
    response_description="Item Entity",
    response_model=NiceItem,
    response_model_exclude_unset=True,
    description=get_item_description,
    responses=responses,
)
async def get_item(region: Region, item_id: int):
    if item_id in masters[region].mstItemId:
        return nice.get_nice_item(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Quest data",
    response_description="Quest Phase Entity",
    response_model=NiceQuestPhase,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_quest_phase(region: Region, quest_id: int, phase: int):
    """
    Get the nice quest data from the given quest ID and phase number
    """
    if (
        quest_id in masters[region].mstQuestId
        and phase in masters[region].mstQuestPhaseId[quest_id]
    ):
        return nice.get_nice_quest_phase(region, quest_id, phase)
    else:
        raise HTTPException(status_code=404, detail="Quest not found")
