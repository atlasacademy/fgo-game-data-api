from typing import Iterable, Optional

import orjson
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from ..data.custom_mappings import EXTRA_CHARAFIGURES
from ..data.shop import get_shop_cost_item_id
from ..db.helpers import ai, event, fetch, item, quest, script, skill, svt, td, war
from ..redis import Redis
from ..redis.helpers.reverse import RedisReverse, get_reverse_ids
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import FUNC_VALS_NOT_BUFF, DetailMissionCondType
from ..schemas.gameenums import (
    BgmFlag,
    ClassBoardSkillType,
    CondType,
    PayType,
    PurchaseType,
    VoiceCondType,
)
from ..schemas.nice import COSTUME_LIMIT_NO_LESS_THAN
from ..schemas.raw import (
    EXTRA_ATTACK_TD_ID,
    AiCollection,
    AiEntity,
    BgmEntity,
    BuffEntity,
    BuffEntityNoReverse,
    ClassBoardEntity,
    CommandCodeEntity,
    EnemyMasterEntity,
    EventEntity,
    EventMissionEntity,
    FunctionEntity,
    FunctionEntityNoReverse,
    ItemEntity,
    MasterMissionEntity,
    MstBgm,
    MstBgmRelease,
    MstBlankEarthSpot,
    MstBoxGacha,
    MstBoxGachaTalk,
    MstBuff,
    MstClassBoardBase,
    MstClassBoardClass,
    MstClassBoardCommandSpell,
    MstClassBoardLine,
    MstClassBoardLock,
    MstClassBoardSquare,
    MstClosedMessage,
    MstCombineAppendPassiveSkill,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineMaterial,
    MstCombineSkill,
    MstCommandCode,
    MstCommandCodeComment,
    MstCommandCodeSkill,
    MstCommonConsume,
    MstCommonRelease,
    MstCv,
    MstEnemyMaster,
    MstEnemyMasterBattle,
    MstEquip,
    MstEquipAdd,
    MstEquipExp,
    MstEquipSkill,
    MstEvent,
    MstEventAdd,
    MstEventAlloutBattle,
    MstEventBulletinBoard,
    MstEventBulletinBoardRelease,
    MstEventCampaign,
    MstEventCommandAssist,
    MstEventCooltimeReward,
    MstEventDigging,
    MstEventDiggingBlock,
    MstEventDiggingReward,
    MstEventFortification,
    MstEventFortificationDetail,
    MstEventFortificationSvt,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventMissionGroup,
    MstEventMural,
    MstEventPointActivity,
    MstEventPointBuff,
    MstEventPointGroup,
    MstEventQuest,
    MstEventQuestCooltime,
    MstEventRandomMission,
    MstEventRecipe,
    MstEventRecipeGift,
    MstEventReward,
    MstEventRewardScene,
    MstEventRewardSet,
    MstEventTower,
    MstEventVoicePlay,
    MstFriendship,
    MstFunc,
    MstFuncGroup,
    MstGift,
    MstGiftAdd,
    MstHeelPortrait,
    MstIllustrator,
    MstItem,
    MstMap,
    MstMapGimmick,
    MstMasterMission,
    MstShop,
    MstShopRelease,
    MstShopScript,
    MstSpot,
    MstSpotAdd,
    MstSpotRoad,
    MstSvt,
    MstSvtAdd,
    MstSvtAppendPassiveSkill,
    MstSvtAppendPassiveSkillUnlock,
    MstSvtCard,
    MstSvtCardAdd,
    MstSvtChange,
    MstSvtCoin,
    MstSvtComment,
    MstSvtCommentAdd,
    MstSvtCostume,
    MstSvtExp,
    MstSvtExtra,
    MstSvtGroup,
    MstSvtIndividuality,
    MstSvtLimit,
    MstSvtLimitAdd,
    MstSvtLimitImage,
    MstSvtMultiPortrait,
    MstSvtPassiveSkill,
    MstSvtScript,
    MstSvtVoice,
    MstSvtVoiceRelation,
    MstTreasureBox,
    MstTreasureBoxGift,
    MstVoice,
    MstWar,
    MstWarAdd,
    MstWarQuestSelection,
    MysticCodeEntity,
    QuestEntity,
    QuestPhaseEntity,
    ReversedBuff,
    ReversedBuffType,
    ReversedFunction,
    ReversedFunctionType,
    ReversedSkillTd,
    ReversedSkillTdType,
    ScriptEntity,
    ServantEntity,
    ShopEntity,
    SkillEntity,
    SkillEntityNoReverse,
    TdEntity,
    TdEntityNoReverse,
    WarEntity,
)


async def get_buff_entity_no_reverse(
    conn: AsyncConnection, buff_id: int, mstBuff: Optional[MstBuff] = None
) -> BuffEntityNoReverse:
    if not mstBuff:
        mstBuff = await fetch.get_one(conn, MstBuff, buff_id)
    if not mstBuff:
        raise HTTPException(status_code=404, detail="Buff not found")
    return BuffEntityNoReverse(mstBuff=mstBuff)


async def get_buff_entity(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    mstBuff: Optional[MstBuff] = None,
) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(
        await get_buff_entity_no_reverse(conn, buff_id, mstBuff)
    )
    if reverse and reverseDepth >= ReverseDepth.function:
        func_ids = await get_reverse_ids(
            redis, region, RedisReverse.BUFF_TO_FUNC, buff_id
        )
        buff_reverse = ReversedBuff(
            function=[
                await get_func_entity(
                    conn, redis, region, func_id, reverse, reverseDepth
                )
                for func_id in func_ids
            ]
        )
        buff_entity.reverse = ReversedBuffType(raw=buff_reverse)
    return buff_entity


async def get_func_entity_no_reverse(
    conn: AsyncConnection,
    func_id: int,
    expand: bool = False,
    mstFunc: Optional[MstFunc] = None,
) -> FunctionEntityNoReverse:
    if not mstFunc:
        mstFunc = await fetch.get_one(conn, MstFunc, func_id)
    if not mstFunc:
        raise HTTPException(status_code=404, detail="Function not found")
    func_entity = FunctionEntityNoReverse(
        mstFunc=mstFunc,
        mstFuncGroup=await fetch.get_all(conn, MstFuncGroup, func_id),
    )
    if expand and func_entity.mstFunc.funcType not in FUNC_VALS_NOT_BUFF:
        func_entity.mstFunc.expandedVals = []
        for buff_id in func_entity.mstFunc.vals:
            mstBuff = await fetch.get_one(conn, MstBuff, buff_id)
            if mstBuff:
                func_entity.mstFunc.expandedVals.append(
                    await get_buff_entity_no_reverse(conn, buff_id, mstBuff)
                )
    return func_entity


