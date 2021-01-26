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
    mstAi,
    mstAiField,
    mstAiAct,
]
