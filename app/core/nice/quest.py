from collections import defaultdict
from typing import Any, Optional, Union

from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...db.helpers import war
from ...rayshift.quest import get_quest_detail
from ...schemas.common import Language, NiceQuestScript, Region
from ...schemas.enums import CLASS_NAME
from ...schemas.gameenums import (
    COND_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
)
from ...schemas.nice import (
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
    MstQuestMessage,
    MstQuestRelease,
    MstStage,
    MstWar,
    QuestEntity,
    QuestPhaseEntity,
    ScriptFile,
)
from .. import raw
from ..utils import get_traits_list, get_translation
from .base_script import get_script_url
from .bgm import get_nice_bgm
from .enemy import get_quest_enemies
from .follower import get_nice_support_servants
from .gift import get_nice_gift
from .item import get_nice_item_amount


settings = Settings()


def get_nice_quest_script(region: Region, script_file_name: str) -> NiceQuestScript:
    return NiceQuestScript(
        scriptId=script_file_name, script=get_script_url(region, script_file_name)
    )


def get_nice_quest_release(
    raw_quest_release: MstQuestRelease,
    closed_messages: list[MstClosedMessage],
) -> NiceQuestRelease:
    closed_message = next(
        message
        for message in closed_messages
        if message.id == raw_quest_release.closedMessageId
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
        enemies=enemies,
    )


def get_nice_all_scripts(
    region: Region, scripts: list[ScriptFile]
) -> list[NiceQuestPhaseScript]:
    phase_scripts: dict[int, list[NiceQuestScript]] = defaultdict(list)
    for script in sorted(scripts, key=lambda s: s.scriptFileName):
        phase_scripts[script.phase].append(
            get_nice_quest_script(region, script.scriptFileName)
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
) -> dict[str, Any]:
    if not mstWar:
        mstWar = await war.get_war_from_spot(conn, raw_quest.mstQuest.spotId)

    nice_data: dict[str, Any] = {
        "id": raw_quest.mstQuest.id,
        "name": get_translation(lang, raw_quest.mstQuest.name),
        "type": QUEST_TYPE_NAME[raw_quest.mstQuest.type],
        "consumeType": QUEST_CONSUME_TYPE_NAME[raw_quest.mstQuest.consumeType],
        "consumeItem": [
            nice_item_amount
            for consumeItem in raw_quest.mstQuestConsumeItem
            for nice_item_amount in await get_nice_item_amount(
                conn, region, consumeItem.itemIds, consumeItem.nums, lang
            )
        ],
        "consume": raw_quest.mstQuest.actConsume,
        "spotId": raw_quest.mstQuest.spotId,
        "warId": mstWar.id,
        "warLongName": get_translation(lang, mstWar.longName),
        "chapterId": raw_quest.mstQuest.chapterId,
        "chapterSubId": raw_quest.mstQuest.chapterSubId,
        "chapterSubStr": raw_quest.mstQuest.chapterSubStr,
        "gifts": [get_nice_gift(gift) for gift in raw_quest.mstGift],
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


async def get_nice_quest_phase(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> NiceQuestPhase:
    raw_quest = await raw.get_quest_phase_entity(conn, quest_id, phase)
    nice_data = await get_nice_quest(conn, region, raw_quest, lang)

    stages = sorted(raw_quest.mstStage, key=lambda stage: stage.wave)

    quest_enemies: list[list[QuestEnemy]] = [[]] * len(raw_quest.mstStage)
    if stages:
        quest_detail = await get_quest_detail(conn, region, quest_id, phase)
        if quest_detail:
            quest_enemies = await get_quest_enemies(
                conn, redis, region, quest_detail, lang
            )

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
        "className": [
            CLASS_NAME[class_id] for class_id in raw_quest.mstQuestPhase.classIds
        ],
        "individuality": get_traits_list(raw_quest.mstQuestPhase.individuality),
        "qp": raw_quest.mstQuestPhase.qp,
        "exp": raw_quest.mstQuestPhase.playerExp,
        "bond": raw_quest.mstQuestPhase.friendshipExp,
        "battleBgId": raw_quest.mstQuestPhase.battleBgId,
        "scripts": [
            get_nice_quest_script(region, script)
            for script in sorted(raw_quest.scripts)
        ],
        "messages": [
            get_nice_quest_message(message)
            for message in sorted(
                raw_quest.mstQuestMessage, key=lambda script: script.idx
            )
        ],
        "supportServants": support_servants,
        "stages": [
            get_nice_stage(region, stage, enemies, raw_quest.mstBgm)
            for stage, enemies in zip(stages, quest_enemies)
        ],
    }

    if raw_quest.mstQuestPhaseDetail:
        nice_data["spotId"] = raw_quest.mstQuestPhaseDetail.spotId
        detail_mstWar = await war.get_war_from_spot(
            conn, raw_quest.mstQuestPhaseDetail.spotId
        )
        nice_data["warId"] = detail_mstWar.id
        nice_data["warLongName"] = get_translation(lang, detail_mstWar.longName)
        nice_data["consumeType"] = QUEST_CONSUME_TYPE_NAME[
            raw_quest.mstQuestPhaseDetail.consumeType
        ]
        nice_data["consume"] = raw_quest.mstQuestPhaseDetail.actConsume

    return NiceQuestPhase.parse_obj(nice_data)
