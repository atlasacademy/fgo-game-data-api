from fastapi import APIRouter, Depends, Query, Response
from fastapi_cache.decorator import cache

from ..config import Settings
from ..core import raw, search
from ..db.helpers.cc import get_cc_id
from ..db.helpers.svt import get_ce_id, get_svt_id
from ..redis import Redis
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import AiType
from ..schemas.raw import (
    AiCollection,
    BattleMasterImageEntity,
    BattleMessageEntity,
    BattleMessageGroupEntity,
    BgmEntity,
    BuffEntity,
    ClassBoardEntity,
    CommandCodeEntity,
    EnemyMasterEntity,
    EventEntity,
    EventMissionEntity,
    FunctionEntity,
    GachaEntity,
    ItemEntity,
    MasterMissionEntity,
    MstEventAlloutBattle,
    MstSvtScript,
    MysticCodeEntity,
    QuestEntity,
    QuestPhaseEntity,
    ScriptEntity,
    ScriptSearchResult,
    ServantEntity,
    ShopEntity,
    SkillEntity,
    TdEntity,
    WarEntity,
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
from .deps import get_db, get_redis
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
@cache()
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        if not search_param.excludeCollectionNo:
            search_param.excludeCollectionNo = [0]
        matches = await search.search_servant(conn, search_param)
        return list_response(
            [
                await raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
                for mstSvt in matches
            ]
        )


get_servant_description = """
Get servant info from ID

If the given ID is a servant's collectionNo, the corresponding servant data is returned.
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
@cache()
async def get_servant(
    region: Region,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(region) as conn:
        servant_id = await get_svt_id(conn, servant_id)
        servant_entity = await raw.get_servant_entity(conn, servant_id, expand, lore)
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
@cache()
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_equip(conn, search_param)
        return list_response(
            [
                await raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
                for mstSvt in matches
            ]
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
@cache()
async def get_equip(
    region: Region,
    equip_id: int,
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(region) as conn:
        equip_id = await get_ce_id(conn, equip_id)
        servant_entity = await raw.get_servant_entity(conn, equip_id, expand, lore)
        return item_response(servant_entity)


@router.get(
    "/{region}/svt/search",
    summary="Find and get servant data",
    description=SvtSearchQueryParams.DESCRIPTION + svt_expand_lore_description,
    response_description="Raw Servant Entities",
    response_model=list[ServantEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_svt(
    search_param: SvtSearchQueryParams = Depends(SvtSearchQueryParams),
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_servant(conn, search_param)
        return list_response(
            [
                await raw.get_servant_entity(conn, mstSvt.id, expand, lore, mstSvt)
                for mstSvt in matches
            ]
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
@cache()
async def get_svt(
    region: Region,
    svt_id: int,
    expand: bool = False,
    lore: bool = False,
) -> Response:
    async with get_db(region) as conn:
        servant_entity = await raw.get_servant_entity(conn, svt_id, expand, lore)
        return item_response(servant_entity)


@router.get(
    "/{region}/svtScript",
    summary="Get servant script data",
    response_description="Servant Scipt Entity",
    response_model=list[MstSvtScript],
    response_model_exclude_unset=True,
)
@cache()
async def get_svt_scripts(region: Region, charaId: list[int] = Query([])) -> Response:
    async with get_db(region) as conn:
        servant_entity = await raw.get_svt_scripts(conn, charaId)
        return list_response(servant_entity)


@router.get(
    "/{region}/eventAlloutBattle",
    summary="Get servant script data",
    response_description="Servant Scipt Entity",
    response_model=list[MstEventAlloutBattle],
    response_model_exclude_unset=True,
)
@cache()
async def get_event_allout(region: Region, eventId: list[int] = Query([])) -> Response:
    async with get_db(region) as conn:
        allouts = await raw.get_event_allout(conn, eventId)
        return list_response(allouts)


@router.get(
    "/{region}/MC/{mc_id}",
    summary="Get Mystic Code data",
    response_description="Mystic Code entity",
    response_model=MysticCodeEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_mystic_code(
    region: Region,
    mc_id: int,
    expand: bool = False,
) -> Response:
    """
    Get Mystic Code info from ID

    - **expand**: Expand the skills and functions.
    """
    async with get_db(region) as conn:
        mc_entity = await raw.get_mystic_code_entity(conn, mc_id, expand)
        return item_response(mc_entity)


@router.get(
    "/{region}/CC/{cc_id}",
    summary="Get Command Code data",
    response_description="Command Code entity",
    response_model=CommandCodeEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_command_code(
    region: Region, cc_id: int, expand: bool = False
) -> Response:
    """
    Get Command Code info from ID

    - **expand**: Expand the skills and functions.
    """
    async with get_db(region) as conn:
        cc_id = await get_cc_id(conn, cc_id)
        cc_entity = await raw.get_command_code_entity(conn, cc_id, expand)
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
    response_description="Raw Skill Entities",
    response_model=list[SkillEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_skill(
    search_param: SkillSearchParams = Depends(SkillSearchParams),
    reverse: bool = False,
    expand: bool = False,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_skill(conn, search_param)
        return list_response(
            [
                await raw.get_skill_entity(
                    conn,
                    redis,
                    search_param.region,
                    mstSkill.id,
                    reverse,
                    expand=expand,
                )
                for mstSkill in matches
            ]
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
@cache()
async def get_skill(
    region: Region,
    skill_id: int,
    reverse: bool = False,
    expand: bool = False,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        skill_entity = await raw.get_skill_entity(
            conn, redis, region, skill_id, reverse, expand=expand
        )
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
    response_description="Raw NP Entities",
    response_model=list[TdEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_td(
    search_param: TdSearchParams = Depends(TdSearchParams),
    reverse: bool = False,
    expand: bool = False,
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_td(conn, search_param)
        return list_response(
            [
                await raw.get_td_entity(conn, td.id, reverse, expand=expand)
                for td in matches
            ]
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
@cache()
async def get_td(
    region: Region,
    np_id: int,
    reverse: bool = False,
    expand: bool = False,
) -> Response:
    async with get_db(region) as conn:
        td_entity = await raw.get_td_entity(conn, np_id, reverse, expand=expand)
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
@cache()
async def find_function(
    search_param: FuncSearchQueryParams = Depends(FuncSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_func(conn, search_param)
        return list_response(
            [
                await raw.get_func_entity(
                    conn,
                    redis,
                    search_param.region,
                    mstFunc.id,
                    reverse,
                    reverseDepth,
                    expand,
                    mstFunc,
                )
                for mstFunc in matches
            ]
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
@cache()
async def get_function(
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        func_entity = await raw.get_func_entity(
            conn, redis, region, func_id, reverse, reverseDepth, expand
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
@cache()
async def find_buff(
    search_param: BuffSearchQueryParams = Depends(BuffSearchQueryParams),
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_buff(conn, search_param)
        return list_response(
            [
                await raw.get_buff_entity(
                    conn,
                    redis,
                    search_param.region,
                    mstBuff.id,
                    reverse,
                    reverseDepth,
                    mstBuff,
                )
                for mstBuff in matches
            ]
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
@cache()
async def get_buff(
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    redis: Redis = Depends(get_redis),
) -> Response:
    async with get_db(region) as conn:
        buff_entity = await raw.get_buff_entity(
            conn, redis, region, buff_id, reverse, reverseDepth
        )
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
@cache()
async def find_item(
    search_param: ItemSearchQueryParams = Depends(ItemSearchQueryParams),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_item(conn, search_param)
        return list_response(ItemEntity(mstItem=mstItem) for mstItem in matches)


@router.get(
    "/{region}/item/{item_id}",
    summary="Get Item data",
    response_description="Item Entity",
    response_model=ItemEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_item(region: Region, item_id: int) -> Response:
    """
    Get the item data from the given ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_item_entity(conn, item_id))


