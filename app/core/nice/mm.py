from collections import defaultdict
from typing import Optional

from sqlalchemy.engine import Connection

from ...schemas.nice import NiceMasterMission
from ...schemas.raw import MasterMissionEntity, MstGift, MstMasterMission
from .. import raw
from .event import get_nice_missions


def get_nice_master_mission_from_raw(raw_mm: MasterMissionEntity) -> NiceMasterMission:
    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in raw_mm.mstGift:
        gift_maps[gift.id].append(gift)

    missions = get_nice_missions(
        raw_mm.mstEventMission,
        raw_mm.mstEventMissionCondition,
        raw_mm.mstEventMissionConditionDetail,
        gift_maps,
    )
    return NiceMasterMission(
        id=raw_mm.mstMasterMission.id,
        startedAt=raw_mm.mstMasterMission.startedAt,
        endedAt=raw_mm.mstMasterMission.endedAt,
        closedAt=raw_mm.mstMasterMission.closedAt,
        missions=missions,
    )


def get_nice_master_mission(
    conn: Connection, mm_id: int, mstMasterMission: Optional[MstMasterMission] = None
) -> NiceMasterMission:
    raw_mm = raw.get_master_mission_entity(conn, mm_id, mstMasterMission)
    return get_nice_master_mission_from_raw(raw_mm)


def get_all_nice_mms(
    conn: Connection, mstMasterMissions: list[MstMasterMission]
) -> list[NiceMasterMission]:  # pragma: no cover
    return [get_nice_master_mission(conn, mm.id, mm) for mm in mstMasterMissions]
