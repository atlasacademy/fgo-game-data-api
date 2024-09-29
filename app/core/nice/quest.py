import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional, Union, cast

from fastapi import HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...db.helpers import war
from ...db.helpers.quest import get_questSelect_container
from ...db.helpers.rayshift import (
    get_all_quest_hashes,
    get_all_support_servants,
    get_cutin_drops,
    get_cutin_skills,
    get_rayshift_drops,
    get_war_board_quest_details,
    quest_has_cutins,
)
from ...rayshift.quest import get_quest_detail
from ...redis import Redis
from ...redis.helpers.quest import RayshiftRedisData, get_stages_cache, set_stages_cache
from ...schemas.common import Language, Region, ScriptLink
from ...schemas.enums import STAGE_LIMIT_ACT_TYPE_NAME, get_class_name
from ...schemas.gameenums import (
    AI_ALLOCATION_SVT_FLAG_NAME,
    BATTLE_ENVIRONMENT_GRANT_TYPE_NAME,
    COND_TYPE_NAME,
    FREQUENCY_TYPE_NAME,
    QUEST_AFTER_CLEAR_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    RESTRICTION_RANGE_TYPE_NAME,
    RESTRICTION_TYPE_NAME,
    Quest_FLAG_NAME,
    QuestType,
)
from ...schemas.nice import (
    AssetURL,
    DeckType,
    EnemyDrop,
    NiceAiAllocation,
    NiceBattleBg,
    NiceBgm,
    NiceQuest,
    NiceQuestHint,
    NiceQuestMessage,
    NiceQuestPhase,
    NiceQuestPhasePresent,
    NiceQuestPhaseRestriction,
    NiceQuestPhaseScript,
    NiceQuestRelease,
    NiceQuestReleaseOverwrite,
    NiceRestriction,
    NiceStage,
    NiceStageCutIn,
    NiceStageStartMovie,
    QuestEnemy,
    SupportServant,
)
from ...schemas.raw import (
    MstBattleBg,
    MstBgm,
    MstBlankEarthSpot,
    MstClosedMessage,
    MstQuestHint,
    MstQuestMessage,
    MstQuestPhasePresent,
    MstQuestRelease,
    MstQuestReleaseOverwrite,
    MstQuestRestriction,
    MstRestriction,
    MstSpot,
    MstStage,
    MstWar,
    QuestEntity,
    QuestPhaseEntity,
    ScriptFile,
)
from .. import raw
from ..rayshift import get_quest_enemy_hash
from ..utils import fmt_url, get_flags, get_nice_trait, get_traits_list, get_translation
from .base_script import get_nice_script_link
from .bgm import get_nice_bgm
from .enemy import QuestEnemies, get_nice_drop, get_quest_enemies, get_war_board_enemies
from .follower import get_nice_support_servants
from .gift import GiftData, get_gift_map, get_nice_gifts
from .item import get_nice_item_amount, get_nice_item_from_raw
from .stage_cutin import get_quest_stage_cutins


settings = Settings()


def get_nice_quest_release(
    raw_quest_release: MstQuestRelease,
    closed_messages: list[MstClosedMessage],
) -> NiceQuestRelease:
    closed_message = next(
        (
            message
            for message in closed_messages
            if message.id == raw_quest_release.closedMessageId
        ),
        None,
    )
    return NiceQuestRelease(
        type=COND_TYPE_NAME[raw_quest_release.type],
        targetId=raw_quest_release.targetId,
        value=raw_quest_release.value,
        closedMessage=closed_message.message if closed_message else "",
    )


def get_nice_quest_release_overwrite(
    raw_release_overwrite: MstQuestReleaseOverwrite,
    closed_messages: list[MstClosedMessage],
) -> NiceQuestReleaseOverwrite:
    closed_message = next(
        (
            message
            for message in closed_messages
            if message.id == raw_release_overwrite.closedMessageId
        ),
        None,
    )
    return NiceQuestReleaseOverwrite(
        priority=raw_release_overwrite.priority,
        condType=COND_TYPE_NAME[raw_release_overwrite.condType],
        condId=raw_release_overwrite.condId,
        condNum=raw_release_overwrite.condNum,
        closedMessage=closed_message.message if closed_message else "",
        overlayClosedMessage=raw_release_overwrite.overlayClosedMessage,
        eventId=raw_release_overwrite.eventId,
        startedAt=raw_release_overwrite.startedAt,
        endedAt=raw_release_overwrite.endedAt,
    )


