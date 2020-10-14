from typing import Any, Iterable, List, Mapping, TypeVar, Union

from .enums import TRAIT_NAME, Trait
from .schemas.basic import BasicEquip, BasicServant
from .schemas.common import NiceTrait


VT = TypeVar("VT")
LT = TypeVar("LT")


def get_safe(input_dict: Mapping[Any, VT], key: LT) -> Union[VT, LT]:
    """
    A dict getter that returns the key if it's not found in the dict.
    The enums mapping is or will be incomplete eventually.
    """
    return input_dict.get(key, key)


def get_nice_trait(individuality: int) -> NiceTrait:
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
    return [get_nice_trait(individuality) for individuality in input_idv]


def sort_by_collection_no(
    input_list: List[Union[BasicServant, BasicEquip]]
) -> List[Union[BasicServant, BasicEquip]]:
    return sorted(input_list, key=lambda x: x.collectionNo)
