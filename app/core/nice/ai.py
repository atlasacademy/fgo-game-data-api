from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import AI_TIMING_NAME, AiTiming
from ...schemas.gameenums import (
    AI_ACT_NUM_NAME,
    AI_ACT_TARGET_NAME,
    AI_ACT_TYPE_NAME,
    AI_COND_NAME,
    AiActType,
    NiceAiActNum,
)
from ...schemas.nice import NiceAi, NiceAiAct, NiceAiCollection, NiceSkill
from ...schemas.raw import AiEntity, MstAiAct
from ..raw import get_ai_collection
from ..utils import get_traits_list
from .skill import get_nice_skill_from_id
from .td import get_nice_td_from_id


settings = Settings()


async def get_nice_ai_act(
    conn: AsyncConnection,
    region: Region,
    mstAiAct: MstAiAct,
    lang: Language = Language.jp,
) -> NiceAiAct:
    nice_ai_act = NiceAiAct(
        id=mstAiAct.id,
        type=AI_ACT_TYPE_NAME[mstAiAct.type],
        target=AI_ACT_TARGET_NAME[mstAiAct.target],
        targetIndividuality=get_traits_list(mstAiAct.targetIndividuality),
    )
    if mstAiAct.type == AiActType.NOBLE_PHANTASM and len(mstAiAct.skillVals) >= 3:
        nice_ai_act.noblePhantasmId = mstAiAct.skillVals[0]
        nice_ai_act.noblePhantasmLv = mstAiAct.skillVals[1]
        nice_ai_act.noblePhantasmOc = mstAiAct.skillVals[2]
        nice_ai_act.noblePhantasm = await get_nice_td_from_id(
            conn, region, mstAiAct.skillVals[0], lang
        )
    elif len(mstAiAct.skillVals) >= 2:
        nice_ai_act.skillId = mstAiAct.skillVals[0]
        nice_ai_act.skillLv = mstAiAct.skillVals[1]
        nice_ai_act.skill = await get_nice_skill_from_id(
            conn, region, mstAiAct.skillVals[0], NiceSkill, lang
        )
    return nice_ai_act


async def get_nice_ai(
    conn: AsyncConnection,
    region: Region,
    one_ai: AiEntity,
    lang: Language = Language.jp,
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
        aiAct=await get_nice_ai_act(conn, region, one_ai.mstAiAct, lang),
        avals=one_ai.mstAi.avals,
        parentAis=one_ai.parentAis,
        infoText=one_ai.mstAi.infoText,
    )
    if one_ai.mstAi.timing:
        nice_ai.timing = one_ai.mstAi.timing
        nice_ai.timingDescription = AI_TIMING_NAME.get(
            one_ai.mstAi.timing, AiTiming.unknown
        )
    return nice_ai


async def get_nice_ai_collection(
    conn: AsyncConnection,
    region: Region,
    ai_id: int,
    field: bool = False,
    lang: Language = Language.jp,
) -> NiceAiCollection:
    full_ai = await get_ai_collection(conn, ai_id, field)
    return NiceAiCollection(
        mainAis=[await get_nice_ai(conn, region, ai, lang) for ai in full_ai.mainAis],
        relatedAis=[
            await get_nice_ai(conn, region, ai, lang) for ai in full_ai.relatedAis
        ],
        relatedQuests=full_ai.relatedQuests,
    )
