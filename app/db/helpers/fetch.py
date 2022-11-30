from typing import Iterable, Optional, Type, TypeVar, Union

from sqlalchemy import Table
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import ColumnElement, select

from ...models.raw import (
    AssetStorage,
    mstBgm,
    mstBgmRelease,
    mstBoxGacha,
    mstBoxGachaTalk,
    mstBuff,
    mstClosedMessage,
    mstCombineAppendPassiveSkill,
    mstCombineCostume,
    mstCombineLimit,
    mstCombineMaterial,
    mstCombineSkill,
    mstCommandCode,
    mstCommandCodeComment,
    mstCommandCodeSkill,
    mstCommonConsume,
    mstCommonRelease,
    mstConstant,
    mstCv,
    mstEquip,
    mstEquipAdd,
    mstEquipExp,
    mstEquipSkill,
    mstEvent,
    mstEventBulletinBoard,
    mstEventBulletinBoardRelease,
    mstEventCampaign,
    mstEventCooltimeReward,
    mstEventDigging,
    mstEventDiggingBlock,
    mstEventDiggingReward,
    mstEventFortification,
    mstEventFortificationDetail,
    mstEventFortificationSvt,
    mstEventMission,
    mstEventMissionCondition,
    mstEventMissionConditionDetail,
    mstEventPointBuff,
    mstEventPointGroup,
    mstEventQuest,
    mstEventQuestCooltime,
    mstEventRandomMission,
    mstEventRecipe,
    mstEventRecipeGift,
    mstEventReward,
    mstEventRewardScene,
    mstEventRewardSet,
    mstEventTower,
    mstEventVoicePlay,
    mstFriendship,
    mstFunc,
    mstFuncGroup,
    mstGift,
    mstGiftAdd,
    mstIllustrator,
    mstItem,
    mstMap,
    mstMapGimmick,
    mstMasterMission,
    mstQuest,
    mstShop,
    mstShopRelease,
    mstShopScript,
    mstSpot,
    mstSpotRoad,
    mstSvt,
    mstSvtAdd,
    mstSvtAppendPassiveSkill,
    mstSvtAppendPassiveSkillUnlock,
    mstSvtCard,
    mstSvtChange,
    mstSvtCoin,
    mstSvtComment,
    mstSvtCommentAdd,
    mstSvtCostume,
    mstSvtExp,
    mstSvtExtra,
    mstSvtGroup,
    mstSvtIndividuality,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtLimitImage,
    mstSvtMultiPortrait,
    mstSvtPassiveSkill,
    mstSvtScript,
    mstSvtVoiceRelation,
    mstTreasureBox,
    mstTreasureBoxGift,
    mstVoice,
    mstWar,
    mstWarAdd,
    mstWarQuestSelection,
)
from ...schemas.base import BaseModelORJson
from ...schemas.raw import (
    AssetStorageLine,
    MstBgm,
    MstBgmRelease,
    MstBoxGacha,
    MstBoxGachaTalk,
    MstBuff,
    MstClosedMessage,
    MstCombineAppendPassiveSkill,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineMaterial,
    MstCombineSkill,
    MstCommandCode,
    MstCommandCodeComment,
    MstCommandCodeSkill,
    MstCommonConsume,
    MstCommonRelease,
    MstConstant,
    MstCv,
    MstEquip,
    MstEquipAdd,
    MstEquipExp,
    MstEquipSkill,
    MstEvent,
    MstEventBulletinBoard,
    MstEventBulletinBoardRelease,
    MstEventCampaign,
    MstEventCooltimeReward,
    MstEventDigging,
    MstEventDiggingBlock,
    MstEventDiggingReward,
    MstEventFortification,
    MstEventFortificationDetail,
    MstEventFortificationSvt,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventPointBuff,
    MstEventPointGroup,
    MstEventQuest,
    MstEventQuestCooltime,
    MstEventRandomMission,
    MstEventRecipe,
    MstEventRecipeGift,
    MstEventReward,
    MstEventRewardScene,
    MstEventRewardSet,
    MstEventTower,
    MstEventVoicePlay,
    MstFriendship,
    MstFunc,
    MstFuncGroup,
    MstGift,
    MstGiftAdd,
    MstIllustrator,
    MstItem,
    MstMap,
    MstMapGimmick,
    MstMasterMission,
    MstQuest,
    MstShop,
    MstShopRelease,
    MstShopScript,
    MstSpot,
    MstSpotRoad,
    MstSvt,
    MstSvtAdd,
    MstSvtAppendPassiveSkill,
    MstSvtAppendPassiveSkillUnlock,
    MstSvtCard,
    MstSvtChange,
    MstSvtCoin,
    MstSvtComment,
    MstSvtCommentAdd,
    MstSvtCostume,
    MstSvtExp,
    MstSvtExtra,
    MstSvtGroup,
    MstSvtIndividuality,
    MstSvtLimit,
    MstSvtLimitAdd,
    MstSvtLimitImage,
    MstSvtMultiPortrait,
    MstSvtPassiveSkill,
    MstSvtScript,
    MstSvtVoiceRelation,
    MstTreasureBox,
    MstTreasureBoxGift,
    MstVoice,
    MstWar,
    MstWarAdd,
    MstWarQuestSelection,
)


