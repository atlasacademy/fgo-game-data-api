from decimal import Decimal
from typing import Optional

from pydantic import Field, HttpUrl

from .base import BaseModelORJson
from .common import BasicCostume, MCAssets, NiceBuffScript, NiceTrait
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
    NiceSvtType,
    NiceWarFlag,
)


class BasicBuff(BaseModelORJson):
    id: int
    name: str
    icon: HttpUrl
    type: NiceBuffType
    script: NiceBuffScript
    vals: list[NiceTrait]
    tvals: list[NiceTrait]
    ckSelfIndv: list[NiceTrait]
    ckOpIndv: list[NiceTrait]


class BasicFunction(BaseModelORJson):
    funcId: int
    funcType: NiceFuncType
    funcTargetType: NiceFuncTargetType
    funcTargetTeam: FuncApplyTarget
    functvals: list[NiceTrait]
    funcquestTvals: list[NiceTrait]
    traitVals: list[NiceTrait] = []
    buffs: list[BasicBuff]


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
    type: NiceSvtType
    flag: NiceSvtFlag
    className: SvtClass
    attribute: Attribute
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
    type: NiceSvtType
    flag: NiceSvtFlag
    rarity: int
    atkMax: int
    hpMax: int
    face: HttpUrl
    bondEquipOwner: Optional[int]
    valentineEquipOwner: Optional[int]


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
    coordinates: list[list[Decimal]]
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