def get_nice_quest_message(message: MstQuestMessage) -> NiceQuestMessage:
    return NiceQuestMessage(
        idx=message.idx,
        message=message.message,
        condType=COND_TYPE_NAME[message.condType],
        targetId=message.targetId,
        targetNum=message.targetNum,
    )


def get_nice_quest_hints(hint: MstQuestHint) -> NiceQuestHint:
    return NiceQuestHint(
        title=hint.title, message=hint.message, leftIndent=hint.leftIndent
    )


def get_nice_quest_restriction(
    quest_restriction: MstQuestRestriction, restriction: MstRestriction
) -> NiceQuestPhaseRestriction:
    return NiceQuestPhaseRestriction(
        restriction=NiceRestriction(
            id=restriction.id,
            name=restriction.name,
            type=RESTRICTION_TYPE_NAME[restriction.type],
            rangeType=RESTRICTION_RANGE_TYPE_NAME[restriction.rangeType],
            targetVals=restriction.targetVals,
            targetVals2=restriction.targetVals2 if restriction.targetVals2 else [],
        ),
        frequencyType=FREQUENCY_TYPE_NAME[quest_restriction.frequencyType],
        dialogMessage=quest_restriction.dialogMessage,
        noticeMessage=quest_restriction.noticeMessage,
        title=quest_restriction.title,
    )


def get_nice_battle_bg(battle_bg: MstBattleBg) -> NiceBattleBg:
    return NiceBattleBg(
        id=battle_bg.id,
        type=BATTLE_ENVIRONMENT_GRANT_TYPE_NAME[battle_bg.type],
        priority=battle_bg.priority,
        individuality=get_traits_list(battle_bg.individuality),
        imageId=battle_bg.imageId,
    )


def get_nice_stage(
    region: Region,
    raw_stage: MstStage,
    enemies: list[QuestEnemy],
    bgms: list[MstBgm],
    bgs: list[MstBattleBg],
    waveStartMovies: dict[int, list[NiceStageStartMovie]],
    stage_cutins: dict[int, NiceStageCutIn],
    lang: Language,
) -> NiceStage:
    filtered_bgms = [bgm for bgm in bgms if bgm.id == raw_stage.bgmId]
    if filtered_bgms:
        bgm = get_nice_bgm(region, filtered_bgms[0], lang)
    else:
        bgm = NiceBgm(id=0, name="", originalName="", fileName="", notReleased=True)

    return NiceStage(
        wave=raw_stage.wave,
        bgm=bgm,
        startEffectId=raw_stage.startEffectId,
        fieldAis=raw_stage.script.get("aiFieldIds", []),
        call=raw_stage.script.get("call", []),
        enemyFieldPosCount=raw_stage.script.get("enemyFieldPosCount"),
        enemyActCount=raw_stage.script.get("EnemyActCount"),
        turn=raw_stage.script.get("turn"),
        limitAct=(
            STAGE_LIMIT_ACT_TYPE_NAME[raw_stage.script["LimitAct"]]
            if "LimitAct" in raw_stage.script
            else None
        ),
        battleBg=(
            next(
                (
                    get_nice_battle_bg(bg)
                    for bg in bgs
                    if bg.id == raw_stage.script["changeBgId"]
                    and bg.type == raw_stage.script["changeBgType"]
                ),
                None,
            )
            if "changeBgId" in raw_stage.script and "changeBgType" in raw_stage.script
            else None
        ),
        NoEntryIds=raw_stage.script.get("NoEntryIds"),
        waveStartMovies=waveStartMovies.get(raw_stage.wave, []),
        cutin=stage_cutins.get(raw_stage.wave, None),
        aiAllocations=(
            [
                NiceAiAllocation(
                    aiIds=ai_allocation["aiIds"],
                    individuality=get_nice_trait(ai_allocation["individuality"]),
                    applySvtType=get_flags(
                        ai_allocation["applySvtType"], AI_ALLOCATION_SVT_FLAG_NAME
                    ),
                )
                for ai_allocation in raw_stage.script["aiAllocations"]
            ]
            if "aiAllocations" in raw_stage.script
            else None
        ),
        originalScript=raw_stage.script or {},
        enemies=enemies,
    )


