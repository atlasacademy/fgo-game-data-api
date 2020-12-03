from typing import Any, Iterable, List, Mapping, TypeVar, Union

from .enums import TRAIT_NAME, Trait
from .schemas.basic import BasicEquip, BasicServant
from .schemas.common import NiceTrait


VT = TypeVar("VT")
LT = TypeVar("LT")


def get_safe(input_dict: Mapping[Any, VT], key: LT) -> Union[VT, LT]:
    """
    A dict getter that returns the lookup key if it's not found in the dict.
    """
    return input_dict.get(key, key)


def get_nice_trait(individuality: int) -> NiceTrait:
    """Return the corresponding NiceTrait object given the individuality"""
    if individuality >= 0:
        return NiceTrait(
            id=individuality, name=TRAIT_NAME.get(individuality, Trait.unknown)
        )

    return NiceTrait(
        id=-individuality,
        name=TRAIT_NAME.get(-individuality, Trait.unknown),
        negative=True,
    )


def get_traits_list(input_idv: Iterable[int]) -> List[NiceTrait]:
    """
    Return the corresponding list NiceTrait objects given the individuality list
    """
    return [get_nice_trait(individuality) for individuality in input_idv]


def sort_by_collection_no(
    input_list: Iterable[Union[BasicServant, BasicEquip]]
) -> List[Union[BasicServant, BasicEquip]]:
    """
    Return given list of basic svt objects sorted by their collectionNo attribute
    """
    return sorted(input_list, key=lambda x: x.collectionNo)
