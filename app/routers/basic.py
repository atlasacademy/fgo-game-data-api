from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.engine import Connection

from ..config import Settings
from ..core import basic, search
from ..data.gamedata import masters
from ..schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicEvent,
    BasicFunctionReverse,
    BasicMysticCode,
    BasicServant,
    BasicSkillReverse,
    BasicTdReverse,
    BasicWar,
)
from ..schemas.common import Language, Region, ReverseDepth
from ..schemas.search import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
)
from .deps import get_db
from .utils import get_error_code, item_response, language_parameter, list_response


settings = Settings()
router = APIRouter(prefix="/basic", tags=["basic"])


basic_find_servant_extra = """
- **lang**: returns English names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + basic_find_servant_extra,
    response_description="Basic Servant Entities",
    response_model=List[BasicServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Optional[Language] = None,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_servant(conn, search_param, limit=10000)
    return list_response(
        basic.get_basic_servant(search_param.region, svt_id, lang) for svt_id in matches
    )


get_servant_description = """Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field.
"""
get_servant_description += basic_find_servant_extra
pre_processed_data_links = """

Preprocessed data:
- [NA servant](/export/NA/basic_servant.json)
- [JP servant](/export/JP/basic_servant.json)
- [JP servant with English names](/export/JP/basic_servant_lang_en.json)
"""

if settings.documentation_all_nice:
    get_servant_description += pre_processed_data_links


@router.get(
    "/{region}/servant/{servant_id}",
    summary="Get servant data",
    response_description="Basic Servant Entity",
    response_model=BasicServant,
    response_model_exclude_unset=True,
    description=get_servant_description,
    responses=get_error_code([400, 403]),
)
async def get_servant(
    region: Region, servant_id: int, lang: Optional[Language] = None
) -> Response:
    if servant_id in masters[region].mstSvtServantCollectionNo:
        servant_id = masters[region].mstSvtServantCollectionNo[servant_id]
    if servant_id in masters[region].mstSvtServantCollectionNo.values():
        return item_response(basic.get_basic_servant(region, servant_id, lang))
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + basic_find_servant_extra,
    response_description="Basic Equip Entities",
    response_model=List[BasicEquip],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    lang: Optional[Language] = None,
) -> Response:
    matches = search.search_equip(search_param, limit=10000)
    return list_response(
        basic.get_basic_equip(search_param.region, svt_id, lang) for svt_id in matches
    )


get_equip_description = """Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field.
"""
get_equip_description += basic_find_servant_extra
pre_processed_equip_links = """

Preprocessed data:
- [NA CE](/export/NA/basic_equip.json)
- [JP CE](/export/JP/basic_equip.json)
"""

if settings.documentation_all_nice:
    get_equip_description += pre_processed_equip_links


@router.get(
    "/{region}/equip/{equip_id}",
    summary="Get CE data",
    response_description="Basic CE Entity",
    response_model=BasicEquip,
    response_model_exclude_unset=True,
    description=get_equip_description,
    responses=get_error_code([400, 403]),
)
async def get_equip(
    region: Region, equip_id: int, lang: Optional[Language] = None
) -> Response:
    if equip_id in masters[region].mstSvtEquipCollectionNo:
        equip_id = masters[region].mstSvtEquipCollectionNo[equip_id]
    if equip_id in masters[region].mstSvtEquipCollectionNo.values():
        return item_response(basic.get_basic_equip(region, equip_id, lang))
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + basic_find_servant_extra,
    response_description="Basic Servant Entities",
    response_model=List[BasicServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    lang: Optional[Language] = None,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_servant(conn, search_param, limit=10000)
    return list_response(
        basic.get_basic_servant(search_param.region, svt_id, lang) for svt_id in matches
    )


@router.get(
    "/{region}/svt/{svt_id}",
    summary="Get svt data",
    response_description="Servant Entity",
    response_model=BasicServant,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_svt(
    region: Region, svt_id: int, lang: Language = Depends(language_parameter)
) -> Response:
    """
    Get svt info from ID

    Only use actual IDs for lookup. Does not convert from collectionNo.
    The endpoint is not limited to servants or equips ids.
    """
    if svt_id in masters[region].mstSvtId:
        return item_response(basic.get_basic_servant(region, svt_id, lang))
    else:
        raise HTTPException(status_code=404, detail="Svt not found")


get_mc_description = "Get basic Mystic Code info from ID"
pre_processed_mc_links = """

Preprocessed data:
- [NA Mystic Code](/export/NA/basic_mystic_code.json)
- [JP Mystic Code](/export/JP/basic_mystic_code.json)
"""

if settings.documentation_all_nice:
    get_mc_description += pre_processed_mc_links


@router.get(
    "/{region}/MC/{mc_id}",
    summary="Get Mystic Code data",
    description=get_mc_description,
    response_description="Mystic Code entity",
    response_model=BasicMysticCode,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_mystic_code(
    region: Region, mc_id: int, lang: Language = Depends(language_parameter)
) -> Response:
    if mc_id in masters[region].mstEquipId:
        return item_response(basic.get_basic_mc(region, mc_id, lang))
    else:
        raise HTTPException(status_code=404, detail="Mystic Code not found")


get_cc_description = "Get basic Command Code info from ID"
pre_processed_cc_links = """

