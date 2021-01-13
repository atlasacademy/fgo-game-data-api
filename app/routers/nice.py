from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from ..config import Settings
from ..data import nice, search
from ..data.common import Language, Region, ReverseData, ReverseDepth
from ..data.gamedata import masters
from ..data.schemas.nice import (
    NiceBaseFunctionReverse,
    NiceBuffReverse,
    NiceCommandCode,
    NiceEquip,
    NiceEvent,
    NiceItem,
    NiceMysticCode,
    NiceQuest,
    NiceQuestPhase,
    NiceServant,
    NiceSkillReverse,
    NiceTdReverse,
    NiceWar,
)
from .deps import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
    get_error_code,
    language_parameter,
)
from .utils import item_response, list_response


settings = Settings()
router = APIRouter(prefix="/nice", tags=["nice"])


svt_lang_lore_description = """
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
- **lore**: Add profile info to the response
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + svt_lang_lore_description,
    response_description="Servant Entity",
    response_model=List[NiceServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    matches = search.search_servant(search_param)
    return list_response(
        nice.get_nice_servant_model(search_param.region, svt_id, lang, lore)
        for svt_id in matches
    )


get_servant_description = """Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field.

"""
pre_processed_data_links = """

Preprocessed data:
- [NA servant](/export/NA/nice_servant.json), [NA Servant with lore](/export/NA/nice_servant_lore.json)
- [JP servant](/export/JP/nice_servant.json), [JP Servant with lore](/export/JP/nice_servant_lore.json)
"""

get_servant_description += svt_lang_lore_description

if settings.documentation_all_nice:
    get_servant_description += pre_processed_data_links


@router.get(
    "/{region}/servant/{servant_id}",
    summary="Get servant data",
    description=get_servant_description,
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_servant(
    region: Region,
    servant_id: int,
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    if servant_id in masters[region].mstSvtServantCollectionNo:
        servant_id = masters[region].mstSvtServantCollectionNo[servant_id]
    if servant_id in masters[region].mstSvtServantCollectionNo.values():
        return item_response(
            nice.get_nice_servant_model(region, servant_id, lang, lore)
        )
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


equip_lore_description = """
- **lore**: Add profile info to the response
"""


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + equip_lore_description,
    response_description="Equip Entity",
    response_model=List[NiceEquip],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    matches = search.search_equip(search_param)
    return list_response(
        nice.get_nice_equip_model(search_param.region, svt_id, lang, lore)
        for svt_id in matches
    )


get_equip_description = """Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field.

"""
pre_processed_equip_links = """

Preprocessed data:
- [NA CE](/export/NA/nice_equip.json), [NA CE with lore](/export/NA/nice_equip_lore.json)
- [JP CE](/export/JP/nice_equip.json), [JP CE with lore](/export/JP/nice_equip_lore.json)
"""

get_equip_description += equip_lore_description

if settings.documentation_all_nice:
    get_equip_description += pre_processed_equip_links


@router.get(
    "/{region}/equip/{equip_id}",
    summary="Get CE data",
    description=get_equip_description,
    response_description="CE Entity",
    response_model=NiceEquip,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_equip(
    region: Region,
    equip_id: int,
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    if equip_id in masters[region].mstSvtEquipCollectionNo:
        equip_id = masters[region].mstSvtEquipCollectionNo[equip_id]
    if equip_id in masters[region].mstSvtEquipCollectionNo.values():
        return item_response(nice.get_nice_equip_model(region, equip_id, lang, lore))
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + svt_lang_lore_description,
    response_description="Nice Servant Entities",
    response_model=List[NiceServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    matches = search.search_servant(search_param)
    return list_response(
        nice.get_nice_servant_model(search_param.region, svt_id, lang, lore)
        for svt_id in matches
    )


@router.get(
    "/{region}/svt/{svt_id}",
    summary="Get svt data",
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_svt(
    region: Region,
    svt_id: int,
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    """
    Get svt info from ID

    Only use actual IDs for lookup. Does not convert from collectionNo.
    The endpoint is not limited to servants or equips ids.
    """
    if svt_id in masters[region].mstSvtId:
        return item_response(nice.get_nice_servant_model(region, svt_id, lang, lore))
    else:
        raise HTTPException(status_code=404, detail="Svt not found")


get_mc_description = "Get nice Mystic Code info from ID"
pre_processed_mc_links = """

