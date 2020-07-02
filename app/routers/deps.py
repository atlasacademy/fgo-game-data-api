import inspect
from dataclasses import dataclass, field
from typing import ClassVar, List, Optional, Union

from fastapi import Query
from pydantic import BaseModel

from ..data.common import Region
from ..data.enums import Attribute, Gender, PlayableSvtClass, Trait


class DetailMessage(BaseModel):
    detail: str


@dataclass
class ServantSearchQueryParams:
    region: Region
    name: Optional[str] = None
    rarity: List[int] = Query(None, ge=0, le=5)
    className: List[PlayableSvtClass] = Query(None)
    gender: List[Gender] = Query(None)
    attribute: List[Attribute] = Query(None)
    trait: List[Union[Trait, int]] = Query(None)
    hasSearchParams: bool = field(init=False)

    def __post_init__(self):
        self.hasSearchParams = any(
            [
                self.name,
                self.rarity,
                self.className,
                self.gender,
                self.attribute,
                self.trait,
            ]
        )

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched servant entities.

        - **name**: servant name. Searching JP data using English name works too.
        - **rarity**: Integer 0-6
        - **className**: an item in the className enum. See the className detail in the Nice Servant response.
        - **gender**: female, male or unknown
        - **attribute**: human, sky, earth, star or beast
        - **trait**: an integer or an item in the trait enum. See the traits detail in the Nice Servant response.
        """
    )


@dataclass
class EquipSearchQueryParams:
    region: Region
    name: Optional[str] = None
    rarity: List[int] = Query(None, ge=1, le=5)
    hasSearchParams: bool = field(init=False)

    def __post_init__(self):
        self.hasSearchParams = any([self.name, self.rarity])

    DESCRIPTION: ClassVar[str] = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data
        - **rarity**: Integer 0-6
        """
    )