Preprocessed data:
- [NA Command Code](/export/NA/basic_command_code.json)
- [JP Command Code](/export/JP/basic_command_code.json)
- [JP Command Code with English names](/export/JP/basic_command_code_lang_en.json)
"""

if settings.documentation_all_nice:
    get_cc_description += pre_processed_cc_links


@router.get(
    "/{region}/CC/{cc_id}",
    summary="Get Command Code data",
    description=get_cc_description,
    response_description="Command Code entity",
    response_model=BasicCommandCode,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_command_code(
    region: Region,
    cc_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    if cc_id in masters[region].mstCCCollectionNo:
        cc_id = masters[region].mstCCCollectionNo[cc_id]
    if cc_id in masters[region].mstCommandCodeId:
        return item_response(basic.get_basic_cc(region, cc_id, lang))
    else:
        raise HTTPException(status_code=404, detail="Command Code not found")


basic_skill_extra = """
- **reverse**: Reverse lookup the servants that have this skill
and return the reverse skill objects.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/skill/search",
    summary="Find and get skill data",
    description=SkillSearchParams.DESCRIPTION + basic_skill_extra,
    response_description="Basic Skill Entities",
    response_model=List[BasicSkillReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_skill(conn, search_param, limit=10000)
    return list_response(
        basic.get_basic_skill(search_param.region, skill_id, lang, reverse)
        for skill_id in matches
    )


@router.get(
    "/{region}/skill/{skill_id}",
    summary="Get skill data",
    description="Get the skill data fro mthe given ID" + basic_skill_extra,
    response_description="Skill entity",
    response_model=BasicSkillReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_skill(
    region: Region,
    skill_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
) -> Response:
    if skill_id in masters[region].mstSkillId:
        return item_response(basic.get_basic_skill(region, skill_id, lang, reverse))
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


basic_td_extra = """
- **reverse**: Reverse lookup the servants that have this NP
and return the reversed servant objects.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/NP/search",
    summary="Find and get NP data",
    description=TdSearchParams.DESCRIPTION + basic_td_extra,
    response_description="Basic NP Entities",
    response_model=List[BasicTdReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_td(conn, search_param, limit=10000)
    return list_response(
        basic.get_basic_td(search_param.region, td_id, lang, reverse)
        for td_id in matches
    )


@router.get(
    "/{region}/NP/{np_id}",
    summary="Get NP data",
    description="Get the NP data from the given ID" + basic_td_extra,
    response_description="NP entity",
    response_model=BasicTdReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_td(
    region: Region,
    np_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
) -> Response:
    if np_id in masters[region].mstTreasureDeviceId:
        return item_response(basic.get_basic_td(region, np_id, lang, reverse))
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
    responses=get_error_code([400, 403]),
)
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
) -> Response:
    matches = search.search_func(search_param, limit=10000)
    return list_response(
        basic.get_basic_function(
            search_param.region, func_id, lang, reverse, reverseDepth
        )
        for func_id in matches
    )


@router.get(
    "/{region}/function/{func_id}",
    summary="Get function data",
    description="Get the function data from the given ID"
    + function_reverse_lang_description,
    response_description="Function entity",
    response_model=BasicFunctionReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def get_function(
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
) -> Response:
    if func_id in masters[region].mstFuncId:
        return item_response(
            basic.get_basic_function(region, func_id, lang, reverse, reverseDepth)
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
    responses=get_error_code([400, 403]),
)
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
) -> Response:
    matches = search.search_buff(search_param, limit=10000)
    return list_response(
        basic.get_basic_buff(search_param.region, buff_id, lang, reverse, reverseDepth)
        for buff_id in matches
    )


@router.get(
    "/{region}/buff/{buff_id}",
    summary="Get buff data",
    description="Get the buff data from the given ID" + buff_reverse_lang_description,
    response_description="Buff Entity",
    response_model=BasicBuffReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_buff(
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
) -> Response:
    if buff_id in masters[region].mstBuffId:
        return item_response(
            basic.get_basic_buff(region, buff_id, lang, reverse, reverseDepth)
        )
    else:
        raise HTTPException(status_code=404, detail="Buff not found")


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Basic Event Entity",
    response_model=BasicEvent,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_event(region: Region, event_id: int) -> Response:
    """
    Get the basic event data from the given event ID
    """
    if event_id in masters[region].mstEventId:
        return item_response(basic.get_basic_event(region, event_id))
    else:
        raise HTTPException(status_code=404, detail="Event not found")


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="Basic War Entity",
    response_model=BasicWar,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_war(region: Region, war_id: int) -> Response:
    """
    Get the basic war data from the given event ID
    """
    if war_id in masters[region].mstWarId:
        return item_response(basic.get_basic_war(region, war_id))
    else:
        raise HTTPException(status_code=404, detail="Event not found")
