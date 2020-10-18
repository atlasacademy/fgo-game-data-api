from typing import Iterable, List, Set, Union

from fastapi import HTTPException
from fuzzywuzzy import fuzz, utils

from ..routers.deps import (
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
from .common import Region
from .enums import (
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
from .gamedata import masters
from .translations import TRANSLATIONS
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
    search_param: Union[ServantSearchQueryParams, SvtSearchQueryParams],
    limit: int = 100,
) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    svt_type_ints = {SVT_TYPE_NAME_REVERSE[item] for item in search_param.type}
    svt_flag_ints = {SVT_FLAG_NAME_REVERSE[item] for item in search_param.flag}
    rarity_ints = set(search_param.rarity)
    class_ints = {CLASS_NAME_REVERSE[item] for item in search_param.className}
    gender_ints = {GENDER_TYPE_NAME_REVERSE[item] for item in search_param.gender}
    attribute_ints = {ATTRIBUTE_NAME_REVERSE[item] for item in search_param.attribute}
    trait_ints = reverse_traits(search_param.trait)

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.type in svt_type_ints
        and item.flag in svt_flag_ints
        and item.collectionNo not in search_param.excludeCollectionNo
        and item.classId in class_ints
        and item.genderType in gender_ints
        and item.attri in attribute_ints
        and (
            trait_ints.issubset(item.individuality)
            or any(
                [
                    trait_ints.issubset(limit.individuality)
                    for limit in masters[search_param.region].mstSvtLimitAddId.get(
                        item.id, []
                    )
                ]
            )
        )
        and masters[search_param.region].mstSvtLimitId[item.id][0].rarity in rarity_ints
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
            or match_name(search_param.name, get_safe(TRANSLATIONS, item.name))
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]


def search_equip(search_param: EquipSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    svt_type = {SVT_TYPE_NAME_REVERSE[item] for item in search_param.type}
    svt_flag_ints = {SVT_FLAG_NAME_REVERSE[item] for item in search_param.flag}
    rarity = set(search_param.rarity)

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.type in svt_type
        and item.flag in svt_flag_ints
        and item.collectionNo not in search_param.excludeCollectionNo
        and masters[search_param.region].mstSvtLimitId[item.id][0].rarity in rarity
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
            or match_name(search_param.name, get_safe(TRANSLATIONS, item.name))
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]


def search_skill_svt(
    region: Region,
    skill_id: int,
    num: List[int],
    priority: List[int],
    strengthStatus: List[int],
) -> bool:
    svt_skills = masters[region].mstSvtSkillId.get(skill_id, [])
    if svt_skills:
        svt_skill = svt_skills[0]
        return (
            svt_skill.num in num
            and svt_skill.priority in priority
            and svt_skill.strengthStatus in strengthStatus
        )
    else:
        return (
            num == SkillSearchParamsDefault.num
            and priority == SkillSearchParamsDefault.priority
            and strengthStatus == SkillSearchParamsDefault.strengthStatus
        )


def search_skill_lv(
    region: Region, skill_id: int, lvl1coolDown: List[int], numFunctions: List[int],
) -> bool:
    skill_lv = masters[region].mstSkillLvId[skill_id][0]
    return skill_lv.chargeTurn in lvl1coolDown and len(skill_lv.funcId) in numFunctions


def search_skill(search_param: SkillSearchParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    type_ints = {SKILL_TYPE_NAME_REVERSE[item] for item in search_param.type}
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
        item
        for item in masters[search_param.region].mstSkill
        if item.type in type_ints
        and search_skill_svt(
            search_param.region, item.id, num, priority, strengthStatus,
        )
        and search_skill_lv(search_param.region, item.id, lvl1coolDown, numFunctions,)
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]


def search_td_svt(
    region: Region,
    td_id: int,
    card: Set[int],
    hits: List[int],
    strengthStatus: List[int],
) -> bool:
    svt_td = masters[region].mstSvtTreasureDeviceId[td_id][0]
    return (
        svt_td.cardId in card
        and len(svt_td.damage) in hits
        and svt_td.strengthStatus in strengthStatus
    )


def search_td_lv(
    region: Region,
    td_id: int,
    numFunctions: List[int],
    minNpNpGain: int,
    maxNpNpGain: int,
) -> bool:
    td_lv = masters[region].mstTreasureDeviceLvId[td_id][0]
    return (
        len(td_lv.funcId) in numFunctions
        and minNpNpGain <= td_lv.tdPoint <= maxNpNpGain
    )


def search_td(search_param: TdSearchParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    card_ints = {CARD_TYPE_NAME_REVERSE[item] for item in search_param.card}
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
        item
        for item in masters[search_param.region].mstTreasureDevice
        if individuality.issubset(item.individuality)
        and search_td_svt(search_param.region, item.id, card_ints, hits, strengthStatus)
        and search_td_lv(
            search_param.region,
            item.id,
            numFunctions,
            search_param.minNpNpGain,
            search_param.maxNpNpGain,
        )
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]


def search_buff(search_param: BuffSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    buff_types = {BUFF_TYPE_NAME_REVERSE[item] for item in search_param.type}
    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    ckSelfIndv = reverse_traits(search_param.ckSelfIndv)
    ckOpIndv = reverse_traits(search_param.ckOpIndv)

    matches = [
        item
        for item in masters[search_param.region].mstBuff
        if ((not search_param.type) or (search_param.type and item.type in buff_types))
        and (
            (not search_param.buffGroup)
            or (search_param.buffGroup and item.buffGroup in search_param.buffGroup)
        )
        and vals.issubset(item.vals)
        and tvals.issubset(item.tvals)
        and ckSelfIndv.issubset(item.ckSelfIndv)
        and ckOpIndv.issubset(item.ckOpIndv)
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.detail)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]


def search_func(search_param: FuncSearchQueryParams, limit: int = 100) -> List[int]:
    if not search_param.hasSearchParams:
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    func_types = {FUNC_TYPE_NAME_REVERSE[item] for item in search_param.type}
    target_types = {
        FUNC_TARGETTYPE_NAME_REVERSE[item] for item in search_param.targetType
    }
    apply_targets = {
        FUNC_APPLYTARGET_NAME_REVERSE[item] for item in search_param.targetTeam
    }
    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    questTvals = reverse_traits(search_param.questTvals)

    matches = [
        item
        for item in masters[search_param.region].mstFunc
        if (
            (not search_param.type)
            or (search_param.type and item.funcType in func_types)
        )
        and (
            (not search_param.targetType)
            or (search_param.targetType and item.targetType in target_types)
        )
        and (
            (not search_param.targetTeam)
            or (search_param.targetTeam and item.applyTarget in apply_targets)
        )
        and vals.issubset(item.vals)
        and tvals.issubset(item.tvals)
        and questTvals.issubset(item.questTvals)
    ]

    if search_param.popupText:
        matches = [
            item
            for item in matches
            if match_name(search_param.popupText, item.popupText)
        ]

    if len(matches) > limit:
        raise HTTPException(status_code=403, detail=TOO_MANY_RESULTS.format(limit))

    return [item.id for item in matches]
