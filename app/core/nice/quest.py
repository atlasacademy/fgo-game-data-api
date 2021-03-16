from typing import Any, Union

from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.gamedata import masters
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
    NiceQuestPhase,
    NiceQuestRelease,
    NiceStage,
    QuestEnemy,
)
from ...schemas.raw import MstQuestRelease, MstStage, QuestEntity, QuestPhaseEntity
from .. import raw
from ..utils import get_traits_list
from .bgm import get_nice_bgm
from .enemy import get_quest_enemies
from .gift import get_nice_gift
from .item import get_nice_item_amount


settings = Settings()


def get_nice_quest_release(
    region: Region, raw_quest_release: MstQuestRelease
) -> NiceQuestRelease:
    return NiceQuestRelease(
        type=COND_TYPE_NAME[raw_quest_release.type],
        targetId=raw_quest_release.targetId,
        value=raw_quest_release.value,
        closedMessage=masters[region].mstClosedMessageId.get(
            raw_quest_release.closedMessageId, ""
        ),
    )


def get_nice_stage(
    region: Region, raw_stage: MstStage, enemies: list[QuestEnemy]
) -> NiceStage:
    return NiceStage(
        wave=raw_stage.wave,
        bgm=get_nice_bgm(region, raw_stage.bgmId),
        fieldAis=raw_stage.script.get("aiFieldIds", []),
        enemies=enemies,
    )


def get_nice_quest(
    region: Region, raw_quest: Union[QuestEntity, QuestPhaseEntity]
) -> dict[str, Any]:
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
        "warId": masters[region].spotToWarId[raw_quest.mstQuest.spotId],
        "gifts": get_nice_gift(region, raw_quest.mstQuest.giftId),
        "releaseConditions": [
            get_nice_quest_release(region, release)
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
        get_nice_quest(region, raw.get_quest_entity(conn, quest_id))
    )


async def get_nice_quest_phase(
    conn: Connection,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> NiceQuestPhase:
    raw_quest = raw.get_quest_phase_entity(conn, quest_id, phase)
    nice_data = get_nice_quest(region, raw_quest)

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
        "stages": [
            get_nice_stage(region, stage, enemies)
            for stage, enemies in zip(stages, quest_enemies)
        ],
    }

    if raw_quest.mstQuestPhaseDetail:
        nice_data["spotId"] = raw_quest.mstQuestPhaseDetail.spotId
        nice_data["consumeType"] = QUEST_CONSUME_TYPE_NAME[
            raw_quest.mstQuestPhaseDetail.consumeType
        ]
        nice_data["consume"] = raw_quest.mstQuestPhaseDetail.actConsume

    return NiceQuestPhase.parse_obj(nice_data)
