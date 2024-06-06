from decimal import Decimal
from typing import Annotated, Any, Optional, Sequence

from pydantic import Field, HttpUrl

from .base import BaseModelORJson, DecimalSerializer
from .common import BasicCostume, BuffScript, MCAssets, NiceTrait
from .enums import Attribute, FuncApplyTarget, SvtClass
from .gameenums import (
    NiceBuffType,
    NiceConsumeType,
    NiceEventType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceQuestAfterClearType,
    NiceQuestFlag,
    NiceQuestType,
    NiceSvtFlag,
    NiceSvtFlagOriginal,
    NiceSvtType,
    NiceWarFlag,
)


class BasicBuff(BaseModelORJson):
    id: int
    name: str
    originalName: str
    detail: str
    icon: HttpUrl
    type: NiceBuffType
    buffGroup: int
    script: BuffScript
    originalScript: dict[str, Any]
    vals: list[NiceTrait]
    tvals: list[NiceTrait]
    ckSelfIndv: list[NiceTrait]
    ckOpIndv: list[NiceTrait]
    maxRate: int


class BasicFunction(BaseModelORJson):
    funcId: int
    funcType: NiceFuncType
    funcTargetType: NiceFuncTargetType
    funcTargetTeam: FuncApplyTarget
    functvals: list[NiceTrait]
    overWriteTvalsList: list[list[NiceTrait]]
    funcquestTvals: list[NiceTrait]
    funcPopupText: str
    traitVals: list[NiceTrait] = []
    buffs: Sequence[BasicBuff]


class BasicSkill(BaseModelORJson):
    id: int
    name: str
    ruby: str
    icon: Optional[HttpUrl] = None


class BasicTd(BaseModelORJson):
    id: int
    name: str
    ruby: str


class BasicServant(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    originalName: str
    overwriteName: str | None = None
    originalOverwriteName: str | None = None
    type: NiceSvtType
    flag: NiceSvtFlag
    flags: list[NiceSvtFlagOriginal]
    classId: int
    className: SvtClass | str
    attribute: Attribute
    traits: list[NiceTrait]
    rarity: int
    atkMax: int
    hpMax: int
    face: HttpUrl
    costume: dict[int, BasicCostume] = Field(
        ...,
        title="Costume Details",
        description="Mapping <Costume BattleCharaID, Costume Detail>.",
    )


class BasicEquip(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    originalName: str
    type: NiceSvtType
    flag: NiceSvtFlag
    flags: list[NiceSvtFlagOriginal]
    rarity: int
    atkMax: int
    hpMax: int
    face: HttpUrl
    bondEquipOwner: Optional[int] = None
    valentineEquipOwner: Optional[int] = None


class BasicMysticCode(BaseModelORJson):
    id: int
    name: str
    item: MCAssets


class BasicCommandCode(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    rarity: int
    face: HttpUrl


class BasicReversedSkillTd(BaseModelORJson):
    servant: list[BasicServant] = []
    MC: list[BasicMysticCode] = []
    CC: list[BasicCommandCode] = []


class BasicReversedSkillTdType(BaseModelORJson):
    basic: Optional[BasicReversedSkillTd] = None


class BasicSkillReverse(BasicSkill):
    reverse: Optional[BasicReversedSkillTdType] = None


class BasicTdReverse(BasicTd):
    reverse: Optional[BasicReversedSkillTdType] = None


class BasicReversedFunction(BaseModelORJson):
    skill: list[BasicSkillReverse] = []
    NP: list[BasicTdReverse] = []


class BasicReversedFunctionType(BaseModelORJson):
    basic: Optional[BasicReversedFunction] = None


class BasicFunctionReverse(BasicFunction):
    reverse: Optional[BasicReversedFunctionType] = None


class BasicReversedBuff(BaseModelORJson):
    function: list[BasicFunctionReverse] = []


class BasicReversedBuffType(BaseModelORJson):
    basic: Optional[BasicReversedBuff] = None


class BasicBuffReverse(BasicBuff):
    reverse: Optional[BasicReversedBuffType] = None


class BasicEvent(BaseModelORJson):
    id: int
    type: NiceEventType
    name: str
    noticeAt: int
    startedAt: int
    endedAt: int
    finishedAt: int
    materialOpenedAt: int
    warIds: list[int]


class BasicWar(BaseModelORJson):
    id: int
    coordinates: list[list[Annotated[Decimal, DecimalSerializer]]]
    age: str
    name: str
    longName: str
    flags: list[NiceWarFlag]
    eventId: int
    eventName: str


class BasicQuest(BaseModelORJson):
    id: int
    name: str
    type: NiceQuestType
    flags: list[NiceQuestFlag]
    afterClear: NiceQuestAfterClearType
    consumeType: NiceConsumeType
    consume: int
    spotId: int
    spotName: str
    warId: int
    warLongName: str
    priority: int
    noticeAt: int
    openedAt: int
    closedAt: int


class BasicQuestPhase(BasicQuest):
    phase: int
    individuality: list[NiceTrait]
    qp: int
    exp: int
    bond: int
    battleBgId: int
