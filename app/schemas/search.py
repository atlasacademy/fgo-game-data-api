import inspect
from dataclasses import dataclass
from typing import ClassVar, Optional, Union

from fastapi import Query

from .common import Region
from .enums import (
    NICE_SERVANT_TYPES,
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
    NiceBuffType,
    NiceCardType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceItemType,
    NicePayType,
    NiceQuestFlag,
    NiceQuestType,
    NiceShopType,
    NiceSvtFlag,
    NiceSvtType,
)


@dataclass
class ServantSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    illustrator: Optional[str] = Query(None, max_length=999)
    cv: Optional[str] = Query(None, max_length=999)
    excludeCollectionNo: list[int] = Query([0])
    type: list[NiceSvtType] = Query(NICE_SERVANT_TYPES)
    flag: list[NiceSvtFlag] = Query([])
    rarity: list[int] = Query([])
    className: list[SvtClass] = Query(PLAYABLE_CLASS_LIST)
    gender: list[NiceGender] = Query([])
    attribute: list[Attribute] = Query([])
    trait: list[Union[Trait, int]] = Query([])
    notTrait: list[Union[Trait, int]] = Query([])
    voiceCondSvt: list[int] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.illustrator,
                self.cv,
                self.type != NICE_SERVANT_TYPES,
                self.flag,
                self.rarity,
                self.className != PLAYABLE_CLASS_LIST,
                self.gender,
                self.attribute,
                self.trait,
                self.notTrait,
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
        - **notTrait**: an integer or an item in the `trait` enum. The result entities won't have any of the traits
        in the list.
        - **voiceCondValue**: servant `collectionNo` or servant `ID`. Will find the servants that
        have voice lines directed to the given servants.

        At least one of `name`, `type`, `rarity`, `className`, `gender`, `attribute`,
        `trait` or `voiceCondSvt` is required for the query.
        """
    )


@dataclass
class SvtSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    illustrator: Optional[str] = Query(None, max_length=999)
    cv: Optional[str] = Query(None, max_length=999)
    excludeCollectionNo: list[int] = Query([])
    type: list[NiceSvtType] = Query([])
    flag: list[NiceSvtFlag] = Query([])
    rarity: list[int] = Query([], ge=0, le=5)
    className: list[SvtClass] = Query([])
    gender: list[NiceGender] = Query([])
    attribute: list[Attribute] = Query([])
    trait: list[Union[Trait, int]] = Query([])
    notTrait: list[Union[Trait, int]] = Query([])
    voiceCondSvt: list[int] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.illustrator,
                self.cv,
                self.type,
                self.flag,
                self.rarity,
                self.className,
                self.gender,
                self.attribute,
                self.trait,
                self.notTrait,
                self.voiceCondSvt,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **illustrator**: Illustrator name. Exact match required.
        - **cv**: Voice actor name. Exact match required.
        - **excludeCollectionNo**: int. Won't return records with the specified `collectionNo`.
        - **type**: servant type. See the `NiceSvtType` enum for the options.
        - **flag**: svt flag. See the `NiceSvtFlag` enum for the options.
        - **rarity**: `rarity` of the svt object.
        - **className**: an item in the `className` enum. See the `className` detail in the Nice Servant response.
        - **gender**: `female`, `male` or `unknown`.
        - **attribute**: `human`, `sky`, `earth`, `star` or `beast`.
        - **trait**: an integer or an item in the `trait` enum. See the traits detail in the Nice Servant response.
        - **notTrait**: an integer or an item in the `trait` enum. The result entities won't have any of the traits
        in the list.
        - **voiceCondValue**: servant `collectionNo` or servant `ID`. Will find the servants that
        have voice lines directed to the given servants.

        At least one of `name`, `type`, `rarity`, `className`, `gender`, `attribute`
        `trait` or `voiceCondSvt` is required for the query.
        """
    )


