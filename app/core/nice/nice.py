from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...redis import Redis
from ...redis.helpers.reverse import RedisReverse, get_reverse_ids
from ...schemas.basic import (
    BasicReversedBuff,
    BasicReversedFunction,
    BasicReversedSkillTd,
)
from ...schemas.common import Language, Region, ReverseData, ReverseDepth
from ...schemas.nice import (
    NiceBaseFunctionReverse,
    NiceBuffReverse,
    NiceEquip,
    NiceReversedBuff,
    NiceReversedBuffType,
    NiceReversedFunction,
    NiceReversedFunctionType,
    NiceReversedSkillTd,
    NiceReversedSkillTdType,
    NiceServant,
    NiceSkillReverse,
    NiceTdReverse,
)
from ...schemas.raw import MstBuff, MstFunc, MstSvt, ServantEntity
from .. import raw
from ..basic import (
    get_basic_cc,
    get_basic_function,
    get_basic_mc,
    get_basic_servant,
    get_basic_skill,
    get_basic_td,
)
from .buff import get_nice_buff
from .cc import get_nice_command_code
from .func import get_nice_function
from .mc import get_nice_mystic_code
from .skill import get_nice_skill_from_raw
from .svt.svt import get_nice_servant
from .td import get_nice_td


settings = Settings()


async def get_nice_servant_model(
    conn: AsyncConnection,
    region: Region,
    item_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
    raw_svt: Optional[ServantEntity] = None,
) -> NiceServant:
    return NiceServant.parse_obj(
        await get_nice_servant(conn, region, item_id, lang, lore, mstSvt, raw_svt)
    )


async def get_nice_equip_model(
    conn: AsyncConnection,
    region: Region,
    item_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
    raw_svt: Optional[ServantEntity] = None,
) -> NiceEquip:
    return NiceEquip.parse_obj(
        await get_nice_servant(conn, region, item_id, lang, lore, mstSvt, raw_svt)
    )


async def get_nice_buff_with_reverse(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
    mstBuff: Optional[MstBuff] = None,
) -> NiceBuffReverse:
    raw_buff = await raw.get_buff_entity_no_reverse(conn, buff_id, mstBuff)
    nice_buff = NiceBuffReverse.parse_obj(get_nice_buff(raw_buff, region))
    if reverse and reverseDepth >= ReverseDepth.function:
        func_ids = await get_reverse_ids(
            redis, region, RedisReverse.BUFF_TO_FUNC, buff_id
        )
        if reverseData == ReverseData.basic:
            basic_buff_reverse = BasicReversedBuff(
                function=[
                    await get_basic_function(
                        redis, region, func_id, lang, reverse, reverseDepth
                    )
                    for func_id in func_ids
                ]
            )
            nice_buff.reverse = NiceReversedBuffType(basic=basic_buff_reverse)
        else:
            buff_reverse = NiceReversedBuff(
                function=[
                    await get_nice_func_with_reverse(
                        conn, redis, region, func_id, lang, reverse, reverseDepth
                    )
                    for func_id in func_ids
                ]
            )
            nice_buff.reverse = NiceReversedBuffType(nice=buff_reverse)
    return nice_buff


async def get_nice_func_with_reverse(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
    mstFunc: Optional[MstFunc] = None,
) -> NiceBaseFunctionReverse:
    raw_func = await raw.get_func_entity_no_reverse(conn, func_id, True, mstFunc)
    nice_func = NiceBaseFunctionReverse.parse_obj(
        await get_nice_function(conn, region, raw_func)
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        skill_ids = await get_reverse_ids(
            redis, region, RedisReverse.FUNC_TO_SKILL, func_id
        )
        td_ids = await get_reverse_ids(redis, region, RedisReverse.FUNC_TO_TD, func_id)
        if reverseData == ReverseData.basic:
            basic_func_reverse = BasicReversedFunction(
                skill=[
                    await get_basic_skill(
                        redis, region, skill_id, lang, reverse, reverseDepth
                    )
                    for skill_id in skill_ids
                ],
                NP=[
                    await get_basic_td(
                        redis, region, td_id, lang, reverse, reverseDepth
                    )
                    for td_id in td_ids
                ],
            )
            nice_func.reverse = NiceReversedFunctionType(basic=basic_func_reverse)
        else:
            func_reverse = NiceReversedFunction(
                skill=[
                    await get_nice_skill_with_reverse(
                        conn, redis, region, skill_id, lang, reverse, reverseDepth
                    )
                    for skill_id in skill_ids
                ],
                NP=[
                    await get_nice_td_with_reverse(
                        conn, redis, region, td_id, lang, reverse, reverseDepth
                    )
                    for td_id in td_ids
                ],
            )
            nice_func.reverse = NiceReversedFunctionType(nice=func_reverse)
    return nice_func


async def get_nice_skill_with_reverse(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceSkillReverse:
    raw_skill = await raw.get_skill_entity_no_reverse(conn, skill_id, expand=True)
    nice_skill = await get_nice_skill_from_raw(
        conn, region, raw_skill, NiceSkillReverse, lang
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in raw_skill.mstSvtSkill}

        passiveSkills = set(
            await get_reverse_ids(
                redis, region, RedisReverse.PASSIVE_SKILL_TO_SVT, skill_id
            )
        )
        mc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_MC, skill_id
        )
        cc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_CC, skill_id
        )

        if reverseData == ReverseData.basic:
            basic_skill_reverse = BasicReversedSkillTd(
                servant=[
                    await get_basic_servant(redis, region, svt_id, lang=lang)
                    for svt_id in sorted(activeSkills | passiveSkills)
                ],
                MC=[await get_basic_mc(redis, region, mc_id, lang) for mc_id in mc_ids],
                CC=[await get_basic_cc(redis, region, cc_id, lang) for cc_id in cc_ids],
            )
            nice_skill.reverse = NiceReversedSkillTdType(basic=basic_skill_reverse)
        else:
            skill_reverse = NiceReversedSkillTd(
                servant=[
                    await get_nice_servant_model(conn, region, svt_id, lang=lang)
                    for svt_id in sorted(activeSkills | passiveSkills)
                ],
                MC=[
                    await get_nice_mystic_code(conn, region, mc_id, lang)
                    for mc_id in mc_ids
                ],
                CC=[
                    await get_nice_command_code(conn, region, cc_id, lang)
                    for cc_id in cc_ids
                ],
            )
            nice_skill.reverse = NiceReversedSkillTdType(nice=skill_reverse)
    return nice_skill


async def get_nice_td_with_reverse(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceTdReverse:
    raw_td = await raw.get_td_entity_no_reverse(conn, td_id, expand=True)

    nice_td = NiceTdReverse.parse_obj(
        (await get_nice_td(conn, raw_td, -1, region, lang))[0]
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        if reverseData == ReverseData.basic:
            basic_td_reverse = BasicReversedSkillTd(
                servant=[
                    await get_basic_servant(redis, region, svt_id.svtId, lang=lang)
                    for svt_id in raw_td.mstSvtTreasureDevice
                ]
            )
            nice_td.reverse = NiceReversedSkillTdType(basic=basic_td_reverse)
        else:
            td_reverse = NiceReversedSkillTd(
                servant=[
                    await get_nice_servant_model(conn, region, svt_id.svtId, lang=lang)
                    for svt_id in raw_td.mstSvtTreasureDevice
                ]
            )
            nice_td.reverse = NiceReversedSkillTdType(nice=td_reverse)
    return nice_td
