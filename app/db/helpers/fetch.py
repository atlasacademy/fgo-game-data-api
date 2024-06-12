from typing import Iterable, Optional, Type, TypeVar, Union

from sqlalchemy import Table
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import ColumnElement, select

from ...models.raw import (
    AssetStorage,
    mstBattleMasterImage,
    mstBattleMessage,
    mstBattleMessageGroup,
    mstBgm,
    mstBgmRelease,
    mstBlankEarthSpot,
    mstBoxGacha,
    mstBoxGachaTalk,
    mstBuff,
    mstClassBoardBase,
    mstClassBoardClass,
    mstClassBoardCommandSpell,
    mstClassBoardLine,
    mstClassBoardLock,
    mstClassBoardSquare,
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
    mstCompleteMission,
    mstConstant,
    mstCv,
    mstEnemyMaster,
    mstEnemyMasterBattle,
    mstEquip,
    mstEquipAdd,
    mstEquipExp,
    mstEquipSkill,
    mstEvent,
    mstEventAdd,
    mstEventAlloutBattle,
    mstEventBulletinBoard,
    mstEventBulletinBoardRelease,
    mstEventCampaign,
    mstEventCommandAssist,
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
    mstEventMissionGroup,
    mstEventMural,
    mstEventPointActivity,
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
    mstEventSvt,
    mstEventTower,
    mstEventVoicePlay,
    mstFriendship,
    mstFunc,
    mstFuncGroup,
    mstGacha,
    mstGift,
    mstGiftAdd,
    mstHeelPortrait,
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
    mstSpotAdd,
    mstSpotRoad,
    mstSvt,
    mstSvtAdd,
    mstSvtAppendPassiveSkill,
    mstSvtAppendPassiveSkillUnlock,
    mstSvtCard,
    mstSvtCardAdd,
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
    mstSvtOverwrite,
    mstSvtPassiveSkill,
    mstSvtScript,
    mstSvtVoiceRelation,
    mstTreasureBox,
    mstTreasureBoxGift,
    mstVoice,
    mstWar,
    mstWarAdd,
    mstWarBoard,
    mstWarBoardQuest,
    mstWarBoardStage,
    mstWarBoardStageLayout,
    mstWarBoardTreasure,
    mstWarQuestSelection,
)
from ...schemas.base import BaseModelORJson
from ...schemas.raw import (
    AssetStorageLine,
    MstBattleMasterImage,
    MstBattleMessage,
    MstBattleMessageGroup,
    MstBgm,
    MstBgmRelease,
    MstBlankEarthSpot,
    MstBoxGacha,
    MstBoxGachaTalk,
    MstBuff,
    MstClassBoardBase,
    MstClassBoardClass,
    MstClassBoardCommandSpell,
    MstClassBoardLine,
    MstClassBoardLock,
    MstClassBoardSquare,
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
    MstCompleteMission,
    MstConstant,
    MstCv,
    MstEnemyMaster,
    MstEnemyMasterBattle,
    MstEquip,
    MstEquipAdd,
    MstEquipExp,
    MstEquipSkill,
    MstEvent,
    MstEventAdd,
    MstEventAlloutBattle,
    MstEventBulletinBoard,
    MstEventBulletinBoardRelease,
    MstEventCampaign,
    MstEventCommandAssist,
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
    MstEventMissionGroup,
    MstEventMural,
    MstEventPointActivity,
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
    MstEventSvt,
    MstEventTower,
    MstEventVoicePlay,
    MstFriendship,
    MstFunc,
    MstFuncGroup,
    MstGacha,
    MstGift,
    MstGiftAdd,
    MstHeelPortrait,
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
    MstSpotAdd,
    MstSpotRoad,
    MstSvt,
    MstSvtAdd,
    MstSvtAppendPassiveSkill,
    MstSvtAppendPassiveSkillUnlock,
    MstSvtCard,
    MstSvtCardAdd,
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
    MstSvtOverwrite,
    MstSvtPassiveSkill,
    MstSvtScript,
    MstSvtVoiceRelation,
    MstTreasureBox,
    MstTreasureBoxGift,
    MstVoice,
    MstWar,
    MstWarAdd,
    MstWarBoard,
    MstWarBoardQuest,
    MstWarBoardStage,
    MstWarBoardStageLayout,
    MstWarBoardTreasure,
    MstWarQuestSelection,
)
from .utils import fetch_one


