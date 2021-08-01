from sqlalchemy.ext.asyncio import AsyncConnection

from ....schemas.common import Language, Region
from ....schemas.nice import NiceServantAppendPassiveSkill
from ....schemas.raw import (
    MstSvtAppendPassiveSkill,
    MstSvtAppendPassiveSkillUnlock,
    ServantEntity,
    SkillEntityNoReverse,
)
from ..item import get_nice_item_amount
from ..skill import get_nice_skill_with_svt


async def get_nice_append_passive(
    conn: AsyncConnection,
    region: Region,
    svt_id: int,
    svt_append: MstSvtAppendPassiveSkill,
    append_skill: SkillEntityNoReverse,
    unlock: MstSvtAppendPassiveSkillUnlock,
    lang: Language,
) -> NiceServantAppendPassiveSkill:
    nice_skill = (
        await get_nice_skill_with_svt(conn, append_skill, svt_id, region, lang)
    )[0]
    nice_unlock = await get_nice_item_amount(
        conn,
        region,
        unlock.itemIds,
        unlock.itemNums,
        lang,
    )
    return NiceServantAppendPassiveSkill(
        num=svt_append.num,
        priority=svt_append.priority,
        skill=nice_skill,
        unlockMaterials=nice_unlock,
    )


async def get_nice_svt_append_passives(
    conn: AsyncConnection,
    region: Region,
    svt: ServantEntity,
    lang: Language,
) -> list[NiceServantAppendPassiveSkill]:
    append_passives: list[NiceServantAppendPassiveSkill] = []
    for skill in svt.mstSvtAppendPassiveSkill:
        raw_skill = next(
            raw_skill
            for raw_skill in svt.expandedAppendPassive
            if raw_skill.mstSkill.id == skill.skillId
        )
        unlock = next(
            unlock
            for unlock in svt.mstSvtAppendPassiveSkillUnlock
            if unlock.num == skill.num
        )
        append_passive = await get_nice_append_passive(
            conn, region, svt.mstSvt.id, skill, raw_skill, unlock, lang
        )
        append_passives.append(append_passive)

    return append_passives
