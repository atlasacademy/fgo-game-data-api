from fastapi import APIRouter, Depends, Response
from fastapi_cache.decorator import cache

from ..config import Settings
from ..core import search
from ..core.nice import (
    ai,
    bgm,
    cc,
    enemy_master,
    item,
    mc,
    mm,
    nice,
    quest,
    script,
    war,
)
from ..core.nice.common_release import get_nice_common_releases_from_id
from ..core.nice.event.event import get_nice_event
from ..core.nice.event.shop import get_nice_shop_from_raw, get_nice_shops_from_raw
from ..core.nice.script import get_nice_script_search_result
from ..db.helpers.cc import get_cc_id
from ..db.helpers.svt import get_ce_id, get_svt_id
from ..redis import Redis
from ..schemas.common import Language, Region, ReverseData, ReverseDepth
from ..schemas.enums import AiType
from ..schemas.nice import (
    NiceAiCollection,
    NiceBaseFunctionReverse,
    NiceBgmEntity,
    NiceBuffReverse,
    NiceCommandCode,
    NiceCommonRelease,
    NiceEnemyMaster,
    NiceEquip,
    NiceEvent,
    NiceItem,
    NiceMasterMission,
    NiceMysticCode,
    NiceQuest,
    NiceQuestPhase,
    NiceScript,
    NiceScriptSearchResult,
    NiceServant,
    NiceShop,
    NiceSkillReverse,
    NiceTdReverse,
    NiceWar,
)
from ..schemas.search import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ItemSearchQueryParams,
    ScriptSearchQueryParams,
    ServantSearchQueryParams,
    ShopSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
)
from .deps import get_db, get_db_transaction, get_redis, language_parameter
from .utils import get_error_code, item_response, list_response


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
    response_model=list[NiceServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
@cache()
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_servant(conn, search_param)
        return list_response(
            [
                await nice.get_nice_servant_model(
                    conn, search_param.region, mstSvt.id, lang, lore, mstSvt
                )
                for mstSvt in matches
            ]
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
@cache()
async def get_servant(
    region: Region,
    servant_id: int,
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    async with get_db(region) as conn:
        servant_id = await get_svt_id(conn, servant_id)
        return item_response(
            await nice.get_nice_servant_model(conn, region, servant_id, lang, lore)
        )


equip_lore_description = """
- **lore**: Add profile info to the response
"""


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + equip_lore_description,
    response_description="Equip Entity",
    response_model=list[NiceEquip],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
@cache()
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_equip(conn, search_param)
        return list_response(
            [
                await nice.get_nice_equip_model(
                    conn, search_param.region, mstSvt.id, lang, lore, mstSvt
                )
                for mstSvt in matches
            ]
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
@cache()
async def get_equip(
    region: Region,
    equip_id: int,
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    async with get_db(region) as conn:
        equip_id = await get_ce_id(conn, equip_id)
        return item_response(
            await nice.get_nice_equip_model(conn, region, equip_id, lang, lore)
        )


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + svt_lang_lore_description,
    response_description="Nice Servant Entities",
    response_model=list[NiceServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
@cache()
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    lang: Language = Depends(language_parameter),
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_servant(conn, search_param)
        return list_response(
            [
                await nice.get_nice_servant_model(
                    conn, search_param.region, mstSvt.id, lang, lore, mstSvt
                )
                for mstSvt in matches
            ]
        )


@router.get(
    "/{region}/svt/{svt_id}",
    summary="Get svt data",
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache()
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
    async with get_db(region) as conn:
        return item_response(
            await nice.get_nice_servant_model(conn, region, svt_id, lang, lore)
        )


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
@cache()
async def get_mystic_code(
    region: Region,
    mc_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(region) as conn:
        return item_response(await mc.get_nice_mystic_code(conn, region, mc_id, lang))


get_cc_description = "Get nice Command Code info from ID"
pre_processed_cc_links = """

Preprocessed data:
- [NA Command Code](/export/NA/nice_command_code.json)
- [JP Command Code](/export/JP/nice_command_code.json)
- [JP Command Code with English names](/export/JP/nice_command_code_lang_en.json)
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
@cache()
async def get_command_code(
    region: Region,
    cc_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(region) as conn:
        cc_id = await get_cc_id(conn, cc_id)
        return item_response(await cc.get_nice_command_code(conn, region, cc_id, lang))


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
    response_model=list[NiceSkillReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_skill(conn, search_param)
        return list_response(
            [
                await nice.get_nice_skill_with_reverse(
                    conn,
                    redis,
                    search_param.region,
                    mstSkill.id,
                    lang,
                    reverse,
                    reverseData=reverseData,
                )
                for mstSkill in matches
            ]
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
@cache()
async def get_skill(
    region: Region,
    skill_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        return item_response(
            await nice.get_nice_skill_with_reverse(
                conn, redis, region, skill_id, lang, reverse, reverseData=reverseData
            )
        )


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
    response_model=list[NiceTdReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_td(conn, search_param)
        return list_response(
            [
                await nice.get_nice_td_with_reverse(
                    conn,
                    redis,
                    search_param.region,
                    td.id,
                    lang,
                    reverse,
                    reverseData=reverseData,
                )
                for td in matches
            ]
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
@cache()
async def get_td(
    region: Region,
    np_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        return item_response(
            await nice.get_nice_td_with_reverse(
                conn, redis, region, np_id, lang, reverse, reverseData=reverseData
            )
        )


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
    response_model=list[NiceBaseFunctionReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
@cache()
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_func(conn, search_param)
        return list_response(
            [
                await nice.get_nice_func_with_reverse(
                    conn,
                    redis,
                    search_param.region,
                    mstFunc.id,
                    lang,
                    reverse,
                    reverseDepth,
                    reverseData,
                    mstFunc,
                )
                for mstFunc in matches
            ]
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
@cache()
async def get_function(
    region: Region,
    func_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        return item_response(
            await nice.get_nice_func_with_reverse(
                conn, redis, region, func_id, lang, reverse, reverseDepth, reverseData
            )
        )


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
    response_model=list[NiceBuffReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403, 500]),
)
@cache()
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_buff(conn, search_param)
        return list_response(
            [
                await nice.get_nice_buff_with_reverse(
                    conn,
                    redis,
                    search_param.region,
                    mstBuff.id,
                    lang,
                    reverse,
                    reverseDepth,
                    reverseData,
                    mstBuff,
                )
                for mstBuff in matches
            ]
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
@cache()
async def get_buff(
    region: Region,
    buff_id: int,
    lang: Language = Depends(language_parameter),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        return item_response(
            await nice.get_nice_buff_with_reverse(
                conn, redis, region, buff_id, lang, reverse, reverseDepth, reverseData
            )
        )


@router.get(
    "/{region}/item/search",
    summary="Find and get item data",
    description=ItemSearchQueryParams.DESCRIPTION,
    response_description="Item entity",
    response_model=list[NiceItem],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_item(
    search_param: ItemSearchQueryParams = Depends(ItemSearchQueryParams),
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_item(conn, search_param)
        return list_response(
            item.get_nice_item_from_raw(search_param.region, mstItem, lang)
            for mstItem in matches
        )


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
@cache()
async def get_item(
    region: Region,
    item_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice item data from the given item ID
    """
    async with get_db(region) as conn:
        return item_response(await item.get_nice_item(conn, region, item_id, lang))


@router.get(
    "/{region}/mm/{master_mission_id}",
    summary="Get Master Mission data",
    response_description="Master Mission Entity",
    response_model=NiceMasterMission,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_mm(
    region: Region,
    master_mission_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the master mission data from the given master mission ID
    """
    async with get_db(region) as conn:
        return item_response(
            await mm.get_nice_master_mission(conn, region, master_mission_id, lang)
        )


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Nice Event Entity",
    response_model=NiceEvent,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache()
async def get_event(
    region: Region,
    event_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice event data from the given event ID
    """
    async with get_db(region) as conn:
        return item_response(await get_nice_event(conn, region, event_id, lang))


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="Nice War Entity",
    response_model=NiceWar,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache(expire=settings.quest_cache_length)
async def get_war(
    region: Region,
    war_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice war data from the given war ID
    """
    async with get_db(region) as conn:
        return item_response(await war.get_nice_war(conn, region, war_id, lang))


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
async def get_quest_phase(
    region: Region,
    quest_id: int,
    phase: int,
    redis: Redis = Depends(get_redis),
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db_transaction(region) as conn:
        return item_response(
            await quest.get_nice_quest_phase(conn, redis, region, quest_id, phase, lang)
        )


@router.get(
    "/{region}/quest/{quest_id}",
    summary="Get Nice Quest data",
    response_description="Quest Entity",
    response_model=NiceQuest,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache(expire=settings.quest_cache_length)
async def get_quest(
    region: Region,
    quest_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice quest data from the given quest ID
    """
    async with get_db(region) as conn:
        return item_response(
            await quest.get_nice_quest_alone(conn, region, quest_id, lang)
        )


@router.get(
    "/{region}/script/search",
    summary="Find and get script data",
    description=ScriptSearchQueryParams.DESCRIPTION,
    response_description="Script Search Result",
    response_model=list[NiceScriptSearchResult],
    response_model_exclude_unset=True,
)
async def find_script(
    search_param: ScriptSearchQueryParams = Depends(ScriptSearchQueryParams),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_script(conn, search_param)
        return list_response(
            get_nice_script_search_result(search_param.region, match)
            for match in matches
        )


@router.get(
    "/{region}/script/{script_id}",
    summary="Get Script data",
    response_description="Nice Script Entity",
    response_model=NiceScript,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_script(
    region: Region,
    script_id: str,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice script data from the given script ID
    """
    async with get_db(region) as conn:
        return item_response(
            await script.get_nice_script(conn, region, script_id, lang)
        )


@router.get(
    "/{region}/ai/{ai_type}/{ai_id}",
    summary="Get AI data",
    response_description="Nice AI Entity",
    response_model=NiceAiCollection,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_ai_field(
    region: Region,
    ai_type: AiType,
    ai_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the nice AI data from the given AI ID
    """
    field_flag = ai_type == AiType.field
    async with get_db(region) as conn:
        ai_entity = await ai.get_nice_ai_collection(
            conn, region, ai_id, field=field_flag, lang=lang
        )
        return item_response(ai_entity)


@router.get(
    "/{region}/bgm/{bgm_id}",
    summary="Get Nice BGM data",
    response_description="BGM Entity",
    response_model=NiceBgmEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_bgm(
    region: Region,
    bgm_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the BGM data from the given BGM ID
    """
    async with get_db(region) as conn:
        return item_response(await bgm.get_nice_bgm_entity(conn, region, bgm_id, lang))


@router.get(
    "/{region}/shop/search",
    summary="Find and get nice shop data",
    description="Find and get nice shop data",
    response_description="Nice Shop Entities",
    response_model=list[NiceShop],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_shop(
    search_param: ShopSearchQueryParams = Depends(ShopSearchQueryParams),
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_shop(conn, search_param, limit=10000)
        return list_response(
            await get_nice_shops_from_raw(conn, search_param.region, matches, lang)
        )


@router.get(
    "/{region}/shop/{shop_id}",
    summary="Get Nice Shop data",
    response_description="Nice Shop Entity",
    response_model=NiceShop,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_shop(
    region: Region,
    shop_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the shop data from the given shop ID
    """
    async with get_db(region) as conn:
        return item_response(await get_nice_shop_from_raw(conn, region, shop_id, lang))


@router.get(
    "/{region}/common-release/{common_release_id}",
    summary="Get Nice Common Release data",
    response_description="List of Nice Common Release Entities",
    response_model=list[NiceCommonRelease],
    response_model_exclude_unset=True,
)
@cache()
async def get_common_releases(region: Region, common_release_id: int) -> Response:
    """
    Get the common release data from the given ID
    """
    async with get_db(region) as conn:
        return list_response(
            await get_nice_common_releases_from_id(conn, common_release_id)
        )


@router.get(
    "/{region}/enemy-master/{master_id}",
    summary="Get Enemy Master data",
    response_description="Nice Enemy Master Entity",
    response_model=NiceEnemyMaster,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_enemy_master(
    region: Region,
    master_id: int,
) -> Response:
    async with get_db(region) as conn:
        return item_response(
            await enemy_master.get_nice_enemy_master(conn, region, master_id)
        )
