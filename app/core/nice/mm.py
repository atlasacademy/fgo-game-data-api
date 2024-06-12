from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from ...core.basic import get_basic_quest_from_raw
from ...schemas.common import Language, Region
from ...schemas.nice import NiceCompleteMission, NiceMasterMission
from ...schemas.raw import (
    MasterMissionEntity,
    MstBgm,
    MstCompleteMission,
    MstMasterMission,
)
from .. import raw
from .bgm import get_nice_bgm
from .event.mission import get_nice_missions
from .gift import GiftData, get_gift_map, get_nice_gifts


def get_nice_complete_mission(
    region: Region,
    mission: MstCompleteMission,
    gift_data: GiftData,
    bgm: MstBgm | None,
    lang: Language,
) -> NiceCompleteMission:
    return NiceCompleteMission(
        objectId=mission.objectId,
        presentMessageId=mission.presentMessageId,
        gifts=get_nice_gifts(region, mission.giftId, gift_data),
        bgm=get_nice_bgm(region, bgm, lang),
    )


def get_nice_master_mission_from_raw(
    region: Region, raw_mm: MasterMissionEntity, lang: Language
) -> NiceMasterMission:
    gift_map = get_gift_map(raw_mm.mstGift)
    gift_data = GiftData(raw_mm.mstGiftAdd, gift_map)

    missions = get_nice_missions(
        region,
        raw_mm.mstEventMission,
        raw_mm.mstEventMissionCondition,
        raw_mm.mstEventMissionConditionDetail,
        gift_data,
    )
    return NiceMasterMission(
        id=raw_mm.mstMasterMission.id,
        startedAt=raw_mm.mstMasterMission.startedAt,
        endedAt=raw_mm.mstMasterMission.endedAt,
        closedAt=raw_mm.mstMasterMission.closedAt,
        missions=missions,
        completeMission=(
            get_nice_complete_mission(
                region, raw_mm.mstCompleteMission, gift_data, raw_mm.mstBgm, lang
            )
            if raw_mm.mstCompleteMission
            else None
        ),
        quests=[
            get_basic_quest_from_raw(mstQuest, lang) for mstQuest in raw_mm.mstQuest
        ],
    )


async def get_nice_master_mission(
    conn: AsyncConnection,
    region: Region,
    mm_id: int,
    lang: Language,
    mstMasterMission: Optional[MstMasterMission] = None,
) -> NiceMasterMission:
    raw_mm = await raw.get_master_mission_entity(conn, mm_id, mstMasterMission)
    return get_nice_master_mission_from_raw(region, raw_mm, lang)


async def get_all_nice_mms(
    conn: AsyncConnection,
    region: Region,
    mstMasterMissions: list[MstMasterMission],
    lang: Language,
) -> list[NiceMasterMission]:  # pragma: no cover
    return [
        await get_nice_master_mission(conn, region, mm.id, lang, mm)
        for mm in mstMasterMissions
    ]
