from typing import Iterable, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import (
    mstBoxGacha,
    mstBoxGachaBase,
    mstEvent,
    mstEventMission,
    mstEventMissionCondition,
    mstEventMissionConditionDetail,
    mstEventPointBuff,
    mstEventReward,
    mstEventRewardSet,
    mstEventTower,
    mstEventTowerReward,
    mstShop,
)
from ...schemas.raw import (
    MstBoxGacha,
    MstBoxGachaBase,
    MstEvent,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventPointBuff,
    MstEventReward,
    MstEventRewardSet,
    MstEventTower,
    MstEventTowerReward,
    MstShop,
)


def get_mstEvent(conn: Connection, event_id: int) -> Optional[MstEvent]:
    mstEvent_stmt = select(mstEvent).where(mstEvent.c.id == event_id)
    event = conn.execute(mstEvent_stmt).fetchone()
    if event:
        return MstEvent.from_orm(event)

    return None


def get_mstShop(conn: Connection, event_id: int) -> list[MstShop]:
    mstShop_stmt = (
        select(mstShop).where(mstShop.c.eventId == event_id).order_by(mstShop.c.id)
    )
    return [MstShop.from_orm(shop) for shop in conn.execute(mstShop_stmt).fetchall()]


def get_mstShop_by_id(conn: Connection, shop_id: int) -> MstShop:
    mstShop_stmt = select(mstShop).where(mstShop.c.id == shop_id)
    return MstShop.from_orm(conn.execute(mstShop_stmt).fetchone())


def get_mstEventReward(conn: Connection, event_id: int) -> list[MstEventReward]:
    mstEventReward_stmt = select(mstEventReward).where(
        mstEventReward.c.eventId == event_id
    )
    return [
        MstEventReward.from_orm(reward)
        for reward in conn.execute(mstEventReward_stmt).fetchall()
    ]


def get_mstEventRewardSet(conn: Connection, event_id: int) -> list[MstEventRewardSet]:
    mstEventRewardSet_stmt = select(mstEventRewardSet).where(
        mstEventRewardSet.c.eventId == event_id
    )
    return [
        MstEventRewardSet.from_orm(reward_set)
        for reward_set in conn.execute(mstEventRewardSet_stmt).fetchall()
    ]


def get_mstEventPointBuff(conn: Connection, event_id: int) -> list[MstEventPointBuff]:
    mstEventPointBuff_stmt = (
        select(mstEventPointBuff)
        .where(mstEventPointBuff.c.eventId == event_id)
        .order_by(mstEventPointBuff.c.id)
    )
    return [
        MstEventPointBuff.from_orm(pointBuff)
        for pointBuff in conn.execute(mstEventPointBuff_stmt).fetchall()
    ]


def get_mstEventMission(conn: Connection, target_id: int) -> list[MstEventMission]:
    mstEventMission_stmt = (
        select(mstEventMission)
        .where(mstEventMission.c.missionTargetId == target_id)
        .order_by(mstEventMission.c.id)
    )
    return [
        MstEventMission.from_orm(mission)
        for mission in conn.execute(mstEventMission_stmt).fetchall()
    ]


def get_mstEventMissionCondition(
    conn: Connection, mission_ids: Iterable[int]
) -> list[MstEventMissionCondition]:
    mstEventMissionCondition_stmt = (
        select(mstEventMissionCondition)
        .where(mstEventMissionCondition.c.missionId.in_(mission_ids))
        .order_by(mstEventMissionCondition.c.id)
    )
    return [
        MstEventMissionCondition.from_orm(missionCond)
        for missionCond in conn.execute(mstEventMissionCondition_stmt).fetchall()
    ]


def get_mstEventMissionConditionDetail(
    conn: Connection, cond_detail_ids: Iterable[int]
) -> list[MstEventMissionConditionDetail]:
    mstEventMissionConditionDetail_stmt = (
        select(mstEventMissionConditionDetail)
        .where(mstEventMissionConditionDetail.c.id.in_(cond_detail_ids))
        .order_by(mstEventMissionConditionDetail.c.id)
    )
    return [
        MstEventMissionConditionDetail.from_orm(condDetail)
        for condDetail in conn.execute(mstEventMissionConditionDetail_stmt).fetchall()
    ]


def get_mstEventTower(conn: Connection, event_id: int) -> list[MstEventTower]:
    mstEventTower_stmt = (
        select(mstEventTower)
        .where(mstEventTower.c.eventId == event_id)
        .order_by(mstEventTower.c.towerId)
    )
    return [
        MstEventTower.from_orm(tower)
        for tower in conn.execute(mstEventTower_stmt).fetchall()
    ]


def get_mstEventTowerReward(
    conn: Connection, event_id: int
) -> list[MstEventTowerReward]:
    mstEventTowerReward_stmt = (
        select(mstEventTowerReward)
        .where(mstEventTowerReward.c.eventId == event_id)
        .order_by(mstEventTowerReward.c.towerId, mstEventTowerReward.c.floor)
    )
    return [
        MstEventTowerReward.from_orm(tower_reward)
        for tower_reward in conn.execute(mstEventTowerReward_stmt).fetchall()
    ]


def get_mstBoxGacha(conn: Connection, event_id: int) -> list[MstBoxGacha]:
    mstBoxGacha_stmt = (
        select(mstBoxGacha)
        .where(mstBoxGacha.c.eventId == event_id)
        .order_by(mstBoxGacha.c.id)
    )
    return [
        MstBoxGacha.from_orm(box_gacha)
        for box_gacha in conn.execute(mstBoxGacha_stmt).fetchall()
    ]


def get_mstBoxGachaBase(
    conn: Connection, box_gacha_base_ids: Iterable[int]
) -> list[MstBoxGachaBase]:
    mstBoxGachaBase_stmt = (
        select(mstBoxGachaBase)
        .where(mstBoxGachaBase.c.id.in_(box_gacha_base_ids))
        .order_by(mstBoxGachaBase.c.id, mstBoxGachaBase.c.no)
    )
    return [
        MstBoxGachaBase.from_orm(box_gacha_base)
        for box_gacha_base in conn.execute(mstBoxGachaBase_stmt).fetchall()
    ]
