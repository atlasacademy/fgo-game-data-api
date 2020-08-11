from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Response

from ..config import Settings
from ..data import basic, search
from ..data.common import Language, Region, ReverseDepth
from ..data.gamedata import masters
from ..data.schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicFunctionReverse,
    BasicMysticCode,
    BasicServant,
    BasicSkillReverse,
    BasicTdReverse,
)
from .deps import (
    BuffSearchQueryParams,
    DetailMessage,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
    language_parameter,
)
from .utils import item_response, list_response


settings = Settings()


responses: Dict[Union[str, int], Any] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


router = APIRouter()


nice_find_servant_extra = """
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + nice_find_servant_extra,
    response_description="Basic Servant Entities",
    response_model=List[BasicServant],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Optional[Language] = None,
) -> List[Dict[str, Any]]:
    if search_param.hasSearchParams:
        matches = search.search_servant(search_param)
        return [
            basic.get_basic_svt(search_param.region, item, lang) for item in matches
        ]
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_servant_description = """Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field.

- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""
pre_processed_data_links = """

Preprocessed data:
- [NA servant](/export/NA/basic_servant.json)
- [JP servant](/export/JP/basic_servant.json)
- [JP servant with English names](/export/JP/basic_servant_lang_en.json)
"""

if settings.documentation_all_nice:
    get_servant_description += pre_processed_data_links


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Basic Servant Entity",
    response_model=BasicServant,
    response_model_exclude_unset=True,
    description=get_servant_description,
    responses=responses,
)
async def get_servant(
    region: Region, item_id: int, lang: Optional[Language] = None
) -> Dict[str, Any]:
    if item_id in masters[region].mstSvtServantCollectionNo:
        item_id = masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in masters[region].mstSvtServantCollectionNo.values():
        return basic.get_basic_svt(region, item_id, lang)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION,
    response_description="Basic Equip Entities",
    response_model=List[BasicEquip],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
) -> List[Dict[str, Any]]:
    if search_param.hasSearchParams:
        matches = search.search_equip(search_param)
        return [basic.get_basic_svt(search_param.region, item) for item in matches]
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_equip_description = """Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field.
"""
pre_processed_equip_links = """

Preprocessed data:
- [NA CE](/export/NA/basic_equip.json)
- [JP CE](/export/JP/basic_equip.json)
"""

if settings.documentation_all_nice:
    get_equip_description += pre_processed_equip_links


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    response_description="Basic CE Entity",
    response_model=BasicEquip,
    response_model_exclude_unset=True,
    description=get_equip_description,
    responses=responses,
)
async def get_equip(region: Region, item_id: int) -> Dict[str, Any]:
    if item_id in masters[region].mstSvtEquipCollectionNo:
        item_id = masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in masters[region].mstSvtEquipCollectionNo.values():
        return basic.get_basic_svt(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


get_mc_description = "Get basic Mystic Code info from ID"
pre_processed_mc_links = """

Preprocessed data:
- [NA Mystic Code](/export/NA/basic_mystic_code.json)
- [JP Mystic Code](/export/JP/basic_mystic_code.json)
"""

if settings.documentation_all_nice:
    get_mc_description += pre_processed_mc_links


@router.get(
    "/{region}/MC/{item_id}",
    summary="Get Mystic Code data",
    description=get_mc_description,
    response_description="Mystic Code entity",
    response_model=BasicMysticCode,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_mystic_code(region: Region, item_id: int) -> Response:
    if item_id in masters[region].mstEquipId:
        return item_response(basic.get_basic_mc(region, item_id))
    else:
        raise HTTPException(status_code=404, detail="Mystic Code not found")


get_cc_description = "Get basic Command Code info from ID"
pre_processed_cc_links = """

Preprocessed data:
- [NA Command Code](/export/NA/basic_command_code.json)
- [JP Command Code](/export/JP/basic_command_code.json)
"""

if settings.documentation_all_nice:
    get_cc_description += pre_processed_cc_links


@router.get(
    "/{region}/CC/{item_id}",
    summary="Get Command Code data",
    description=get_cc_description,
    response_description="Command Code entity",
    response_model=BasicCommandCode,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_command_code(region: Region, item_id: int) -> Response:
    if item_id in masters[region].mstCommandCodeId:
        return item_response(basic.get_basic_cc(region, item_id))
    else:
        raise HTTPException(status_code=404, detail="Command Code not found")


@router.get(
    "/{region}/skill/{item_id}",
    summary="Get skill data",
    response_description="Skill entity",
    response_model=BasicSkillReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_skill(
    region: Region,
    item_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    """
    if item_id in masters[region].mstSkillId:
        return item_response(basic.get_basic_skill(region, item_id, lang, reverse))
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@router.get(
    "/{region}/NP/{item_id}",
    summary="Get NP data",
    response_description="NP entity",
    response_model=BasicTdReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_td(
    region: Region,
    item_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    """
    if item_id in masters[region].mstTreasureDeviceId:
        return item_response(basic.get_basic_td(region, item_id, lang, reverse))
    else:
        raise HTTPException(status_code=404, detail="NP not found")


function_reverse_lang_description = """
- **reverse**: Reverse lookup the skills that have this function
and return the reversed skill objects.
- **reverseDepth**: Controls the depth of the reverse lookup: func -> skill/np -> servant.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/function/search",
    summary="Find and get function data",
    description=FuncSearchQueryParams.DESCRIPTION + function_reverse_lang_description,
    response_description="Function entity",
    response_model=List[BasicFunctionReverse],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
) -> Response:
    if search_param.hasSearchParams:
        matches = search.search_func(search_param)
        entity_list = [
            basic.get_basic_function(
                search_param.region, item, lang, reverse, reverseDepth
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
    + function_reverse_lang_description,
    response_description="Function entity",
    response_model=BasicFunctionReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_function(
    region: Region,
    item_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
) -> Response:
    if item_id in masters[region].mstFuncId:
        return item_response(
            basic.get_basic_function(region, item_id, lang, reverse, reverseDepth)
        )
    else:
        raise HTTPException(status_code=404, detail="Function not found")


buff_reverse_lang_description = """
- **reverse**: Reverse lookup the functions that have this buff
and return the reversed function objects.
- **reverseDepth**: Controls the depth of the reverse lookup: buff -> func -> skill/np -> servant.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/buff/search",
    summary="Find and get buff data",
    description=BuffSearchQueryParams.DESCRIPTION + buff_reverse_lang_description,
    response_description="Function entity",
    response_model=List[BasicBuffReverse],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
) -> Response:
    if search_param.hasSearchParams:
        matches = search.search_buff(search_param)
        entity_list = [
            basic.get_basic_buff(search_param.region, item, lang, reverse, reverseDepth)
            for item in matches
        ]
        return list_response(entity_list)
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


@router.get(
    "/{region}/buff/{item_id}",
    summary="Get buff data",
    description="Get the buff data from the given ID" + buff_reverse_lang_description,
    response_description="Buff Entity",
    response_model=BasicBuffReverse,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_buff(
    region: Region,
    item_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
) -> Response:
    if item_id in masters[region].mstBuffId:
        return item_response(
            basic.get_basic_buff(region, item_id, lang, reverse, reverseDepth)
        )
    else:
        raise HTTPException(status_code=404, detail="Buff not found")
