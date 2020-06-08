import inspect
from typing import List, Optional, Union

from fastapi import Query
from pydantic import BaseModel

from ..data.common import Region
from ..data.enums import Attribute, Gender, PlayableSvtClass, Trait


class DetailMessage(BaseModel):
    detail: str


class ServantSearchQueryParams:
    def __init__(
        self,
        region: Region,
        name: Optional[str] = None,
        rarity: List[int] = Query(None, ge=0, le=5),
        className: List[PlayableSvtClass] = Query(None),
        gender: List[Gender] = Query(None),
        attribute: List[Attribute] = Query(None),
        trait: List[Union[Trait, int]] = Query(None),
    ):
        self.region = region
        self.name = name
        self.rarity = rarity
        self.className = className
        self.gender = gender
        self.attribute = attribute
        self.trait = trait
        self.hasSearchParams = any([name, rarity, className, gender, attribute, trait])

    DESCRIPTION = inspect.cleandoc(
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


class EquipSearchQueryParams:
    def __init__(
        self,
        region: Region,
        name: Optional[str] = None,
        rarity: List[int] = Query(None, ge=1, le=5),
    ):
        self.region = region
        self.name = name
        self.rarity = rarity
        self.hasSearchParams = any([name, rarity])

    DESCRIPTION = inspect.cleandoc(
        """
        Search and return the list of matched equip entities.

        - **name**: in English if you are searching NA data and in Japanese if you are searching JP data
        - **rarity**: Integer 0-6
        """
    )
