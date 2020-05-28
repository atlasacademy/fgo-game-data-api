from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ..data import gamedata
from ..data.models.common import DetailMessage, Region
from ..data.models.enums import SvtClass, Attribute, Gender, Trait
from ..data.models.raw import (
    BuffEntity,
    FunctionEntity,
    MstItem,
    ServantEntity,
    SkillEntity,
    TdEntity,
)


responses: Dict[Union[str, int], Any] = {
    404: {"model": DetailMessage, "description": "Item not found"}
}


router = APIRouter()


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    response_description="Servant Entity",
    response_model=List[ServantEntity],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    region: Region,
    name: Optional[str] = None,
    rarity: List[int] = Query(None, ge=0, le=5),
    className: List[SvtClass] = Query(None),
    gender: List[Gender] = Query(None),
    attribute: List[Attribute] = Query(None),
    trait: List[Union[Trait, int]] = Query(None),
    expand: bool = False,
):
    """
    Get servant info from ID

    Search the servants' names list for the given name and return the best match.

    - **name**: English if you are searching NA data and Japanese if you are searching JP data
    - **rarity**: Integer 0-6
    - **className**: an item in the className enum. See the className detail in the Nice Servant response.
    - **gender**: female, male or unknown
    - **attribute**: human, sky, earth, star or beast
    - **trait**: an integer or an item in the trait enum. See the traits detail in the Nice Servant response.
    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if trait or className or name:
        matches = gamedata.search_servant(
            region, name, rarity, className, gender, attribute, trait
        )
        entity_list = [
            gamedata.get_servant_entity(region, item, expand) for item in matches
        ]
        out_json = (
            f"[{','.join([item.json(exclude_unset=True) for item in entity_list])}]"
        )
        return Response(out_json, media_type="application/json",)
    else:
        raise HTTPException(status_code=400, detail="No query found")


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_servant(region: Region, item_id: int, expand: bool = False):
    """
    Get servant info from ID

    If the given ID is a servants's collectionNo, the corresponding servant data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not servant data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in gamedata.masters[region].mstSvtServantCollectionNo:
        item_id = gamedata.masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in gamedata.masters[region].mstSvtId:
        servant_entity = gamedata.get_servant_entity(region, item_id, expand)
        return Response(
            servant_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    response_description="CE entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_equip(region: Region, item_id: int, expand: bool = False):
    """
    Get CE info from ID

    If the given ID is a CE's collectionNo, the corresponding CE data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not CE data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in gamedata.masters[region].mstSvtEquipCollectionNo:
        item_id = gamedata.masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in gamedata.masters[region].mstSvtId:
        servant_entity = gamedata.get_servant_entity(region, item_id, expand)
        return Response(
            servant_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/skill/{item_id}",
    summary="Get skill data",
    response_description="Skill entity",
    response_model=SkillEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_skill(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    - **expand**: Add expanded function objects to mstSkillLv.expandedFuncId
    from the function IDs in mstSkillLv.funcId.
    """
    if item_id in gamedata.masters[region].mstSkillId:
        skill_entity = gamedata.get_skill_entity(region, item_id, reverse, expand)
        return Response(
            skill_entity.json(exclude_unset=True), media_type="application/json",
        )
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
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    - **expand**: Add expanded function objects to mstTreasureDeviceLv.expandedFuncId
    from the function IDs in mstTreasureDeviceLv.funcId.
    """
    if item_id in gamedata.masters[region].mstTreasureDeviceId:
        td_entity = gamedata.get_td_entity(region, item_id, reverse, expand)
        return Response(
            td_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="NP not found")


@router.get(
    "/{region}/function/{item_id}",
    summary="Get function data",
    response_description="Function entity",
    response_model=FunctionEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_function(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the function data from the given ID

    - **reverse**: Reverse lookup the skills that have this function
    and return the reversed skill objects.
    Will search recursively and return all entities in path: func -> skill -> servant.
    - **expand**: Add buff objects to mstFunc.expandedVals
    from the buff IDs in mstFunc.vals.
    """
    if item_id in gamedata.masters[region].mstFuncId:
        func_entity = gamedata.get_func_entity(region, item_id, reverse, expand)
        return Response(
            func_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Function not found")


@router.get(
    "/{region}/buff/{item_id}",
    summary="Get buff data",
    response_description="Buff entity",
    response_model=BuffEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_buff(region: Region, item_id: int, reverse: bool = False):
    """
    Get the buff data from the given ID

    - **reverse**: Reverse lookup the functions that have this buff
    and return the reversed function objects.
    Will search recursively and return all entities in path: buff -> func -> skill -> servant.
    """
    if item_id in gamedata.masters[region].mstBuffId:
        buff_entity = gamedata.get_buff_entity(region, item_id, reverse)
        return Response(
            buff_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Buff not found")


@router.get(
    "/{region}/item/{item_id}",
    summary="Get Item data",
    response_description="Item Entity",
    response_model=MstItem,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_item(region: Region, item_id: int):
    """
    Get the item data from the given ID
    """
    if item_id in gamedata.masters[region].mstItemId:
        return gamedata.masters[region].mstItemId[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")
