from typing import List, Optional

from pydantic import HttpUrl

from ..enums import (
    FuncApplyTarget,
    NiceBuffType,
    NiceEventType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceSvtType,
    SvtClass,
)
from .base import BaseModelORJson
from .common import MCAssets, NiceTrait


class BasicBuff(BaseModelORJson):
    id: int
    name: str
    icon: HttpUrl
    type: NiceBuffType
    vals: List[NiceTrait]
    tvals: List[NiceTrait]
    ckSelfIndv: List[NiceTrait]
    ckOpIndv: List[NiceTrait]


class BasicFunction(BaseModelORJson):
    funcId: int
    funcType: NiceFuncType
    funcTargetType: NiceFuncTargetType
    funcTargetTeam: FuncApplyTarget
    functvals: List[NiceTrait]
    funcquestTvals: List[NiceTrait]
    traitVals: List[NiceTrait] = []
    buffs: List[BasicBuff]


class BasicSkill(BaseModelORJson):
    id: int
    name: str
    icon: Optional[HttpUrl] = None


class BasicTd(BaseModelORJson):
    id: int
    name: str


class BasicServant(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    type: NiceSvtType
    className: SvtClass
    rarity: int
    atkMax: int
    hpMax: int
    face: HttpUrl


class BasicEquip(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    type: NiceSvtType
    rarity: int
    atkMax: int
    hpMax: int
    face: HttpUrl


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
    servant: List[BasicServant] = []
    MC: List[BasicMysticCode] = []
    CC: List[BasicCommandCode] = []


class BasicReversedSkillTdType(BaseModelORJson):
    basic: Optional[BasicReversedSkillTd] = None


class BasicSkillReverse(BasicSkill):
    reverse: Optional[BasicReversedSkillTdType] = None


class BasicTdReverse(BasicTd):
    reverse: Optional[BasicReversedSkillTdType] = None


class BasicReversedFunction(BaseModelORJson):
    skill: List[BasicSkillReverse] = []
    NP: List[BasicTdReverse] = []


class BasicReversedFunctionType(BaseModelORJson):
    basic: Optional[BasicReversedFunction] = None


class BasicFunctionReverse(BasicFunction):
    reverse: Optional[BasicReversedFunctionType] = None


class BasicReversedBuff(BaseModelORJson):
    function: List[BasicFunctionReverse] = []


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
