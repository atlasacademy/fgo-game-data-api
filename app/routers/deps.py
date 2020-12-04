import inspect
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Iterable, List, Mapping, Optional, Type, Union

from fastapi import Query
from pydantic import BaseModel

from ..data.common import Language, Region
from ..data.enums import (
    ATTRIBUTE_NAME,
    CARD_TYPE_NAME,
    CLASS_NAME,
    GENDER_TYPE_NAME,
    PLAYABLE_CLASS_LIST,
    SKILL_TYPE_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    Attribute,
    FuncApplyTarget,
    NiceBuffType,
    NiceCardType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceSkillType,
    NiceSvtFlag,
    NiceSvtType,
    SvtClass,
    Trait,
)


class DetailMessage(BaseModel):
    detail: str


ErrorDetailType = Dict[str, Union[Type[DetailMessage], str]]
ERROR_CODE: Dict[int, ErrorDetailType] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    403: {"model": DetailMessage, "description": "Response too big"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


def get_error_code(
    error_codes: Union[Iterable[int], Mapping[int, Any]]
) -> Dict[Union[int, str], ErrorDetailType]:
    return {k: v for k, v in ERROR_CODE.items() if k in error_codes}


def language_parameter(lang: Optional[Language] = None) -> Language:
    if lang:
        return lang
    else:
        return Language.jp


SERVANT_TYPE = [
    NiceSvtType.normal,
    NiceSvtType.heroine,
    NiceSvtType.enemyCollectionDetail,
]


@dataclass
class ServantSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: List[int] = Query([0])
    type: List[NiceSvtType] = Query(SERVANT_TYPE)
    flag: List[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: List[int] = Query(list(range(6)), ge=0, le=5)
    className: List[SvtClass] = Query(PLAYABLE_CLASS_LIST)
    gender: List[NiceGender] = Query(list(GENDER_TYPE_NAME.values()))
    attribute: List[Attribute] = Query(list(ATTRIBUTE_NAME.values()))
    trait: List[Union[Trait, int]] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type != SERVANT_TYPE,
                self.flag != list(SVT_FLAG_NAME.values()),
                self.rarity != list(range(6)),
                self.className != PLAYABLE_CLASS_LIST,
                self.gender != list(GENDER_TYPE_NAME.values()),
                self.attribute != list(ATTRIBUTE_NAME.values()),
                self.trait,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **excludeCollectionNo**: int, defaults to 0. Won't return records with the specified collectionNo.
        - **type**: servant type, defaults to `[normal, heroine, enemyCollectionDetail]`.
        See the NiceSvtType enum for the options.
        - **flag**: svt flag. See the NiceSvtFlag enum for the options.
        - **rarity**: rarity of the servant.
        - **className**: an item in the className enum, defaults to `PLAYABLE_CLASS_LIST`.
        See the className detail in the Nice Servant response.
        - **gender**: female, male or unknown.
        - **attribute**: human, sky, earth, star or beast.
        - **trait**: an integer or an item in the trait enum. See the traits detail in the Nice Servant response.

        At least one of name, type, rarity, className, gender, attribute and trait is required for the query.
        """
    )


@dataclass
class SvtSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: List[int] = Query([-1])
    type: List[NiceSvtType] = Query(list(SVT_TYPE_NAME.values()))
    flag: List[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: List[int] = Query(list(range(6)), ge=0, le=5)
    className: List[SvtClass] = Query(list(CLASS_NAME.values()))
    gender: List[NiceGender] = Query(list(GENDER_TYPE_NAME.values()))
    attribute: List[Attribute] = Query(list(ATTRIBUTE_NAME.values()))
    trait: List[Union[Trait, int]] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type != list(SVT_TYPE_NAME.values()),
                self.flag != list(SVT_FLAG_NAME.values()),
                self.rarity != list(range(6)),
                self.className != list(CLASS_NAME.values()),
                self.gender != list(GENDER_TYPE_NAME.values()),
                self.attribute != list(ATTRIBUTE_NAME.values()),
                self.trait,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **excludeCollectionNo**: int. Won't return records with the specified collectionNo.
        - **type**: servant type. See the NiceSvtType enum for the options.
        - **flag**: svt flag. See the NiceSvtFlag enum for the options.
        - **rarity**: rarity of the svt object.
        - **className**: an item in the className enum. See the className detail in the Nice Servant response.
        - **gender**: female, male or unknown.
        - **attribute**: human, sky, earth, star or beast.
        - **trait**: an integer or an item in the trait enum. See the traits detail in the Nice Servant response.

        At least one of name, type, rarity, className, gender, attribute and trait is required for the query.
        """
    )


@dataclass
class EquipSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: List[int] = Query([0])
    type: List[NiceSvtType] = Query([NiceSvtType.servantEquip])
    flag: List[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: List[int] = Query(list(range(1, 6)), ge=1, le=5)

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type != [NiceSvtType.servantEquip],
                self.flag != list(SVT_FLAG_NAME.values()),
                self.rarity != list(range(1, 6)),
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **excludeCollectionNo**: int, defaults to 0. Won't return records with the specified collectionNo.
        - **type**: servant type, defaults to `[servantEquip]`. See the NiceSvtType for the options.
        - **flag**: svt flag. See the NiceSvtFlag enum for the options.
        - **rarity**: rarity of the CE.

        At least one of name, type or rarity is required for the query.
        """
    )


class SkillSearchParamsDefault:
    type = list(SKILL_TYPE_NAME.values())
    num: List[int] = [1, 2, 3]
    priority: List[int] = list(range(1, 6))
    strengthStatus: List[int] = list(range(0, 100))
    lvl1coolDown: List[int] = list(range(-1, 100))
    numFunctions: List[int] = list(range(1, 201))


@dataclass
class SkillSearchParams:
    region: Region
    name: Optional[str] = None
    type: List[NiceSkillType] = Query(SkillSearchParamsDefault.type)
    num: List[int] = Query(
        None, ge=min(SkillSearchParamsDefault.num), le=max(SkillSearchParamsDefault.num)
    )
    priority: List[int] = Query(
        None,
        ge=min(SkillSearchParamsDefault.priority),
        le=max(SkillSearchParamsDefault.priority),
    )
    strengthStatus: List[int] = Query(
        None,
        ge=min(SkillSearchParamsDefault.strengthStatus),
        le=max(SkillSearchParamsDefault.strengthStatus),
    )
    lvl1coolDown: List[int] = Query(
        None,
        ge=min(SkillSearchParamsDefault.lvl1coolDown),
        le=max(SkillSearchParamsDefault.lvl1coolDown),
    )
    numFunctions: List[int] = Query(
        None,
        ge=min(SkillSearchParamsDefault.numFunctions),
        le=max(SkillSearchParamsDefault.numFunctions),
    )

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type != SkillSearchParamsDefault.type,
                self.num,
                self.priority,
                self.strengthStatus,
                self.lvl1coolDown,
                self.numFunctions,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched skill entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **type**: `passive` or `active`.
        - **num**: skill number on the servant: 1, 2 or 3.
        - **priority**: visual display order. It is usually a better number for strengthening status.
        - **strengthStatus**: strengthening status.
        - **lvl1coolDown**: Cooldown at level 1.
        - **numFunctions**: Number of functions in the skill.

        At least one of the parameter is required for the query.
        """
    )


class TdSearchParamsDefault:
    card = list(CARD_TYPE_NAME.values())
    hits: List[int] = list(range(1, 21))
    strengthStatus: List[int] = [0, 1, 2]
    numFunctions: List[int] = list(range(1, 21))
    minNpNpGain: int = 0
    maxNpNpGain: int = 300


@dataclass
class TdSearchParams:
    region: Region
    name: Optional[str] = None
    card: List[NiceCardType] = Query(TdSearchParamsDefault.card)
    individuality: List[Union[Trait, int]] = Query([])
    hits: List[int] = Query(
        None, ge=min(TdSearchParamsDefault.hits), le=max(TdSearchParamsDefault.hits)
    )
    strengthStatus: List[int] = Query(
        None,
        ge=min(TdSearchParamsDefault.strengthStatus),
        le=max(TdSearchParamsDefault.strengthStatus),
    )
    numFunctions: List[int] = Query(
        None,
        ge=min(TdSearchParamsDefault.numFunctions),
        le=max(TdSearchParamsDefault.numFunctions),
    )
    minNpNpGain: int = Query(
        TdSearchParamsDefault.minNpNpGain,
        ge=TdSearchParamsDefault.minNpNpGain,
        le=TdSearchParamsDefault.maxNpNpGain,
    )
    maxNpNpGain: int = Query(
        TdSearchParamsDefault.maxNpNpGain,
        ge=TdSearchParamsDefault.minNpNpGain,
        le=TdSearchParamsDefault.maxNpNpGain,
    )

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.card != TdSearchParamsDefault.card,
                self.individuality,
                self.hits,
                self.strengthStatus,
                self.numFunctions,
                self.minNpNpGain != TdSearchParamsDefault.minNpNpGain,
                self.maxNpNpGain != TdSearchParamsDefault.maxNpNpGain,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **card**: card type of the NP.
        - **hits**: number of hits of the NP.
        - **strengthStatus**: strength status of the NP.
        - **numFunctions**: number of functions the NP has.
        - **minNpNpGain**: NP gain of the NP is at least this value.
        - **maxNpNpGain**: NP gain of the NP is at most this value.

        At least one of the parameter is required for the query.
        """
    )


@dataclass
class BuffSearchQueryParams:
    region: Region
    name: Optional[str] = None
    type: List[NiceBuffType] = Query([])
    buffGroup: List[int] = Query([])
    vals: List[Union[Trait, int]] = Query([])
    tvals: List[Union[Trait, int]] = Query([])
    ckSelfIndv: List[Union[Trait, int]] = Query([])
    ckOpIndv: List[Union[Trait, int]] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type,
                self.buffGroup,
                self.vals,
                self.tvals,
                self.ckSelfIndv,
                self.ckOpIndv,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched buffs.

        - **name**: buff name, will search both buff name and buff detail.
        - **type**: buff type, one of NiceBuffType enum.
        - **buffGroup**: buff group.
        - **vals**: an integer or a trait enum.
        - **tvals**: an integer or a trait enum.
        - **ckSelfIndv**: an integer or a trait enum.
        - **ckOpIndv**: an integer or a trait enum.

        At least one of the parameter is required for the query.
        """
    )


@dataclass
class FuncSearchQueryParams:
    region: Region
    popupText: Optional[str] = None
    type: List[NiceFuncType] = Query([])
    targetType: List[NiceFuncTargetType] = Query([])
    targetTeam: List[FuncApplyTarget] = Query([])
    vals: List[Union[Trait, int]] = Query([])
    tvals: List[Union[Trait, int]] = Query([])
    questTvals: List[Union[Trait, int]] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.popupText,
                self.type,
                self.targetType,
                self.targetTeam,
                self.vals,
                self.tvals,
                self.questTvals,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched buffs.

        - **popupText**: string.
        - **type**: an item of NiceFuncType.
        - **targetType**: an item of NiceFuncTargetType.
        - **targetTeam**: `player`, `enemy` or `playerAndEnemy`.
        - **vals**: an integer or a trait enum. Note that trait enums will be converted to integers before searching
        so the search might return vals with buffs that have the same ids.
        - **tvals**: an integer or a trait enum.
        - **questTvals**: integer.

        At least one of the parameter is required for the query.
        """
    )