schema_map_fetch_one: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement]
] = {
    MstSvt: (mstSvt, mstSvt.c.id),
    MstCv: (mstCv, mstCv.c.id),
    MstIllustrator: (mstIllustrator, mstIllustrator.c.id),
    MstCommandCode: (mstCommandCode, mstCommandCode.c.id),
    MstWar: (mstWar, mstWar.c.id),
    MstEquip: (mstEquip, mstEquip.c.id),
    MstEnemyMaster: (mstEnemyMaster, mstEnemyMaster.c.id),
    MstEvent: (mstEvent, mstEvent.c.id),
    MstConstant: (mstConstant, mstConstant.c.name),
    MstQuest: (mstQuest, mstQuest.c.id),
    MstBuff: (mstBuff, mstBuff.c.id),
    MstFunc: (mstFunc, mstFunc.c.id),
    MstItem: (mstItem, mstItem.c.id),
    MstBgm: (mstBgm, mstBgm.c.id),
    MstShop: (mstShop, mstShop.c.id),
    MstShopScript: (mstShopScript, mstShopScript.c.shopId),
    MstEventMission: (mstEventMission, mstEventMission.c.id),
    MstMasterMission: (mstMasterMission, mstMasterMission.c.id),
    MstCompleteMission: (mstCompleteMission, mstCompleteMission.c.masterMissionId),
    MstSvtExtra: (mstSvtExtra, mstSvtExtra.c.svtId),
    MstSvtCoin: (mstSvtCoin, mstSvtCoin.c.svtId),
    MstSvtAdd: (mstSvtAdd, mstSvtAdd.c.svtId),
    MstEventDigging: (mstEventDigging, mstEventDigging.c.eventId),
    MstClassBoardBase: (mstClassBoardBase, mstClassBoardBase.c.id),
    MstGacha: (mstGacha, mstGacha.c.id),
}

TFetchOne = TypeVar("TFetchOne", bound=BaseModelORJson)


async def get_one(
    conn: AsyncConnection, schema: Type[TFetchOne], where_id: Union[int, str]
) -> Optional[TFetchOne]:
    table, where_col = schema_map_fetch_one[schema]
    stmt = select(table).where(where_col == where_id)
    try:
        entity_db = await fetch_one(conn, stmt)
    except DBAPIError:
        return None

    if entity_db:
        return schema.from_orm(entity_db)

    return None