@router.get(
    "/{region}/event-mission/{mission_id}",
    summary="Get Event Mission data",
    response_description="Event Mission Entity",
    response_model=EventMissionEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_event_mission(region: Region, mission_id: int) -> Response:
    """
    Get the event mission data from the given mission ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_event_mission_entity(conn, mission_id))


@router.get(
    "/{region}/mm/{master_mission_id}",
    summary="Get Master Mission data",
    response_description="Master Mission Entity",
    response_model=MasterMissionEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_mm(region: Region, master_mission_id: int) -> Response:
    """
    Get the master mission data from the given master mission ID
    """
    async with get_db(region) as conn:
        return item_response(
            await raw.get_master_mission_entity(conn, master_mission_id)
        )


@router.get(
    "/{region}/event/{event_id}",
    summary="Get Event data",
    response_description="Event Entity",
    response_model=EventEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_event(region: Region, event_id: int) -> Response:
    """
    Get the event data from the given event ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_event_entity(conn, event_id))


@router.get(
    "/{region}/war/{war_id}",
    summary="Get War data",
    response_description="War Entity",
    response_model=WarEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache(expire=settings.quest_cache_length)
async def get_war(region: Region, war_id: int) -> Response:
    """
    Get the war data from the given war ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_war_entity(conn, war_id))


@router.get(
    "/{region}/quest/{quest_id}/{phase}",
    summary="Get Quest Phase data",
    response_description="Quest Phase Entity",
    response_model=QuestPhaseEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache(expire=settings.quest_cache_length)
async def get_quest_phase(
    region: Region,
    quest_id: int,
    phase: int,
) -> Response:
    """
    Get the quest phase data from the given quest ID and phase number
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_quest_phase_entity(conn, quest_id, phase))


@router.get(
    "/{region}/quest/{quest_id}",
    summary="Get Quest data",
    response_description="Quest Entity",
    response_model=QuestEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache(expire=settings.quest_cache_length)
async def get_quest(
    region: Region,
    quest_id: int,
) -> Response:
    """
    Get the quest data from the given quest ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_quest_entity(conn, quest_id))


@router.get(
    "/{region}/script/search",
    summary="Find and get script data",
    description=ScriptSearchQueryParams.DESCRIPTION,
    response_description="Script Search Result",
    response_model=list[ScriptSearchResult],
    response_model_exclude_unset=True,
)
async def find_script(
    search_param: ScriptSearchQueryParams = Depends(ScriptSearchQueryParams),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_script(conn, search_param)
        return list_response(matches)


@router.get(
    "/{region}/script/{script_id}",
    summary="Get Script data",
    response_description="Script Entity",
    response_model=ScriptEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_script(region: Region, script_id: str) -> Response:
    """
    Get the script data from the given script ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_script_entity(conn, script_id))


