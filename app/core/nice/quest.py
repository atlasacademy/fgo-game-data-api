from typing import Any, Optional, Union

from sqlalchemy.engine import Connection

from ...config import Settings
from ...db.helpers import war
from ...rayshift.quest import get_quest_detail
from ...schemas.common import Language, Region
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
    NiceQuestRelease,
    NiceStage,
    QuestEnemy,
)
from ...schemas.raw import (
    MstBgm,
    MstClosedMessage,
    MstQuestMessage,
    MstQuestRelease,
    MstStage,
    QuestEntity,
    QuestPhaseEntity,
)
from .. import raw
from ..utils import get_traits_list
from .bgm import get_nice_bgm
from .enemy import get_quest_enemies
from .gift import get_nice_gift
from .item import get_nice_item_amount
from .script import get_nice_quest_script


settings = Settings()


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


def get_nice_quest(
    conn: Connection,
    region: Region,
    raw_quest: Union[QuestEntity, QuestPhaseEntity],
    war_id: Optional[int] = None,
) -> dict[str, Any]:
    if war_id:
        warId = war_id
    else:
        warId = war.get_war_from_spot(conn, raw_quest.mstQuest.spotId)

    nice_data: dict[str, Any] = {
        "id": raw_quest.mstQuest.id,
        "name": raw_quest.mstQuest.name,
        "type": QUEST_TYPE_NAME[raw_quest.mstQuest.type],
        "consumeType": QUEST_CONSUME_TYPE_NAME[raw_quest.mstQuest.consumeType],
        "consumeItem": [
            nice_item_amount
            for consumeItem in raw_quest.mstQuestConsumeItem
            for nice_item_amount in get_nice_item_amount(
                region, consumeItem.itemIds, consumeItem.nums
            )
        ],
        "consume": raw_quest.mstQuest.actConsume,
        "spotId": raw_quest.mstQuest.spotId,
        "warId": warId,
        "gifts": [get_nice_gift(gift) for gift in raw_quest.mstGift],
        "releaseConditions": [
            get_nice_quest_release(release, raw_quest.mstClosedMessage)
            for release in raw_quest.mstQuestRelease
        ],
        "phases": raw_quest.phases,
        "phasesWithEnemies": raw_quest.phasesWithEnemies,
        "phasesNoBattle": raw_quest.phasesNoBattle,
        "noticeAt": raw_quest.mstQuest.noticeAt,
        "openedAt": raw_quest.mstQuest.openedAt,
        "closedAt": raw_quest.mstQuest.closedAt,
    }
    return nice_data


def get_nice_quest_alone(conn: Connection, region: Region, quest_id: int) -> NiceQuest:
    return NiceQuest.parse_obj(
        get_nice_quest(conn, region, raw.get_quest_entity(conn, quest_id))
    )


async def get_nice_quest_phase(
    conn: Connection,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> NiceQuestPhase:
    raw_quest = raw.get_quest_phase_entity(conn, quest_id, phase)
    nice_data = get_nice_quest(conn, region, raw_quest)

    stages = sorted(raw_quest.mstStage, key=lambda stage: stage.wave)

    quest_enemies: list[list[QuestEnemy]] = [[]] * len(raw_quest.mstStage)
    if stages:
        quest_detail = await get_quest_detail(conn, region, quest_id, phase)
        if quest_detail:
            quest_enemies = get_quest_enemies(conn, region, quest_detail, lang)

    nice_data |= {
        "phase": raw_quest.mstQuestPhase.phase,
        "className": [
            CLASS_NAME[class_id] for class_id in raw_quest.mstQuestPhase.classIds
        ],
        "individuality": get_traits_list(raw_quest.mstQuestPhase.individuality),
        "qp": raw_quest.mstQuestPhase.qp,
        "exp": raw_quest.mstQuestPhase.playerExp,
        "bond": raw_quest.mstQuestPhase.friendshipExp,
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
        "stages": [
            get_nice_stage(region, stage, enemies, raw_quest.mstBgm)
            for stage, enemies in zip(stages, quest_enemies)
        ],
    }

    if raw_quest.mstQuestPhaseDetail:
        nice_data["spotId"] = raw_quest.mstQuestPhaseDetail.spotId
        nice_data["warId"] = war.get_war_from_spot(
            conn, raw_quest.mstQuestPhaseDetail.spotId
        )
        nice_data["consumeType"] = QUEST_CONSUME_TYPE_NAME[
            raw_quest.mstQuestPhaseDetail.consumeType
        ]
        nice_data["consume"] = raw_quest.mstQuestPhaseDetail.actConsume

    return NiceQuestPhase.parse_obj(nice_data)