schema_map_fetch_one: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement]
] = {
    MstSvt: (mstSvt, mstSvt.c.id),
    MstCv: (mstCv, mstCv.c.id),
    MstIllustrator: (mstIllustrator, mstIllustrator.c.id),
    MstCommandCode: (mstCommandCode, mstCommandCode.c.id),
    MstWar: (mstWar, mstWar.c.id),
    MstEquip: (mstEquip, mstEquip.c.id),
    MstEvent: (mstEvent, mstEvent.c.id),
    MstConstant: (mstConstant, mstConstant.c.name),
    MstQuest: (mstQuest, mstQuest.c.id),
    MstBuff: (mstBuff, mstBuff.c.id),
    MstFunc: (mstFunc, mstFunc.c.id),
    MstItem: (mstItem, mstItem.c.id),
    MstBgm: (mstBgm, mstBgm.c.id),
    MstShop: (mstShop, mstShop.c.id),
    MstShopScript: (mstShopScript, mstShopScript.c.shopId),
    MstMasterMission: (mstMasterMission, mstMasterMission.c.id),
    MstSvtExtra: (mstSvtExtra, mstSvtExtra.c.svtId),
    MstSvtCoin: (mstSvtCoin, mstSvtCoin.c.svtId),
    MstSvtAdd: (mstSvtAdd, mstSvtAdd.c.svtId),
    MstEventDigging: (mstEventDigging, mstEventDigging.c.eventId),
}

TFetchOne = TypeVar("TFetchOne", bound=BaseModelORJson)


async def get_one(
    conn: AsyncConnection, schema: Type[TFetchOne], where_id: Union[int, str]
) -> Optional[TFetchOne]:
    table, where_col = schema_map_fetch_one[schema]
    stmt = select(table).where(where_col == where_id)
    try:
        entity_db = (await conn.execute(stmt)).fetchone()
    except DBAPIError:
        return None

    if entity_db:
        return schema.from_orm(entity_db)

    return None


