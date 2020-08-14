from typing import Iterable, List, Set, Union

from fuzzywuzzy import fuzz, utils

from ..routers.deps import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ServantSearchQueryParams,
    SvtSearchQueryParams,
)
from .enums import (
    ATTRIBUTE_NAME_REVERSE,
    BUFF_TYPE_NAME_REVERSE,
    CLASS_NAME_REVERSE,
    FUNC_APPLYTARGET_NAME_REVERSE,
    FUNC_TARGETTYPE_NAME_REVERSE,
    FUNC_TYPE_NAME_REVERSE,
    GENDER_NAME_REVERSE,
    SVT_TYPE_NAME_REVERSE,
    TRAIT_NAME_REVERSE,
    Trait,
)
from .gamedata import masters
from .translations import SVT_NAME_JP_EN


def reverse_traits(traits: Iterable[Union[Trait, int]]) -> Set[int]:
    return {TRAIT_NAME_REVERSE.get(item, item) for item in traits}  # type: ignore


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

    if len(p1) >= 5 and p1 in p2:
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
    search_param: Union[ServantSearchQueryParams, SvtSearchQueryParams]
) -> List[int]:
    svt_type_ints = {SVT_TYPE_NAME_REVERSE[item] for item in search_param.type}
    rarity_ints = set(search_param.rarity)
    class_ints = {CLASS_NAME_REVERSE[item] for item in search_param.className}
    gender_ints = {GENDER_NAME_REVERSE[item] for item in search_param.gender}
    attribute_ints = {ATTRIBUTE_NAME_REVERSE[item] for item in search_param.attribute}
    trait_ints = reverse_traits(search_param.trait)

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.type in svt_type_ints
        and item.collectionNo != search_param.excludeCollectionNo
        and item.classId in class_ints
        and item.genderType in gender_ints
        and item.attri in attribute_ints
        and trait_ints.issubset(set(item.individuality))
        and masters[search_param.region].mstSvtLimitId[item.id][0].rarity in rarity_ints
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
            or match_name(search_param.name, SVT_NAME_JP_EN.get(item.name, item.name))
        ]

    return [item.id for item in matches]


def search_equip(search_param: EquipSearchQueryParams) -> List[int]:
    svt_type = {SVT_TYPE_NAME_REVERSE[item] for item in search_param.type}
    rarity = set(search_param.rarity)

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.type in svt_type
        and item.collectionNo != search_param.excludeCollectionNo
        and masters[search_param.region].mstSvtLimitId[item.id][0].rarity in rarity
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.ruby)
        ]

    return [item.id for item in matches]


def search_buff(search_param: BuffSearchQueryParams) -> List[int]:

    if not search_param.type:
        buff_types = set(BUFF_TYPE_NAME_REVERSE.values())
    else:
        buff_types = {BUFF_TYPE_NAME_REVERSE[item] for item in search_param.type}

    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    ckSelfIndv = reverse_traits(search_param.ckSelfIndv)
    ckOpIndv = reverse_traits(search_param.ckOpIndv)

    matches = [
        item
        for item in masters[search_param.region].mstBuff
        if item.type in buff_types
        and vals.issubset(set(item.vals))
        and tvals.issubset(set(item.tvals))
        and ckSelfIndv.issubset(set(item.ckSelfIndv))
        and ckOpIndv.issubset(set(item.ckOpIndv))
    ]

    if search_param.name:
        matches = [
            item
            for item in matches
            if match_name(search_param.name, item.name)
            or match_name(search_param.name, item.detail)
        ]

    return [item.id for item in matches]


def search_func(search_param: FuncSearchQueryParams) -> List[int]:

    if not search_param.type:
        func_types = set(FUNC_TYPE_NAME_REVERSE.values())
    else:
        func_types = {FUNC_TYPE_NAME_REVERSE[item] for item in search_param.type}

    if not search_param.targetType:
        target_types = set(FUNC_TARGETTYPE_NAME_REVERSE.values())
    else:
        target_types = {
            FUNC_TARGETTYPE_NAME_REVERSE[item] for item in search_param.targetType
        }

    if not search_param.targetTeam:
        apply_targets = set(FUNC_APPLYTARGET_NAME_REVERSE.values())
    else:
        apply_targets = {
            FUNC_APPLYTARGET_NAME_REVERSE[item] for item in search_param.targetTeam
        }

    vals = reverse_traits(search_param.vals)
    tvals = reverse_traits(search_param.tvals)
    questTvals = reverse_traits(search_param.questTvals)

    matches = [
        item
        for item in masters[search_param.region].mstFunc
        if item.funcType in func_types
        and item.targetType in target_types
        and item.applyTarget in apply_targets
        and vals.issubset(set(item.vals))
        and tvals.issubset(set(item.tvals))
        and questTvals.issubset(set(item.questTvals))
    ]

    if search_param.popupText:
        matches = [
            item
            for item in matches
            if match_name(search_param.popupText, item.popupText)
        ]

    return [item.id for item in matches]