@dataclass
class EquipSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    illustrator: Optional[str] = Query(None, max_length=999)
    excludeCollectionNo: list[int] = Query([0])
    type: list[NiceSvtType] = Query([NiceSvtType.servantEquip])
    flag: list[NiceSvtFlag] = Query([])
    rarity: list[int] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.illustrator,
                self.type != [NiceSvtType.servantEquip],
                self.flag,
                self.rarity,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **illustrator**: Illustrator name. Exact match required.
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
    name: Optional[str] = Query(None, max_length=999)
    type: Optional[list[NiceSkillType]] = Query(None)
    num: Optional[list[int]] = Query(None)
    priority: Optional[list[int]] = Query(None)
    strengthStatus: Optional[list[int]] = Query(None)
    lvl1coolDown: Optional[list[int]] = Query(None)
    numFunctions: Optional[list[int]] = Query(None)
    svalsContain: str | None = Query(None)
    triggerSkillId: list[int] | None = Query(None)

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
                self.svalsContain is not None and self.svalsContain.strip() != "",
                self.triggerSkillId,
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
        - **svalsContain**: Skill's svals should contain this pattern.
        - **triggerSkillId**: Trigger Skill IDs that are called by this skill.

        At least one of the parameter is required for the query.

        [1] Notice that multiple servants can have the same skill, the search will look into all servants
        with the skill and check if any servant satisfy the conditions.
        """
    )


@dataclass
class TdSearchParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    card: Optional[list[NiceCardType]] = Query(None)
    individuality: list[Union[Trait, int]] = Query([])
    hits: Optional[list[int]] = Query(None)
    strengthStatus: Optional[list[int]] = Query(None)
    numFunctions: Optional[list[int]] = Query(None)
    minNpNpGain: Optional[int] = None
    maxNpNpGain: Optional[int] = None
    svalsContain: str | None = Query(None)
    triggerSkillId: list[int] | None = Query(None)

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
                self.svalsContain is not None and self.svalsContain.strip() != "",
                self.triggerSkillId,
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
        - **svalsContain**: NP's svals should contain this pattern.
        - **triggerSkillId**: Trigger Skill IDs that are called by this skill.

        At least one of the parameter is required for the query.
        """
    )


@dataclass
class BuffSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
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
    popupText: Optional[str] = Query(None, max_length=999)
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
    name: Optional[str] = Query(None, max_length=999)
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


@dataclass
class QuestSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    spotName: Optional[str] = None
    warId: list[int] = Query([])
    type: list[NiceQuestType] = Query([])
    flag: list[NiceQuestFlag] = Query([])
    fieldIndividuality: list[Union[Trait, int]] = Query([])
    battleBgId: Optional[int] = None
    bgmId: Optional[int] = None
    fieldAiId: Optional[int] = None
    enemySvtId: Optional[int] = None
    enemySvtAiId: Optional[int] = None
    enemyTrait: list[Union[Trait, int]] = Query([])
    enemyClassName: list[SvtClass] = Query([])
    enemySkillId: list[int] | None = Query(None)
    enemyNoblePhantasmId: list[int] | None = Query(None)

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.spotName,
                self.warId,
                self.type,
                self.flag,
                self.fieldIndividuality,
                self.battleBgId,
                self.bgmId,
                self.enemySvtAiId,
                self.enemySvtId,
                self.fieldAiId,
                self.enemyTrait,
                self.enemyClassName,
                self.enemySkillId,
                self.enemyNoblePhantasmId,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched items.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data.
        - **spotName**: name of quests's spot.
        - **warId**: War ID.
        - **type**: Quest Type Enum.
        - **flag**: Quest Flag Enum.
        - **fieldIndividuality**: Trait Enum or an Integer.
        - **battleBgId**: Battle BG ID.
        - **bgmId**: BGM ID.
        - **fieldAiId**: Field AI ID.
        - **enemySvtId**: Enemy's svt ID (Note that this is not `collectionNo`). Some quests use 99xxxxx svt ID instead of the playable svt ID.
        - **enemySvtAiId**: Enemy's servant AI ID.
        - **enemyTrait**: Enemy's Trait. Trait Enum or an Integer.
        - **enemyClassName**: Enemy's Class Name Enum.
        - **enemySkillId**: Enemy's Skill, Passive Skill,
        - **enemyNoblePhantasmId**: Enemy's NP

        At least one of the parameter is required for the query.
        """
    )


@dataclass
class ScriptSearchQueryParams:
    region: Region
    query: str = Query(..., max_length=999)
    scriptFileName: str | None = Query(default=None, max_length=99)
    warId: list[int] = Query([])

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matching scripts.

        - **query**: search query https://groonga.org/docs/reference/grn_expr/query_syntax.html.
        (Queries starting with `column:` are not supported).
        - **scriptFileName**: The script name should contain this string.
        - **warId**: War ID of the quest that with the script.
        For example: 30001 string for LB1 scripts or 9401 for interlude scripts.
        """
    )

    def hasSearchParams(self) -> bool:
        return 1 <= len(self.query.strip()) <= 999


@dataclass
class ShopSearchQueryParams:
    region: Region
    name: Optional[str] = Query(None, max_length=999)
    eventId: list[int] = Query([])
    type: list[NiceShopType] = Query([])
    payType: list[NicePayType] = Query([])

    def hasSearchParams(self) -> bool:
        return any(
            [
                self.name,
                self.eventId,
                self.type,
                self.payType,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched shop entities.
        """
    )