def get_nice_all_scripts(
    region: Region, scripts: list[ScriptFile]
) -> list[NiceQuestPhaseScript]:
    phase_scripts: dict[int, list[ScriptLink]] = defaultdict(list)
    for script in sorted(scripts, key=lambda s: s.scriptFileName):
        phase_scripts[script.phase].append(
            get_nice_script_link(region, script.scriptFileName)
        )

    return [
        NiceQuestPhaseScript(phase=phase, scripts=phase_scripts[phase])
        for phase in sorted(phase_scripts)
    ]


def get_nice_quest_present(
    region: Region, quest_present: MstQuestPhasePresent, gift_data: GiftData
) -> NiceQuestPhasePresent:
    return NiceQuestPhasePresent(
        phase=quest_present.phase,
        gifts=get_nice_gifts(region, quest_present.giftId, gift_data),
        giftIcon=(
            fmt_url(
                AssetURL.items,
                base_url=settings.asset_url,
                region=region,
                item_id=quest_present.giftIconId,
            )
            if quest_present.giftIconId != 0
            else None
        ),
        condType=COND_TYPE_NAME[quest_present.condType],
        condId=quest_present.condId,
        condNum=quest_present.condNum,
        originalScript=quest_present.script,
    )


def get_nice_quest_with_war_spot(
    region: Region,
    raw_quest: Union[QuestEntity, QuestPhaseEntity],
    lang: Language,
    mstWar: MstWar,
    mstSpot: MstSpot | MstBlankEarthSpot,
) -> dict[str, Any]:
    gift_map = get_gift_map(raw_quest.mstGift)
    gift_data = GiftData(raw_quest.mstGiftAdd, gift_map)

    nice_data: dict[str, Any] = {
        "id": raw_quest.mstQuest.id,
        "name": get_translation(lang, raw_quest.mstQuest.name),
        "originalName": raw_quest.mstQuest.name,
        "type": QUEST_TYPE_NAME[raw_quest.mstQuest.type],
        "flags": get_flags(raw_quest.mstQuest.flag, Quest_FLAG_NAME),
        "consumeType": QUEST_CONSUME_TYPE_NAME[raw_quest.mstQuest.consumeType],
        "consumeItem": [
            nice_item_amount
            for consumeItem in raw_quest.mstQuestConsumeItem
            for nice_item_amount in get_nice_item_amount(
                [
                    get_nice_item_from_raw(region, item, lang)
                    for item in raw_quest.mstItem
                    if item.id in consumeItem.itemIds
                ],
                consumeItem.nums,
            )
        ],
        "consume": raw_quest.mstQuest.actConsume,
        "recommendLv": raw_quest.mstQuest.recommendLv,
        "afterClear": QUEST_AFTER_CLEAR_NAME[raw_quest.mstQuest.afterClear],
        "spotId": raw_quest.mstQuest.spotId,
        "spotName": get_translation(lang, mstSpot.name),
        "warId": mstWar.id,
        "warLongName": get_translation(lang, mstWar.longName),
        "chapterId": raw_quest.mstQuest.chapterId,
        "chapterSubId": raw_quest.mstQuest.chapterSubId,
        "chapterSubStr": raw_quest.mstQuest.chapterSubStr,
        "giftIcon": (
            AssetURL.items.format(
                base_url=settings.asset_url,
                region=region,
                item_id=raw_quest.mstQuest.giftIconId,
            )
            if raw_quest.mstQuest.giftIconId != 0
            else None
        ),
        "gifts": get_nice_gifts(region, raw_quest.mstQuest.giftId, gift_data),
        "releaseConditions": [
            get_nice_quest_release(release, raw_quest.mstClosedMessage)
            for release in raw_quest.mstQuestRelease
        ],
        "releaseOverwrites": [
            get_nice_quest_release_overwrite(release, raw_quest.mstClosedMessage)
            for release in raw_quest.mstQuestReleaseOverwrite
        ],
        "presents": [
            get_nice_quest_present(region, quest_present, gift_data)
            for quest_present in raw_quest.mstQuestPhasePresent
        ],
        "phases": sorted(raw_quest.phases),
        "phasesWithEnemies": sorted(raw_quest.phasesWithEnemies),
        "phasesNoBattle": sorted(raw_quest.phasesNoBattle),
        "phaseScripts": get_nice_all_scripts(region, raw_quest.allScripts),
        "priority": raw_quest.mstQuest.priority,
        "noticeAt": raw_quest.mstQuest.noticeAt,
        "openedAt": raw_quest.mstQuest.openedAt,
        "closedAt": raw_quest.mstQuest.closedAt,
    }
    return nice_data