schema_table_fetch_all: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement, ColumnElement]
] = {
    MstSvtCard: (mstSvtCard, mstSvtCard.c.svtId, mstSvtCard.c.cardId),
    MstSvtLimit: (mstSvtLimit, mstSvtLimit.c.svtId, mstSvtLimit.c.limitCount),
    MstCombineSkill: (mstCombineSkill, mstCombineSkill.c.id, mstCombineSkill.c.skillLv),
    MstSvtChange: (mstSvtChange, mstSvtChange.c.svtId, mstSvtChange.c.priority),
    MstSvtCostume: (mstSvtCostume, mstSvtCostume.c.svtId, mstSvtCostume.c.id),
    MstSvtExp: (mstSvtExp, mstSvtExp.c.type, mstSvtExp.c.lv),
    MstFriendship: (mstFriendship, mstFriendship.c.id, mstFriendship.c.rank),
    MstSvtComment: (mstSvtComment, mstSvtComment.c.svtId, mstSvtComment.c.id),
    MstSvtCommentAdd: (
        mstSvtCommentAdd,
        mstSvtCommentAdd.c.svtId,
        mstSvtCommentAdd.c.id,
    ),
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
    MstSvtLimitImage: (
        mstSvtLimitImage,
        mstSvtLimitImage.c.svtId,
        mstSvtLimitImage.c.limitCount,
    ),
    MstSvtAppendPassiveSkill: (
        mstSvtAppendPassiveSkill,
        mstSvtAppendPassiveSkill.c.svtId,
        mstSvtAppendPassiveSkill.c.num,
    ),
    MstSvtAppendPassiveSkillUnlock: (
        mstSvtAppendPassiveSkillUnlock,
        mstSvtAppendPassiveSkillUnlock.c.svtId,
        mstSvtAppendPassiveSkillUnlock.c.num,
    ),
    MstCombineAppendPassiveSkill: (
        mstCombineAppendPassiveSkill,
        mstCombineAppendPassiveSkill.c.svtId,
        mstCombineAppendPassiveSkill.c.skillLv,
    ),
    MstMap: (mstMap, mstMap.c.warId, mstMap.c.id),
    MstWarAdd: (mstWarAdd, mstWarAdd.c.warId, mstWarAdd.c.priority),
    MstWarQuestSelection: (
        mstWarQuestSelection,
        mstWarQuestSelection.c.warId,
        mstWarQuestSelection.c.priority,
    ),
    MstEquipSkill: (mstEquipSkill, mstEquipSkill.c.equipId, mstEquipSkill.c.num),
    MstEquipExp: (mstEquipExp, mstEquipExp.c.equipId, mstEquipExp.c.lv),
    MstEquipAdd: (mstEquipAdd, mstEquipAdd.c.equipId, mstEquipAdd.c.id),
    MstEventMission: (
        mstEventMission,
        mstEventMission.c.missionTargetId,
        mstEventMission.c.id,
    ),
    MstEventRandomMission: (
        mstEventRandomMission,
        mstEventRandomMission.c.eventId,
        mstEventRandomMission.c.missionId,
    ),
    MstShop: (mstShop, mstShop.c.eventId, mstShop.c.id),
    MstShopRelease: (mstShopRelease, mstShopRelease.c.shopId, mstShopRelease.c.shopId),
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
    MstEventPointGroup: (
        mstEventPointGroup,
        mstEventPointGroup.c.eventId,
        mstEventPointGroup.c.groupId,
    ),
    MstEventTower: (mstEventTower, mstEventTower.c.eventId, mstEventTower.c.towerId),
    MstBoxGacha: (mstBoxGacha, mstBoxGacha.c.eventId, mstBoxGacha.c.id),
    MstCombineMaterial: (
        mstCombineMaterial,
        mstCombineMaterial.c.id,
        mstCombineMaterial.c.lv,
    ),
    MstSvtPassiveSkill: (
        mstSvtPassiveSkill,
        mstSvtPassiveSkill.c.svtId,
        mstSvtPassiveSkill.c.skillId,
    ),
    MstFuncGroup: (mstFuncGroup, mstFuncGroup.c.funcId, mstFuncGroup.c.eventId),
    MstBgmRelease: (mstBgmRelease, mstBgmRelease.c.bgmId, mstBgmRelease.c.id),
    MstSvtIndividuality: (
        mstSvtIndividuality,
        mstSvtIndividuality.c.svtId,
        mstSvtIndividuality.c.idx,
    ),
    MstTreasureBox: (mstTreasureBox, mstTreasureBox.c.eventId, mstTreasureBox.c.id),
    MstEventDiggingBlock: (
        mstEventDiggingBlock,
        mstEventDiggingBlock.c.eventId,
        mstEventDiggingBlock.c.id,
    ),
    MstEventDiggingReward: (
        mstEventDiggingReward,
        mstEventDiggingReward.c.eventId,
        mstEventDiggingReward.c.id,
    ),
    MstEventCooltimeReward: (
        mstEventCooltimeReward,
        mstEventCooltimeReward.c.eventId,
        mstEventCooltimeReward.c.spotId,
    ),
    MstEventQuestCooltime: (
        mstEventQuestCooltime,
        mstEventQuestCooltime.c.eventId,
        mstEventQuestCooltime.c.questId,
    ),
    MstEventFortification: (
        mstEventFortification,
        mstEventFortification.c.eventId,
        mstEventFortification.c.idx,
    ),
    MstEventFortificationDetail: (
        mstEventFortificationDetail,
        mstEventFortificationDetail.c.eventId,
        mstEventFortificationDetail.c.fortificationIdx,
    ),
    MstEventFortificationSvt: (
        mstEventFortificationSvt,
        mstEventFortificationSvt.c.eventId,
        mstEventFortificationSvt.c.fortificationIdx,
    ),
    MstEventQuest: (
        mstEventQuest,
        mstEventQuest.c.eventId,
        mstEventQuest.c.questId,
    ),
    MstEventCampaign: (
        mstEventCampaign,
        mstEventCampaign.c.eventId,
        mstEventCampaign.c.idx,
    ),
    MstSvtMultiPortrait: (
        mstSvtMultiPortrait,
        mstSvtMultiPortrait.c.svtId,
        mstSvtMultiPortrait.c.limitCount,
    ),
    MstEventRewardScene: (
        mstEventRewardScene,
        mstEventRewardScene.c.eventId,
        mstEventRewardScene.c.slot,
    ),
    MstEventVoicePlay: (
        mstEventVoicePlay,
        mstEventVoicePlay.c.eventId,
        mstEventVoicePlay.c.slot,
    ),
    MstEventBulletinBoard: (
        mstEventBulletinBoard,
        mstEventBulletinBoard.c.eventId,
        mstEventBulletinBoard.c.id,
    ),
    MstEventRecipe: (
        mstEventRecipe,
        mstEventRecipe.c.eventId,
        mstEventRecipe.c.id,
    ),
}

