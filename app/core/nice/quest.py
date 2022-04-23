import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional, Union

from fastapi_cache.decorator import cache
from redis.asyncio import Redis  # type: ignore
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...db.helpers import war
from ...db.helpers.quest import get_questSelect_container
from ...db.helpers.rayshift import get_rayshift_drops
from ...rayshift.quest import get_quest_detail
from ...redis.helpers.quest import RayshiftRedisData, get_stages_cache, set_stages_cache
from ...schemas.common import Language, Region, ScriptLink
from ...schemas.enums import CLASS_NAME
from ...schemas.gameenums import (
    COND_TYPE_NAME,
    QUEST_AFTER_CLEAR_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    Quest_FLAG_NAME,
)
from ...schemas.nice import (
    DeckType,
    EnemyDrop,
    NiceQuest,
    NiceQuestMessage,
    NiceQuestPhase,
    NiceQuestPhaseScript,
    NiceQuestRelease,
    NiceStage,
    QuestEnemy,
    SupportServant,
)
from ...schemas.raw import (
    MstBgm,
    MstClosedMessage,
    MstGift,
    MstQuestMessage,
    MstQuestRelease,
    MstSpot,
    MstStage,
    MstWar,
    QuestEntity,
    QuestPhaseEntity,
    ScriptFile,
)
from .. import raw
from ..utils import get_flags, get_traits_list, get_translation
from .base_script import get_nice_script_link
from .bgm import get_nice_bgm
from .enemy import get_nice_drop, get_quest_enemies
from .follower import get_nice_support_servants
from .gift import get_nice_gift
from .item import get_nice_item_amount_db


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


def get_nice_quest_message(message: MstQuestMessage) -> NiceQuestMessage:
    return NiceQuestMessage(
        idx=message.idx,
        message=message.message,
        condType=COND_TYPE_NAME[message.condType],
        targetId=message.targetId,
        targetNum=message.targetNum,
    )


