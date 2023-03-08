from sqlalchemy.ext.asyncio import AsyncConnection

from ....schemas.common import Language, Region
from ....schemas.nice import NiceItem, NiceServantAppendPassiveSkill, NiceSkill
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
    item_map: dict[int, NiceItem],
    lang: Language,
) -> NiceServantAppendPassiveSkill:
    nice_skill = (
        await get_nice_skill_with_svt(conn, append_skill, svt_id, region, lang)
    )[0]
    items = [item_map[item_id] for item_id in unlock.itemIds]
    nice_unlock = get_nice_item_amount(items, unlock.itemNums)
    return NiceServantAppendPassiveSkill(
        num=svt_append.num,
        priority=svt_append.priority,
        skill=NiceSkill.parse_obj(nice_skill),
        unlockMaterials=nice_unlock,
    )


async def get_nice_svt_append_passives(
    conn: AsyncConnection,
    region: Region,
    svt: ServantEntity,
    item_map: dict[int, NiceItem],
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
            conn, region, svt.mstSvt.id, skill, raw_skill, unlock, item_map, lang
        )
        append_passives.append(append_passive)

    return append_passives
