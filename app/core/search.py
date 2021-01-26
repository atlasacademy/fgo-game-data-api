from typing import Iterable, List, Set, Union

from fastapi import HTTPException
from fuzzywuzzy import fuzz, utils
from sqlalchemy.engine import Connection

from ..data.gamedata import masters
from ..data.translations import TRANSLATIONS
from ..db.helpers.svt import get_related_voice_id
from ..schemas.common import Region
from ..schemas.enums import (
    ATTRIBUTE_NAME_REVERSE,
    BUFF_TYPE_NAME_REVERSE,
    CARD_TYPE_NAME_REVERSE,
    CLASS_NAME_REVERSE,
    FUNC_APPLYTARGET_NAME_REVERSE,
    FUNC_TARGETTYPE_NAME_REVERSE,
    FUNC_TYPE_NAME_REVERSE,
    GENDER_TYPE_NAME_REVERSE,
    SKILL_TYPE_NAME_REVERSE,
    SVT_FLAG_NAME_REVERSE,
    SVT_TYPE_NAME_REVERSE,
    TRAIT_NAME_REVERSE,
    Trait,
)
from ..schemas.search import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SkillSearchParamsDefault,
    SvtSearchQueryParams,
    TdSearchParams,
    TdSearchParamsDefault,
)
from .utils import get_safe


INSUFFICIENT_QUERY = (
    "Insufficient query. Please check the docs for the required parameters."
)
TOO_MANY_RESULTS = "More than {} items found. Please narrow down the query."


def reverse_traits(traits: Iterable[Union[Trait, int]]) -> Set[int]:
    return {
        TRAIT_NAME_REVERSE[trait] if isinstance(trait, Trait) else trait
        for trait in traits
    }


accent_from = "àáâäèéëíðñóöùúāēīŋōšαβḗḫ"
accent_to__ = "aaaaeeeidnoouuaeinosabeh"
translation_table = {ord(k): v for k, v in zip(accent_from, accent_to__)}


SPECIAL_REPLACE = {"artoria": "altria"}


def match_name(search_param: str, name: str) -> bool:
    """Modified from fuzzywuzzy.token_set_ratio"""
    p1 = utils.full_process(search_param).translate(translation_table)
    p2 = utils.full_process(name).translate(translation_table)

    for k, v in SPECIAL_REPLACE.items():
        p1 = p1.replace(k, v)
        p2 = p2.replace(k, v)

    if not utils.validate_string(p1):
        return False
    if not utils.validate_string(p2):
        return False

    # Doesn't seem to be needed now but might be useful in the future
    # ALTERNATIVE_DIVIDER = ["-", "="]
    # for divider in ALTERNATIVE_DIVIDER:
    #     p1 = p1.replace(divider, " ")
    #     p2 = p2.replace(divider, " ")

    if p1 in p2:
        return True

    # pull tokens
    tokens1 = set(p1.split())
    tokens2 = set(p2.split())

    intersection = tokens1.intersection(tokens2)
    diff1to2 = tokens1.difference(tokens2)
    diff2to1 = tokens2.difference(tokens1)

    sorted_sect = " ".join(sorted(intersection))
    sorted_1to2 = " ".join(sorted(diff1to2))
    sorted_2to1 = " ".join(sorted(diff2to1))

    combined_1to2 = sorted_sect + " " + sorted_1to2
    combined_2to1 = sorted_sect + " " + sorted_2to1

    # strip
    sorted_sect = sorted_sect.strip()
    combined_1to2 = combined_1to2.strip()
    combined_2to1 = combined_2to1.strip()

    NAME_MATCH_THRESHOLD = 80

    # Use sorted_sect first so "Okita Souji (Alter)" works as expected
    # This way "a b c" search_param will match to "a b c d e" but not vice versa
    if sorted_sect:
        return fuzz.ratio(sorted_sect, combined_1to2) > NAME_MATCH_THRESHOLD
    else:
        return fuzz.ratio(combined_2to1, combined_1to2) > NAME_MATCH_THRESHOLD