TFetchAll = TypeVar("TFetchAll", bound=BaseModelORJson)


async def get_all(
    conn: AsyncConnection, schema: Type[TFetchAll], where_id: int
) -> list[TFetchAll]:
    table, where_col, order_col = schema_table_fetch_all[schema]
    stmt = select(table).where(where_col == where_id).order_by(order_col)
    result = await conn.execute(stmt)
    return [schema.from_orm(db_row) for db_row in result.fetchall()]


schema_table_fetch_all_multiple: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement, list[ColumnElement]]
] = {
    MstSpot: (mstSpot, mstSpot.c.mapId, [mstSpot.c.id]),
    MstVoice: (mstVoice, mstVoice.c.id, [mstVoice.c.id]),
    MstSvtGroup: (mstSvtGroup, mstSvtGroup.c.id, [mstSvtGroup.c.svtId]),
    MstEventMissionCondition: (
        mstEventMissionCondition,
        mstEventMissionCondition.c.missionId,
        [mstEventMissionCondition.c.id],
    ),
    MstEventMissionConditionDetail: (
        mstEventMissionConditionDetail,
        mstEventMissionConditionDetail.c.id,
        [mstEventMissionConditionDetail.c.id],
    ),
    MstSvtVoiceRelation: (
        mstSvtVoiceRelation,
        mstSvtVoiceRelation.c.svtId,
        [mstSvtVoiceRelation.c.svtId],
    ),
    MstBgm: (mstBgm, mstBgm.c.id, [mstBgm.c.id]),
    MstGift: (mstGift, mstGift.c.id, [mstGift.c.id, mstGift.c.sort_id]),
    MstGiftAdd: (mstGiftAdd, mstGiftAdd.c.giftId, [mstGiftAdd.c.giftId]),
    MstShopScript: (mstShopScript, mstShopScript.c.shopId, [mstShopScript.c.shopId]),
    MstShopRelease: (
        mstShopRelease,
        mstShopRelease.c.shopId,
        [mstShopRelease.c.shopId],
    ),
    MstItem: (mstItem, mstItem.c.id, [mstItem.c.id]),
    MstMapGimmick: (mstMapGimmick, mstMapGimmick.c.mapId, [mstMapGimmick.c.id]),
    MstClosedMessage: (
        mstClosedMessage,
        mstClosedMessage.c.id,
        [mstClosedMessage.c.id],
    ),
    MstShop: (mstShop, mstShop.c.id, [mstShop.c.id]),
    MstQuest: (mstQuest, mstQuest.c.id, [mstQuest.c.id]),
    MstSvtScript: (mstSvtScript, mstSvtScript.c.id, [mstSvtScript.c.id]),
    MstTreasureBoxGift: (
        mstTreasureBoxGift,
        mstTreasureBoxGift.c.id,
        [mstTreasureBoxGift.c.id],
    ),
    MstCommonConsume: (
        mstCommonConsume,
        mstCommonConsume.c.id,
        [mstCommonConsume.c.id],
    ),
    MstCommonRelease: (
        mstCommonRelease,
        mstCommonRelease.c.id,
        [mstCommonRelease.c.id],
    ),
    MstSpotRoad: (mstSpotRoad, mstSpotRoad.c.mapId, [mstSpotRoad.c.id]),
    MstBoxGachaTalk: (mstBoxGachaTalk, mstBoxGachaTalk.c.id, [mstBoxGachaTalk.c.id]),
    MstSvtExtra: (mstSvtExtra, mstSvtExtra.c.svtId, [mstSvtExtra.c.svtId]),
    MstEventBulletinBoardRelease: (
        mstEventBulletinBoardRelease,
        mstEventBulletinBoardRelease.c.bulletinBoardId,
        [mstEventBulletinBoardRelease.c.bulletinBoardId],
    ),
    MstEventRecipeGift: (
        mstEventRecipeGift,
        mstEventRecipeGift.c.recipeId,
        [mstEventRecipeGift.c.recipeId, mstEventRecipeGift.c.idx],
    ),
}

