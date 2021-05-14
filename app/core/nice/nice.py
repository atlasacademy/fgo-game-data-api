from typing import Optional

from sqlalchemy.engine import Connection

from ...config import Settings
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
from ...schemas.raw import MstBuff, MstFunc, MstSvt
from .. import raw, reverse as reverse_ids
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


def get_nice_servant_model(
    conn: Connection,
    region: Region,
    item_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
) -> NiceServant:
    return NiceServant.parse_obj(
        get_nice_servant(conn, region, item_id, lang, lore, mstSvt)
    )


def get_nice_equip_model(
    conn: Connection,
    region: Region,
    item_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
) -> NiceEquip:
    return NiceEquip.parse_obj(
        get_nice_servant(conn, region, item_id, lang, lore, mstSvt)
    )


def get_nice_buff_with_reverse(
    conn: Connection,
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
    mstBuff: Optional[MstBuff] = None,
) -> NiceBuffReverse:
    raw_buff = raw.get_buff_entity_no_reverse(region, buff_id, mstBuff)
    nice_buff = NiceBuffReverse.parse_obj(get_nice_buff(raw_buff, region))
    if reverse and reverseDepth >= ReverseDepth.function:
        if reverseData == ReverseData.basic:
            basic_buff_reverse = BasicReversedBuff(
                function=(
                    get_basic_function(region, func_id, lang, reverse, reverseDepth)
                    for func_id in reverse_ids.buff_to_func(region, buff_id)
                )
            )
            nice_buff.reverse = NiceReversedBuffType(basic=basic_buff_reverse)
        else:
            buff_reverse = NiceReversedBuff(
                function=(
                    get_nice_func_with_reverse(
                        conn, region, func_id, lang, reverse, reverseDepth
                    )
                    for func_id in reverse_ids.buff_to_func(region, buff_id)
                )
            )
            nice_buff.reverse = NiceReversedBuffType(nice=buff_reverse)
    return nice_buff


def get_nice_func_with_reverse(
    conn: Connection,
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
    mstFunc: Optional[MstFunc] = None,
) -> NiceBaseFunctionReverse:
    raw_func = raw.get_func_entity_no_reverse(region, func_id, True, mstFunc)
    nice_func = NiceBaseFunctionReverse.parse_obj(get_nice_function(region, raw_func))

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        if reverseData == ReverseData.basic:
            basic_func_reverse = BasicReversedFunction(
                skill=(
                    get_basic_skill(region, skill_id, lang, reverse, reverseDepth)
                    for skill_id in reverse_ids.func_to_skillId(region, func_id)
                ),
                NP=(
                    get_basic_td(region, td_id, lang, reverse, reverseDepth)
                    for td_id in reverse_ids.func_to_tdId(region, func_id)
                ),
            )
            nice_func.reverse = NiceReversedFunctionType(basic=basic_func_reverse)
        else:
            func_reverse = NiceReversedFunction(
                skill=(
                    get_nice_skill_with_reverse(
                        conn, region, skill_id, lang, reverse, reverseDepth
                    )
                    for skill_id in reverse_ids.func_to_skillId(region, func_id)
                ),
                NP=(
                    get_nice_td_with_reverse(
                        conn, region, td_id, lang, reverse, reverseDepth
                    )
                    for td_id in reverse_ids.func_to_tdId(region, func_id)
                ),
            )
            nice_func.reverse = NiceReversedFunctionType(nice=func_reverse)
    return nice_func


def get_nice_skill_with_reverse(
    conn: Connection,
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceSkillReverse:
    raw_skill = raw.get_skill_entity_no_reverse(conn, skill_id, expand=True)
    nice_skill = get_nice_skill_from_raw(region, raw_skill, lang)

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in raw_skill.mstSvtSkill}
        passiveSkills = reverse_ids.passive_to_svtId(region, skill_id)
        if reverseData == ReverseData.basic:
            basic_skill_reverse = BasicReversedSkillTd(
                servant=(
                    get_basic_servant(region, svt_id, lang=lang)
                    for svt_id in activeSkills | passiveSkills
                ),
                MC=(
                    get_basic_mc(region, mc_id, lang)
                    for mc_id in reverse_ids.skill_to_MCId(region, skill_id)
                ),
                CC=(
                    get_basic_cc(region, cc_id, lang)
                    for cc_id in reverse_ids.skill_to_CCId(region, skill_id)
                ),
            )
            nice_skill.reverse = NiceReversedSkillTdType(basic=basic_skill_reverse)
        else:
            skill_reverse = NiceReversedSkillTd(
                servant=(
                    get_nice_servant_model(conn, region, svt_id, lang=lang)
                    for svt_id in activeSkills | passiveSkills
                ),
                MC=(
                    get_nice_mystic_code(conn, region, mc_id, lang)
                    for mc_id in reverse_ids.skill_to_MCId(region, skill_id)
                ),
                CC=(
                    get_nice_command_code(conn, region, cc_id, lang)
                    for cc_id in reverse_ids.skill_to_CCId(region, skill_id)
                ),
            )
            nice_skill.reverse = NiceReversedSkillTdType(nice=skill_reverse)
    return nice_skill


def get_nice_td_with_reverse(
    conn: Connection,
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceTdReverse:
    raw_td = raw.get_td_entity_no_reverse(conn, td_id, expand=True)

    # All td_id has a svtTd entry
    svt_id = next(svt_id.svtId for svt_id in raw_td.mstSvtTreasureDevice)
    nice_td = NiceTdReverse.parse_obj(get_nice_td(raw_td, svt_id, region, lang)[0])

    if reverse and reverseDepth >= ReverseDepth.servant:
        if reverseData == ReverseData.basic:
            basic_td_reverse = BasicReversedSkillTd(
                servant=[
                    get_basic_servant(region, svt_id.svtId, lang=lang)
                    for svt_id in raw_td.mstSvtTreasureDevice
                ]
            )
            nice_td.reverse = NiceReversedSkillTdType(basic=basic_td_reverse)
        else:
            td_reverse = NiceReversedSkillTd(
                servant=[
                    get_nice_servant_model(conn, region, svt_id.svtId, lang=lang)
                    for svt_id in raw_td.mstSvtTreasureDevice
                ]
            )
            nice_td.reverse = NiceReversedSkillTdType(nice=td_reverse)
    return nice_td
