import inspect
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional, Union

from fastapi import Query
from pydantic import BaseModel

from ..data.common import Language, Region
from ..data.enums import (
    ATTRIBUTE_NAME,
    GENDER_NAME,
    PLAYABLE_CLASS_LIST,
    Attribute,
    FuncApplyTarget,
    Gender,
    NiceBuffType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceSvtType,
    SvtClass,
    Trait,
)


class DetailMessage(BaseModel):
    detail: str


def language_parameter(lang: Optional[Language] = None) -> Language:
    if lang:
        return lang
    else:
        return Language.jp


@dataclass
class ServantSearchQueryParams:
    region: Region
    hasSearchParams: bool = field(init=False)
    name: Optional[str] = None
    type: List[NiceSvtType] = Query(
        [NiceSvtType.normal, NiceSvtType.heroine, NiceSvtType.enemyCollectionDetail]
    )
    rarity: List[int] = Query(list(range(6)), ge=0, le=5)
    className: List[SvtClass] = Query(PLAYABLE_CLASS_LIST)
    gender: List[Gender] = Query(list(GENDER_NAME.values()))
    attribute: List[Attribute] = Query(list(ATTRIBUTE_NAME.values()))
    trait: List[Union[Trait, int]] = Query([])

    def __post_init__(self) -> None:
        self.hasSearchParams = any(
            [
                self.name,
                self.rarity != list(range(6)),
                self.className != PLAYABLE_CLASS_LIST,
                self.gender != list(GENDER_NAME.values()),
                self.attribute != list(ATTRIBUTE_NAME.values()),
                self.trait != [],
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **type**: servant type, defaults to `[normal, heroine, enemyCollectionDetail]`.
        See the NiceSvtType enum for the options. Must not be the only parameter given.
        - **rarity**: Integers 0-6.
        - **className**: an item in the className enum, defaults to `PLAYABLE_CLASS_LIST`.
        See the className detail in the Nice Servant response.
        - **gender**: female, male or unknown.
        - **attribute**: human, sky, earth, star or beast.
        - **trait**: an integer or an item in the trait enum. See the traits detail in the Nice Servant response.
        """
    )


@dataclass
class EquipSearchQueryParams:
    region: Region
    hasSearchParams: bool = field(init=False)
    name: Optional[str] = None
    type: List[NiceSvtType] = Query([NiceSvtType.servantEquip])
    rarity: List[int] = Query(list(range(1, 6)), ge=1, le=5)

    def __post_init__(self) -> None:
        self.hasSearchParams = any([self.name, self.rarity != list(range(1, 6))])

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data
        - **type**: servant type, defaults to `[servantEquip]`. See the NiceSvtType for the options.
        Must not be the only parameter given.
        - **rarity**: Integers 0-6
        """
    )


@dataclass
class BuffSearchQueryParams:
    region: Region
    hasSearchParams: bool = field(init=False)
    name: Optional[str] = None
    type: List[NiceBuffType] = Query(None)
    vals: List[Union[Trait, int]] = Query([])
    tvals: List[Union[Trait, int]] = Query([])
    ckSelfIndv: List[Union[Trait, int]] = Query([])
    ckOpIndv: List[Union[Trait, int]] = Query([])

    def __post_init__(self) -> None:
        self.hasSearchParams = any(
            [
                self.name,
                self.type,
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
        - **vals**: an integer or a trait enum.
        - **tvals**: an integer or a trait enum.
        - **ckSelfIndv**: an integer or a trait enum.
        - **ckOpIndv**: an integer or a trait enum.
        """
    )


@dataclass
class FuncSearchQueryParams:
    region: Region
    hasSearchParams: bool = field(init=False)
    popupText: Optional[str] = None
    type: List[NiceFuncType] = Query(None)
    targetType: List[NiceFuncTargetType] = Query(None)
    targetTeam: List[FuncApplyTarget] = Query(None)
    vals: List[Union[Trait, int]] = Query([])
    tvals: List[Union[Trait, int]] = Query([])
    questTvals: List[Union[Trait, int]] = Query([])

    def __post_init__(self) -> None:
        self.hasSearchParams = any(
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
        - **vals**: an integer or a trait enum.
        - **tvals**: an integer or a trait enum.
        - **questTvals**: integer.
        """
    )