def search_servant(
    conn: Connection,
    search_param: Union[ServantSearchQueryParams, SvtSearchQueryParams],
    limit: int = 100,
) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    svt_type_ints = {SVT_TYPE_NAME_REVERSE[svt_type] for svt_type in search_param.type}
    svt_flag_ints = {SVT_FLAG_NAME_REVERSE[svt_flag] for svt_flag in search_param.flag}
    rarity_ints = set(search_param.rarity)
    class_ints = {CLASS_NAME_REVERSE[svt_class] for svt_class in search_param.className}
    gender_ints = {
        GENDER_TYPE_NAME_REVERSE[svt_gender] for svt_gender in search_param.gender
    }
    attribute_ints = {
        ATTRIBUTE_NAME_REVERSE[svt_attribute]
        for svt_attribute in search_param.attribute
    }
    trait_ints = reverse_traits(search_param.trait)

    matches = [
        svt
        for svt in masters[search_param.region].mstSvt
        if svt.type in svt_type_ints
        and svt.flag in svt_flag_ints
        and svt.collectionNo not in search_param.excludeCollectionNo
        and svt.classId in class_ints
        and svt.genderType in gender_ints
        and svt.attri in attribute_ints
        and (
            trait_ints.issubset(svt.individuality)
            or any(
                trait_ints.issubset(limit.individuality)
                for limit in masters[search_param.region].mstSvtLimitAddId.get(
                    svt.id, []
                )
            )
        )
        and masters[search_param.region].mstSvtLimitId[svt.id][0].rarity in rarity_ints
    ]

    if search_param.voiceCondSvt:
        converted_to_svt_id = {
            masters[search_param.region].mstSvtServantCollectionNo.get(svt_id, svt_id)
            for svt_id in search_param.voiceCondSvt
        }
        voice_cond_svt = {
            svt_id
            for svt_id in converted_to_svt_id
            if svt_id in masters[search_param.region].mstSvtServantCollectionNo.values()
        }
        voice_cond_group = {
            group.id
            for svt_id in converted_to_svt_id
            for group in masters[search_param.region].mstSvtGroupSvtId.get(svt_id, [])
        }
        voice_svt_id = get_related_voice_id(conn, voice_cond_svt, voice_cond_group)
        matches = [svt for svt in matches if svt.id in voice_svt_id]

    if search_param.name:
        matches = [
            svt
            for svt in matches
            if match_name(search_param.name, svt.name)
            or match_name(search_param.name, svt.ruby)
            or match_name(search_param.name, get_safe(TRANSLATIONS, svt.name))
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [svt.id for svt in matches]


def search_equip(search_param: EquipSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    svt_type = {SVT_TYPE_NAME_REVERSE[svt_type] for svt_type in search_param.type}
    svt_flag_ints = {SVT_FLAG_NAME_REVERSE[svt_flag] for svt_flag in search_param.flag}
    rarity = set(search_param.rarity)

    matches = [
        svt
        for svt in masters[search_param.region].mstSvt
        if svt.type in svt_type
        and svt.flag in svt_flag_ints
        and svt.collectionNo not in search_param.excludeCollectionNo
        and masters[search_param.region].mstSvtLimitId[svt.id][0].rarity in rarity
    ]

    if search_param.name:
        matches = [
            svt
            for svt in matches
            if match_name(search_param.name, svt.name)
            or match_name(search_param.name, svt.ruby)
            or match_name(search_param.name, get_safe(TRANSLATIONS, svt.name))
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [svt.id for svt in matches]


def search_skill_svt(
    region: Region,
    skill_id: int,
    num: List[int],
    priority: List[int],
    strengthStatus: List[int],
) -> bool:
    svt_skills = masters[region].mstSvtSkillId.get(skill_id, [])
    if svt_skills:
        return any(
            svt_skill.num in num
            and svt_skill.priority in priority
            and svt_skill.strengthStatus in strengthStatus
            for svt_skill in svt_skills
        )
    else:
        return (
            num == SkillSearchParamsDefault.num
            and priority == SkillSearchParamsDefault.priority
            and strengthStatus == SkillSearchParamsDefault.strengthStatus
        )


def search_skill_lv(
    region: Region, skill_id: int, lvl1coolDown: List[int], numFunctions: List[int]
) -> bool:
    skill_lv_1 = next(
        skill_lv
        for skill_lv in masters[region].mstSkillLvId[skill_id]
        if skill_lv.lv == 1
    )
    return (
        skill_lv_1.chargeTurn in lvl1coolDown and len(skill_lv_1.funcId) in numFunctions
    )


def search_skill(search_param: SkillSearchParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    type_ints = {
        SKILL_TYPE_NAME_REVERSE[skill_type] for skill_type in search_param.type
    }
    num = search_param.num if search_param.num else SkillSearchParamsDefault.num
    priority = (
        search_param.priority
        if search_param.priority
        else SkillSearchParamsDefault.priority
    )
    strengthStatus = (
        search_param.strengthStatus
        if search_param.strengthStatus
        else SkillSearchParamsDefault.strengthStatus
    )
    lvl1coolDown = (
        search_param.lvl1coolDown
        if search_param.lvl1coolDown
        else SkillSearchParamsDefault.lvl1coolDown
    )
    numFunctions = (
        search_param.numFunctions
        if search_param.numFunctions
        else SkillSearchParamsDefault.numFunctions
    )

    matches = [
        skill
        for skill in masters[search_param.region].mstSkill
        if skill.type in type_ints
        and search_skill_svt(
            search_param.region, skill.id, num, priority, strengthStatus
        )
        and search_skill_lv(search_param.region, skill.id, lvl1coolDown, numFunctions)
    ]

    if search_param.name:
        matches = [
            skill
            for skill in matches
            if match_name(search_param.name, skill.name)
            or match_name(search_param.name, skill.ruby)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [skill.id for skill in matches]


def search_td_svt(
    region: Region,
    td_id: int,
    card: Set[int],
    hits: List[int],
    strengthStatus: List[int],
) -> bool:
    svt_tds = masters[region].mstSvtTreasureDeviceId[td_id]
    return any(
        svt_td.cardId in card
        and len(svt_td.damage) in hits
        and svt_td.strengthStatus in strengthStatus
        for svt_td in svt_tds
    )


def search_td_lv(
    region: Region,
    td_id: int,
    numFunctions: List[int],
    minNpNpGain: int,
    maxNpNpGain: int,
) -> bool:
    td_lv_1 = next(
        td_lv for td_lv in masters[region].mstTreasureDeviceLvId[td_id] if td_lv.lv == 1
    )
    return (
        len(td_lv_1.funcId) in numFunctions
        and minNpNpGain <= td_lv_1.tdPoint <= maxNpNpGain
    )


def search_td(search_param: TdSearchParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    card_ints = {CARD_TYPE_NAME_REVERSE[td_catd] for td_catd in search_param.card}
    individuality = reverse_traits(search_param.individuality)
    hits = search_param.hits if search_param.hits else TdSearchParamsDefault.hits
    strengthStatus = (
        search_param.strengthStatus
        if search_param.strengthStatus
        else TdSearchParamsDefault.strengthStatus
    )
    numFunctions = (
        search_param.numFunctions
        if search_param.numFunctions
        else TdSearchParamsDefault.numFunctions
    )

    matches = [
        td
        for td in masters[search_param.region].mstTreasureDevice
        if individuality.issubset(td.individuality)
        and search_td_svt(search_param.region, td.id, card_ints, hits, strengthStatus)
        and search_td_lv(
            search_param.region,
            td.id,
            numFunctions,
            search_param.minNpNpGain,
            search_param.maxNpNpGain,
        )
    ]

    if search_param.name:
        matches = [
            td
            for td in matches
            if match_name(search_param.name, td.name)
            or match_name(search_param.name, td.ruby)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [td.id for td in matches]


def search_buff(search_param: BuffSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    buff_types = {BUFF_TYPE_NAME_REVERSE[buff_type] for buff_type in search_param.type}
    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    ckSelfIndv = reverse_traits(search_param.ckSelfIndv)
    ckOpIndv = reverse_traits(search_param.ckOpIndv)

    matches = [
        buff
        for buff in masters[search_param.region].mstBuff
        if ((not search_param.type) or (search_param.type and buff.type in buff_types))
        and (
            (not search_param.buffGroup)
            or (search_param.buffGroup and buff.buffGroup in search_param.buffGroup)
        )
        and vals.issubset(buff.vals)
        and tvals.issubset(buff.tvals)
        and ckSelfIndv.issubset(buff.ckSelfIndv)
        and ckOpIndv.issubset(buff.ckOpIndv)
    ]

    if search_param.name:
        matches = [
            buff
            for buff in matches
            if match_name(search_param.name, buff.name)
            or match_name(search_param.name, buff.detail)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [buff.id for buff in matches]


def search_func(search_param: FuncSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    func_types = {FUNC_TYPE_NAME_REVERSE[func_type] for func_type in search_param.type}
    target_types = {
        FUNC_TARGETTYPE_NAME_REVERSE[func_targettype]
        for func_targettype in search_param.targetType
    }
    apply_targets = {
        FUNC_APPLYTARGET_NAME_REVERSE[func_applytarget]
        for func_applytarget in search_param.targetTeam
    }
    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    questTvals = reverse_traits(search_param.questTvals)

    matches = [
        func
        for func in masters[search_param.region].mstFunc
        if (
            (not search_param.type)
            or (search_param.type and func.funcType in func_types)
        )
        and (
            (not search_param.targetType)
            or (search_param.targetType and func.targetType in target_types)
        )
        and (
            (not search_param.targetTeam)
            or (search_param.targetTeam and func.applyTarget in apply_targets)
        )
        and vals.issubset(func.vals)
        and tvals.issubset(func.tvals)
        and questTvals.issubset(func.questTvals)
    ]

    if search_param.popupText:
        matches = [
            func
            for func in matches
            if match_name(search_param.popupText, func.popupText)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [func.id for func in matches]
