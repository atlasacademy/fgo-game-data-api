from typing import Any, Dict, Iterable, List, Mapping, Union

from .enums import TRAIT_NAME, Trait


def get_safe(input_dict: Mapping[Any, Any], key: Any) -> Any:
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
