import sqlalchemy
from sqlalchemy import ARRAY, Boolean, Column, Integer, String, Table
from sqlalchemy.dialects.postgresql import JSONB


metadata = sqlalchemy.MetaData()


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
    Column("skillNum", Integer, nullable=True),
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
    Column("effectFlag", Integer, nullable=True),
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


mstSvtVoice = Table(
    "mstSvtVoice",
    metadata,
    Column("scriptJson", JSONB),
    Column("id", Integer, index=True),
    Column("voicePrefix", Integer),
    Column("type", Integer),
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


mstSvtComment = Table(
    "mstSvtComment",
    metadata,
    Column("condValues", ARRAY(Integer), nullable=True),
    Column("svtId", Integer, index=True),
    Column("id", Integer),
    Column("priority", Integer),
    Column("condMessage", String),
    Column("comment", String),
    Column("condType", Integer),
    Column("condValue2", Integer),
)


mstShop = Table(
    "mstShop",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("prices", ARRAY(Integer)),
    Column("targetIds", ARRAY(Integer)),
    Column("script", JSONB),
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


TABLES_TO_BE_LOADED = [
    mstSkill,
    mstSkillDetail,
    mstSvtSkill,
    mstSkillLv,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstSvtTreasureDevice,
    mstTreasureDeviceLv,
    mstSvtVoice,
    mstSvtComment,
    mstShop,
    mstAi,
    mstAiField,
    mstAiAct,
]
