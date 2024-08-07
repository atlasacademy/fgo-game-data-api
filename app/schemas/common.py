from enum import StrEnum
from typing import Any, Optional, Union

from pydantic import BaseModel, HttpUrl

from .base import BaseModelORJson
from .enums import SvtClass, Trait
from .gameenums import (
    NiceBuffConvertLimitType,
    NiceBuffConvertType,
    NiceBuffType,
    NiceClassRelationOverwriteType,
)


class RepoInfo(BaseModelORJson):
    hash: str
    timestamp: int


class Region(StrEnum):
    """Region Enum"""

    JP = "JP"
    NA = "NA"
    CN = "CN"
    KR = "KR"
    TW = "TW"


class Language(StrEnum):
    """Language Enum"""

    jp = "jp"
    en = "en"


class ReverseData(StrEnum):
    """Reverse Data Detail Level"""

    basic = "basic"
    nice = "nice"


class ReverseDepth(StrEnum):
    """Reverse Data Depth"""

    function = "function"
    skillNp = "skillNp"
    servant = "servant"

    def order(self) -> int:
        self_value = str(self.value)
        if self.value == "function":
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
    atkSide: dict[SvtClass | str, dict[SvtClass | str, RelationOverwriteDetail]]
    defSide: dict[SvtClass | str, dict[SvtClass | str, RelationOverwriteDetail]]


class BuffConvertScript(BaseModel):
    OverwritePopupText: list[str]


class BuffConvert(BaseModel):
    """Buff Convert

    Due to a limitation in Pydantic and OpenAPI schema generation, `dict[str, Any]`
    is used in place of either BasicBuff or NiceBuff
    """

    targetLimit: NiceBuffConvertLimitType
    convertType: NiceBuffConvertType
    targets: list[int] | list[NiceTrait] | list[dict[str, Any]]
    targetBuffs: list[dict[str, Any]]
    targetIndividualities: list[NiceTrait]
    convertBuffs: list[dict[str, Any]]
    script: BuffConvertScript
    effectId: int


class BuffScript(BaseModel):
    checkIndvType: Optional[int] = None
    CheckOpponentBuffTypes: Optional[list[NiceBuffType]] = None
    relationId: Optional[NiceBuffRelationOverwrite] = None
    ReleaseText: Optional[str] = None
    DamageRelease: Optional[int] = None
    INDIVIDUALITIE: Optional[NiceTrait] = None
    INDIVIDUALITIE_COUNT_ABOVE: int | None = None
    INDIVIDUALITIE_COUNT_BELOW: int | None = None
    INDIVIDUALITIE_AND: list[NiceTrait] | None = None
    INDIVIDUALITIE_OR: list[NiceTrait] | None = None
    UpBuffRateBuffIndiv: Optional[list[NiceTrait]] = None
    HP_LOWER: Optional[int] = None
    HP_HIGHER: int | None = None
    CounterMessage: str | None = None
    avoidanceText: str | None = None
    gutsText: str | None = None
    missText: str | None = None
    AppId: int | None = None
    IncludeIgnoreIndividuality: int | None = None
    ProgressSelfTurn: int | None = None
    TargetIndiv: NiceTrait | None = None
    extendLowerLimit: int | None = None
    convert: BuffConvert | None = None
    useFirstTimeInTurn: int | None = None
    fromCommandSpell: int | None = None
    fromMasterEquip: int | None = None


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
