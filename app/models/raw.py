import sqlalchemy
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Index,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from .base import metadata


mstConstant = Table(
    "mstConstant",
    metadata,
    Column("name", String, index=True),
    Column("value", Integer),
    Column("createdAt", Integer),
)


mstBuff = Table(
    "mstBuff",
    metadata,
    Column("vals", ARRAY(Integer)),
    Column("tvals", ARRAY(Integer)),
    Column("ckSelfIndv", ARRAY(Integer)),
    Column("ckOpIndv", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("buffGroup", Integer),
    Column("type", Integer),
    Column("name", String),
    Column("detail", String),
    Column("iconId", Integer),
    Column("maxRate", Integer),
    Column("effectId", Integer),
)


mstClassRelationOverwrite = Table(
    "mstClassRelationOverwrite",
    metadata,
    Column("id", Integer, index=True),
    Column("atkSide", Integer),
    Column("atkClass", Integer),
    Column("defClass", Integer),
    Column("damageRate", Integer),
    Column("type", Integer),
)


mstFunc = Table(
    "mstFunc",
    metadata,
    Column("vals", ARRAY(Integer)),
    Column("tvals", ARRAY(Integer)),
    Column("questTvals", ARRAY(Integer)),
    Column("effectList", ARRAY(Integer)),
    Column("popupTextColor", Integer),
    Column("id", Integer, primary_key=True),
    Column("cond", Integer),
    Column("funcType", Integer),
    Column("targetType", Integer),
    Column("applyTarget", Integer),
    Column("popupIconId", Integer),
    Column("popupText", String),
    Column("categoryId", Integer),
)


mstFuncGroup = Table(
    "mstFuncGroup",
    metadata,
    Column("funcId", Integer, index=True),
    Column("eventId", Integer),
    Column("baseFuncId", Integer),
    Column("nameTotal", String),
    Column("name", String),
    Column("iconId", Integer),
    Column("priority", Integer),
    Column("isDispValue", Boolean),
)


mstSkill = Table(
    "mstSkill",
    metadata,
    Column("effectList", ARRAY(Integer)),
    Column("actIndividuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("type", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("maxLv", Integer),
    Column("iconId", Integer),
    Column("motion", Integer),
)


mstSkillDetail = Table(
    "mstSkillDetail",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("detail", String),
    Column("detailShort", String),
)


mstSvtSkill = Table(
    "mstSvtSkill",
    metadata,
    Column("strengthStatus", Integer),
    Column("skillNum", Integer),
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("skillId", Integer, index=True),
    Column("condQuestId", Integer),
    Column("condQuestPhase", Integer),
    Column("condLv", Integer),
    Column("condLimitCount", Integer),
    Column("eventId", Integer),
    Column("flag", Integer),
)


mstSkillLv = Table(
    "mstSkillLv",
    metadata,
    Column("funcId", ARRAY(Integer)),
    Column("svals", ARRAY(String)),
    Column("script", JSONB),
    Column("skillId", Integer, index=True),
    Column("lv", Integer),
    Column("chargeTurn", Integer),
    Column("skillDetailId", Integer),
    Column("priority", Integer),
)


mstTreasureDevice = Table(
    "mstTreasureDevice",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("seqId", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("rank", String),
    Column("maxLv", Integer),
    Column("typeText", String),
    Column("attackAttri", Integer),
    Column("effectFlag", Integer),
)


mstTreasureDeviceDetail = Table(
    "mstTreasureDeviceDetail",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("detail", String),
    Column("detailShort", String),
)


mstSvtTreasureDevice = Table(
    "mstSvtTreasureDevice",
    metadata,
    Column("damage", ARRAY(Integer)),
    Column("strengthStatus", Integer),
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("flag", Integer),
    Column("imageIndex", Integer),
    Column("treasureDeviceId", Integer, index=True),
    Column("condQuestId", Integer),
    Column("condQuestPhase", Integer),
    Column("condLv", Integer),
    Column("condFriendshipRank", Integer),
    Column("motion", Integer),
    Column("cardId", Integer),
)


mstTreasureDeviceLv = Table(
    "mstTreasureDeviceLv",
    metadata,
    Column("funcId", ARRAY(Integer)),
    Column("svals", ARRAY(String)),
    Column("svals2", ARRAY(String)),
    Column("svals3", ARRAY(String)),
    Column("svals4", ARRAY(String)),
    Column("svals5", ARRAY(String)),
    Column("treaureDeviceId", Integer, index=True),
    Column("lv", Integer),
    Column("gaugeCount", Integer),
    Column("detailId", Integer),
    Column("tdPoint", Integer),
    Column("tdPointQ", Integer),
    Column("tdPointA", Integer),
    Column("tdPointB", Integer),
    Column("tdPointEx", Integer),
    Column("tdPointDef", Integer),
    Column("qp", Integer),
)


mstSvt = Table(
    "mstSvt",
    metadata,
    Column("relateQuestIds", ARRAY(Integer)),
    Column("individuality", ARRAY(Integer)),
    Column("classPassive", ARRAY(Integer)),
    Column("cardIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("baseSvtId", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("battleName", String),
    Column("classId", Integer),
    Column("type", Integer),
    Column("limitMax", Integer),
    Column("rewardLv", Integer),
    Column("friendshipId", Integer),
    Column("maxFriendshipRank", Integer),
    Column("genderType", Integer),
    Column("attri", Integer),
    Column("combineSkillId", Integer),
    Column("combineLimitId", Integer),
    Column("sellQp", Integer),
    Column("sellMana", Integer),
    Column("sellRarePri", Integer),
    Column("expType", Integer),
    Column("combineMaterialId", Integer),
    Column("cost", Integer),
    Column("battleSize", Integer),
    Column("hpGaugeY", Integer),
    Column("starRate", Integer),
    Column("deathRate", Integer),
    Column("attackAttri", Integer),
    Column("illustratorId", Integer),
    Column("cvId", Integer),
    Column("collectionNo", Integer),
    Column("materialStoryPriority", Integer),
    Column("flag", Integer),
)


mstSvtCard = Table(
    "mstSvtCard",
    metadata,
    Column("normalDamage", ARRAY(Integer)),
    Column("singleDamage", ARRAY(Integer)),
    Column("trinityDamage", ARRAY(Integer)),
    Column("unisonDamage", ARRAY(Integer)),
    Column("grandDamage", ARRAY(Integer)),
    Column("attackIndividuality", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("cardId", Integer),
    Column("motion", Integer),
    Column("attackType", Integer),
)


mstCombineLimit = Table(
    "mstCombineLimit",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("svtLimit", Integer),
    Column("qp", Integer),
)


mstCombineSkill = Table(
    "mstCombineSkill",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("skillLv", Integer),
    Column("qp", Integer),
)


mstCombineCostume = Table(
    "mstCombineCostume",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("costumeId", Integer),
    Column("qp", Integer),
)


mstVoice = Table(
    "mstVoice",
    metadata,
    Column("id", String, primary_key=True),
    Column("priority", Integer),
    Column("svtVoiceType", Integer),
    Column("name", String),
    Column("nameDefault", String),
    Column("condType", Integer),
    Column("condValue", Integer),
    Column("voicePlayedValue", Integer),
    Column("firstPlayPriority", Integer),
    Column("closedType", Integer),
    Column("flag", Integer),
)


mstSvtVoice = Table(
    "mstSvtVoice",
    metadata,
    Column("scriptJson", JSONB),
    Column("id", Integer, index=True),
    Column("voicePrefix", Integer),
    Column("type", Integer),
    Index(
        "mstSvtVoiceGIN",
        sqlalchemy.text('"scriptJson" jsonb_path_ops'),
        postgresql_using="gin",
    ),
)


mstSvtVoiceRelation = Table(
    "mstSvtVoiceRelation",
    metadata,
    Column("svtId", Integer, index=True),
    Column("relationSvtId", Integer),
    Column("ascendOrder", Integer),
)


mstSvtGroup = Table(
    "mstSvtGroup",
    metadata,
    Column("id", Integer, index=True),
    Column("svtId", Integer, index=True),
)


mstVoicePlayCond = Table(
    "mstVoicePlayCond",
    metadata,
    Column("svtId", Integer, index=True),
    Column("voicePrefix", Integer),
    Column("voiceId", String),
    Column("idx", Integer),
    Column("condGroup", Integer),
    Column("condType", Integer),
    Column("targetId", Integer),
    Column("condValues", ARRAY(Integer)),
)


mstSvtLimit = Table(
    "mstSvtLimit",
    metadata,
    Column("weaponColor", Integer),
    Column("svtId", Integer, index=True),
    Column("limitCount", Integer),
    Column("rarity", Integer),
    Column("lvMax", Integer),
    Column("weaponGroup", Integer),
    Column("weaponScale", Integer),
    Column("effectFolder", Integer),
    Column("hpBase", Integer),
    Column("hpMax", Integer),
    Column("atkBase", Integer),
    Column("atkMax", Integer),
    Column("criticalWeight", Integer),
    Column("power", Integer),
    Column("defense", Integer),
    Column("agility", Integer),
    Column("magic", Integer),
    Column("luck", Integer),
    Column("treasureDevice", Integer),
    Column("policy", Integer),
    Column("personality", Integer),
    Column("deity", Integer),
    Column("stepProbability", Integer),
    Column("strParam", String),
)


mstSvtLimitAdd = Table(
    "mstSvtLimitAdd",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("svtId", Integer, index=True),
    Column("limitCount", Integer, index=True),
    Column("battleCharaId", Integer),
    Column("fileConvertLimitCount", Integer),
    Column("battleCharaLimitCount", Integer),
    Column("battleCharaOffsetX", Integer),
    Column("battleCharaOffsetY", Integer),
    Column("battleCharaOffsetZ", Integer),
    Column("svtVoiceId", Integer),
    Column("voicePrefix", Integer),
)


mstSvtChange = Table(
    "mstSvtChange",
    metadata,
    Column("beforeTreasureDeviceIds", ARRAY(Integer)),
    Column("afterTreasureDeviceIds", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("priority", Integer),
    Column("condType", Integer),
    Column("condTargetId", Integer),
    Column("condValue", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("battleName", String),
    Column("svtVoiceId", Integer),
    Column("limitCount", Integer),
    Column("flag", Integer),
    Column("battleSvtId", Integer),
)


mstSvtCostume = Table(
    "mstSvtCostume",
    metadata,
    Column("svtId", Integer, index=True),
    Column("id", Integer, index=True),
    Column("groupIndex", Integer),
    Column("name", String),
    Column("shortName", String),
    Column("detail", String),
    Column("itemGetInfo", String),
    Column("releaseInfo", String),
    Column("costumeReleaseDetail", String),
    Column("priority", Integer),
    Column("flag", Integer),
    Column("costumeCollectionNo", Integer),
    Column("openedAt", Integer),
    Column("endedAt", Integer),
)


mstSvtExp = Table(
    "mstSvtExp",
    metadata,
    Column("type", Integer, index=True),
    Column("lv", Integer),
    Column("exp", Integer),
    Column("curve", Integer),
)


mstFriendship = Table(
    "mstFriendship",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("rank", Integer),
    Column("friendship", Integer),
    Column("qp", Integer),
)


mstCombineMaterial = Table(
    "mstCombineMaterial",
    metadata,
    Column("id", Integer, index=True),
    Column("lv", Integer),
    Column("value", Integer),
    Column("createdAt", Integer),
)


mstSvtScript = Table(
    "mstSvtScript",
    metadata,
    Column("extendData", JSONB),
    Column("id", BigInteger, index=True),
    Column("form", Integer),
    Column("faceX", Integer),
    Column("faceY", Integer),
    Column("bgImageId", Integer),
    Column("scale", Numeric),
    Column("offsetX", Integer),
    Column("offsetY", Integer),
    Column("offsetXMyroom", Integer),
    Column("offsetYMyroom", Integer),
)


mstSvtComment = Table(
    "mstSvtComment",
    metadata,
    Column("condValues", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("id", Integer),
    Column("priority", Integer),
    Column("condMessage", String),
    Column("comment", String),
    Column("condType", Integer),
    Column("condValue2", Integer),
)


mstSubtitle = Table(
    "mstSubtitle",
    metadata,
    Column("id", String),
    Column("serif", String),
    Column("svtId", Integer, index=True),
)


mstEquip = Table(
    "mstEquip",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("detail", String),
    Column("condUserLv", Integer),
    Column("maxLv", Integer),
    Column("maleImageId", Integer),
    Column("femaleImageId", Integer),
    Column("imageId", Integer),
    Column("maleSpellId", Integer),
    Column("femaleSpellId", Integer),
)


mstEquipExp = Table(
    "mstEquipExp",
    metadata,
    Column("equipId", Integer, index=True),
    Column("lv", Integer),
    Column("exp", Integer),
    Column("skillLv1", Integer),
    Column("skillLv2", Integer),
    Column("skillLv3", Integer),
)


mstEquipSkill = Table(
    "mstEquipSkill",
    metadata,
    Column("equipId", Integer, index=True),
    Column("num", Integer),
    Column("skillId", Integer),
    Column("condLv", Integer),
)


mstItem = Table(
    "mstItem",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("eventId", Integer),
    Column("eventGroupId", Integer),
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("detail", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer),
    Column("type", Integer),
    Column("unit", String),
    Column("value", Integer),
    Column("sellQp", Integer),
    Column("isSell", Boolean),
    Column("priority", Integer),
    Column("dropPriority", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstCommandCode = Table(
    "mstCommandCode",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("collectionNo", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("rarity", Integer),
    Column("sellQp", Integer),
    Column("sellMana", Integer),
    Column("sellRarePri", Integer),
)


mstCommandCodeSkill = Table(
    "mstCommandCodeSkill",
    metadata,
    Column("commandCodeId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("skillId", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstCommandCodeComment = Table(
    "mstCommandCodeComment",
    metadata,
    Column("commandCodeId", Integer, index=True),
    Column("comment", String),
    Column("illustratorId", Integer),
)


mstCv = Table(
    "mstCv",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("comment", String),
)


mstIllustrator = Table(
    "mstIllustrator",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("comment", String),
)


mstGift = Table(
    "mstGift",
    metadata,
    Column("id", Integer, index=True),
    Column("type", Integer),
    Column("objectId", Integer),
    Column("priority", Integer),
    Column("num", Integer),
)


mstSetItem = Table(
    "mstSetItem",
    metadata,
    Column("id", Integer, index=True),
    Column("purchaseType", Integer),
    Column("targetId", Integer),
    Column("setNum", Integer),
    Column("createdAt", Integer),
)


mstShop = Table(
    "mstShop",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("prices", ARRAY(Integer)),
    Column("targetIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("anotherPayType", Integer),
    Column("anotherItemIds", ARRAY(Integer)),
    Column("useAnotherPayCommonReleaseId", Integer),
    Column("id", Integer, primary_key=True),
    Column("baseShopId", Integer),
    Column("eventId", Integer, index=True),
    Column("slot", Integer),
    Column("flag", Integer),
    Column("priority", Integer),
    Column("purchaseType", Integer),
    Column("setNum", Integer),
    Column("payType", Integer),
    Column("shopType", Integer),
    Column("limitNum", Integer),
    Column("defaultLv", Integer),
    Column("defaultLimitCount", Integer),
    Column("name", String),
    Column("detail", String),
    Column("infoMessage", String),
    Column("warningMessage", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer),
    Column("openedAt", Integer),
    Column("closedAt", Integer),
)


mstEvent = Table(
    "mstEvent",
    metadata,
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("baseEventId", Integer),
    Column("type", Integer),
    Column("openType", Integer),
    Column("name", String),
    Column("shortName", String),
    Column("detail", String),
    Column("noticeBannerId", Integer),
    Column("bannerId", Integer),
    Column("iconId", Integer),
    Column("bannerPriority", Integer),
    Column("openHours", Integer),
    Column("intervalHours", Integer),
    Column("noticeAt", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("finishedAt", Integer),
    Column("materialOpenedAt", Integer),
    Column("linkType", Integer),
    Column("linkBody", String),
    Column("deviceType", Integer),
    Column("myroomBgId", Integer),
    Column("myroomBgmId", Integer),
    Column("createdAt", Integer),
)


mstEventReward = Table(
    "mstEventReward",
    metadata,
    Column("eventId", Integer, index=True),
    Column("groupId", Integer),
    Column("point", Integer),
    Column("type", Integer),
    Column("giftId", Integer),
    Column("bgImageId", Integer),
    Column("presentMessageId", Integer),
)


mstEventPointBuff = Table(
    "mstEventPointBuff",
    metadata,
    Column("funcIds", ARRAY(Integer)),
    Column("id", Integer),
    Column("eventId", Integer, index=True),
    Column("groupId", Integer),
    Column("eventPoint", Integer),
    Column("name", String),
    Column("detail", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer),
    Column("value", Integer),
)


mstEventMission = Table(
    "mstEventMission",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("flag", Integer),
    Column("type", Integer),
    Column("missionTargetId", Integer, index=True),
    Column("dispNo", Integer),
    Column("notfyPriority", Integer),
    Column("name", String),
    Column("detail", String),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("closedAt", Integer),
    Column("rewardType", Integer),
    Column("presentMessageId", Integer),
    Column("giftId", Integer),
    Column("bannerGroup", Integer),
    Column("priority", Integer),
    Column("rewardRarity", Integer),
)


mstEventMissionCondition = Table(
    "mstEventMissionCondition",
    metadata,
    Column("targetIds", ARRAY(Integer)),
    Column("missionId", Integer, index=True),
    Column("missionProgressType", Integer),
    Column("priority", Integer),
    Column("id", Integer),
    Column("missionTargetId", Integer),
    Column("condGroup", Integer),
    Column("condType", Integer),
    Column("targetNum", Integer),
    Column("conditionMessage", String),
    Column("closedMessage", String),
    Column("flag", Integer),
)


mstEventMissionConditionDetail = Table(
    "mstEventMissionConditionDetail",
    metadata,
    Column("targetIds", ARRAY(Integer)),
    Column("addTargetIds", ARRAY(Integer)),
    Column("targetQuestIndividualities", ARRAY(Integer)),
    Column("targetEventIds", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("missionTargetId", Integer),
    Column("missionCondType", Integer),
    Column("logicType", Integer),
    Column("conditionLinkType", Integer),
)


mstEventTower = Table(
    "mstEventTower",
    metadata,
    Column("eventId", Integer, index=True),
    Column("towerId", Integer),
    Column("name", String),
    Column("topFloor", Integer),
    Column("floorLabel", String),
    Column("openEffectId", Integer),
    Column("flag", Integer),
)


mstEventTowerReward = Table(
    "mstEventTowerReward",
    metadata,
    Column("eventId", Integer, index=True),
    Column("towerId", Integer),
    Column("floor", Integer),
    Column("giftId", Integer),
    Column("iconId", Integer),
    Column("presentMessageId", Integer),
    Column("boardMessage", String),
    Column("boardImageId", Integer),
)


mstBoxGacha = Table(
    "mstBoxGacha",
    metadata,
    Column("baseIds", ARRAY(Integer)),
    Column("pickupIds", ARRAY(Integer), nullable=True),
    Column("talkIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer),
    Column("eventId", Integer, index=True),
    Column("slot", Integer),
    Column("guideDisplayName", String),
    Column("payType", Integer),
    Column("payTargetId", Integer),
    Column("payValue", Integer),
    Column("detailUrl", String),
    Column("priority", Integer),
    Column("flag", Integer),
)


mstBoxGachaBase = Table(
    "mstBoxGachaBase",
    metadata,
    Column("id", Integer, index=True),
    Column("no", Integer),
    Column("type", Integer),
    Column("targetId", Integer),
    Column("isRare", Boolean),
    Column("iconId", Integer),
    Column("bannerId", Integer),
    Column("priority", Integer),
    Column("maxNum", Integer),
    Column("detail", String),
)


mstEventRewardSet = Table(
    "mstEventRewardSet",
    metadata,
    Column("rewardSetType", Integer),
    Column("eventId", Integer, index=True),
    Column("id", Integer, index=True),
    Column("iconId", Integer),
    Column("name", String),
    Column("detail", String),
    Column("bgImageId", Integer),
)


mstBgm = Table(
    "mstBgm",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fileName", String),
    Column("name", String),
    Column("priority", Integer),
    Column("detail", String),
    Column("flag", Integer),
    Column("shopId", Integer),
    Column("logoId", Integer),
)


mstWar = Table(
    "mstWar",
    metadata,
    Column("coordinates", JSONB),
    Column("id", Integer, primary_key=True),
    Column("age", String),
    Column("name", String),
    Column("longName", String),
    Column("bannerId", Integer),
    Column("mapImageId", Integer),
    Column("mapImageW", Integer),
    Column("mapImageH", Integer),
    Column("headerImageId", Integer),
    Column("priority", Integer),
    Column("parentWarId", Integer),
    Column("materialParentWarId", Integer),
    Column("flag", Integer),
    Column("emptyMessage", String),
    Column("bgmId", Integer),
    Column("scriptId", String),
    Column("startType", Integer),
    Column("targetId", BigInteger),
    Column("eventId", Integer),
    Column("lastQuestId", Integer),
    Column("assetId", Integer),
)


mstMap = Table(
    "mstMap",
    metadata,
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("warId", Integer),
    Column("mapImageId", Integer),
    Column("mapImageW", Integer),
    Column("mapImageH", Integer),
    Column("headerImageId", Integer),
    Column("bgmId", Integer),
)


mstSpot = Table(
    "mstSpot",
    metadata,
    Column("joinSpotIds", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("warId", Integer, index=True),
    Column("mapId", Integer),
    Column("name", String),
    Column("imageId", Integer),
    Column("x", Integer),
    Column("y", Integer),
    Column("imageOfsX", Integer),
    Column("imageOfsY", Integer),
    Column("nameOfsX", Integer),
    Column("nameOfsY", Integer),
    Column("questOfsX", Integer),
    Column("questOfsY", Integer),
    Column("nextOfsX", Integer),
    Column("nextOfsY", Integer),
    Column("dispCondType1", Integer),
    Column("dispTargetId1", Integer),
    Column("dispTargetValue1", Integer),
    Column("dispCondType2", Integer),
    Column("dispTargetId2", Integer),
    Column("dispTargetValue2", Integer),
    Column("activeCondType", Integer),
    Column("activeTargetId", Integer),
    Column("activeTargetValue", Integer),
    Column("closedMessage", String),
    Column("flag", Integer),
)


mstWarAdd = Table(
    "mstWarAdd",
    metadata,
    Column("script", JSONB),
    Column("warId", Integer, index=True),
    Column("type", Integer),
    Column("priority", Integer),
    Column("overwriteId", Integer),
    Column("overwriteStr", String),
    Column("condType", Integer),
    Column("targetId", Integer),
    Column("value", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstQuest = Table(
    "mstQuest",
    metadata,
    Column("beforeActionVals", ARRAY(String)),
    Column("afterActionVals", ARRAY(String)),
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("nameRuby", String),
    Column("type", Integer),
    Column("consumeType", Integer),
    Column("actConsume", Integer),
    Column("chaldeaGateCategory", Integer),
    Column("spotId", Integer, index=True),
    Column("giftId", Integer),
    Column("priority", Integer),
    Column("bannerType", Integer),
    Column("bannerId", Integer),
    Column("iconId", Integer),
    Column("charaIconId", Integer),
    Column("giftIconId", Integer),
    Column("forceOperation", Integer),
    Column("afterClear", Integer),
    Column("displayHours", Integer),
    Column("intervalHours", Integer),
    Column("chapterId", Integer),
    Column("chapterSubId", Integer),
    Column("chapterSubStr", String),
    Column("recommendLv", String),
    Column("hasStartAction", Integer),
    Column("flag", BigInteger),
    Column("scriptQuestId", Integer),
    Column("noticeAt", Integer),
    Column("openedAt", Integer),
    Column("closedAt", Integer),
)


mstQuestRelease = Table(
    "mstQuestRelease",
    metadata,
    Column("questId", Integer, index=True),
    Column("type", Integer),
    Column("targetId", Integer),
    Column("value", BigInteger),
    Column("openLimit", Integer),
    Column("closedMessageId", Integer),
    Column("imagePriority", Integer),
)


mstClosedMessage = Table(
    "mstClosedMessage",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("message", String),
)


mstQuestConsumeItem = Table(
    "mstQuestConsumeItem",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("nums", ARRAY(Integer)),
    Column("questId", Integer, primary_key=True),
)


mstQuestPhase = Table(
    "mstQuestPhase",
    metadata,
    Column("classIds", ARRAY(Integer)),
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("isNpcOnly", Boolean),
    Column("battleBgId", Integer),
    Column("battleBgType", Integer),
    Column("qp", Integer),
    Column("playerExp", Integer),
    Column("friendshipExp", Integer),
    Column("giftId", Integer),
)


mstQuestPhaseDetail = Table(
    "mstQuestPhaseDetail",
    metadata,
    Column("beforeActionVals", ARRAY(String)),
    Column("afterActionVals", ARRAY(String)),
    Column("boardMessage", JSONB),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("spotId", Integer),
    Column("consumeType", Integer),
    Column("actConsume", Integer),
    Column("flag", BigInteger),
)


mstStage = Table(
    "mstStage",
    metadata,
    Column("npcDeckIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("questId", Integer),
    Column("questPhase", Integer),
    Column("wave", Integer),
    Column("enemyInfo", Integer),
    Column("bgmId", Integer),
    Column("startEffectId", Integer),
)


mstAi = Table(
    "mstAi",
    metadata,
    Column("id", Integer, index=True),
    Column("idx", Integer),
    Column("actNum", Integer),
    Column("priority", Integer),
    Column("probability", Integer),
    Column("cond", Integer),
    Column("vals", ARRAY(Integer)),
    Column("aiActId", Integer),
    Column("avals", ARRAY(Integer)),
    Column("infoText", String),
)


mstAiField = Table(
    "mstAiField",
    metadata,
    Column("id", Integer, index=True),
    Column("idx", Integer),
    Column("script", JSONB),
    Column("actNum", Integer),
    Column("priority", Integer),
    Column("probability", Integer),
    Column("cond", Integer),
    Column("vals", ARRAY(Integer)),
    Column("aiActId", Integer),
    Column("avals", ARRAY(Integer)),
    Column("infoText", String),
    Column("timing", Integer),
)


mstAiAct = Table(
    "mstAiAct",
    metadata,
    Column("targetIndividuality", ARRAY(Integer)),
    Column("skillVals", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("type", Integer),
    Column("target", Integer),
    Column("createdAt", Integer),
)


TABLES_WITH_PK = [
    mstBuff,
    mstFunc,
    mstSkill,
    mstTreasureDevice,
    mstSvt,
    mstVoice,
    mstEquip,
    mstCommandCode,
    mstCv,
    mstIllustrator,
    mstItem,
    mstShop,
    mstBgm,
    mstWar,
    mstMap,
    mstSpot,
    mstQuest,
    mstClosedMessage,
    mstAiAct,
    mstEvent,
    mstEventMission,
    mstEventMissionConditionDetail,
]


TABLES_TO_BE_LOADED = [
    mstConstant,
    mstClassRelationOverwrite,
    mstFuncGroup,
    mstSkillDetail,
    mstSvtSkill,
    mstSkillLv,
    mstTreasureDeviceDetail,
    mstSvtTreasureDevice,
    mstTreasureDeviceLv,
    mstSvtCard,
    mstSvtLimit,
    mstCombineLimit,
    mstCombineSkill,
    mstCombineCostume,
    mstSvtLimitAdd,
    mstSvtChange,
    mstSvtCostume,
    mstSvtVoice,
    mstSvtVoiceRelation,
    mstVoicePlayCond,
    mstSvtComment,
    mstSvtGroup,
    mstSvtScript,
    mstSvtExp,
    mstFriendship,
    mstCombineMaterial,
    mstEquipExp,
    mstEquipSkill,
    mstCommandCodeSkill,
    mstCommandCodeComment,
    mstGift,
    mstSetItem,
    mstEventReward,
    mstEventRewardSet,
    mstEventPointBuff,
    mstEventMissionCondition,
    mstEventTower,
    mstEventTowerReward,
    mstBoxGacha,
    mstBoxGachaBase,
    mstWarAdd,
    mstQuestRelease,
    mstQuestConsumeItem,
    mstQuestPhase,
    mstQuestPhaseDetail,
    mstStage,
    mstAi,
    mstAiField,
]