def get_nice_stage(
    region: Region, raw_stage: MstStage, enemies: list[QuestEnemy], bgms: list[MstBgm]
) -> NiceStage:
    bgm = get_nice_bgm(region, next(bgm for bgm in bgms if bgm.id == raw_stage.bgmId))
    return NiceStage(
        wave=raw_stage.wave,
        bgm=bgm,
        fieldAis=raw_stage.script.get("aiFieldIds", []),
        call=raw_stage.script.get("call", []),
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


async def get_nice_quest(
    conn: AsyncConnection,
    region: Region,
    raw_quest: Union[QuestEntity, QuestPhaseEntity],
    lang: Language,
    mstWar: Optional[MstWar] = None,
    mstSpot: Optional[MstSpot] = None,
) -> dict[str, Any]:
    if not mstWar:
        mstWar = await war.get_war_from_spot(conn, raw_quest.mstQuest.spotId)
    if not mstSpot:
        mstSpot = await war.get_spot_from_id(conn, raw_quest.mstQuest.spotId)

    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in raw_quest.mstGift:
        gift_maps[gift.id].append(gift)

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
            for nice_item_amount in await get_nice_item_amount_db(
                conn, region, consumeItem.itemIds, consumeItem.nums, lang
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
        "gifts": [
            get_nice_gift(region, gift, raw_quest.mstGiftAdd, gift_maps)
            for gift in raw_quest.mstGift
            if gift.id == raw_quest.mstQuest.giftId
        ],
        "releaseConditions": [
            get_nice_quest_release(release, raw_quest.mstClosedMessage)
            for release in raw_quest.mstQuestRelease
        ],
        "phases": sorted(raw_quest.phases),
        "phasesWithEnemies": sorted(raw_quest.phasesWithEnemies),
        "phasesNoBattle": sorted(raw_quest.phasesNoBattle),
        "phaseScripts": get_nice_all_scripts(region, raw_quest.allScripts),
        "noticeAt": raw_quest.mstQuest.noticeAt,
        "openedAt": raw_quest.mstQuest.openedAt,
        "closedAt": raw_quest.mstQuest.closedAt,
    }
    return nice_data


async def get_nice_quest_alone(
    conn: AsyncConnection, region: Region, quest_id: int, lang: Language
) -> NiceQuest:
    raw_quest = await raw.get_quest_entity(conn, quest_id)
    return NiceQuest.parse_obj(await get_nice_quest(conn, region, raw_quest, lang))


@dataclass
class DBQuestPhase:
    raw: QuestPhaseEntity
    nice: NiceQuestPhase


@cache()  # type: ignore
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

    support_servants: list[SupportServant] = []
    if raw_quest.npcFollower:
        support_servants = await get_nice_support_servants(
            conn,
            redis,
            region,
            raw_quest.npcFollower,
            raw_quest.npcFollowerRelease,
            raw_quest.npcSvtFollower,
            raw_quest.npcSvtEquip,
            lang,
        )

    nice_data |= {
        "phase": raw_quest.mstQuestPhase.phase,
        "drops": [],
        "className": [
            CLASS_NAME[class_id] for class_id in raw_quest.mstQuestPhase.classIds
        ],
        "individuality": get_traits_list(raw_quest.mstQuestPhase.individuality),
        "qp": raw_quest.mstQuestPhase.qp,
        "exp": raw_quest.mstQuestPhase.playerExp,
        "bond": raw_quest.mstQuestPhase.friendshipExp,
        "isNpcOnly": raw_quest.mstQuestPhase.isNpcOnly,
        "battleBgId": raw_quest.mstQuestPhase.battleBgId,
        "extraDetail": raw_quest.mstQuestPhase.script,
        "scripts": [
            get_nice_script_link(region, script) for script in sorted(raw_quest.scripts)
        ],
        "messages": [
            get_nice_quest_message(message)
            for message in sorted(
                raw_quest.mstQuestMessage, key=lambda script: script.idx
            )
        ],
        "supportServants": support_servants,
        "stages": [],
    }

    if raw_quest.mstQuestPhaseDetail:
        if raw_quest.mstQuestPhaseDetail.spotId != raw_quest.mstQuest.spotId:
            mstSpot = await war.get_spot_from_id(
                conn, raw_quest.mstQuestPhaseDetail.spotId
            )
            nice_data["spotId"] = raw_quest.mstQuestPhaseDetail.spotId
            nice_data["spotName"] = get_translation(lang, mstSpot.name)
        nice_data["recommendLv"] = (
            raw_quest.mstQuestPhaseDetail.recommendLv or raw_quest.mstQuest.recommendLv
        )
        detail_mstWar = await war.get_war_from_spot(
            conn, raw_quest.mstQuestPhaseDetail.spotId
        )
        nice_data["warId"] = detail_mstWar.id
        nice_data["warLongName"] = get_translation(lang, detail_mstWar.longName)
        nice_data["consumeType"] = QUEST_CONSUME_TYPE_NAME[
            raw_quest.mstQuestPhaseDetail.consumeType
        ]
        nice_data["consume"] = raw_quest.mstQuestPhaseDetail.actConsume

    return DBQuestPhase(raw_quest, NiceQuestPhase.parse_obj(nice_data))


async def get_nice_quest_phase(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> NiceQuestPhase:
    db_data: DBQuestPhase = await get_nice_quest_phase_no_rayshift(
        conn, redis, region, quest_id, phase, lang
    )

    if "questSelect" in db_data.raw.mstQuestPhase.script:
        questSelect: int | None = db_data.raw.mstQuestPhase.script["questSelect"].index(
            quest_id
        )
    else:
        questSelect = None

    rayshift_data = await get_stages_cache(
        redis, region, quest_id, phase, questSelect, lang
    )

    if rayshift_data:
        db_data.nice.stages = rayshift_data.stages
        db_data.nice.drops = rayshift_data.quest_drops
        return db_data.nice

    stages = sorted(db_data.raw.mstStage, key=lambda stage: stage.wave)
    save_stages_cache = True

    nice_quest_drops: list[EnemyDrop] = []
    quest_enemies: list[list[QuestEnemy]] = [[]] * len(db_data.raw.mstStage)
    if stages:
        rayshift_quest_id = quest_id
        if questSelect is None:
            quest_select_owner = await get_questSelect_container(conn, quest_id, phase)
            if quest_select_owner:
                rayshift_quest_id = quest_select_owner.questId
                questSelect = quest_select_owner.script["questSelect"].index(quest_id)
        rayshift_quest_detail = await get_quest_detail(
            conn, region, rayshift_quest_id, phase, questSelect
        )
        rayshift_quest_drops = await get_rayshift_drops(
            conn, rayshift_quest_id, phase, questSelect
        )
        if rayshift_quest_detail:
            quest_enemies = await get_quest_enemies(
                conn,
                redis,
                region,
                stages,
                rayshift_quest_detail,
                rayshift_quest_drops,
                lang,
            )
            nice_quest_drops = [
                get_nice_drop(drop)
                for drop in rayshift_quest_drops
                if drop.stage == -1
                and drop.deckType == DeckType.ENEMY
                and drop.deckId == -1
            ]
        else:
            save_stages_cache = False

    new_nice_stages = [
        get_nice_stage(region, stage, enemies, db_data.raw.mstBgm)
        for stage, enemies in zip(stages, quest_enemies)
    ]
    db_data.nice.stages = new_nice_stages
    db_data.nice.drops = nice_quest_drops
    if save_stages_cache:
        cache_data = RayshiftRedisData(
            quest_drops=nice_quest_drops, stages=new_nice_stages
        )
        long_ttl = time.time() > db_data.nice.closedAt
        await set_stages_cache(
            redis, cache_data, region, quest_id, phase, questSelect, lang, long_ttl
        )

    return db_data.nice