@router.get(
    "/{region}/ai/{ai_type}/{ai_id}",
    summary="Get AI data",
    response_description="AI Entity",
    response_model=AiCollection,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_ai_field(region: Region, ai_type: AiType, ai_id: int) -> Response:
    """
    Get the AI data from the given AI ID
    """
    async with get_db(region) as conn:
        field_flag = ai_type == AiType.field
        ai_entity = await raw.get_ai_collection(conn, ai_id, field=field_flag)
        return item_response(ai_entity)


@router.get(
    "/{region}/bgm/{bgm_id}",
    summary="Get BGM data",
    response_description="BGM Entity",
    response_model=BgmEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_bgm(region: Region, bgm_id: int) -> Response:
    """
    Get the BGM data from the given BGM ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_bgm_entity(conn, bgm_id))


@router.get(
    "/{region}/shop/search",
    summary="Find and get shop data",
    description="Find and get shop data",
    response_description="Shop Entities",
    response_model=list[ShopEntity],
    response_model_exclude_unset=True,
    responses=get_error_code([400, 403]),
)
@cache()
async def find_shop(
    search_param: ShopSearchQueryParams = Depends(ShopSearchQueryParams),
) -> Response:
    async with get_db(search_param.region) as conn:
        matches = await search.search_shop(conn, search_param, limit=10000)
        return list_response(await raw.get_shop_entities(conn, matches))


@router.get(
    "/{region}/shop/{shop_id}",
    summary="Get Shop data",
    response_description="Shop Entity",
    response_model=ShopEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_shop(
    region: Region,
    shop_id: int,
) -> Response:
    """
    Get the shop data from the given shop ID
    """
    async with get_db(region) as conn:
        return item_response(await raw.get_shop_entity(conn, shop_id))


@router.get(
    "/{region}/enemy-master/{master_id}",
    summary="Get Enemy Master data",
    response_description="Enemy Master entity",
    response_model=EnemyMasterEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_enemy_master(
    region: Region,
    master_id: int,
) -> Response:
    """
    Get Enemy Master info from ID
    """
    async with get_db(region) as conn:
        enemy_master_entity = await raw.get_enemy_master_entity(conn, master_id)
        return item_response(enemy_master_entity)


@router.get(
    "/{region}/battle-master-image/{image_id}",
    summary="Get Battle Master Image data",
    response_description="Battle Master Image entity",
    response_model=BattleMasterImageEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_battle_master_image(
    region: Region,
    image_id: int,
) -> Response:
    """
    Get Battle Master Image info from ID
    """
    async with get_db(region) as conn:
        battle_master_image_entity = await raw.get_battle_master_image_entity(
            conn, image_id
        )
        return item_response(battle_master_image_entity)


@router.get(
    "/{region}/battle-message/{message_id}",
    summary="Get Battle Message data",
    response_description="Battle Message entity",
    response_model=BattleMessageEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_battle_message(
    region: Region,
    message_id: int,
) -> Response:
    """
    Get Battle Message info from ID
    """
    async with get_db(region) as conn:
        battle_message_entity = await raw.get_battle_message_entity(conn, message_id)
        return item_response(battle_message_entity)


@router.get(
    "/{region}/battle-message-group/{group_id}",
    summary="Get Battle Message Group data",
    response_description="Battle Message Group entity",
    response_model=BattleMessageGroupEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_battle_message_group(
    region: Region,
    group_id: int,
) -> Response:
    """
    Get Battle Message Group info from ID
    """
    async with get_db(region) as conn:
        battle_message_group_entity = await raw.get_battle_message_group_entity(
            conn, group_id
        )
        return item_response(battle_message_group_entity)


@router.get(
    "/{region}/class-board/{class_board_id}",
    summary="Get Class Board data",
    response_description="Class Board entity",
    response_model=ClassBoardEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_class_board(
    region: Region,
    class_board_id: int,
) -> Response:
    """
    Get Class Board info from ID
    """
    async with get_db(region) as conn:
        class_board_entity = await raw.get_class_board_entity(conn, class_board_id)
        return item_response(class_board_entity)


@router.get(
    "/{region}/gacha/{gacha_id}",
    summary="Get Banner data",
    response_description="Gacha entity",
    response_model=GachaEntity,
    response_model_exclude_unset=True,
    responses=get_error_code([404]),
)
@cache()
async def get_gacha(
    region: Region,
    gacha_id: int,
) -> Response:
    """
    Get Gacha info from ID
    """
    async with get_db(region) as conn:
        gacha_entity = await raw.get_gacha_entity(conn, gacha_id)
        return item_response(gacha_entity)
