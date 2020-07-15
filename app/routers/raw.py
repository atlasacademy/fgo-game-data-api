from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException

from ..data import raw, search
from ..data.common import Region, ReverseDepth
from ..data.gamedata import masters
from ..data.schemas.raw import (
    BuffEntity,
    CommandCodeEntity,
    FunctionEntity,
    ItemEntity,
    MysticCodeEntity,
    QuestPhaseEntity,
    ServantEntity,
    SkillEntity,
    TdEntity,
)
from .deps import (
    BuffSearchQueryParams,
    DetailMessage,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
)
from .utils import item_response, list_response


responses: Dict[Union[str, int], Any] = {
    404: {"model": DetailMessage, "description": "Item not found"}
}


router = APIRouter()


svt_expand_lore_description = """
- **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
from the skill IDs in mstSvt.classPassive.
Expand all other skills and functions as well.
- **lore**: Add profile info to the response.
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + svt_expand_lore_description,
    response_description="Servant Entity",
    response_model=List[ServantEntity],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
):
    if search_param.hasSearchParams:
        matches = search.search_servant(search_param)
        entity_list = [
            raw.get_servant_entity(search_param.region, item, expand, lore)
            for item in matches
        ]
        return list_response(entity_list)
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_servant_description = """
Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field. As a result, it can return not servant data.
"""


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    description=get_servant_description + svt_expand_lore_description,
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_servant(
    region: Region, item_id: int, expand: bool = False, lore: bool = False
):
    if item_id in masters[region].mstSvtServantCollectionNo:
        item_id = masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in masters[region].mstSvtId:
        servant_entity = raw.get_servant_entity(region, item_id, expand, lore)
        return item_response(servant_entity)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + svt_expand_lore_description,
    response_description="CE entity",
    response_model=List[ServantEntity],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
):
    if search_param.hasSearchParams:
        matches = search.search_equip(search_param)
        entity_list = [
            raw.get_servant_entity(search_param.region, item, expand, lore)
            for item in matches
        ]
        return list_response(entity_list)
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_ce_description = """
Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field. As a result, it can return not CE data.
"""


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    description=get_ce_description + svt_expand_lore_description,
    response_description="CE entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_equip(
    region: Region, item_id: int, expand: bool = False, lore: bool = False
):
    if item_id in masters[region].mstSvtEquipCollectionNo:
        item_id = masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in masters[region].mstSvtId:
        servant_entity = raw.get_servant_entity(region, item_id, expand, lore)
        return item_response(servant_entity)
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/MC/{item_id}",
    summary="Get Mystic Code data",
    response_description="Mystic Code entity",
    response_model=MysticCodeEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_mystic_code(region: Region, item_id: int, expand: bool = False):
    """
    Get Mystic Code info from ID

    - **expand**: Expand the skills and functions.
    """
    if item_id in masters[region].mstEquipId:
        mc_entity = raw.get_mystic_code_entity(region, item_id, expand)
        return item_response(mc_entity)
    else:
        raise HTTPException(status_code=404, detail="Mystic Code not found")


@router.get(
    "/{region}/CC/{item_id}",
    summary="Get Command Code data",
    response_description="Command Code entity",
    response_model=CommandCodeEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_command_code(region: Region, item_id: int, expand: bool = False):
    """
    Get Command Code info from ID

    - **expand**: Expand the skills and functions.
    """
    if item_id in masters[region].mstCommandCodeId:
        cc_entity = raw.get_command_code_entity(region, item_id, expand)
        return item_response(cc_entity)
    else:
        raise HTTPException(status_code=404, detail="Command Code not found")


@router.get(
    "/{region}/skill/{item_id}",
    summary="Get skill data",
    response_description="Skill entity",
    response_model=SkillEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_skill(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False,
):
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    - **expand**: Add expanded function objects to mstSkillLv.expandedFuncId
    from the function IDs in mstSkillLv.funcId.
    """
    if item_id in masters[region].mstSkillId:
        skill_entity = raw.get_skill_entity(region, item_id, reverse, expand=expand)
        return item_response(skill_entity)
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@router.get(
    "/{region}/NP/{item_id}",
    summary="Get NP data",
    response_description="NP entity",
    response_model=TdEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_td(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False,
):
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    - **expand**: Add expanded function objects to mstTreasureDeviceLv.expandedFuncId
    from the function IDs in mstTreasureDeviceLv.funcId.
    """
    if item_id in masters[region].mstTreasureDeviceId:
        td_entity = raw.get_td_entity(region, item_id, reverse, expand=expand)
        return item_response(td_entity)
    else:
        raise HTTPException(status_code=404, detail="NP not found")


function_reverse_expand_description = """
- **reverse**: Reverse lookup the skills that have this function
and return the reversed skill objects.
- **reverseDepth**: Controls the depth of the reverse lookup: func -> skill/np -> servant.
- **expand**: Add buff objects to mstFunc.expandedVals from the buff ID in mstFunc.vals.
"""


@router.get(
    "/{region}/function/search",
    summary="Find and get function data",
    description=FuncSearchQueryParams.DESCRIPTION + function_reverse_expand_description,
    response_description="Function entity",
    response_model=List[FunctionEntity],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
):
    if search_param.hasSearchParams:
        matches = search.search_func(search_param)
        entity_list = [
            raw.get_func_entity(
                search_param.region, item, reverse, reverseDepth, expand
            )
            for item in matches
        ]
        return list_response(entity_list)
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


@router.get(
    "/{region}/function/{item_id}",
    summary="Get function data",
    description="Get the function data from the given ID"
    + function_reverse_expand_description,
    response_description="Function entity",
    response_model=FunctionEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_function(
    region: Region,
    item_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
):
    if item_id in masters[region].mstFuncId:
        func_entity = raw.get_func_entity(
            region, item_id, reverse, reverseDepth, expand
        )
        return item_response(func_entity)
    else:
        raise HTTPException(status_code=404, detail="Function not found")


buff_reverse_description = """
- **reverse**: Reverse lookup the functions that have this buff
and return the reversed function objects.
- **reverseDepth**: Controls the depth of the reverse lookup: buff -> func -> skill/np -> servant.
"""


@router.get(
    "/{region}/buff/search",
    summary="Find and get buff data",
    description=BuffSearchQueryParams.DESCRIPTION + buff_reverse_description,
    response_description="Function entity",
    response_model=List[BuffEntity],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
):
    if search_param.hasSearchParams:
        matches = search.search_buff(search_param)
        entity_list = [
            raw.get_buff_entity(search_param.region, item, reverse, reverseDepth)
            for item in matches
        ]
        return list_response(entity_list)
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


@router.get(
    "/{region}/buff/{item_id}",
    summary="Get buff data",
    description="Get the buff data from the given ID" + buff_reverse_description,
    response_description="Buff entity",
    response_model=BuffEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_buff(
    region: Region,
    item_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
):
    if item_id in masters[region].mstBuffId:
        buff_entity = raw.get_buff_entity(region, item_id, reverse, reverseDepth)
        return item_response(buff_entity)
    else:
        raise HTTPException(status_code=404, detail="Buff not found")


@router.get(
    "/{region}/item/{item_id}",
    summary="Get Item data",
    response_description="Item Entity",
    response_model=ItemEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_item(region: Region, item_id: int):
    """
    Get the item data from the given ID
    """
    if item_id in masters[region].mstItemId:
        return {"mstItem": masters[region].mstItemId[item_id]}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Quest data",
    response_description="Quest Phase Entity",
    response_model=QuestPhaseEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_quest_phase(region: Region, quest_id: int, phase: int):
    """
    Get the quest data from the given quest ID and phase number
    """
    if (
        quest_id in masters[region].mstQuestId
        and phase in masters[region].mstQuestPhaseId[quest_id]
    ):
        quest_entity = raw.get_quest_phase_entity(region, quest_id, phase)
        return item_response(quest_entity)
    else:
        raise HTTPException(status_code=404, detail="Quest not found")
