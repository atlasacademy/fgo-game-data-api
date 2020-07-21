from enum import Enum
from typing import TypeVar


T = TypeVar("T", bound="ReverseDepth")


class Region(str, Enum):
    NA = "NA"
    JP = "JP"


class ReverseDepth(str, Enum):
    function = "function"
    skillNp = "skillNp"
    servant = "servant"

    def order(self) -> int:
        # https://github.com/PyCQA/pylint/issues/2306
        self_value = str(self.value)
        if self_value == "function":
            return 1
        elif self_value == "skillNp":
            return 2
        else:
            return 3

    def __ge__(self: T, other: T) -> bool:  # type: ignore[override]
        if other.__class__ is self.__class__:
            return self.order() >= other.order()
        return NotImplemented