Preprocessed data:
- [NA Mystic Code](/export/NA/nice_mystic_code.json)
- [JP Mystic Code](/export/JP/nice_mystic_code.json)
"""

if settings.documentation_all_nice:
    get_mc_description += pre_processed_mc_links


@router.get(
    "/{region}/MC/{mc_id}",
    summary="Get Mystic Code data",
    description=get_mc_description,
    response_description="Mystic Code entity",
    response_model=NiceMysticCode,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_mystic_code(region: Region, mc_id: int) -> Response:
    if mc_id in masters[region].mstEquipId:
        return item_response(nice.get_nice_mystic_code(region, mc_id))
    else:
        raise HTTPException(status_code=404, detail="Mystic Code not found")


get_cc_description = "Get nice Command Code info from ID"
pre_processed_cc_links = """

Preprocessed data:
- [NA Command Code](/export/NA/nice_command_code.json)
- [JP Command Code](/export/JP/nice_command_code.json)
"""

if settings.documentation_all_nice:
    get_cc_description += pre_processed_cc_links


@router.get(
    "/{region}/CC/{cc_id}",
    summary="Get Command Code data",
    description=get_cc_description,
    response_description="Command Code entity",
    response_model=NiceCommandCode,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_command_code(region: Region, cc_id: int) -> Response:
    if cc_id in masters[region].mstCommandCodeId:
        return item_response(nice.get_nice_command_code(region, cc_id))
    else:
        raise HTTPException(status_code=404, detail="Command Code not found")


nice_skill_extra = """
- **reverse**: Reverse lookup the servants that have this skill
and return the reverse skill objects.
- **reverseData**: if set to `basic`, will return basic entities.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/skill/search",
    summary="Find and get skill data",
    description=SkillSearchParams.DESCRIPTION + nice_skill_extra,
    response_description="Nice Skill entities",
    response_model=List[NiceSkillReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    matches = search.search_skill(search_param)
    return list_response(
        nice.get_nice_skill_alone(
            search_param.region, skill_id, lang, reverse, reverseData=reverseData
        )
        for skill_id in matches
    )


@router.get(
    "/{region}/skill/{skill_id}",
    summary="Get skill data",
    description="Get the skill data from the given ID" + nice_skill_extra,
    response_description="Nice Skill entity",
    response_model=NiceSkillReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_skill(
    region: Region,
    skill_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    if skill_id in masters[region].mstSkillId:
        return item_response(
            nice.get_nice_skill_alone(
                region, skill_id, lang, reverse, reverseData=reverseData
            )
        )
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


nice_td_extra = """
- **reverse**: Reverse lookup the servants that have this NP
and return the reversed servant objects.
- **reverseData**: if set to `basic`, will return basic entities.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/NP/search",
    summary="Find and get NP data",
    description=TdSearchParams.DESCRIPTION + nice_td_extra,
    response_description="Nice NP Entities",
    response_model=List[NiceTdReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    matches = search.search_td(search_param)
    return list_response(
        nice.get_nice_td_alone(
            search_param.region, td_id, lang, reverse, reverseData=reverseData
        )
        for td_id in matches
    )


@router.get(
    "/{region}/NP/{np_id}",
    summary="Get NP data",
    description="Get the NP data from the given ID" + nice_td_extra,
    response_description="Nice NP entity",
    response_model=NiceTdReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_td(
    region: Region,
    np_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    if np_id in masters[region].mstTreasureDeviceId:
        return item_response(
            nice.get_nice_td_alone(
                region, np_id, lang, reverse, reverseData=reverseData
            )
        )
    else:
        raise HTTPException(status_code=404, detail="NP not found")


function_reverse_lang_description = """
- **reverse**: Reverse lookup the skills that have this function
and return the reversed skill objects.
- **reverseDepth**: Controls the depth of the reverse lookup: func -> skill/np -> servant.
- **reverseData**: if set to `basic`, will return basic entities.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/function/search",
    summary="Find and get function data",
    description=FuncSearchQueryParams.DESCRIPTION + function_reverse_lang_description,
    response_description="Function entity",
    response_model=List[NiceBaseFunctionReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    matches = search.search_func(search_param)
    return list_response(
        nice.get_nice_func_alone(
            search_param.region, func_id, lang, reverse, reverseDepth, reverseData
        )
        for func_id in matches
    )


@router.get(
    "/{region}/function/{func_id}",
    summary="Get function data",
    description="Get the function data from the given ID"
    + function_reverse_lang_description,
    response_description="Function entity",
    response_model=NiceBaseFunctionReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_function(
    region: Region,
    func_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    if func_id in masters[region].mstFuncId:
        return item_response(
            nice.get_nice_func_alone(
                region, func_id, lang, reverse, reverseDepth, reverseData
            )
        )
    else:
        raise HTTPException(status_code=404, detail="Function not found")


buff_reverse_lang_description = """
- **reverse**: Reverse lookup the functions that have this buff
and return the reversed function objects.
- **reverseDepth**: Controls the depth of the reverse lookup: buff -> func -> skill/np -> servant.
- **reverseData**: if set to `basic`, will return basic entities.
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/buff/search",
    summary="Find and get buff data",
    description=BuffSearchQueryParams.DESCRIPTION + buff_reverse_lang_description,
    response_description="Function entity",
    response_model=List[NiceBuffReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    matches = search.search_buff(search_param)
    return list_response(
        nice.get_nice_buff_alone(
            search_param.region, buff_id, lang, reverse, reverseDepth, reverseData
        )
        for buff_id in matches
    )


@router.get(
    "/{region}/buff/{buff_id}",
    summary="Get buff data",
    description="Get the buff data from the given ID" + buff_reverse_lang_description,
    response_description="Buff Entity",
    response_model=NiceBuffReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_buff(
    region: Region,
    buff_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
) -> Response:
    if buff_id in masters[region].mstBuffId:
        return item_response(
            nice.get_nice_buff_alone(
                region, buff_id, lang, reverse, reverseDepth, reverseData
            )
        )
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
    description=get_item_description,
    response_description="Item Entity",
    response_model=NiceItem,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_item(region: Region, item_id: int) -> Response:
    """
    Get the nice item data from the given item ID
    """
    if item_id in masters[region].mstItemId:
        return item_response(nice.get_nice_item(region, item_id))
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Nice Event Entity",
    response_model=NiceEvent,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_event(region: Region, event_id: int) -> Response:
    """
    Get the nice event data from the given event ID
    """
    if event_id in masters[region].mstEventId:
        return item_response(nice.get_nice_event(region, event_id))
    else:
        raise HTTPException(status_code=404, detail="Event not found")


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="Nice War Entity",
    response_model=NiceWar,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_war(region: Region, war_id: int) -> Response:
    """
    Get the nice war data from the given war ID
    """
    if war_id in masters[region].mstWarId:
        return item_response(nice.get_nice_war(region, war_id))
    else:
        raise HTTPException(status_code=404, detail="War not found")


get_quest_phase_description = (
    "Get the nice quest phase data from the given quest ID and phase number"
)


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Nice Quest Phase data",
    description=get_quest_phase_description,
    response_description="Quest Phase Entity",
    response_model=NiceQuestPhase,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_quest_phase(region: Region, quest_id: int, phase: int) -> Response:
    if (
        quest_id in masters[region].mstQuestPhaseId
        and phase in masters[region].mstQuestPhaseId[quest_id]
    ):
        return item_response(nice.get_nice_quest_phase(region, quest_id, phase))
    else:
        raise HTTPException(status_code=404, detail="Quest Phase not found")


@router.get(
    "/{region}/quest/{quest_id}",
    summary="Get Nice Quest data",
    response_description="Quest Entity",
    response_model=NiceQuest,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
async def get_quest(region: Region, quest_id: int) -> Response:
    """
    Get the nice quest data from the given quest ID
    """
    if quest_id in masters[region].mstQuestId:
        return item_response(nice.get_nice_quest_alone(region, quest_id))
    else:
        raise HTTPException(status_code=404, detail="Quest not found")
