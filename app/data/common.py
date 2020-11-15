from enum import Enum
from typing import Union


class Region(str, Enum):
    """Region Enum"""

    NA = "NA"
    JP = "JP"


class Language(str, Enum):
    """Language Enum"""

    en = "en"
    jp = "jp"


class ReverseData(str, Enum):
    """Reverse Data Detail Level"""

    basic = "basic"
    nice = "nice"


class ReverseDepth(str, Enum):
    """Reverse Data Depth"""

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

    def __ge__(self: "ReverseDepth", other: Union["ReverseDepth", str]) -> bool:
        if isinstance(other, ReverseDepth):
            return self.order() >= other.order()
        return str(self.value) >= other
