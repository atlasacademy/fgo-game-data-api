from typing import List

from fuzzywuzzy import fuzz, utils

from ..routers.deps import EquipSearchQueryParams, ServantSearchQueryParams
from .enums import (
    ATTRIBUTE_NAME_REVERSE,
    GENDER_NAME_REVERSE,
    PLAYABLE_CLASS_NAME_REVERSE,
    TRAIT_NAME_REVERSE,
)
from .gamedata import masters
from .translations import SVT_NAME_JP_EN


def match_name(search_param: str, name: str) -> bool:
    """Modified from fuzzywuzzy.token_set_ratio"""
    p1 = utils.full_process(search_param, force_ascii=True)
    p2 = utils.full_process(name, force_ascii=True)

    if not utils.validate_string(p1):
        return False
    if not utils.validate_string(p2):
        return False

    # Doesn't seem to be needed now but might be useful in the future
    # ALTERNATIVE_DIVIDER = ["-", "="]
    # for divider in ALTERNATIVE_DIVIDER:
    #     p1 = p1.replace(divider, " ")
    #     p2 = p2.replace(divider, " ")

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
        return fuzz.ratio(sorted_sect, combined_1to2) > NAME_MATCH_THRESHOLD  # type: ignore
    else:
        return fuzz.ratio(combined_2to1, combined_1to2) > NAME_MATCH_THRESHOLD  # type: ignore


def search_servant(search_param: ServantSearchQueryParams) -> List[int]:

    if not search_param.rarity:
        rarity = set(range(6))
    else:
        rarity = set(search_param.rarity)

    if not search_param.className:
        class_ints = PLAYABLE_CLASS_NAME_REVERSE.values()
    else:
        class_ints = {PLAYABLE_CLASS_NAME_REVERSE[item] for item in search_param.className}  # type: ignore

    if not search_param.gender:
        gender_ints = GENDER_NAME_REVERSE.values()
    else:
        gender_ints = {GENDER_NAME_REVERSE[item] for item in search_param.gender}  # type: ignore

    if not search_param.attribute:
        attribute_ints = ATTRIBUTE_NAME_REVERSE.values()
    else:
        attribute_ints = {ATTRIBUTE_NAME_REVERSE[item] for item in search_param.attribute}  # type: ignore

    if not search_param.trait:
        search_param.trait = []
    trait_ints = {TRAIT_NAME_REVERSE.get(item, item) for item in search_param.trait}  # type: ignore

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.isServant()
        and item.collectionNo != 0
        and item.classId in class_ints
        and item.genderType in gender_ints
        and item.attri in attribute_ints
        and trait_ints.issubset(set(item.individuality))
        and masters[search_param.region].mstSvtLimitId[item.id][0].rarity in rarity
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

    if not search_param.rarity:
        rarity = set(range(1, 6))
    else:
        rarity = set(search_param.rarity)

    matches = [
        item
        for item in masters[search_param.region].mstSvt
        if item.isEquip()
        and item.collectionNo != 0
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
