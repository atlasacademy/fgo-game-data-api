import inspect
from dataclasses import dataclass
from typing import ClassVar, Optional, Union

from fastapi import Query

from .common import Region
from .enums import (
    ATTRIBUTE_NAME,
    CLASS_NAME,
    PLAYABLE_CLASS_LIST,
    Attribute,
    FuncApplyTarget,
    NiceItemBGType,
    NiceItemUse,
    NiceSkillType,
    SvtClass,
    Trait,
)
from .gameenums import (
    GENDER_TYPE_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    NiceBuffType,
    NiceCardType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceItemType,
    NiceSvtFlag,
    NiceSvtType,
)


SERVANT_TYPE = [
    NiceSvtType.normal,
    NiceSvtType.heroine,
    NiceSvtType.enemyCollectionDetail,
]


@dataclass
class ServantSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: list[int] = Query([0])
    type: list[NiceSvtType] = Query(SERVANT_TYPE)
    flag: list[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: list[int] = Query(list(range(6)), ge=0, le=5)
    className: list[SvtClass] = Query(PLAYABLE_CLASS_LIST)
    gender: list[NiceGender] = Query(list(GENDER_TYPE_NAME.values()))
    attribute: list[Attribute] = Query(list(ATTRIBUTE_NAME.values()))
    trait: list[Union[Trait, int]] = Query([])
    voiceCondSvt: list[int] = Query([])

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
                self.voiceCondSvt,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **excludeCollectionNo**: int, defaults to 0. Won't return records with the specified `collectionNo`.
        - **type**: servant type, defaults to `[normal, heroine, enemyCollectionDetail]`.
        See the `NiceSvtType` enum for the options.
        - **flag**: svt flag. See the `NiceSvtFlag` enum for the options.
        - **rarity**: rarity of the servant.
        - **className**: an item in the `className` enum, defaults to `PLAYABLE_CLASS_LIST`.
        See the `className` detail in the Nice Servant response.
        - **gender**: `female`, `male` or `unknown`.
        - **attribute**: `human`, `sky`, `earth`, `star` or `beast`.
        - **trait**: an integer or an item in the `trait` enum. See the traits detail in the Nice Servant response.
        - **voiceCondValue**: servant `collectionNo` or servant `ID`. Will find the servants that
        have voice lines directed to the given servants.

        At least one of `name`, `type`, `rarity`, `className`, `gender`, `attribute`,
        `trait` or `voiceCondSvt` is required for the query.
        """
    )


@dataclass
class SvtSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: list[int] = Query([-1])
    type: list[NiceSvtType] = Query(list(SVT_TYPE_NAME.values()))
    flag: list[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: list[int] = Query(list(range(6)), ge=0, le=5)
    className: list[SvtClass] = Query(list(CLASS_NAME.values()))
    gender: list[NiceGender] = Query(list(GENDER_TYPE_NAME.values()))
    attribute: list[Attribute] = Query(list(ATTRIBUTE_NAME.values()))
    trait: list[Union[Trait, int]] = Query([])
    voiceCondSvt: list[int] = Query([])

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
                self.voiceCondSvt,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **excludeCollectionNo**: int. Won't return records with the specified `collectionNo`.
        - **type**: servant type. See the `NiceSvtType` enum for the options.
        - **flag**: svt flag. See the `NiceSvtFlag` enum for the options.
        - **rarity**: `rarity` of the svt object.
        - **className**: an item in the `className` enum. See the `className` detail in the Nice Servant response.
        - **gender**: `female`, `male` or `unknown`.
        - **attribute**: `human`, `sky`, `earth`, `star` or `beast`.
        - **trait**: an integer or an item in the `trait` enum. See the traits detail in the Nice Servant response.
        - **voiceCondValue**: servant `collectionNo` or servant `ID`. Will find the servants that
        have voice lines directed to the given servants.

        At least one of `name`, `type`, `rarity`, `className`, `gender`, `attribute`
        `trait` or `voiceCondSvt` is required for the query.
        """
    )


@dataclass
class EquipSearchQueryParams:
    region: Region
    name: Optional[str] = None
    excludeCollectionNo: list[int] = Query([0])
    type: list[NiceSvtType] = Query([NiceSvtType.servantEquip])
    flag: list[NiceSvtFlag] = Query(list(SVT_FLAG_NAME.values()))
    rarity: list[int] = Query(list(range(1, 6)), ge=1, le=5)

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
        - **excludeCollectionNo**: int, defaults to 0. Won't return records with the specified `collectionNo`.
        - **type**: servant type, defaults to `[servantEquip]`. See the `NiceSvtType` for the options.
        - **flag**: svt flag. See the `NiceSvtFlag` enum for the options.
        - **rarity**: `rarity` of the CE.

        At least one of `name`, `type`, `flag` or `rarity` is required for the query.
        """
    )


@dataclass
class SkillSearchParams:
    region: Region
    name: Optional[str] = None
    type: Optional[list[NiceSkillType]] = Query(None)
    num: Optional[list[int]] = Query(None)
    priority: Optional[list[int]] = Query(None)
    strengthStatus: Optional[list[int]] = Query(None)
    lvl1coolDown: Optional[list[int]] = Query(None)
    numFunctions: Optional[list[int]] = Query(None)

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.type,
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
        - **num**: skill number on the servant: 1, 2 or 3. [1]
        - **priority**: visual display order. It is usually a better number for strengthening status. [1]
        - **strengthStatus**: strengthening status. [1]
        - **lvl1coolDown**: Cooldown at level 1.
        - **numFunctions**: Number of functions in the skill.

        At least one of the parameter is required for the query.

        [1] Notice that multiple servants can have the same skill, the search will look into all servants
        with the skill and check if any servant satisfy the conditions.
        """
    )


@dataclass
class TdSearchParams:
    region: Region
    name: Optional[str] = None
    card: Optional[list[NiceCardType]] = Query(None)
    individuality: list[Union[Trait, int]] = Query([])
    hits: Optional[list[int]] = Query(None)
    strengthStatus: Optional[list[int]] = Query(None)
    numFunctions: Optional[list[int]] = Query(None)
    minNpNpGain: Optional[int] = None
    maxNpNpGain: Optional[int] = None

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.card,
                self.individuality,
                self.hits,
                self.strengthStatus,
                self.numFunctions,
                self.minNpNpGain is not None,
                self.maxNpNpGain is not None,
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
    type: list[NiceBuffType] = Query([])
    buffGroup: list[int] = Query([])
    vals: list[Union[Trait, int]] = Query([])
    tvals: list[Union[Trait, int]] = Query([])
    ckSelfIndv: list[Union[Trait, int]] = Query([])
    ckOpIndv: list[Union[Trait, int]] = Query([])

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
    type: list[NiceFuncType] = Query([])
    targetType: list[NiceFuncTargetType] = Query([])
    targetTeam: list[FuncApplyTarget] = Query([])
    vals: list[Union[Trait, int]] = Query([])
    tvals: list[Union[Trait, int]] = Query([])
    questTvals: list[Union[Trait, int]] = Query([])

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


@dataclass
class ItemSearchQueryParams:
    region: Region
    name: Optional[str] = None
    individuality: list[Union[Trait, int]] = Query([])
    type: list[NiceItemType] = Query([])
    background: list[NiceItemBGType] = Query([])
    use: list[NiceItemUse] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.individuality,
                self.type,
                self.background,
                self.use,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched items.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **individuality**: an integer or a trait enum.
        - **type**: an item of NiceItemType.
        - **background**: an item of `NiceItemBGType`.
        - **use**: an item of `NiceItemUse`.

        At least one of the parameter is required for the query.
        """
    )