schema_table_fetch_all: dict[  # type:ignore
    Type[BaseModelORJson], tuple[Table, ColumnElement, ColumnElement]
] = {
    MstSvtCard: (mstSvtCard, mstSvtCard.c.svtId, mstSvtCard.c.cardId),
    MstSvtCardAdd: (mstSvtCardAdd, mstSvtCardAdd.c.svtId, mstSvtCardAdd.c.cardId),
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
    MstEnemyMasterBattle: (
        mstEnemyMasterBattle,
        mstEnemyMasterBattle.c.enemyMasterId,
        mstEnemyMasterBattle.c.id,
    ),
    MstBattleMasterImage: (
        mstBattleMasterImage,
        mstBattleMasterImage.c.id,
        mstBattleMasterImage.c.type,
    ),
    MstBattleMessage: (mstBattleMessage, mstBattleMessage.c.id, mstBattleMessage.c.idx),
    MstBattleMessageGroup: (
        mstBattleMessageGroup,
        mstBattleMessageGroup.c.groupId,
        mstBattleMessageGroup.c.messageId,
    ),
    MstEventAdd: (mstEventAdd, mstEventAdd.c.eventId, mstEventAdd.c.priority),
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
    MstEventCommandAssist: (
        mstEventCommandAssist,
        mstEventCommandAssist.c.eventId,
        mstEventCommandAssist.c.id,
    ),
    MstClassBoardClass: (
        mstClassBoardClass,
        mstClassBoardClass.c.classBoardBaseId,
        mstClassBoardClass.c.classId,
    ),
    MstClassBoardLine: (
        mstClassBoardLine,
        mstClassBoardLine.c.classBoardBaseId,
        mstClassBoardLine.c.id,
    ),
    MstClassBoardSquare: (
        mstClassBoardSquare,
        mstClassBoardSquare.c.classBoardBaseId,
        mstClassBoardSquare.c.id,
    ),
    MstHeelPortrait: (
        mstHeelPortrait,
        mstHeelPortrait.c.eventId,
        mstHeelPortrait.c.id,
    ),
    MstEventMural: (
        mstEventMural,
        mstEventMural.c.eventId,
        mstEventMural.c.id,
    ),
    MstEventPointActivity: (
        mstEventPointActivity,
        mstEventPointActivity.c.eventId,
        mstEventPointActivity.c.groupId,
    ),
    MstWarBoard: (mstWarBoard, mstWarBoard.c.eventId, mstWarBoard.c.id),
    MstSvtOverwrite: (
        mstSvtOverwrite,
        mstSvtOverwrite.c.svtId,
        mstSvtOverwrite.c.priority,
    ),
    MstEventSvt: (
        mstEventSvt,
        mstEventSvt.c.eventId,
        mstEventSvt.c.svtId,
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
    MstBlankEarthSpot: (
        mstBlankEarthSpot,
        mstBlankEarthSpot.c.mapId,
        [mstBlankEarthSpot.c.id],
    ),
    MstSpotAdd: (mstSpotAdd, mstSpotAdd.c.spotId, [mstSpotAdd.c.priority]),
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
    MstCompleteMission: (
        mstCompleteMission,
        mstCompleteMission.c.masterMissionId,
        [mstCompleteMission.c.masterMissionId],
    ),
    MstSvtVoiceRelation: (
        mstSvtVoiceRelation,
        mstSvtVoiceRelation.c.svtId,
        [mstSvtVoiceRelation.c.svtId],
    ),
    MstBgm: (mstBgm, mstBgm.c.id, [mstBgm.c.id]),
    MstGift: (
        mstGift,
        mstGift.c.id,
        [
            mstGift.c.id,
            mstGift.c.priority.desc(),
            mstGift.c.type,
            mstGift.c.objectId,
            mstGift.c.sort_id,
        ],
    ),
    MstGiftAdd: (mstGiftAdd, mstGiftAdd.c.giftId, [mstGiftAdd.c.giftId]),
    MstShopScript: (mstShopScript, mstShopScript.c.shopId, [mstShopScript.c.shopId]),
    MstShopRelease: (
        mstShopRelease,
        mstShopRelease.c.shopId,
        [
            mstShopRelease.c.shopId,
            mstShopRelease.c.priority,
            mstShopRelease.c.condType,
            mstShopRelease.c.condNum,
        ],
    ),
    MstItem: (mstItem, mstItem.c.id, [mstItem.c.id]),
    MstMapGimmick: (mstMapGimmick, mstMapGimmick.c.mapId, [mstMapGimmick.c.id]),
    MstClosedMessage: (
        mstClosedMessage,
        mstClosedMessage.c.id,
        [mstClosedMessage.c.id],
    ),
    MstBattleMessage: (
        mstBattleMessage,
        mstBattleMessage.c.id,
        [mstBattleMessage.c.id, mstBattleMessage.c.idx],
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
        [
            mstCommonRelease.c.id,
            mstCommonRelease.c.priority,
            mstCommonRelease.c.condGroup,
            mstCommonRelease.c.condType,
            mstCommonRelease.c.condId,
        ],
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
    MstEventAlloutBattle: (
        mstEventAlloutBattle,
        mstEventAlloutBattle.c.eventId,
        [mstEventAlloutBattle.c.eventId, mstEventAlloutBattle.c.alloutBattleId],
    ),
    MstEventMissionGroup: (
        mstEventMissionGroup,
        mstEventMissionGroup.c.id,
        [mstEventMissionGroup.c.id, mstEventMissionGroup.c.missionId],
    ),
    MstClassBoardLock: (
        mstClassBoardLock,
        mstClassBoardLock.c.id,
        [mstClassBoardLock.c.id],
    ),
    MstClassBoardCommandSpell: (
        mstClassBoardCommandSpell,
        mstClassBoardCommandSpell.c.id,
        [
            mstClassBoardCommandSpell.c.id,
            mstClassBoardCommandSpell.c.commandSpellId,
            mstClassBoardCommandSpell.c.lv,
        ],
    ),
    MstWarBoardStage: (
        mstWarBoardStage,
        mstWarBoardStage.c.warBoardId,
        [mstWarBoardStage.c.warBoardId, mstWarBoardStage.c.id],
    ),
    MstWarBoardStageLayout: (
        mstWarBoardStageLayout,
        mstWarBoardStageLayout.c.stageId,
        [mstWarBoardStageLayout.c.stageId, mstWarBoardStageLayout.c.squareIndex],
    ),
    MstWarBoardTreasure: (
        mstWarBoardTreasure,
        mstWarBoardTreasure.c.id,
        [mstWarBoardTreasure.c.id],
    ),
    MstWarBoardQuest: (
        mstWarBoardQuest,
        mstWarBoardQuest.c.stageId,
        [mstWarBoardQuest.c.stageId],
    ),
    MstEventCampaign: (
        mstEventCampaign,
        mstEventCampaign.c.eventId,
        [
            mstEventCampaign.c.eventId,
            mstEventCampaign.c.idx,
            mstEventCampaign.c.target,
            mstEventCampaign.c.priority,
            mstEventCampaign.c.groupId,
        ],
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
    MstEnemyMaster: (mstEnemyMaster, mstEnemyMaster.c.id),
    MstBgm: (mstBgm, mstBgm.c.id),
    MstBgmRelease: (mstBgmRelease, mstBgmRelease.c.bgmId),
    MstItem: (mstItem, mstItem.c.id),
    MstIllustrator: (mstIllustrator, mstIllustrator.c.id),
    MstCv: (mstCv, mstCv.c.id),
    MstMasterMission: (mstMasterMission, mstMasterMission.c.id),
    AssetStorageLine: (AssetStorage, AssetStorage.c.path),
    MstSvt: (mstSvt, mstSvt.c.id),
    MstClassBoardBase: (mstClassBoardBase, mstClassBoardBase.c.id),
    MstGacha: (mstGacha, mstGacha.c.id),
}

TFetchEverything = TypeVar("TFetchEverything", bound=BaseModelORJson)


async def get_everything(
    conn: AsyncConnection, schema: Type[TFetchEverything]
) -> list[TFetchEverything]:  # pragma: no cover
    table, order_col = schema_map_fetch_everything[schema]
    stmt = select(table).order_by(order_col)
    entities_db = (await conn.execute(stmt)).fetchall()

    return [schema.from_orm(entity) for entity in entities_db]