TFetchAllMultiple = TypeVar("TFetchAllMultiple", bound=BaseModelORJson)


async def get_all_multiple(
    conn: AsyncConnection,
    schema: Type[TFetchAllMultiple],
    where_ids: Iterable[Union[int, str]],
) -> list[TFetchAllMultiple]:
    if not where_ids:
        return []
    table, where_col, order_col = schema_table_fetch_all_multiple[schema]
    stmt = select(table).where(where_col.in_(where_ids)).order_by(*order_col)
    result = await conn.execute(stmt)
    return [schema.from_orm(db_row) for db_row in result.fetchall()]


schema_map_fetch_everything: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement]
] = {
    MstWar: (mstWar, mstWar.c.id),
    MstEvent: (mstEvent, mstEvent.c.id),
    MstCommandCode: (mstCommandCode, mstCommandCode.c.id),
    MstEquip: (mstEquip, mstEquip.c.id),
    MstBgm: (mstBgm, mstBgm.c.id),
    MstBgmRelease: (mstBgmRelease, mstBgmRelease.c.bgmId),
    MstItem: (mstItem, mstItem.c.id),
    MstIllustrator: (mstIllustrator, mstIllustrator.c.id),
    MstCv: (mstCv, mstCv.c.id),
    MstMasterMission: (mstMasterMission, mstMasterMission.c.id),
    AssetStorageLine: (AssetStorage, AssetStorage.c.path),
    MstSvt: (mstSvt, mstSvt.c.id),
}

TFetchEverything = TypeVar("TFetchEverything", bound=BaseModelORJson)


async def get_everything(
    conn: AsyncConnection, schema: Type[TFetchEverything]
) -> list[TFetchEverything]:  # pragma: no cover
    table, order_col = schema_map_fetch_everything[schema]
    stmt = select(table).order_by(order_col)
    entities_db = (await conn.execute(stmt)).fetchall()

    return [schema.from_orm(entity) for entity in entities_db]
