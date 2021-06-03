from fastapi import APIRouter, Depends, Response
from sqlalchemy.engine import Connection

from ..config import Settings
from ..core import raw, search
from ..data.gamedata import masters
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import AiType
from ..schemas.raw import (
    AiCollection,
    BuffEntity,
    CommandCodeEntity,
    EventEntity,
    FunctionEntity,
    ItemEntity,
    MysticCodeEntity,
    QuestEntity,
    QuestPhaseEntity,
    ServantEntity,
    SkillEntity,
    TdEntity,
    WarEntity,
)
from ..schemas.search import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ItemSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
)
from .deps import get_db
from .utils import get_error_code, item_response, list_response


settings = Settings()
router = APIRouter(prefix="/raw", tags=["raw"])


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
    response_model=list[ServantEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_servant(conn, search_param)
    return list_response(
        raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
        for mstSvt in matches
    )


get_servant_description = """
Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field. As a result, it can return not servant data.
"""


@router.get(
    "/{region}/servant/{servant_id}",
    summary="Get servant data",
    description=get_servant_description + svt_expand_lore_description,
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_servant(
    region: Region,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    servant_id = masters[region].mstSvtServantCollectionNo.get(servant_id, servant_id)
    servant_entity = raw.get_servant_entity(conn, servant_id, expand, lore)
    return item_response(servant_entity)


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION + svt_expand_lore_description,
    response_description="CE entity",
    response_model=list[ServantEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_equip(conn, search_param)
    return list_response(
        raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
        for mstSvt in matches
    )


get_ce_description = """
Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field. As a result, it can return not CE data.
"""


@router.get(
    "/{region}/equip/{equip_id}",
    summary="Get CE data",
    description=get_ce_description + svt_expand_lore_description,
    response_description="CE entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_equip(
    region: Region,
    equip_id: int,
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    equip_id = masters[region].mstSvtEquipCollectionNo.get(equip_id, equip_id)
    servant_entity = raw.get_servant_entity(conn, equip_id, expand, lore)
    return item_response(servant_entity)


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + svt_expand_lore_description,
    response_description="Nice Servant Entities",
    response_model=list[ServantEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_servant(conn, search_param)
    return list_response(
        raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
        for mstSvt in matches
    )


get_svt_description = """
Get servant info from ID

Only uses actual ID for the lookup.
"""


@router.get(
    "/{region}/svt/{svt_id}",
    summary="Get servant data",
    description=get_svt_description + svt_expand_lore_description,
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_svt(
    svt_id: int,
    expand: bool = False,
    lore: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    servant_entity = raw.get_servant_entity(conn, svt_id, expand, lore)
    return item_response(servant_entity)


@router.get(
    "/{region}/MC/{mc_id}",
    summary="Get Mystic Code data",
    response_description="Mystic Code entity",
    response_model=MysticCodeEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_mystic_code(
    mc_id: int,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    """
    Get Mystic Code info from ID

    - **expand**: Expand the skills and functions.
    """
    mc_entity = raw.get_mystic_code_entity(conn, mc_id, expand)
    return item_response(mc_entity)


@router.get(
    "/{region}/CC/{cc_id}",
    summary="Get Command Code data",
    response_description="Command Code entity",
    response_model=CommandCodeEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_command_code(
    region: Region,
    cc_id: int,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    """
    Get Command Code info from ID

    - **expand**: Expand the skills and functions.
    """
    cc_id = masters[region].mstCCCollectionNo.get(cc_id, cc_id)
    cc_entity = raw.get_command_code_entity(conn, cc_id, expand)
    return item_response(cc_entity)


raw_skill_extra = """
- **reverse**: Reverse lookup the servants that have this skill
and return the reverse skill objects.
- **expand**: Add expanded function objects to mstSkillLv.expandedFuncId
from the function IDs in mstSkillLv.funcId.
"""


@router.get(
    "/{region}/skill/search",
    summary="Find and get skill data",
    description=SkillSearchParams.DESCRIPTION + raw_skill_extra,
    response_description="Basic Skill Entities",
    response_model=list[SkillEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    reverse: bool = False,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_skill(conn, search_param)
    return list_response(
        raw.get_skill_entity(
            conn, search_param.region, mstSkill.id, reverse, expand=expand
        )
        for mstSkill in matches
    )


@router.get(
    "/{region}/skill/{skill_id}",
    summary="Get skill data",
    description="Get the skill data from the given ID" + raw_skill_extra,
    response_description="Skill entity",
    response_model=SkillEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_skill(
    region: Region,
    skill_id: int,
    reverse: bool = False,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    skill_entity = raw.get_skill_entity(conn, region, skill_id, reverse, expand=expand)
    return item_response(skill_entity)


raw_td_extra = """
- **reverse**: Reverse lookup the servants that have this NP
and return the reversed servant objects.
- **expand**: Add expanded function objects to mstTreasureDeviceLv.expandedFuncId
from the function IDs in mstTreasureDeviceLv.funcId.
"""


@router.get(
    "/{region}/NP/search",
    summary="Find and get NP data",
    description=TdSearchParams.DESCRIPTION + raw_td_extra,
    response_description="Nice NP Entities",
    response_model=list[TdEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    reverse: bool = False,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_td(conn, search_param)
    return list_response(
        raw.get_td_entity(conn, td.id, reverse, expand=expand) for td in matches
    )


@router.get(
    "/{region}/NP/{np_id}",
    summary="Get NP data",
    description="Get the NP data from the given ID" + raw_td_extra,
    response_description="NP entity",
    response_model=TdEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_td(
    np_id: int,
    reverse: bool = False,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    td_entity = raw.get_td_entity(conn, np_id, reverse, expand=expand)
    return item_response(td_entity)


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
    response_model=list[FunctionEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_func(conn, search_param)
    return list_response(
        raw.get_func_entity(
            conn,
            search_param.region,
            func_entity.mstFunc.id,
            reverse,
            reverseDepth,
            expand,
            func_entity,
        )
        for func_entity in matches
    )


@router.get(
    "/{region}/function/{func_id}",
    summary="Get function data",
    description="Get the function data from the given ID"
    + function_reverse_expand_description,
    response_description="Function entity",
    response_model=FunctionEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_function(
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    conn: Connection = Depends(get_db),
) -> Response:
    func_entity = raw.get_func_entity(
        conn, region, func_id, reverse, reverseDepth, expand
    )
    return item_response(func_entity)


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
    response_model=list[BuffEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_buff(conn, search_param)
    return list_response(
        raw.get_buff_entity(
            conn, search_param.region, mstBuff.id, reverse, reverseDepth, mstBuff
        )
        for mstBuff in matches
    )


@router.get(
    "/{region}/buff/{buff_id}",
    summary="Get buff data",
    description="Get the buff data from the given ID" + buff_reverse_description,
    response_description="Buff entity",
    response_model=BuffEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_buff(
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    conn: Connection = Depends(get_db),
) -> Response:
    buff_entity = raw.get_buff_entity(conn, region, buff_id, reverse, reverseDepth)
    return item_response(buff_entity)


@router.get(
    "/{region}/item/search",
    summary="Find and get item data",
    description=ItemSearchQueryParams.DESCRIPTION,
    response_description="Item entity",
    response_model=list[ItemEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
async def find_item(
    search_param: ItemSearchQueryParams = Depends(ItemSearchQueryParams),
    conn: Connection = Depends(get_db),
) -> Response:
    matches = search.search_item(conn, search_param)
    return list_response(ItemEntity(mstItem=mstItem) for mstItem in matches)


@router.get(
    "/{region}/item/{item_id}",
    summary="Get Item data",
    response_description="Item Entity",
    response_model=ItemEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_item(item_id: int, conn: Connection = Depends(get_db)) -> Response:
    """
    Get the item data from the given ID
    """
    return item_response(raw.get_item_entity(conn, item_id))


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Event Entity",
    response_model=EventEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_event(event_id: int, conn: Connection = Depends(get_db)) -> Response:
    """
    Get the event data from the given event ID
    """
    return item_response(raw.get_event_entity(conn, event_id))


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="War Entity",
    response_model=WarEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_war(war_id: int, conn: Connection = Depends(get_db)) -> Response:
    """
    Get the war data from the given war ID
    """
    war_response = item_response(raw.get_war_entity(conn, war_id))
    war_response.headers["Bloom-Response-TTL"] = str(settings.quest_cache_length)
    return war_response


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Quest Phase data",
    response_description="Quest Phase Entity",
    response_model=QuestPhaseEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_quest_phase(
    quest_id: int,
    phase: int,
    conn: Connection = Depends(get_db),
) -> Response:
    """
    Get the quest phase data from the given quest ID and phase number
    """
    quest_response = item_response(raw.get_quest_phase_entity(conn, quest_id, phase))
    quest_response.headers["Bloom-Response-TTL"] = str(settings.quest_cache_length)
    return quest_response


@router.get(
    "/{region}/quest/{quest_id}",
    summary="Get Quest data",
    response_description="Quest Entity",
    response_model=QuestEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_quest(
    quest_id: int,
    conn: Connection = Depends(get_db),
) -> Response:
    """
    Get the quest data from the given quest ID
    """
    quest_response = item_response(raw.get_quest_entity(conn, quest_id))
    quest_response.headers["Bloom-Response-TTL"] = str(settings.quest_cache_length)
    return quest_response


@router.get(
    "/{region}/ai/{ai_type}/{ai_id}",
    summary="Get AI data",
    response_description="AI Entity",
    response_model=AiCollection,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
async def get_ai_field(
    ai_type: AiType, ai_id: int, conn: Connection = Depends(get_db)
) -> Response:
    """
    Get the AI data from the given AI ID
    """
    field_flag = ai_type == AiType.field
    ai_entity = raw.get_ai_collection(conn, ai_id, field=field_flag)
    return item_response(ai_entity)
