from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Language, Region
from ...schemas.enums import (
    AI_ACT_NUM_NAME,
    AI_ACT_TARGET_NAME,
    AI_ACT_TYPE_NAME,
    AI_COND_NAME,
    AI_TIMING_NAME,
    AiTiming,
    AiType,
    NiceAiActNum,
)
from ...schemas.nice import NiceAi, NiceAiAct, NiceAiCollection
from ...schemas.raw import AiEntity, MstAiAct
from ..raw import get_ai_collection
from ..utils import get_traits_list
from .skill import get_nice_skill_from_id


settings = Settings()


def get_nice_ai_act(conn: Connection, region: Region, mstAiAct: MstAiAct) -> NiceAiAct:
    nice_ai_act = NiceAiAct(
        id=mstAiAct.id,
        type=AI_ACT_TYPE_NAME[mstAiAct.type],
        target=AI_ACT_TARGET_NAME[mstAiAct.target],
        targetIndividuality=get_traits_list(mstAiAct.targetIndividuality),
    )
    if len(mstAiAct.skillVals) >= 2:
        nice_ai_act.skillId = mstAiAct.skillVals[0]
        nice_ai_act.skillLv = mstAiAct.skillVals[1]
        nice_ai_act.skill = get_nice_skill_from_id(
            conn,
            region,
            mstAiAct.skillVals[0],
            Language.jp if region == Region.JP else Language.en,
        )
    return nice_ai_act


def get_parent_ais(
    region: Region, ai_id: int, field: bool = False
) -> dict[AiType, list[int]]:
    if field:
        return {
            AiType.svt: [],
            AiType.field: sorted(masters[region].parentAiField.get(ai_id, [])),
        }
    else:
        return {
            AiType.svt: sorted(masters[region].parentAiSvt.get(ai_id, [])),
            AiType.field: [],
        }


def get_nice_ai(
    conn: Connection, region: Region, one_ai: AiEntity, field: bool = False
) -> NiceAi:
    nice_ai = NiceAi(
        id=one_ai.mstAi.id,
        idx=one_ai.mstAi.idx,
        actNumInt=one_ai.mstAi.actNum,
        actNum=AI_ACT_NUM_NAME.get(one_ai.mstAi.actNum, NiceAiActNum.unknown),
        priority=one_ai.mstAi.priority,
        probability=one_ai.mstAi.probability,
        cond=AI_COND_NAME[
            one_ai.mstAi.cond if one_ai.mstAi.cond >= 0 else -one_ai.mstAi.cond
        ],
        condNegative=one_ai.mstAi.cond < 0,
        vals=one_ai.mstAi.vals,
        aiAct=get_nice_ai_act(conn, region, one_ai.mstAiAct),
        avals=one_ai.mstAi.avals,
        parentAis=get_parent_ais(region, one_ai.mstAi.id, field),
        infoText=one_ai.mstAi.infoText,
    )
    if one_ai.mstAi.timing:
        nice_ai.timing = one_ai.mstAi.timing
        nice_ai.timingDescription = AI_TIMING_NAME.get(
            one_ai.mstAi.timing, AiTiming.unknown
        )
    return nice_ai


def get_nice_ai_collection(
    conn: Connection, region: Region, ai_id: int, field: bool = False
) -> NiceAiCollection:
    full_ai = get_ai_collection(conn, ai_id, field)
    return NiceAiCollection(
        mainAis=(get_nice_ai(conn, region, ai, field) for ai in full_ai.mainAis),
        relatedAis=(get_nice_ai(conn, region, ai, field) for ai in full_ai.relatedAis),
    )