async def get_func_entity(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    mstFunc: Optional[MstFunc] = None,
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        await get_func_entity_no_reverse(conn, func_id, expand, mstFunc)
    )
    if reverse and reverseDepth >= ReverseDepth.skillNp:
        skill_ids = await get_reverse_ids(
            redis, region, RedisReverse.FUNC_TO_SKILL, func_id
        )
        td_ids = await get_reverse_ids(redis, region, RedisReverse.FUNC_TO_TD, func_id)
        func_reverse = ReversedFunction(
            skill=[
                await get_skill_entity(
                    conn, redis, region, skill_id, reverse, reverseDepth
                )
                for skill_id in skill_ids
            ],
            NP=[
                await get_td_entity(conn, td_id, reverse, reverseDepth)
                for td_id in td_ids
            ],
        )
        func_entity.reverse = ReversedFunctionType(raw=func_reverse)
    return func_entity


async def get_skill_entity_no_reverse_many(
    conn: AsyncConnection, skill_ids: Iterable[int], expand: bool = False
) -> list[SkillEntityNoReverse]:
    if not skill_ids:
        return []
    skill_entities = await skill.get_skillEntity(conn, skill_ids)
    if skill_entities:
        if not expand:
            for skill_entity in skill_entities:
                for skillLv in skill_entity.mstSkillLv:
                    skillLv.expandedFuncId = None
        return skill_entities
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


