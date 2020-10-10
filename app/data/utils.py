from typing import Any, Dict, Iterable, List, Mapping, TypeVar, Union

from .enums import TRAIT_NAME, Trait
from .schemas.basic import BasicEquip, BasicServant


VT = TypeVar("VT")
LT = TypeVar("LT")


def get_safe(input_dict: Mapping[Any, VT], key: LT) -> Union[VT, LT]:
    """
    A dict getter that returns the key if it's not found in the dict.
    The enums mapping is or will be incomplete eventually.
    """
    return input_dict.get(key, key)


def get_traits_list(input_idv: Iterable[int]) -> List[Dict[str, Union[Trait, int]]]:
    return [
        {"id": item, "name": TRAIT_NAME.get(item, Trait.unknown)}
        if item >= 0
        else {
            "id": -item,
            "name": TRAIT_NAME.get(-item, Trait.unknown),
            "negative": True,
        }
        for item in input_idv
    ]


def sort_by_collection_no(
    input_list: List[Union[BasicServant, BasicEquip]]
) -> List[Union[BasicServant, BasicEquip]]:
    return sorted(input_list, key=lambda x: x.collectionNo)
