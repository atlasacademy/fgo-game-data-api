from typing import Any, Union

from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import (
    CLASS_NAME,
    COND_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
)
from ...schemas.nice import NiceQuest, NiceQuestPhase, NiceQuestRelease, NiceStage
from ...schemas.raw import MstQuestRelease, MstStage, QuestEntity, QuestPhaseEntity
from .. import raw
from ..utils import get_traits_list
from .bgm import get_nice_bgm
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


def get_nice_stage(region: Region, raw_stage: MstStage) -> NiceStage:
    return NiceStage(bgm=get_nice_bgm(region, raw_stage.bgmId))


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
        "noticeAt": raw_quest.mstQuest.noticeAt,
        "openedAt": raw_quest.mstQuest.openedAt,
        "closedAt": raw_quest.mstQuest.closedAt,
    }
    return nice_data


def get_nice_quest_alone(conn: Connection, region: Region, quest_id: int) -> NiceQuest:
    return NiceQuest.parse_obj(
        get_nice_quest(region, raw.get_quest_entity(conn, quest_id))
    )


def get_nice_quest_phase(
    conn: Connection, region: Region, quest_id: int, phase: int
) -> NiceQuestPhase:
    raw_quest = raw.get_quest_phase_entity(conn, quest_id, phase)
    nice_data = get_nice_quest(region, raw_quest)
    nice_data.update(
        {
            "phase": raw_quest.mstQuestPhase.phase,
            "className": [
                CLASS_NAME[class_id] for class_id in raw_quest.mstQuestPhase.classIds
            ],
            "individuality": get_traits_list(raw_quest.mstQuestPhase.individuality),
            "qp": raw_quest.mstQuestPhase.qp,
            "exp": raw_quest.mstQuestPhase.playerExp,
            "bond": raw_quest.mstQuestPhase.friendshipExp,
            "stages": [get_nice_stage(region, stage) for stage in raw_quest.mstStage],
        }
    )
    return NiceQuestPhase.parse_obj(nice_data)
