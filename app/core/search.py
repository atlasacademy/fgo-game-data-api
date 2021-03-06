from typing import Iterable, List, Set, Union

from fastapi import HTTPException
from fuzzywuzzy import fuzz, utils
from sqlalchemy.engine import Connection

from ..data.custom_mappings import TRANSLATIONS
from ..data.gamedata import masters
from ..db.helpers.skill import get_skill_search
from ..db.helpers.svt import get_related_voice_id
from ..db.helpers.td import get_td_search
from ..schemas.enums import (
    ATTRIBUTE_NAME_REVERSE,
    BUFF_TYPE_NAME_REVERSE,
    CARD_TYPE_NAME_REVERSE,
    CLASS_NAME_REVERSE,
    FUNC_APPLYTARGET_NAME_REVERSE,
    FUNC_TARGETTYPE_NAME_REVERSE,
    FUNC_TYPE_NAME_REVERSE,
    GENDER_TYPE_NAME_REVERSE,
    ITEM_BG_TYPE_REVERSE,
    ITEM_TYPE_REVERSE,
    SKILL_TYPE_NAME_REVERSE,
    SVT_FLAG_NAME_REVERSE,
    SVT_TYPE_NAME_REVERSE,
    TRAIT_NAME_REVERSE,
    NiceItemUse,
    Trait,
)
from ..schemas.raw import MstItem
from ..schemas.search import (
    BuffSearchQueryParams,
    EquipSearchQueryParams,
    FuncSearchQueryParams,
    ItemSearchQueryParams,
    ServantSearchQueryParams,
    SkillSearchParams,
    SvtSearchQueryParams,
    TdSearchParams,
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
            or trait_ints.issubset(
                masters[search_param.region].mstSvtLimitAddIndividutality.get(
                    svt.id, []
                )
            )
        )
        and masters[search_param.region].mstSvtLimitFirst[svt.id].rarity in rarity_ints
    ]

    if search_param.voiceCondSvt:
        converted_to_svt_id = {
            masters[search_param.region].mstSvtServantCollectionNo.get(svt_id, svt_id)
            for svt_id in search_param.voiceCondSvt
        }
        voice_cond_group = {
            group.id
            for svt_id in converted_to_svt_id
            for group in masters[search_param.region].mstSvtGroupSvtId.get(svt_id, [])
        }
        voice_svt_id = get_related_voice_id(conn, converted_to_svt_id, voice_cond_group)
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
        and masters[search_param.region].mstSvtLimitFirst[svt.id].rarity in rarity
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


def search_skill(
    conn: Connection, search_param: SkillSearchParams, limit: int = 100
) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    type_ints = (
        {SKILL_TYPE_NAME_REVERSE[skill_type] for skill_type in search_param.type}
        if search_param.type
        else None
    )

    matches = get_skill_search(
        conn,
        type_ints,
        search_param.num,
        search_param.priority,
        search_param.strengthStatus,
        search_param.lvl1coolDown,
        search_param.numFunctions,
    )

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


def search_td(
    conn: Connection, search_param: TdSearchParams, limit: int = 100
) -> List[int]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    card_ints = (
        {CARD_TYPE_NAME_REVERSE[td_card] for td_card in search_param.card}
        if search_param.card
        else None
    )
    individuality = reverse_traits(search_param.individuality)

    matches = get_td_search(
        conn,
        individuality,
        card_ints,
        search_param.hits,
        search_param.strengthStatus,
        search_param.numFunctions,
        search_param.minNpNpGain,
        search_param.maxNpNpGain,
    )

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


def search_item(search_param: ItemSearchQueryParams) -> List[MstItem]:
    if not search_param.hasSearchParams():
        raise HTTPException(status_code=400, detail=INSUFFICIENT_QUERY)

    individuality = reverse_traits(search_param.individuality)
    item_type = [ITEM_TYPE_REVERSE[item_type] for item_type in search_param.type]
    bg_type = [ITEM_BG_TYPE_REVERSE[bg_type] for bg_type in search_param.background]

    matches = masters[search_param.region].mstItem

    if individuality:
        matches = [
            item for item in matches if individuality.issubset(item.individuality)
        ]
    if item_type:
        matches = [item for item in matches if item.type in item_type]
    if bg_type:
        matches = [item for item in matches if item.bgImageId in bg_type]

    for item_use, lookup_table in (
        (NiceItemUse.skill, masters[search_param.region].mstCombineSkillItem),
        (NiceItemUse.ascension, masters[search_param.region].mstCombineLimitItem),
        (NiceItemUse.costume, masters[search_param.region].mstCombineCostumeItem),
    ):
        if item_use in search_param.use:
            matches = [item for item in matches if item.id in lookup_table]

    if search_param.name:
        matches = [item for item in matches if match_name(search_param.name, item.name)]

    return matches
