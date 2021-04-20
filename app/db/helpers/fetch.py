# pylint: disable=unsubscriptable-object
from typing import Any, Iterable, Optional, Type, TypeVar, Union

from sqlalchemy import Column, Table
from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from app.schemas.base import BaseModelORJson

from ...models.raw import (
    mstBgm,
    mstBoxGacha,
    mstCombineCostume,
    mstCombineLimit,
    mstCombineMaterial,
    mstCombineSkill,
    mstCommandCode,
    mstCommandCodeComment,
    mstCommandCodeSkill,
    mstConstant,
    mstCv,
    mstEquip,
    mstEquipExp,
    mstEquipSkill,
    mstEvent,
    mstEventMission,
    mstEventMissionCondition,
    mstEventMissionConditionDetail,
    mstEventPointBuff,
    mstEventReward,
    mstEventRewardSet,
    mstEventTower,
    mstFriendship,
    mstGift,
    mstIllustrator,
    mstMap,
    mstShop,
    mstShopScript,
    mstSpot,
    mstSvt,
    mstSvtCard,
    mstSvtChange,
    mstSvtComment,
    mstSvtCostume,
    mstSvtExp,
    mstSvtGroup,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtVoiceRelation,
    mstVoice,
    mstWar,
    mstWarAdd,
)
from ...schemas.raw import (
    MstBgm,
    MstBoxGacha,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineMaterial,
    MstCombineSkill,
    MstCommandCode,
    MstCommandCodeComment,
    MstCommandCodeSkill,
    MstConstant,
    MstCv,
    MstEquip,
    MstEquipExp,
    MstEquipSkill,
    MstEvent,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventPointBuff,
    MstEventReward,
    MstEventRewardSet,
    MstEventTower,
    MstFriendship,
    MstGift,
    MstIllustrator,
    MstMap,
    MstShop,
    MstShopScript,
    MstSpot,
    MstSvt,
    MstSvtCard,
    MstSvtChange,
    MstSvtComment,
    MstSvtCostume,
    MstSvtExp,
    MstSvtGroup,
    MstSvtLimit,
    MstSvtLimitAdd,
    MstSvtVoiceRelation,
    MstVoice,
    MstWar,
    MstWarAdd,
)


schema_map_fetchone: dict[Type[BaseModelORJson], tuple[Table, Column[Any]]] = {
    MstSvt: (mstSvt, mstSvt.c.id),
    MstCv: (mstCv, mstCv.c.id),
    MstIllustrator: (mstIllustrator, mstIllustrator.c.id),
    MstCommandCode: (mstCommandCode, mstCommandCode.c.id),
    MstWar: (mstWar, mstWar.c.id),
    MstEquip: (mstEquip, mstEquip.c.id),
    MstEvent: (mstEvent, mstEvent.c.id),
    MstConstant: (mstConstant, mstConstant.c.name),
}

Tfetchone = TypeVar("Tfetchone", bound=BaseModelORJson)


def get_one(
    conn: Connection, schema: Type[Tfetchone], where_id: Union[int, str]
) -> Optional[Tfetchone]:
    table, where_col = schema_map_fetchone[schema]
    stmt = select(table).where(where_col == where_id)
    entity_db = conn.execute(stmt).fetchone()
    if entity_db:
        return schema.from_orm(entity_db)

    return None


