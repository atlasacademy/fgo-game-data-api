from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, HttpUrl

from .base import BaseModelORJson
from .enums import SvtClass, Trait
from .gameenums import NiceBuffType, NiceClassRelationOverwriteType


class RepoInfo(BaseModelORJson):
    hash: str
    timestamp: int


class Region(str, Enum):
    """Region Enum"""

    NA = "NA"
    JP = "JP"
    CN = "CN"
    KR = "KR"
    TW = "TW"


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


class NiceTrait(BaseModel):
    """Nice trait"""

    id: int
    name: Trait
    negative: Optional[bool] = None


class MCAssets(BaseModel):
    """Mystic Code Assets"""

    male: HttpUrl
    female: HttpUrl


class RelationOverwriteDetail(BaseModel):
    damageRate: int
    type: NiceClassRelationOverwriteType


class NiceBuffRelationOverwrite(BaseModel):
    atkSide: dict[SvtClass, dict[SvtClass, RelationOverwriteDetail]]
    defSide: dict[SvtClass, dict[SvtClass, RelationOverwriteDetail]]


class NiceBuffScript(BaseModel):
    checkIndvType: Optional[int] = None
    CheckOpponentBuffTypes: Optional[list[NiceBuffType]] = None
    relationId: Optional[NiceBuffRelationOverwrite] = None
    ReleaseText: Optional[str] = None
    DamageRelease: Optional[int] = None
    INDIVIDUALITIE: Optional[NiceTrait] = None
    UpBuffRateBuffIndiv: Optional[list[NiceTrait]] = None
    HP_LOWER: Optional[int] = None


class ScriptLink(BaseModelORJson):
    scriptId: str
    script: HttpUrl


class NiceValentineScript(ScriptLink):
    scriptName: str


class StageLink(BaseModel):
    questId: int
    phase: int
    stage: int


class BasicCostume(BaseModelORJson):
    id: int
    costumeCollectionNo: int
    battleCharaId: int
    shortName: str


class NiceCostume(BaseModelORJson):
    id: int
    costumeCollectionNo: int
    battleCharaId: int
    name: str
    shortName: str
    detail: str
    priority: int