async def get_skill_entity_no_reverse(
    conn: AsyncConnection, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    return (await get_skill_entity_no_reverse_many(conn, [skill_id], expand))[0]


async def get_skill_entity(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    skill_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        await get_skill_entity_no_reverse(conn, skill_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = set(
            await get_reverse_ids(
                redis, region, RedisReverse.ACTIVE_SKILL_TO_SVT, skill_id
            )
        )
        passiveSkills = set(
            await get_reverse_ids(
                redis, region, RedisReverse.PASSIVE_SKILL_TO_SVT, skill_id
            )
        )

        mc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_MC, skill_id
        )
        cc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_CC, skill_id
        )

        skill_reverse = ReversedSkillTd(
            servant=[
                await get_servant_entity(conn, svt_id)
                for svt_id in sorted(activeSkills | passiveSkills)
            ],
            MC=[await get_mystic_code_entity(conn, mc_id) for mc_id in mc_ids],
            CC=[await get_command_code_entity(conn, cc_id) for cc_id in cc_ids],
        )
        skill_entity.reverse = ReversedSkillTdType(raw=skill_reverse)
    return skill_entity


async def get_td_entity_no_reverse_many(
    conn: AsyncConnection, td_ids: Iterable[int], expand: bool = False
) -> list[TdEntityNoReverse]:
    if not td_ids:
        return []
    td_entities = await td.get_tdEntity(conn, td_ids)
    if td_entities:
        if not expand:
            for td_entity in td_entities:
                for tdLv in td_entity.mstTreasureDeviceLv:
                    tdLv.expandedFuncId = None
        return td_entities
    else:
        raise HTTPException(status_code=404, detail="NP not found")


async def get_td_entity_no_reverse(
    conn: AsyncConnection, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    return (await get_td_entity_no_reverse_many(conn, [td_id], expand))[0]


async def get_td_entity(
    conn: AsyncConnection,
    td_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> TdEntity:
    td_entity = TdEntity.parse_obj(await get_td_entity_no_reverse(conn, td_id, expand))

    if reverse and reverseDepth >= ReverseDepth.servant:
        td_reverse = ReversedSkillTd(
            servant=[
                await get_servant_entity(conn, svt_id.svtId)
                for svt_id in td_entity.mstSvtTreasureDevice
            ]
        )
        td_entity.reverse = ReversedSkillTdType(raw=td_reverse)
    return td_entity


async def get_svt_scripts(
    conn: AsyncConnection, ids: Iterable[int]
) -> list[MstSvtScript]:
    if not ids:
        return []

    return await fetch.get_all_multiple(conn, MstSvtScript, ids)


async def get_event_allout(
    conn: AsyncConnection, event_ids: Iterable[int]
) -> list[MstEventAlloutBattle]:
    if not event_ids:
        return []

    return await fetch.get_all_multiple(conn, MstEventAlloutBattle, event_ids)


async def get_voice_from_svtVoice(
    conn: AsyncConnection, mstSvtVoices: list[MstSvtVoice]
) -> list[MstVoice]:
    base_voice_ids = {
        info.get_voice_id()
        for svt_voice in mstSvtVoices
        for script_json in svt_voice.scriptJson
        for info in script_json.infos
    }
    return await fetch.get_all_multiple(conn, MstVoice, base_voice_ids)


async def get_voice_group_from_svtVoice(
    conn: AsyncConnection, mstSvtVoices: list[MstSvtVoice]
) -> list[MstSvtGroup]:
    group_ids = {
        cond.value
        for svt_voice in mstSvtVoices
        for script_json in svt_voice.scriptJson
        for cond in (script_json.conds if script_json.conds is not None else [])
        if cond.condType == VoiceCondType.SVT_GROUP
    }
    return await fetch.get_all_multiple(conn, MstSvtGroup, group_ids)


async def get_servant_entity(
    conn: AsyncConnection,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
) -> ServantEntity:
    svt_db = mstSvt if mstSvt else await fetch.get_one(conn, MstSvt, servant_id)
    if not svt_db:
        raise HTTPException(status_code=404, detail="Svt not found")

    mstSvtIndividuality = await fetch.get_all(conn, MstSvtIndividuality, servant_id)
    mstSvtCard = await fetch.get_all(conn, MstSvtCard, servant_id)
    mstSvtCardAdd = await fetch.get_all(conn, MstSvtCardAdd, servant_id)
    mstSvtLimit = await fetch.get_all(conn, MstSvtLimit, servant_id)
    mstCombineSkill = await fetch.get_all(conn, MstCombineSkill, svt_db.combineSkillId)
    mstCombineLimit = await fetch.get_all(conn, MstCombineLimit, svt_db.combineLimitId)
    mstCombineCostume = await fetch.get_all(conn, MstCombineCostume, servant_id)
    mstSvtLimitAdd = await fetch.get_all(conn, MstSvtLimitAdd, servant_id)
    mstSvtLimitImage = await fetch.get_all(conn, MstSvtLimitImage, servant_id)
    mstSvtChange = await fetch.get_all(conn, MstSvtChange, servant_id)
    mstSvtCostume = await fetch.get_all(conn, MstSvtCostume, servant_id)
    mstSvtExp = await fetch.get_all(conn, MstSvtExp, svt_db.expType)
    mstFriendship = await fetch.get_all(conn, MstFriendship, svt_db.friendshipId)
    mstCombineMaterial = await fetch.get_all(
        conn, MstCombineMaterial, svt_db.combineMaterialId
    )
    mstSvtPassiveSkill = await fetch.get_all(conn, MstSvtPassiveSkill, servant_id)
    mstSvtExtra = await fetch.get_one(conn, MstSvtExtra, servant_id)
    mstSvtAppendPassiveSkill = await fetch.get_all(
        conn, MstSvtAppendPassiveSkill, servant_id
    )
    mstSvtAppendPassiveSkillUnlock = await fetch.get_all(
        conn, MstSvtAppendPassiveSkillUnlock, servant_id
    )
    mstCombineAppendPassiveSkill = await fetch.get_all(
        conn, MstCombineAppendPassiveSkill, servant_id
    )
    mstSvtCoin = await fetch.get_one(conn, MstSvtCoin, servant_id)
    mstSvtAdd = await fetch.get_one(conn, MstSvtAdd, servant_id)
    mstSvtMultiPortrait = await fetch.get_all(conn, MstSvtMultiPortrait, servant_id)

    costume_chara_ids = [limit.battleCharaId for limit in mstSvtLimitAdd]
    mstSvtScript = await svt.get_svt_script(
        conn, [servant_id, *costume_chara_ids, *EXTRA_CHARAFIGURES.get(servant_id, [])]
    )

    skill_ids = [
        skill.skillId for skill in await skill.get_mstSvtSkill(conn, svt_id=servant_id)
    ]
    mstSkill = await get_skill_entity_no_reverse_many(conn, skill_ids, expand)

    td_ids = [
        td.treasureDeviceId
        for td in await td.get_mstSvtTreasureDevice(conn, svt_id=servant_id)
        if td.treasureDeviceId != EXTRA_ATTACK_TD_ID
    ]
    mstTreasureDevice = await get_td_entity_no_reverse_many(conn, td_ids, expand)

    item_ids: set[int] = set()
    for combine in (
        mstCombineLimit
        + mstCombineSkill
        + mstCombineAppendPassiveSkill
        + mstCombineCostume
        + mstSvtAppendPassiveSkillUnlock
    ):
        item_ids.update(combine.itemIds)
    if mstSvtCoin is not None:
        item_ids.add(mstSvtCoin.itemId)

    mstItem = await get_multiple_items(conn, item_ids)

    common_release_ids: set[int] = set()
    for limit in mstSvtLimit:
        try:
            strParam = orjson.loads(limit.strParam)
            for field_name in (
                "changeGraphCommonReleaseId",
                "changeIconCommonReleaseId",
            ):
                if field_name in strParam:
                    common_release_ids.add(strParam[field_name])
        except orjson.JSONDecodeError:  # pragma: no cover
            pass

    mstCommonRelease = await fetch.get_all_multiple(
        conn, MstCommonRelease, common_release_ids
    )

    svt_entity = ServantEntity(
        mstSvt=svt_db,
        mstSvtIndividuality=mstSvtIndividuality,
        mstSvtCard=mstSvtCard,
        mstSvtCardAdd=mstSvtCardAdd,
        mstSvtLimit=mstSvtLimit,
        mstCombineSkill=mstCombineSkill,
        mstCombineLimit=mstCombineLimit,
        mstCombineCostume=mstCombineCostume,
        mstCombineMaterial=mstCombineMaterial,
        mstSvtLimitAdd=mstSvtLimitAdd,
        mstSvtLimitImage=mstSvtLimitImage,
        mstSvtChange=mstSvtChange,
        mstSvtPassiveSkill=mstSvtPassiveSkill,
        mstSvtAppendPassiveSkill=mstSvtAppendPassiveSkill,
        mstSvtAppendPassiveSkillUnlock=mstSvtAppendPassiveSkillUnlock,
        mstCombineAppendPassiveSkill=mstCombineAppendPassiveSkill,
        mstSvtCoin=mstSvtCoin,
        mstSvtAdd=mstSvtAdd,
        # needed costume to get the nice limits and costume ids
        mstSvtCostume=mstSvtCostume,
        # needed this to get CharaFigure available forms
        mstSvtScript=mstSvtScript,
        mstSvtExp=mstSvtExp,
        mstFriendship=mstFriendship,
        mstSkill=mstSkill,
        mstTreasureDevice=mstTreasureDevice,
        mstSvtExtra=mstSvtExtra,
        mstItem=mstItem,
        mstSvtMultiPortrait=mstSvtMultiPortrait,
        mstCommonRelease=mstCommonRelease,
    )

    if expand:
        extra_passive_ids = {skill.skillId for skill in mstSvtPassiveSkill}
        append_passive_ids = {skill.skillId for skill in mstSvtAppendPassiveSkill}
        expand_skill_ids = (
            set(svt_entity.mstSvt.classPassive) | extra_passive_ids | append_passive_ids
        )
        expand_skills = {
            skill.mstSkill.id: skill
            for skill in await get_skill_entity_no_reverse_many(
                conn, expand_skill_ids, expand
            )
        }
        svt_entity.mstSvt.expandedClassPassive = [
            expand_skills[skill_id]
            for skill_id in svt_entity.mstSvt.classPassive
            if skill_id in expand_skills
        ]
        svt_entity.expandedExtraPassive = [
            expand_skills[skill.skillId]
            for skill in mstSvtPassiveSkill
            if skill.skillId in expand_skills
        ]
        svt_entity.expandedAppendPassive = [
            expand_skills[skill.skillId]
            for skill in mstSvtAppendPassiveSkill
            if skill.skillId in expand_skills
        ]

    if lore:
        svt_entity.mstCv = await fetch.get_one(conn, MstCv, svt_db.cvId)
        svt_entity.mstIllustrator = await fetch.get_one(
            conn, MstIllustrator, svt_db.illustratorId
        )
        svt_entity.mstSvtComment = await fetch.get_all(conn, MstSvtComment, servant_id)
        svt_entity.mstSvtCommentAdd = await fetch.get_all(
            conn, MstSvtCommentAdd, servant_id
        )

        # Try to match order in the voice tab in game
        voice_ids = []

        for change in svt_entity.mstSvtChange:
            voice_ids.append(change.svtVoiceId)

        voice_ids.append(servant_id)

        for main_id, sub_id in (
            (600700, 600710),  # Jekyll/Hyde
            (800100, 800101),  # Mash
        ):
            if servant_id == main_id:
                voice_ids.append(sub_id)

        # Moriarty deadheat summer lines use his hidden name svt_id
        relation_svt_ids = [change.svtVoiceId for change in svt_entity.mstSvtChange] + [
            servant_id
        ]
        voiceRelations = await fetch.get_all_multiple(
            conn, MstSvtVoiceRelation, relation_svt_ids
        )
        for voiceRelation in voiceRelations:
            voice_ids.append(voiceRelation.relationSvtId)

        order = {voice_id: i for i, voice_id in enumerate(voice_ids)}
        mstSvtVoice = await svt.get_mstSvtVoice(conn, voice_ids)
        mstSubtitle = await svt.get_mstSubtitle(conn, voice_ids)
        mstVoicePlayCond = await svt.get_mstVoicePlayCond(conn, voice_ids)

        svt_entity.mstVoice = await get_voice_from_svtVoice(conn, mstSvtVoice)

        svt_entity.mstSvtGroup = await get_voice_group_from_svtVoice(conn, mstSvtVoice)

        svt_entity.mstSvtVoice = sorted(mstSvtVoice, key=lambda voice: order[voice.id])
        svt_entity.mstVoicePlayCond = sorted(
            mstVoicePlayCond, key=lambda voice: order[voice.svtId]
        )
        svt_entity.mstSubtitle = sorted(
            mstSubtitle, key=lambda sub: order[sub.get_svtId()]
        )

    return svt_entity


async def get_mystic_code_entity(
    conn: AsyncConnection,
    mc_id: int,
    expand: bool = False,
    mstEquip: Optional[MstEquip] = None,
) -> MysticCodeEntity:
    mc_db = mstEquip if mstEquip else await fetch.get_one(conn, MstEquip, mc_id)
    if not mc_db:
        raise HTTPException(status_code=404, detail="Mystic Code not found")

    skill_ids = [mc.skillId for mc in await fetch.get_all(conn, MstEquipSkill, mc_id)]
    mstSkill = await get_skill_entity_no_reverse_many(conn, skill_ids, expand)

    mstEquipAdd = await fetch.get_all(conn, MstEquipAdd, mc_id)
    if mstEquipAdd:
        common_release_ids = [equipAdd.commonReleaseId for equipAdd in mstEquipAdd]
        mstCommonRelease = await fetch.get_all_multiple(
            conn, MstCommonRelease, common_release_ids
        )
    else:
        mstCommonRelease = []

    mc_entity = MysticCodeEntity(
        mstEquip=mc_db,
        mstSkill=mstSkill,
        mstEquipExp=await fetch.get_all(conn, MstEquipExp, mc_id),
        mstEquipAdd=mstEquipAdd,
        mstCommonRelease=mstCommonRelease,
    )
    return mc_entity


async def get_enemy_master_entity(
    conn: AsyncConnection,
    master_id: int,
    mstEnemyMaster: Optional[MstEnemyMaster] = None,
) -> EnemyMasterEntity:
    master_db = (
        mstEnemyMaster
        if mstEnemyMaster
        else await fetch.get_one(conn, MstEnemyMaster, master_id)
    )
    if not master_db:
        raise HTTPException(status_code=404, detail="Enemy Master not found")
    mstEnemyMasterBattle = await fetch.get_all(conn, MstEnemyMasterBattle, master_id)
    return EnemyMasterEntity(
        mstEnemyMaster=master_db, mstEnemyMasterBattle=mstEnemyMasterBattle
    )


async def get_command_code_entity(
    conn: AsyncConnection,
    cc_id: int,
    expand: bool = False,
    mstCc: Optional[MstCommandCode] = None,
) -> CommandCodeEntity:
    cc_db = mstCc if mstCc else await fetch.get_one(conn, MstCommandCode, cc_id)
    if not cc_db:
        raise HTTPException(status_code=404, detail="Command Code not found")

    skill_ids = [
        cc_skill.skillId
        for cc_skill in await fetch.get_all(conn, MstCommandCodeSkill, cc_id)
    ]
    mstSkill = await get_skill_entity_no_reverse_many(conn, skill_ids, expand)

    mstCommandCodeComments = await fetch.get_all(conn, MstCommandCodeComment, cc_id)
    mstCommandCodeComment = (
        mstCommandCodeComments[0] if mstCommandCodeComments else None
    )
    if mstCommandCodeComment:
        mstIllustrator = await fetch.get_one(
            conn, MstIllustrator, mstCommandCodeComment.illustratorId
        )
    else:
        mstIllustrator = None

    return CommandCodeEntity(
        mstCommandCode=cc_db,
        mstSkill=mstSkill,
        mstCommandCodeComment=mstCommandCodeComment,
        mstIllustrator=mstIllustrator,
    )


async def get_multiple_items(
    conn: AsyncConnection, item_ids: Iterable[int]
) -> list[MstItem]:
    items = await fetch.get_all_multiple(conn, MstItem, item_ids)
    item_map = {item.id: item for item in items}
    out_list: list[MstItem] = []
    for item_id in item_ids:
        if item_id in item_map:
            out_list.append(item_map[item_id])
    return out_list


async def get_item_entity(conn: AsyncConnection, item_id: int) -> ItemEntity:
    mstItem = await fetch.get_one(conn, MstItem, item_id)
    if not mstItem:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemEntity(mstItem=mstItem)


async def get_war_entity(conn: AsyncConnection, war_id: int) -> WarEntity:
    war_db = await fetch.get_one(conn, MstWar, war_id)
    if not war_db:
        raise HTTPException(status_code=404, detail="War not found")

    quest_selections = await fetch.get_all(conn, MstWarQuestSelection, war_id)

    maps = await fetch.get_all(conn, MstMap, war_id)
    map_ids = [event_map.id for event_map in maps]

    spots = await fetch.get_all_multiple(conn, MstSpot, map_ids)
    blank_earth_spots = await fetch.get_all_multiple(conn, MstBlankEarthSpot, map_ids)

    spot_ids = [spot.id for spot in spots] + [spot.id for spot in blank_earth_spots]
    spot_adds = await fetch.get_all_multiple(conn, MstSpotAdd, spot_ids)

    quests = await quest.get_quest_by_spot(conn, spot_ids)

    quest_selection_ids = [selection.questId for selection in quest_selections]
    selection_quests = await quest.get_quest_entity(conn, quest_selection_ids)
    selection_spot_ids = {quest.mstQuest.spotId for quest in selection_quests}
    selection_spots = await war.get_spot_from_ids(conn, selection_spot_ids)

    quests += selection_quests
    spots += selection_spots

    bgm_ids = [war_map.bgmId for war_map in maps] + [war_db.bgmId]
    bgms = await fetch.get_all_multiple(conn, MstBgm, bgm_ids)

    spot_roads = await fetch.get_all_multiple(conn, MstSpotRoad, map_ids)

    return WarEntity(
        mstWar=war_db,
        mstEvent=await fetch.get_one(conn, MstEvent, war_db.eventId),
        mstWarAdd=await fetch.get_all(conn, MstWarAdd, war_id),
        mstMap=maps,
        mstMapGimmick=await fetch.get_all_multiple(conn, MstMapGimmick, map_ids),
        mstBgm=bgms,
        mstSpot=spots,
        mstBlankEarthSpot=blank_earth_spots,
        mstSpotAdd=spot_adds,
        mstQuest=quests,
        mstSpotRoad=spot_roads,
        mstWarQuestSelection=quest_selections,
    )


def get_quest_ids_in_conds(
    conds: list[MstEventMissionCondition],
    cond_details: list[MstEventMissionConditionDetail],
) -> set[int]:
    quest_ids: set[int] = set()
    for cond in conds:
        if cond.condType in (CondType.QUEST_CLEAR, CondType.QUEST_CLEAR_NUM):
            quest_ids |= set(cond.targetIds)
    for cond_detail in cond_details:
        if cond_detail.missionCondType in (
            DetailMissionCondType.QUEST_CLEAR_NUM_1,
            DetailMissionCondType.QUEST_CLEAR_NUM_2,
        ):
            quest_ids |= set(cond_detail.targetIds)
    return quest_ids


async def get_event_mission_entity(
    conn: AsyncConnection,
    mission_id: int,
    mstEventMission: MstEventMission | None = None,
) -> EventMissionEntity:
    if not mstEventMission:
        mstEventMission = await fetch.get_one(conn, MstEventMission, mission_id)
    if not mstEventMission:
        raise HTTPException(status_code=404, detail="Event mission not found")

    conds = await fetch.get_all_multiple(conn, MstEventMissionCondition, [mission_id])
    cond_detail_ids = [
        target_id
        for cond in conds
        if cond.condType == CondType.MISSION_CONDITION_DETAIL
        for target_id in cond.targetIds
    ]

    cond_details = await fetch.get_all_multiple(
        conn, MstEventMissionConditionDetail, cond_detail_ids
    )

    gift_ids = {mstEventMission.giftId}

    gift_adds = await fetch.get_all_multiple(conn, MstGiftAdd, gift_ids)
    replacement_gift_ids = {gift.priorGiftId for gift in gift_adds}

    gifts = await fetch.get_all_multiple(conn, MstGift, gift_ids | replacement_gift_ids)

    return EventMissionEntity(
        mstEventMission=mstEventMission,
        mstEventMissionCondition=conds,
        mstEventMissionConditionDetail=cond_details,
        mstGift=gifts,
        mstGiftAdd=gift_adds,
    )


async def get_master_mission_entity(
    conn: AsyncConnection,
    mm_id: int,
    mstMasterMission: Optional[MstMasterMission] = None,
) -> MasterMissionEntity:
    if not mstMasterMission:
        mstMasterMission = await fetch.get_one(conn, MstMasterMission, mm_id)

    missions = await fetch.get_all(conn, MstEventMission, mm_id)
    mission_ids = [mission.id for mission in missions]

    if not mstMasterMission:
        if not missions:
            raise HTTPException(status_code=404, detail="Master mission not found")
        mission = missions[0]
        mstMasterMission = MstMasterMission(
            id=mm_id,
            priority=0,
            startedAt=mission.startedAt,
            endedAt=mission.endedAt,
            closedAt=mission.closedAt,
            imageId=0,
            name="",
        )

    conds = await fetch.get_all_multiple(conn, MstEventMissionCondition, mission_ids)
    cond_detail_ids = [
        target_id
        for cond in conds
        if cond.condType == CondType.MISSION_CONDITION_DETAIL
        for target_id in cond.targetIds
    ]

    cond_details = await fetch.get_all_multiple(
        conn, MstEventMissionConditionDetail, cond_detail_ids
    )

    gift_ids = {mission.giftId for mission in missions}

    gift_adds = await fetch.get_all_multiple(conn, MstGiftAdd, gift_ids)
    replacement_gift_ids = {gift.priorGiftId for gift in gift_adds}

    gifts = await fetch.get_all_multiple(conn, MstGift, gift_ids | replacement_gift_ids)

    quest_ids = get_quest_ids_in_conds(conds, cond_details)
    quests = await quest.get_many_quests_with_war(conn, quest_ids)

    return MasterMissionEntity(
        mstMasterMission=mstMasterMission,
        mstEventMission=missions,
        mstEventMissionCondition=conds,
        mstEventMissionConditionDetail=cond_details,
        mstGift=gifts,
        mstGiftAdd=gift_adds,
        mstQuest=quests,
    )


async def get_event_entity(conn: AsyncConnection, event_id: int) -> EventEntity:
    mstEvent = await fetch.get_one(conn, MstEvent, event_id)
    if not mstEvent:
        raise HTTPException(status_code=404, detail="Event not found")

    missions = await fetch.get_all(conn, MstEventMission, event_id)
    mission_ids = [mission.id for mission in missions]

    conds = await fetch.get_all_multiple(conn, MstEventMissionCondition, mission_ids)
    cond_detail_ids = [
        target_id
        for cond in conds
        if cond.condType == CondType.MISSION_CONDITION_DETAIL
        for target_id in cond.targetIds
    ]

    mission_groups = await fetch.get_all_multiple(
        conn, MstEventMissionGroup, mission_ids
    )

    cond_details = await fetch.get_all_multiple(
        conn, MstEventMissionConditionDetail, cond_detail_ids
    )

    box_gachas = await fetch.get_all(conn, MstBoxGacha, event_id)

    box_gacha_base_ids = [
        base_id for box_gacha in box_gachas for base_id in box_gacha.baseIds
    ]
    gacha_bases = await event.get_mstBoxGachaBase(conn, box_gacha_base_ids)

    box_gacha_talk_ids = {
        talk_id for box_gacha in box_gachas for talk_id in box_gacha.talkIds
    }
    gacha_talks = await fetch.get_all_multiple(
        conn, MstBoxGachaTalk, box_gacha_talk_ids
    )

    command_assists = await fetch.get_all(conn, MstEventCommandAssist, event_id)
    command_assist_release_ids = {
        command.commonReleaseId for command in command_assists
    }
    command_assist_skill_ids = {command.skillId for command in command_assists}

    raw_skills = await get_skill_entity_no_reverse_many(
        conn, command_assist_skill_ids, True
    )

    voice_plays = await fetch.get_all(conn, MstEventVoicePlay, event_id)

    reward_scenes = await fetch.get_all(conn, MstEventRewardScene, event_id)

    costume_limits = [
        svt.SvtLimit(svt_id=svt_id, limit=limit)
        for reward_scene in reward_scenes
        for svt_id, limit in zip(
            reward_scene.guideImageIds, reward_scene.guideLimitCounts, strict=False
        )
        if limit >= COSTUME_LIMIT_NO_LESS_THAN
    ]
    mstSvtLimitAdd = await svt.get_svt_limit_add(conn, costume_limits)

    voice_ids = (
        {voice_play.guideImageId for voice_play in voice_plays}
        | {gacha_talk.guideImageId for gacha_talk in gacha_talks}
        | {guide_id for scene in reward_scenes for guide_id in scene.guideImageIds}
    )

    mstSvtVoice = await svt.get_mstSvtVoice(conn, voice_ids)
    mstVoice = await get_voice_from_svtVoice(conn, mstSvtVoice)
    mstSvtGroup = await get_voice_group_from_svtVoice(conn, mstSvtVoice)
    mstSubtitle = await svt.get_mstSubtitle(conn, voice_ids)
    mstVoicePlayCond = await svt.get_mstVoicePlayCond(conn, voice_ids)
    mstSvtExtra = await fetch.get_all_multiple(conn, MstSvtExtra, voice_ids)

    shops = await fetch.get_all(conn, MstShop, event_id)
    set_item_ids = [
        set_id
        for shop in shops
        for set_id in shop.targetIds
        if shop.purchaseType == PurchaseType.SET_ITEM
    ]
    set_items = await item.get_mstSetItem(conn, set_item_ids)
    shop_consume_ids = {
        shop.itemIds[0] for shop in shops if shop.payType == PayType.COMMON_CONSUME
    }

    shop_ids = [shop.id for shop in shops]
    shop_scripts = await fetch.get_all_multiple(conn, MstShopScript, shop_ids)
    shop_releases = await fetch.get_all_multiple(conn, MstShopRelease, shop_ids)

    rewards = await fetch.get_all(conn, MstEventReward, event_id)

    tower_rewards = await event.get_mstEventTowerReward(conn, event_id)

    treasure_boxes = await fetch.get_all(conn, MstTreasureBox, event_id)
    box_gift_ids = {box.treasureBoxGiftId for box in treasure_boxes}
    box_gifts = await fetch.get_all_multiple(conn, MstTreasureBoxGift, box_gift_ids)

    digging = await fetch.get_one(conn, MstEventDigging, event_id)
    if digging:
        digging_blocks = await fetch.get_all(conn, MstEventDiggingBlock, event_id)
        digging_rewards = await fetch.get_all(conn, MstEventDiggingReward, event_id)
        digging_gift_ids = {reward.giftId for reward in digging_rewards}
        digging_consume_ids = {block.commonConsumeId for block in digging_blocks}
    else:
        digging_blocks = []
        digging_rewards = []
        digging_gift_ids = set()
        digging_consume_ids = set()

    event_cooltimes = await fetch.get_all(conn, MstEventCooltimeReward, event_id)
    cooltime_release_ids = {cooltime.commonReleaseId for cooltime in event_cooltimes}

    bulletins = await fetch.get_all(conn, MstEventBulletinBoard, event_id)
    bulletin_ids = {bulletin.id for bulletin in bulletins}
    bulletin_releases = await fetch.get_all_multiple(
        conn, MstEventBulletinBoardRelease, bulletin_ids
    )

    recipes = await fetch.get_all(conn, MstEventRecipe, event_id)
    recipe_ids = {recipe.id for recipe in recipes}
    recipe_gifts = await fetch.get_all_multiple(conn, MstEventRecipeGift, recipe_ids)
    recipe_release_ids = {recipe.commonReleaseId for recipe in recipes}

    fortifications = await fetch.get_all(conn, MstEventFortification, event_id)
    fortification_details = await fetch.get_all(
        conn, MstEventFortificationDetail, event_id
    )
    fortification_servants = await fetch.get_all(
        conn, MstEventFortificationSvt, event_id
    )
    fortification_gift_ids = {fortification.giftId for fortification in fortifications}
    fortification_release_ids = (
        {fortification.commonReleaseId for fortification in fortifications}
        | {detail.commonReleaseId for detail in fortification_details}
        | {svt.commonReleaseId for svt in fortification_servants}
    )

    common_release_ids = (
        cooltime_release_ids
        | recipe_release_ids
        | fortification_release_ids
        | command_assist_release_ids
    )
    common_releases = await fetch.get_all_multiple(
        conn, MstCommonRelease, common_release_ids
    )

    common_consume_ids = (
        shop_consume_ids
        | digging_consume_ids
        | {box.commonConsumeId for box in treasure_boxes}
        | {recipe.commonConsumeId for recipe in recipes}
    )
    common_consumes = await fetch.get_all_multiple(
        conn, MstCommonConsume, common_consume_ids
    )

    gift_ids = (
        {shop.targetIds[0] for shop in shops if shop.purchaseType == PurchaseType.GIFT}
        | {
            set_item.targetId
            for set_item in set_items
            if set_item.purchaseType == PurchaseType.GIFT
        }
        | {reward.giftId for reward in rewards}
        | {mission.giftId for mission in missions}
        | {tower_reward.giftId for tower_reward in tower_rewards}
        | {box.targetId for box in gacha_bases}
        | {box.extraGiftId for box in treasure_boxes}
        | {treasure_box_gift.giftId for treasure_box_gift in box_gifts}
        | {cooltime.giftId for cooltime in event_cooltimes}
        | {recipe_gift.giftId for recipe_gift in recipe_gifts}
        | digging_gift_ids
        | fortification_gift_ids
    )

    gift_adds = await fetch.get_all_multiple(conn, MstGiftAdd, gift_ids)
    replacement_gift_ids = {gift.priorGiftId for gift in gift_adds}

    gifts = await fetch.get_all_multiple(conn, MstGift, gift_ids | replacement_gift_ids)

    item_ids = (
        {get_shop_cost_item_id(shop) for shop in shops}
        | {lottery.payTargetId for lottery in box_gachas}
        | {recipe.eventPointItemId for recipe in recipes}
    )
    if digging:
        item_ids |= {digging.eventPointItemId}
    mstItem = await get_multiple_items(conn, item_ids)

    bgm_ids = {reward_scene.bgmId for reward_scene in reward_scenes} | {
        reward_scene.afterBgmId for reward_scene in reward_scenes
    }
    mstBgm = [await get_bgm_entity(conn, bgm_id) for bgm_id in bgm_ids]

    return EventEntity(
        mstEvent=mstEvent,
        mstEventAdd=await fetch.get_all(conn, MstEventAdd, event_id),
        mstWar=await event.get_event_wars(conn, event_id),
        mstEventRewardScene=reward_scenes,
        mstEventVoicePlay=voice_plays,
        mstShop=shops,
        mstShopScript=shop_scripts,
        mstShopRelease=shop_releases,
        mstGift=gifts,
        mstGiftAdd=gift_adds,
        mstSetItem=set_items,
        mstEventReward=rewards,
        mstEventRewardSet=await fetch.get_all(conn, MstEventRewardSet, event_id),
        mstEventPointGroup=await fetch.get_all(conn, MstEventPointGroup, event_id),
        mstEventPointBuff=await fetch.get_all(conn, MstEventPointBuff, event_id),
        mstEventMission=missions,
        mstEventRandomMission=await fetch.get_all(
            conn, MstEventRandomMission, event_id
        ),
        mstEventMissionCondition=conds,
        mstEventMissionConditionDetail=cond_details,
        mstEventMissionGroup=mission_groups,
        mstEventTower=await fetch.get_all(conn, MstEventTower, event_id),
        mstEventTowerReward=tower_rewards,
        mstBoxGacha=box_gachas,
        mstBoxGachaBase=gacha_bases,
        mstBoxGachaTalk=gacha_talks,
        mstTreasureBox=treasure_boxes,
        mstTreasureBoxGift=box_gifts,
        mstEventDigging=digging,
        mstEventDiggingBlock=digging_blocks,
        mstEventDiggingReward=digging_rewards,
        mstEventCooltimeReward=event_cooltimes,
        mstEventQuestCooltime=await fetch.get_all(
            conn, MstEventQuestCooltime, event_id
        ),
        mstEventFortification=fortifications,
        mstEventFortificationDetail=fortification_details,
        mstEventFortificationSvt=fortification_servants,
        mstEventQuest=await fetch.get_all(conn, MstEventQuest, event_id),
        mstEventCampaign=await fetch.get_all(conn, MstEventCampaign, event_id),
        mstEventBulletinBoard=bulletins,
        mstEventBulletinBoardRelease=bulletin_releases,
        mstEventRecipe=recipes,
        mstEventRecipeGift=recipe_gifts,
        mstEventCommandAssist=command_assists,
        mstHeelPortrait=await fetch.get_all(conn, MstHeelPortrait, event_id),
        mstEventMural=await fetch.get_all(conn, MstEventMural, event_id),
        mstEventPointActivity=await fetch.get_all(
            conn, MstEventPointActivity, event_id
        ),
        mstItem=mstItem,
        mstCommonConsume=common_consumes,
        mstCommonRelease=common_releases,
        mstSvtVoice=mstSvtVoice,
        mstVoice=mstVoice,
        mstSvtGroup=mstSvtGroup,
        mstSubtitle=mstSubtitle,
        mstVoicePlayCond=mstVoicePlayCond,
        mstSvtExtra=mstSvtExtra,
        mstSvtLimitAdd=mstSvtLimitAdd,
        mstBgm=mstBgm,
        mstSkill=raw_skills,
    )


async def get_quest_entity_many(
    conn: AsyncConnection, quest_id: list[int]
) -> list[QuestEntity]:
    quest_entities = await quest.get_quest_entity(conn, quest_id)
    if quest_entities:
        return quest_entities
    else:
        raise HTTPException(status_code=404, detail="Quest not found")


async def get_quest_entity(conn: AsyncConnection, quest_id: int) -> QuestEntity:
    return (await get_quest_entity_many(conn, [quest_id]))[0]


async def get_quest_phase_entity(
    conn: AsyncConnection, quest_id: int, phase: int
) -> QuestPhaseEntity:
    quest_phase = await quest.get_quest_phase_entity(conn, quest_id, phase)
    if quest_phase:
        stage_remaps = await quest.get_stage_remap(conn, quest_id, phase)
        if stage_remaps:
            remapped_stages = await quest.get_remapped_stages(conn, stage_remaps)
            bgms = await quest.get_bgm_from_stage(conn, remapped_stages)
            quest_phase.mstStage = remapped_stages
            quest_phase.mstBgm = bgms
        return quest_phase
    else:
        raise HTTPException(status_code=404, detail="Quest phase not found")


async def get_script_entity(conn: AsyncConnection, script_id: str) -> ScriptEntity:
    raw_script = await script.get_script(conn, script_id)
    if not raw_script:
        raise HTTPException(status_code=404, detail="Script not found")

    return raw_script


async def get_ai_entities(
    conn: AsyncConnection, ai_id: int, field: bool = False, throw_error: bool = True
) -> list[AiEntity]:
    if field:
        ais = await ai.get_field_ai_entity(conn, ai_id)
    else:
        ais = await ai.get_svt_ai_entity(conn, ai_id)

    if not ais and throw_error:
        raise HTTPException(status_code=404, detail="AI not found")

    return ais


async def get_ai_collection(
    conn: AsyncConnection, ai_id: int, field: bool = False
) -> AiCollection:
    main_ais = await get_ai_entities(conn, ai_id, field)
    retreived_ais = {ai_id}

    to_be_retrieved_ais = {
        ai.mstAi.avals[0] for ai in main_ais if ai.mstAi.avals[0] > 0
    }
    related_ais: list[AiEntity] = []
    while to_be_retrieved_ais:
        for related_ai_id in to_be_retrieved_ais:
            related_ais += await get_ai_entities(
                conn, related_ai_id, field, throw_error=False
            )

        retreived_ais |= to_be_retrieved_ais
        to_be_retrieved_ais = {
            ai.mstAi.avals[0]
            for ai in related_ais
            if ai.mstAi.avals[0] > 0 and ai.mstAi.avals[0] not in retreived_ais
        }

    return AiCollection(
        mainAis=main_ais,
        relatedAis=related_ais,
        relatedQuests=await quest.get_quest_from_ai(conn, ai_id) if field else [],
    )


async def get_bgm_entity(conn: AsyncConnection, bgm_id: int) -> BgmEntity:
    mstBgm = await fetch.get_one(conn, MstBgm, bgm_id)
    if not mstBgm:
        raise HTTPException(status_code=404, detail="BGM not found")

    mstBgmRelease = await fetch.get_all(conn, MstBgmRelease, bgm_id)
    mstClosedMessage = await fetch.get_all_multiple(
        conn, MstClosedMessage, [release.closedMessageId for release in mstBgmRelease]
    )

    bgm_entity = BgmEntity(
        mstBgm=mstBgm, mstBgmRelease=mstBgmRelease, mstClosedMessage=mstClosedMessage
    )

    if mstBgm.flag != BgmFlag.IS_NOT_RELEASE:
        mstShop = await fetch.get_one(conn, MstShop, mstBgm.shopId)
        if mstShop:
            bgm_entity.mstShop = mstShop
            bgm_entity.mstItem = await fetch.get_one(
                conn, MstItem, get_shop_cost_item_id(mstShop)
            )

    return bgm_entity


async def get_all_bgm_entities(
    conn: AsyncConnection,
) -> list[BgmEntity]:  # pragma: no cover
    mstBgms = await fetch.get_everything(conn, MstBgm)

    mstBgmReleases = await fetch.get_everything(conn, MstBgmRelease)
    mstClosedMessages = await fetch.get_all_multiple(
        conn, MstClosedMessage, [release.closedMessageId for release in mstBgmReleases]
    )

    mstShops = await fetch.get_all_multiple(
        conn,
        MstShop,
        [mstBgm.shopId for mstBgm in mstBgms if mstBgm.flag != BgmFlag.IS_NOT_RELEASE],
    )
    mstShop_map = {mstShop.id: mstShop for mstShop in mstShops}

    item_ids = {get_shop_cost_item_id(shop) for shop in mstShops}
    mstItems = await get_multiple_items(conn, item_ids)
    mstItem_map = {mstItem.id: mstItem for mstItem in mstItems}

    out_entities: list[BgmEntity] = []
    for mstBgm in mstBgms:
        mstBgmRelease = [
            mstBgmRelease
            for mstBgmRelease in mstBgmReleases
            if mstBgmRelease.bgmId == mstBgm.id
        ]
        closed_message_ids = [release.closedMessageId for release in mstBgmRelease]
        mstClosedMessage = [
            mstClosedMessage
            for mstClosedMessage in mstClosedMessages
            if mstClosedMessage.id in closed_message_ids
        ]
        bgm_entity = BgmEntity(
            mstBgm=mstBgm,
            mstBgmRelease=mstBgmRelease,
            mstClosedMessage=mstClosedMessage,
        )

        if mstBgm.flag != BgmFlag.IS_NOT_RELEASE:
            mstShop = mstShop_map.get(mstBgm.shopId)
            if mstShop:
                bgm_entity.mstShop = mstShop
                bgm_entity.mstItem = mstItem_map.get(get_shop_cost_item_id(mstShop))

        out_entities.append(bgm_entity)

    return out_entities


async def get_shop_entities(
    conn: AsyncConnection, shops: list[MstShop]
) -> list[ShopEntity]:
    shop_scripts = await fetch.get_all_multiple(
        conn, MstShopScript, [shop.id for shop in shops]
    )
    shop_script_map = {script.shopId: script for script in shop_scripts}
    shop_releases = await fetch.get_all_multiple(
        conn, MstShopRelease, [shop.id for shop in shops]
    )

    item_ids = {get_shop_cost_item_id(shop) for shop in shops}
    common_consume_ids = {
        consume_id
        for shop in shops
        if shop.payType == PayType.COMMON_CONSUME
        for consume_id in shop.itemIds
    }
    mstItem = await get_multiple_items(conn, item_ids)
    item_map = {item.id: item for item in mstItem}

    common_consumes = await fetch.get_all_multiple(
        conn, MstCommonConsume, common_consume_ids
    )

    set_item_ids = {
        set_id
        for shop in shops
        if shop.purchaseType == PurchaseType.SET_ITEM
        for set_id in shop.targetIds
    }
    all_set_items = await item.get_mstSetItem(conn, set_item_ids)

    all_gift_ids = {
        gift_id
        for shop in shops
        if shop.purchaseType == PurchaseType.GIFT
        for gift_id in shop.targetIds
    }
    all_gift_ids |= {
        set_item.targetId
        for set_item in all_set_items
        if set_item.purchaseType == PurchaseType.GIFT
    }

    all_gift_adds = await fetch.get_all_multiple(conn, MstGiftAdd, all_gift_ids)
    replacement_gift_ids = {gift.priorGiftId for gift in all_gift_adds}

    all_gifts = await fetch.get_all_multiple(
        conn, MstGift, all_gift_ids | replacement_gift_ids
    )

    entities: list[ShopEntity] = []
    for shop in shops:
        item_id = get_shop_cost_item_id(shop)
        set_items = (
            [set_item for set_item in all_set_items if set_item.id in shop.targetIds]
            if shop.purchaseType == PurchaseType.SET_ITEM
            else []
        )
        gift_ids = (
            set(shop.targetIds) if shop.purchaseType == PurchaseType.GIFT else set()
        )
        for set_item in set_items:
            if set_item.purchaseType == PurchaseType.GIFT:
                gift_ids.add(set_item.targetId)
        gift_adds = [
            gift_add for gift_add in all_gift_adds if gift_add.giftId in gift_ids
        ]
        gift_ids |= {gift.priorGiftId for gift in gift_adds}
        gifts = [gift for gift in all_gifts if gift.id in gift_ids]
        entities.append(
            ShopEntity(
                mstShop=shop,
                mstSetItem=set_items,
                mstShopRelease=[
                    release for release in shop_releases if release.shopId == shop.id
                ],
                mstShopScript=shop_script_map.get(shop.id),
                mstItem=[item_map[item_id]] if item_id in item_map else [],
                mstCommonConsume=[
                    consume for consume in common_consumes if consume.id in shop.itemIds
                ]
                if shop.payType == PayType.COMMON_CONSUME
                else [],
                mstGift=gifts,
                mstGiftAdd=gift_adds,
            )
        )
    return entities


async def get_raw_mstShop(conn: AsyncConnection, shop_id: int) -> MstShop:
    shop = await fetch.get_one(conn, MstShop, shop_id)

    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    return shop


async def get_shop_entity(conn: AsyncConnection, shop_id: int) -> ShopEntity:
    shop = await get_raw_mstShop(conn, shop_id)
    return (await get_shop_entities(conn, [shop]))[0]


async def get_common_releases(
    conn: AsyncConnection, release_ids: Iterable[int]
) -> list[MstCommonRelease]:
    releases = await fetch.get_all_multiple(conn, MstCommonRelease, release_ids)
    return releases


async def get_class_board_entity(
    conn: AsyncConnection, class_board_id: int
) -> ClassBoardEntity:
    board_db = await fetch.get_one(conn, MstClassBoardBase, class_board_id)
    if not board_db:
        raise HTTPException(status_code=404, detail="Class Board not found")

    classes = await fetch.get_all(conn, MstClassBoardClass, class_board_id)
    lines = await fetch.get_all(conn, MstClassBoardLine, class_board_id)
    squares = await fetch.get_all(conn, MstClassBoardSquare, class_board_id)

    lock_ids = {square.lockId for square in squares if square.lockId > 0}
    locks = await fetch.get_all_multiple(conn, MstClassBoardLock, lock_ids)

    cs_ids = {
        square.targetId
        for square in squares
        if square.skillType == ClassBoardSkillType.COMMAND_SPELL
    }
    command_spells = await fetch.get_all_multiple(
        conn, MstClassBoardCommandSpell, cs_ids
    )

    item_ids: set[int] = set(board_db.dispItemIds)
    item_ids |= {itemId for square in squares for itemId in square.itemIds}
    item_ids |= {itemId for lock in locks for itemId in lock.itemIds}
    mstItem = await get_multiple_items(conn, item_ids)

    skill_ids = {
        square.targetId
        for square in squares
        if square.skillType == ClassBoardSkillType.PASSIVE
    }
    skill_entities = await skill.get_skillEntity(conn, skill_ids)

    return ClassBoardEntity(
        mstClassBoardBase=board_db,
        mstClassBoardClass=classes,
        mstClassBoardLine=lines,
        mstClassBoardSquare=squares,
        mstClassBoardLock=locks,
        mstClassBoardCommandSpell=command_spells,
        mstItem=mstItem,
        mstSkill=skill_entities,
    )