async def get_nice_quest(
    conn: AsyncConnection,
    region: Region,
    raw_quest: Union[QuestEntity, QuestPhaseEntity],
    lang: Language,
    mstWar: Optional[MstWar] = None,
    mstSpot: Optional[MstSpot | MstBlankEarthSpot] = None,
) -> dict[str, Any]:
    if not mstSpot:
        mstSpot = await war.get_spot_from_id(conn, raw_quest.mstQuest.spotId)
    if mstSpot is None:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Quest's spot not found")

    if not mstWar:
        mstWar = await war.get_war_from_spot(conn, raw_quest.mstQuest.spotId)
    if mstWar is None:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Quest's war not found")

    return get_nice_quest_with_war_spot(region, raw_quest, lang, mstWar, mstSpot)


async def get_nice_quest_alone(
    conn: AsyncConnection, region: Region, quest_id: int, lang: Language
) -> NiceQuest:
    raw_quest = await raw.get_quest_entity(conn, quest_id)
    return NiceQuest.parse_obj(await get_nice_quest(conn, region, raw_quest, lang))


@dataclass
class DBQuestPhase:
    raw: QuestPhaseEntity
    nice: NiceQuestPhase


@cache()
async def get_nice_quest_phase_no_rayshift(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> DBQuestPhase:
    raw_quest = await raw.get_quest_phase_entity(conn, quest_id, phase)
    nice_data = await get_nice_quest(conn, region, raw_quest, lang)

    aiNpcIds: list[int] = []
    if "aiNpc" in raw_quest.mstQuestPhase.script:
        aiNpcIds.append(raw_quest.mstQuestPhase.script["aiNpc"]["npcId"])
    if "aiMultiNpc" in raw_quest.mstQuestPhase.script:
        for aiNpc in raw_quest.mstQuestPhase.script["aiMultiNpc"]:
            aiNpcIds.append(aiNpc["npcId"])

    support_servants: list[SupportServant] = []
    if (
        raw_quest.npcFollower
        or "aiNpc" in raw_quest.mstQuestPhase.script
        or "aiMultiNpc" in raw_quest.mstQuestPhase.script
    ):
        npcs = await get_nice_support_servants(
            conn=conn,
            redis=redis,
            region=region,
            npcFollower=raw_quest.npcFollower,
            npcFollowerRelease=raw_quest.npcFollowerRelease,
            npcSvtFollower=raw_quest.npcSvtFollower,
            npcSvtEquip=raw_quest.npcSvtEquip,
            lang=lang,
            aiNpcIds=aiNpcIds,
        )
        support_servants = npcs.support_servants
        if "aiNpc" in raw_quest.mstQuestPhase.script and npcs.ai_npc is not None:
            raw_quest.mstQuestPhase.script["aiNpc"]["npc"] = npcs.ai_npc[
                raw_quest.mstQuestPhase.script["aiNpc"]["npcId"]
            ]
        if "aiMultiNpc" in raw_quest.mstQuestPhase.script:
            for aiNpc in raw_quest.mstQuestPhase.script["aiMultiNpc"]:
                aiNpc["npc"] = npcs.ai_npc[aiNpc["npcId"]]

    restrictions = {
        restriction.id: restriction for restriction in raw_quest.mstRestriction
    }

    nice_data |= {
        "phase": raw_quest.mstQuestPhase.phase,
        "drops": [],
        "className": [
            get_class_name(class_id) for class_id in raw_quest.mstQuestPhase.classIds
        ],
        "individuality": get_traits_list(raw_quest.mstQuestPhase.individuality),
        "qp": raw_quest.mstQuestPhase.qp,
        "exp": raw_quest.mstQuestPhase.playerExp,
        "bond": raw_quest.mstQuestPhase.friendshipExp,
        "isNpcOnly": raw_quest.mstQuestPhase.isNpcOnly,
        "battleBgId": raw_quest.mstQuestPhase.battleBgId,
        "extraDetail": raw_quest.mstQuestPhase.script,
        "battleBg": next(
            (
                get_nice_battle_bg(bg)
                for bg in raw_quest.mstBattleBg
                if bg.id == raw_quest.mstQuestPhase.battleBgId
                and bg.type == raw_quest.mstQuestPhase.battleBgType
            ),
            None,
        ),
        "availableEnemyHashes": [],
        "scripts": [
            get_nice_script_link(region, script) for script in sorted(raw_quest.scripts)
        ],
        "messages": [
            get_nice_quest_message(message)
            for message in sorted(
                raw_quest.mstQuestMessage, key=lambda script: script.idx
            )
        ],
        "hints": [
            get_nice_quest_hints(hint)
            for hint in sorted(raw_quest.mstQuestHint, key=lambda hint: hint.title)
        ],
        "restrictions": [
            get_nice_quest_restriction(
                quest_restriction, restrictions[quest_restriction.restrictionId]
            )
            for quest_restriction in raw_quest.mstQuestRestriction
        ],
        "supportServants": support_servants,
        "stages": [],
    }

    if raw_quest.mstQuestPhaseDetail:
        if raw_quest.mstQuestPhaseDetail.spotId != raw_quest.mstQuest.spotId:
            mstSpot = await war.get_spot_from_id(
                conn, raw_quest.mstQuestPhaseDetail.spotId
            )
            if mstSpot:
                nice_data["spotId"] = raw_quest.mstQuestPhaseDetail.spotId
                nice_data["spotName"] = get_translation(lang, mstSpot.name)
        nice_data["recommendLv"] = (
            raw_quest.mstQuestPhaseDetail.recommendLv or raw_quest.mstQuest.recommendLv
        )
        detail_mstWar = await war.get_war_from_spot(
            conn, raw_quest.mstQuestPhaseDetail.spotId
        )
        if detail_mstWar:
            nice_data["warId"] = detail_mstWar.id
            nice_data["warLongName"] = get_translation(lang, detail_mstWar.longName)
        nice_data["consumeType"] = QUEST_CONSUME_TYPE_NAME[
            raw_quest.mstQuestPhaseDetail.consumeType
        ]
        nice_data["consume"] = raw_quest.mstQuestPhaseDetail.actConsume
        nice_data["flags"] = sorted(
            set(
                nice_data["flags"]
                + get_flags(raw_quest.mstQuestPhaseDetail.flag, Quest_FLAG_NAME)
            )
        )

    return DBQuestPhase(raw_quest, NiceQuestPhase.parse_obj(nice_data))


async def get_nice_quest_phase(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
    questHash: str | None = None,
) -> NiceQuestPhase:
    db_data = cast(
        DBQuestPhase,
        await get_nice_quest_phase_no_rayshift(
            conn, redis, region, quest_id, phase, lang
        ),
    )
    current_time = int(time.time())
    quest_already_closed = current_time > db_data.nice.closedAt

    if "questSelect" in db_data.raw.mstQuestPhase.script:
        questSelectScript: list[int] = db_data.raw.mstQuestPhase.script["questSelect"]
        questSelect: list[int] = [
            i
            for i, questSelectScriptId in enumerate(questSelectScript)
            if questSelectScriptId == quest_id
        ]
    else:
        questSelectScript = []
        questSelect = []

    rayshift_data = await get_stages_cache(
        redis, region, quest_id, phase, lang, questHash
    )

    def set_ai_npc_data(ai_npcs: dict[int, QuestEnemy] | None) -> None:
        if ai_npcs is not None:
            if db_data.nice.extraDetail.aiNpc is not None:
                db_data.nice.extraDetail.aiNpc.detail = ai_npcs[
                    db_data.nice.extraDetail.aiNpc.npc.npcId
                ]
            if db_data.nice.extraDetail.aiMultiNpc is not None:
                for aiNpc in db_data.nice.extraDetail.aiMultiNpc:
                    aiNpc.detail = ai_npcs[aiNpc.npc.npcId]

    def set_follower_data(followers: dict[int, QuestEnemy] | None) -> None:
        if followers is not None:
            for follower in db_data.nice.supportServants:
                if follower.npcSvtFollowerId in followers:
                    follower.detail = followers[follower.npcSvtFollowerId]
                else:
                    for quest_enemy in followers.values():
                        if (
                            quest_enemy.svt.id == follower.svt.id
                            and quest_enemy.limit.limitCount
                            == follower.limit.limitCount
                        ):
                            follower.detail = quest_enemy
                            break

    if rayshift_data:
        db_data.nice.stages = rayshift_data.stages
        db_data.nice.drops = rayshift_data.quest_drops
        if rayshift_data.quest_drops:
            db_data.nice.dropsFromAllHashes = questHash is None
        db_data.nice.availableEnemyHashes = rayshift_data.all_hashes
        if rayshift_data.quest_hash:
            db_data.nice.enemyHash = rayshift_data.quest_hash
        if rayshift_data.quest_select:
            db_data.nice.extraDetail.questSelect = rayshift_data.quest_select
        set_ai_npc_data(rayshift_data.ai_npcs)
        set_follower_data(rayshift_data.followers)
        return db_data.nice

    stages = sorted(db_data.raw.mstStage, key=lambda stage: stage.wave)
    save_stages_cache = True

    nice_quest_drops: list[EnemyDrop] = []
    quest_enemies = QuestEnemies(enemy_waves=[[]] * len(db_data.raw.mstStage))
    all_rayshift_hashes: list[str] = []
    stage_cutins: dict[int, NiceStageCutIn] = {}

    if stages:
        rayshift_quest_id = quest_id
        if not questSelect:
            quest_select_owner = await get_questSelect_container(conn, quest_id, phase)
            if quest_select_owner:
                questSelectScript = quest_select_owner.script["questSelect"]
                db_data.nice.extraDetail.questSelect = questSelectScript

                rayshift_quest_id = quest_select_owner.questId
                questSelect = [
                    i
                    for i, questSelectScriptId in enumerate(questSelectScript)
                    if questSelectScriptId == quest_id
                ]

        min_query_id: int | None = None
        if (
            db_data.raw.mstQuest.type in (QuestType.MAIN, QuestType.FREE)
            and db_data.nice.warId < 1000
        ):
            if region == Region.JP:
                min_query_id = 154613  # 2021-08-01 10:00:00 UTC
            elif region == Region.NA:
                min_query_id = 1062363  # 2022-07-04 09:00:00 UTC
        elif db_data.nice.warId == 1002:
            if region == Region.JP:
                min_query_id = 499538  # 2022-01-02 00:00:00 UTC
            elif region == Region.NA:
                min_query_id = 6481638  # 2024-01-02 00:00:00 UTC

        rayshift_query_questHash = (
            None if db_data.raw.mstQuest.type == QuestType.WAR_BOARD else questHash
        )

        rayshift_kwargs = {
            "conn": conn,
            "quest_id": rayshift_quest_id,
            "phase": phase,
            "questSelect": questSelect,
            "questHash": rayshift_query_questHash,
            "min_query_id": min_query_id,
        }

        runs_with_cutin = await quest_has_cutins(**rayshift_kwargs)  # type:ignore

        if runs_with_cutin:
            cutin_skills, cutin_drops = await asyncio.gather(
                get_cutin_skills(**rayshift_kwargs),  # type:ignore
                get_cutin_drops(**rayshift_kwargs, runs=runs_with_cutin),  # type:ignore
            )
            stage_cutins = await get_quest_stage_cutins(
                conn, region, runs_with_cutin, cutin_drops, cutin_skills, lang
            )

        if db_data.raw.mstQuest.type == QuestType.WAR_BOARD:
            quest_enemy_coro = get_war_board_quest_details(conn, quest_id, phase)
        else:
            quest_enemy_coro = get_quest_detail(
                conn=conn,
                region=region,
                quest_id=rayshift_quest_id,
                phase=phase,
                questSelect=questSelect,
                questHash=questHash,
                rayshift_fallback=not quest_already_closed,
            )

        rayshift_quest_details = await quest_enemy_coro

        (
            rayshift_quest_drops,
            all_rayshift_hashes,
        ) = await asyncio.gather(
            get_rayshift_drops(**rayshift_kwargs),  # type:ignore
            get_all_quest_hashes(conn, rayshift_quest_id, phase, questSelect),
        )

        db_data.nice.availableEnemyHashes = all_rayshift_hashes

        if not rayshift_quest_details:
            save_stages_cache = False
        else:
            rayshift_quest_hash = get_quest_enemy_hash(1, rayshift_quest_details[0])
            if questHash and rayshift_quest_hash != questHash:
                save_stages_cache = False
            else:
                if db_data.raw.mstQuest.type == QuestType.WAR_BOARD:
                    quest_enemies = await get_war_board_enemies(
                        conn, redis, region, rayshift_quest_details, lang
                    )
                else:
                    if db_data.nice.supportServants:
                        support_servant_details = await get_all_support_servants(
                            **rayshift_kwargs  # type:ignore
                        )
                    else:
                        support_servant_details = []
                    quest_enemies = await get_quest_enemies(
                        conn,
                        redis,
                        region,
                        stages,
                        rayshift_quest_details[0],
                        rayshift_quest_drops,
                        support_servant_details,
                        lang,
                        include_spawn_bonus_enemy=True,
                    )
                nice_quest_drops = [
                    get_nice_drop(drop)
                    for drop in rayshift_quest_drops
                    if drop.stage == -1
                    and drop.deckType == DeckType.ENEMY
                    and drop.deckId == -1
                ]
                db_data.nice.enemyHash = rayshift_quest_hash
                db_data.nice.dropsFromAllHashes = questHash is None

    set_ai_npc_data(quest_enemies.ai_npcs)
    set_follower_data(quest_enemies.followers)

    waveStartMovies: dict[int, list[NiceStageStartMovie]] = defaultdict(list)
    if (
        "waveStartMovie" in db_data.raw.mstQuestPhase.script
        and "movieWave" in db_data.raw.mstQuestPhase.script
    ):
        for movie_name, wave in zip(
            db_data.raw.mstQuestPhase.script["waveStartMovie"],
            db_data.raw.mstQuestPhase.script["movieWave"],
            strict=False,
        ):
            waveStartMovies[wave].append(
                NiceStageStartMovie(
                    waveStartMovie=fmt_url(
                        AssetURL.movie,
                        base_url=settings.asset_url,
                        region=region,
                        item_id=movie_name.removesuffix(".usm"),
                    ),
                )
            )

    new_nice_stages = [
        get_nice_stage(
            region,
            stage,
            enemies,
            db_data.raw.mstBgm,
            db_data.raw.mstBattleBg,
            waveStartMovies,
            stage_cutins,
            lang,
        )
        for stage, enemies in zip(stages, quest_enemies.enemy_waves, strict=False)
    ]

    db_data.nice.stages = new_nice_stages
    db_data.nice.drops = nice_quest_drops

    if save_stages_cache:
        cache_data = RayshiftRedisData(
            quest_drops=nice_quest_drops,
            stages=new_nice_stages,
            ai_npcs=quest_enemies.ai_npcs,
            followers=quest_enemies.followers,
            quest_select=questSelectScript,
            quest_hash=db_data.nice.enemyHash,
            all_hashes=all_rayshift_hashes,
        )

        TTL_SCALE = 6
        quest_has_many_runs = (
            cache_data.quest_drops
            and cache_data.quest_drops[0].runs > settings.quest_heavy_cache_threshold
        )

        if quest_already_closed:
            ttl = None
        elif quest_has_many_runs:
            ttl = settings.quest_cache_length * TTL_SCALE
        elif (
            0
            < current_time - db_data.nice.openedAt
            < settings.quest_cache_length * TTL_SCALE
        ):
            ttl = max((current_time - db_data.nice.openedAt) // TTL_SCALE, 150)
        else:
            ttl = settings.quest_cache_length

        await set_stages_cache(
            redis=redis,
            data=cache_data,
            region=region,
            quest_id=quest_id,
            phase=phase,
            lang=lang,
            hash_=questHash,
            ttl=ttl,
        )

    return db_data.nice
