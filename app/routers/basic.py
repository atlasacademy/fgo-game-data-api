from typing import Optional

from fastapi import APIRouter, Depends, Response
from fastapi_cache.decorator import cache

from ..config import Settings
from ..core import basic, search
from ..db.helpers.cc import get_cc_id
from ..db.helpers.svt import get_ce_id, get_svt_id
from ..redis import Redis
from ..schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicEvent,
    BasicFunctionReverse,
    BasicMysticCode,
    BasicQuest,
    BasicQuestPhase,
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
    QuestSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
)
from .deps import get_db, get_redis, language_parameter
from .utils import get_error_code, item_response, list_response


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
    response_model=list[BasicServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Optional[Language] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_servant(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_servant(
                    redis, search_param.region, mstSvt.id, 0, lang=lang, mstSvt=mstSvt
                )
                for mstSvt in matches
            ]
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
@cache()
async def get_servant(
    region: Region,
    servant_id: int,
    lang: Optional[Language] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        servant_id = await get_svt_id(conn, servant_id)
        return item_response(
            await basic.get_basic_servant(redis, region, servant_id, lang=lang)
        )


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + basic_find_servant_extra,
    response_description="Basic Equip Entities",
    response_model=list[BasicEquip],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    lang: Optional[Language] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_equip(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_equip(
                    redis, search_param.region, mstSvt.id, lang, mstSvt
                )
                for mstSvt in matches
            ]
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
@cache()
async def get_equip(
    region: Region,
    equip_id: int,
    lang: Optional[Language] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        equip_id = await get_ce_id(conn, equip_id)
        return item_response(await basic.get_basic_equip(redis, region, equip_id, lang))


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + basic_find_servant_extra,
    response_description="Basic Servant Entities",
    response_model=list[BasicServant],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    lang: Optional[Language] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_servant(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_servant(
                    redis, search_param.region, mstSvt.id, 0, lang=lang, mstSvt=mstSvt
                )
                for mstSvt in matches
            ]
        )


@router.get(
    "/{region}/svt/{svt_id}",
    summary="Get svt data",
    response_description="Servant Entity",
    response_model=BasicServant,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def get_svt(
    region: Region,
    svt_id: int,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    """
    Get svt info from ID

    Only use actual IDs for lookup. Does not convert from collectionNo.
    The endpoint is not limited to servants or equips ids.
    """
    return item_response(
        await basic.get_basic_servant(redis, region, svt_id, lang=lang)
    )


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
@cache()
async def get_mystic_code(
    region: Region,
    mc_id: int,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    return item_response(await basic.get_basic_mc(redis, region, mc_id, lang))


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
@cache()
async def get_command_code(
    region: Region,
    cc_id: int,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        cc_id = await get_cc_id(conn, cc_id)
        return item_response(await basic.get_basic_cc(redis, region, cc_id, lang))


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
    response_model=list[BasicSkillReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_skill(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_skill(
                    redis,
                    search_param.region,
                    mstSkill.id,
                    lang,
                    reverse,
                    mstSkill=mstSkill,
                )
                for mstSkill in matches
            ]
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
@cache()
async def get_skill(
    region: Region,
    skill_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    return item_response(
        await basic.get_basic_skill(redis, region, skill_id, lang, reverse)
    )


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
    response_model=list[BasicTdReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_td(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_td(
                    redis,
                    search_param.region,
                    td.id,
                    lang,
                    reverse,
                    mstTreasureDevice=td,
                )
                for td in matches
            ]
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
@cache()
async def get_td(
    region: Region,
    np_id: int,
    reverse: bool = False,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    return item_response(await basic.get_basic_td(redis, region, np_id, lang, reverse))


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
    response_model=list[BasicFunctionReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_func(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_function_from_raw(
                    redis, search_param.region, mstFunc, lang, reverse, reverseDepth
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
    response_model=BasicFunctionReverse,
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def get_function(
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    return item_response(
        await basic.get_basic_function(
            redis, region, func_id, lang, reverse, reverseDepth
        )
    )


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
    response_model=list[BasicBuffReverse],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_buff(conn, search_param, limit=10000)
        return list_response(
            [
                await basic.get_basic_buff_from_raw(
                    redis, search_param.region, mstBuff, lang, reverse, reverseDepth
                )
                for mstBuff in matches
            ]
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
@cache()
async def get_buff(
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    lang: Language = Depends(language_parameter),
    redis: Redis = Depends(get_redis),
) -> Response:
    return item_response(
        await basic.get_basic_buff(redis, region, buff_id, lang, reverse, reverseDepth)
    )


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Basic Event Entity",
    response_model=BasicEvent,
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
    Get the basic event data from the given event ID
    """
    async with get_db(region) as conn:
        return item_response(await basic.get_basic_event(conn, event_id, lang))


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="Basic War Entity",
    response_model=BasicWar,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache()
async def get_war(
    region: Region,
    war_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the basic war data from the given event ID
    """
    async with get_db(region) as conn:
        return item_response(await basic.get_basic_war(conn, war_id, lang))


@router.get(
    "/{region}/quest/phase/latestEnemyData",
    summary="Get latest quests with enemy data",
    response_description="Basic Quest Phase Entities",
    response_model=list[BasicQuestPhase],
    response_model_exclude_unset=True,
)
@cache(expire=settings.quest_cache_length)
async def get_latest_quest_phase_with_enemies(
    region: Region,
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(region) as conn:
        return list_response(
            await basic.get_basic_quest_latest_with_enemies(conn, lang)
        )


@router.get(
    "/{region}/quest/phase/search",
    summary="Find and get quest phase data",
    description=QuestSearchQueryParams.DESCRIPTION,
    response_description="Basic Quest Phase Entities",
    response_model=list[BasicQuestPhase],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache(expire=settings.quest_cache_length)
async def find_quest_phase(
    search_param: QuestSearchQueryParams = Depends(QuestSearchQueryParams),
    lang: Language = Depends(language_parameter),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_quest(conn, search_param)
        return list_response(
            [basic.get_basic_quest_phase_from_raw(quest, lang) for quest in matches]
        )


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Basic Quest Phase data",
    response_description="Basic Quest Phase Entity",
    response_model=BasicQuestPhase,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache()
async def get_quest_phase(
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the basic quest phase data from the given quest ID and phase number
    """
    async with get_db(region) as conn:
        return item_response(
            await basic.get_basic_quest_phase(conn, quest_id, phase, lang)
        )


@router.get(
    "/{region}/quest/{quest_id}",
    summary="Get Basic Quest data",
    response_description="Basic Quest Entity",
    response_model=BasicQuest,
    response_model_exclude_unset=True,
    responses=get_error_code([404, 500]),
)
@cache()
async def get_quest(
    region: Region,
    quest_id: int,
    lang: Language = Depends(language_parameter),
) -> Response:
    """
    Get the basic quest data from the given quest ID
    """
    async with get_db(region) as conn:
        return item_response(await basic.get_basic_quest(conn, quest_id, lang))
