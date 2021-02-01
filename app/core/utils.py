from typing import Any, Iterable, List, Mapping, TypeVar, Union

from ..data.custom_mappings import TRANSLATIONS
from ..schemas.basic import BasicCommandCode, BasicEquip, BasicServant
from ..schemas.common import NiceTrait
from ..schemas.enums import TRAIT_NAME, Trait
from ..schemas.nice import NiceCommandCode, NiceEquip, NiceServant


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


T = TypeVar(
    "T",
    BasicServant,
    BasicEquip,
    BasicCommandCode,
    NiceServant,
    NiceEquip,
    NiceCommandCode,
)


def sort_by_collection_no(input_list: Iterable[T]) -> List[T]:
    """
    Return given list of basic svt objects sorted by their collectionNo attribute
    """
    return sorted(input_list, key=lambda x: x.collectionNo)


def get_lang_en(svt: T) -> T:
    """
    Returns given svt Pydantic object with English name
    """
    lang_en_svt = svt.copy()
    lang_en_svt.name = get_safe(TRANSLATIONS, svt.name)
    return lang_en_svt