schema_table_fetch_all: dict[
    Type[BaseModelORJson], tuple[Table, Column[Any], Column[Any]]
] = {
    MstSvtCard: (mstSvtCard, mstSvtCard.c.svtId, mstSvtCard.c.cardId),
    MstSvtLimit: (mstSvtLimit, mstSvtLimit.c.svtId, mstSvtLimit.c.limitCount),
    MstCombineSkill: (mstCombineSkill, mstCombineSkill.c.id, mstCombineSkill.c.skillLv),
    MstSvtChange: (mstSvtChange, mstSvtChange.c.svtId, mstSvtChange.c.priority),
    MstSvtCostume: (mstSvtCostume, mstSvtCostume.c.svtId, mstSvtCostume.c.id),
    MstSvtExp: (mstSvtExp, mstSvtExp.c.type, mstSvtExp.c.lv),
    MstFriendship: (mstFriendship, mstFriendship.c.id, mstFriendship.c.rank),
    MstSvtComment: (mstSvtComment, mstSvtComment.c.svtId, mstSvtComment.c.id),
    MstCommandCodeComment: (
        mstCommandCodeComment,
        mstCommandCodeComment.c.commandCodeId,
        mstCommandCodeComment.c.comment,
    ),
    MstCommandCodeSkill: (
        mstCommandCodeSkill,
        mstCommandCodeSkill.c.commandCodeId,
        mstCommandCodeSkill.c.num,
    ),
    MstCombineLimit: (
        mstCombineLimit,
        mstCombineLimit.c.id,
        mstCombineLimit.c.svtLimit,
    ),
    MstCombineCostume: (
        mstCombineCostume,
        mstCombineCostume.c.svtId,
        mstCombineCostume.c.costumeId,
    ),
    MstSvtLimitAdd: (
        mstSvtLimitAdd,
        mstSvtLimitAdd.c.svtId,
        mstSvtLimitAdd.c.limitCount,
    ),
    MstMap: (mstMap, mstMap.c.warId, mstMap.c.id),
    MstWarAdd: (mstWarAdd, mstWarAdd.c.warId, mstWarAdd.c.priority),
    MstEquipSkill: (mstEquipSkill, mstEquipSkill.c.equipId, mstEquipSkill.c.num),
    MstEquipExp: (mstEquipExp, mstEquipExp.c.equipId, mstEquipExp.c.lv),
    MstEventMission: (
        mstEventMission,
        mstEventMission.c.missionTargetId,
        mstEventMission.c.id,
    ),
    MstShop: (mstShop, mstShop.c.eventId, mstShop.c.id),
    MstEventReward: (mstEventReward, mstEventReward.c.eventId, mstEventReward.c.point),
    MstEventRewardSet: (
        mstEventRewardSet,
        mstEventRewardSet.c.eventId,
        mstEventRewardSet.c.id,
    ),
    MstEventPointBuff: (
        mstEventPointBuff,
        mstEventPointBuff.c.eventId,
        mstEventPointBuff.c.id,
    ),
    MstEventTower: (mstEventTower, mstEventTower.c.eventId, mstEventTower.c.towerId),
    MstBoxGacha: (mstBoxGacha, mstBoxGacha.c.eventId, mstBoxGacha.c.id),
    MstCombineMaterial: (
        mstCombineMaterial,
        mstCombineMaterial.c.id,
        mstCombineMaterial.c.lv,
    ),
}

TFetchAll = TypeVar("TFetchAll", bound=BaseModelORJson)


def get_all(
    conn: Connection, schema: Type[TFetchAll], where_id: int
) -> list[TFetchAll]:
    table, where_col, order_col = schema_table_fetch_all[schema]
    stmt = select(table).where(where_col == where_id).order_by(order_col)
    return [schema.from_orm(db_row) for db_row in conn.execute(stmt).fetchall()]


schema_table_fetch_all_multiple: dict[
    Type[BaseModelORJson], tuple[Table, Column[Any], Column[Any]]
] = {
    MstSpot: (mstSpot, mstSpot.c.mapId, mstSpot.c.id),
    MstVoice: (mstVoice, mstVoice.c.id, mstVoice.c.id),
    MstSvtGroup: (mstSvtGroup, mstSvtGroup.c.id, mstSvtGroup.c.svtId),
    MstEventMissionCondition: (
        mstEventMissionCondition,
        mstEventMissionCondition.c.missionId,
        mstEventMissionCondition.c.id,
    ),
    MstEventMissionConditionDetail: (
        mstEventMissionConditionDetail,
        mstEventMissionConditionDetail.c.id,
        mstEventMissionConditionDetail.c.id,
    ),
    MstSvtVoiceRelation: (
        mstSvtVoiceRelation,
        mstSvtVoiceRelation.c.svtId,
        mstSvtVoiceRelation.c.svtId,
    ),
    MstBgm: (mstBgm, mstBgm.c.id, mstBgm.c.id),
    MstGift: (mstGift, mstGift.c.id, mstGift.c.id),
    MstShopScript: (mstShopScript, mstShopScript.c.shopId, mstShopScript.c.shopId),
}

TFetchAllMultiple = TypeVar("TFetchAllMultiple", bound=BaseModelORJson)


def get_all_multiple(
    conn: Connection,
    schema: Type[TFetchAllMultiple],
    where_ids: Iterable[Union[int, str]],
) -> list[TFetchAllMultiple]:
    table, where_col, order_col = schema_table_fetch_all_multiple[schema]
    stmt = select(table).where(where_col.in_(where_ids)).order_by(order_col)
    return [schema.from_orm(db_row) for db_row in conn.execute(stmt).fetchall()]
