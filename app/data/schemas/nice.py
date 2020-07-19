from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, HttpUrl

from ..enums import (
    Attribute,
    FuncApplyTarget,
    Gender,
    NiceBuffType,
    NiceCardType,
    NiceCondType,
    NiceConsumeType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceItemBGType,
    NiceItemType,
    NiceQuestType,
    NiceStatusRank,
    NiceSvtType,
    SvtClass,
    Trait,
)
from .base import BaseModelORJson


class AssetURL:
    charaGraph: Dict[int, str] = {
        0: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
        1: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
        2: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
        3: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    }
    commands: str = "{base_url}/{region}/Servants/Commands/{item_id}/card_servant_{i}.png"
    status: str = "{base_url}/{region}/Servants/Status/{item_id}/status_servant_{i}.png"
    charaGraphDefault: str = "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png"
    skillIcon: str = "{base_url}/{region}/SkillIcons/skill_{item_id:05}.png"
    buffIcon: str = "{base_url}/{region}/BuffIcons/bufficon_{item_id}.png"
    items: str = "{base_url}/{region}/Items/{item_id}.png"
    face: str = "{base_url}/{region}/Faces/f_{item_id}{i}.png"
    mcitem: str = "{base_url}/{region}/Items/masterequip{item_id:05}.png"
    mc: Dict[str, str] = {
        "item": "{base_url}/{region}/Items/masterequip{item_id:05}.png",
        "masterFace": "{base_url}/{region}/MasterFace/equip{item_id:05}.png",
        "masterFigure": "{base_url}/{region}/MasterFigure/equip{item_id:05}.png",
    }
    commandCode: str = "{base_url}/{region}/CommandCodes/c_{item_id}.png"
    commandGraph: str = "{base_url}/{region}/CommandGraph/{item_id}a.png"


class Language(str, Enum):
    en = "en"


class NiceItem(BaseModelORJson):
    id: int
    name: str
    type: Union[NiceItemType, int]
    icon: HttpUrl
    background: NiceItemBGType


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: List[NiceItemAmount]
    qp: int


class BaseVals(BaseModel):
    Rate: Optional[int] = None
    Turn: Optional[int] = None
    Count: Optional[int] = None
    Value: Optional[int] = None
    Value2: Optional[int] = None
    UseRate: Optional[int] = None
    Target: Optional[int] = None
    Correction: Optional[int] = None
    ParamAdd: Optional[int] = None
    ParamMax: Optional[int] = None
    HideMiss: Optional[int] = None
    OnField: Optional[int] = None
    HideNoEffect: Optional[int] = None
    Unaffected: Optional[int] = None
    ShowState: Optional[int] = None
    AuraEffectId: Optional[int] = None
    ActSet: Optional[int] = None
    ActSetWeight: Optional[int] = None
    ShowQuestNoEffect: Optional[int] = None
    CheckDead: Optional[int] = None
    RatioHPHigh: Optional[int] = None
    RatioHPLow: Optional[int] = None
    SetPassiveFrame: Optional[int] = None
    ProcPassive: Optional[int] = None
    ProcActive: Optional[int] = None
    HideParam: Optional[int] = None
    SkillID: Optional[int] = None
    SkillLV: Optional[int] = None
    ShowCardOnly: Optional[int] = None
    EffectSummon: Optional[int] = None
    RatioHPRangeHigh: Optional[int] = None
    RatioHPRangeLow: Optional[int] = None
    TargetList: Optional[int] = None
    OpponentOnly: Optional[int] = None
    StatusEffectId: Optional[int] = None
    EndBattle: Optional[int] = None
    LoseBattle: Optional[int] = None
    AddIndividualty: Optional[int] = None
    AddLinkageTargetIndividualty: Optional[int] = None
    SameBuffLimitTargetIndividuality: Optional[int] = None
    SameBuffLimitNum: Optional[int] = None
    CheckDuplicate: Optional[int] = None
    OnFieldCount: Optional[int] = None
    TargetRarityList: Optional[str] = None
    DependFuncId: Optional[int] = None
    InvalidHide: Optional[int] = None
    OutEnemyNpcId: Optional[int] = None
    InEnemyNpcId: Optional[int] = None
    OutEnemyPosition: Optional[int] = None
    IgnoreIndividuality: Optional[int] = None
    StarHigher: Optional[int] = None
    ChangeTDCommandType: Optional[int] = None
    ShiftNpcId: Optional[int] = None
    DisplayLastFuncInvalidType: Optional[int] = None
    AndCheckIndividualityList: Optional[int] = None
    WinBattleNotRelatedSurvivalStatus: Optional[int] = None
    ForceSelfInstantDeath: Optional[int] = None
    ChangeMaxBreakGauge: Optional[int] = None
    ParamAddMaxValue: Optional[int] = None
    ParamAddMaxCount: Optional[int] = None
    LossHpNoChangeDamage: Optional[int] = None
    IncludePassiveIndividuality: Optional[int] = None
    # These are not DataVals but guesses from SkillLvEntity and EventDropUpValInfo
    Individuality: Optional[int] = None
    EventId: Optional[int] = None
    AddCount: Optional[int] = None
    RateCount: Optional[int] = None
    FriendshipTarget: Optional[NiceFuncTargetType] = None
    # aa0: Optional[int] = None
    # aa1: Optional[int] = None
    # aa2: Optional[int] = None
    # aa3: Optional[int] = None
    # aa4: Optional[int] = None


class Vals(BaseVals):
    DependFuncVals: Optional[BaseVals] = None


class NiceTrait(BaseModel):
    id: int
    name: Trait


class NiceBuff(BaseModelORJson):
    id: int
    name: str
    detail: str
    icon: Optional[HttpUrl] = None
    type: Union[NiceBuffType, int]
    vals: List[NiceTrait]
    tvals: List[NiceTrait]
    ckSelfIndv: List[NiceTrait]
    ckOpIndv: List[NiceTrait]
    maxRate: int


class NiceBaseFunction(BaseModelORJson):
    funcId: int
    funcType: Union[NiceFuncType, int]
    funcTargetType: Union[NiceFuncTargetType, int]
    funcTargetTeam: Union[FuncApplyTarget, int]
    funcPopupText: str
    funcPopupIcon: Optional[HttpUrl] = None
    functvals: List[NiceTrait]
    funcquestTvals: List[NiceTrait]
    traitVals: List[NiceTrait] = []
    buffs: List[NiceBuff]


class NiceFunction(NiceBaseFunction):
    svals: List[Vals]
    svals2: Optional[List[Vals]] = None
    svals3: Optional[List[Vals]] = None
    svals4: Optional[List[Vals]] = None
    svals5: Optional[List[Vals]] = None


class NiceSkill(BaseModelORJson):
    id: int
    num: int = -1
    name: str
    detail: Optional[str] = None
    strengthStatus: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    icon: Optional[HttpUrl] = None
    coolDown: List[int]
    actIndividuality: List[NiceTrait]
    functions: List[NiceFunction]


class NpGain(BaseModel):
    buster: List[int]
    arts: List[int]
    quick: List[int]
    extra: List[int]
    defence: List[int]
    np: List[int]


class NiceTd(BaseModelORJson):
    id: int
    num: int
    card: NiceCardType
    name: str
    rank: str
    type: str
    detail: Optional[str] = None
    npGain: NpGain
    npDistribution: List[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: List[NiceTrait]
    functions: List[NiceFunction]


class MCAssets(BaseModel):
    male: HttpUrl
    female: HttpUrl


class ExtraMCAssets(BaseModel):
    item: MCAssets
    masterFace: MCAssets
    masterFigure: MCAssets


class NiceMysticCode(BaseModelORJson):
    id: int
    name: str
    detail: str
    maxLv: int
    extraAssets: ExtraMCAssets
    skills: List[NiceSkill]
    expRequired: List[int]


class ExtraAssetsUrl(BaseModel):
    ascension: Optional[Dict[int, HttpUrl]] = None
    costume: Optional[Dict[int, HttpUrl]] = None
    equip: Optional[Dict[int, HttpUrl]] = None
    cc: Optional[Dict[int, HttpUrl]] = None


class ExtraCCAssets(BaseModel):
    charaGraph: ExtraAssetsUrl
    faces: ExtraAssetsUrl


class ExtraAssets(ExtraCCAssets):
    commands: ExtraAssetsUrl
    status: ExtraAssetsUrl


class NiceLoreComment(BaseModel):
    id: int
    priority: int
    condMessage: str
    comment: str
    condType: NiceCondType
    condValues: Optional[List[int]]
    condValue2: int


class NiceLoreStats(BaseModel):
    strength: NiceStatusRank  # power
    endurance: NiceStatusRank  # defense
    agility: NiceStatusRank
    magic: NiceStatusRank
    luck: NiceStatusRank
    np: NiceStatusRank  # treasureDevice
    # policy: NiceStatusRank
    # personality: NiceStatusRank
    # deity: NiceStatusRank


class NiceLore(BaseModel):
    cv: str
    illustrator: str
    stats: Optional[NiceLoreStats] = None
    comments: List[NiceLoreComment]


class NiceServant(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    className: SvtClass
    type: NiceSvtType
    rarity: int
    cost: int
    lvMax: int
    extraAssets: ExtraAssets
    gender: Gender
    attribute: Attribute
    traits: List[NiceTrait]
    starAbsorb: int
    starGen: int
    instantDeathChance: int
    cards: List[NiceCardType]
    hitsDistribution: Dict[NiceCardType, List[int]]
    atkBase: int
    atkMax: int
    hpBase: int
    hpMax: int
    growthCurve: int
    atkGrowth: List[int]
    hpGrowth: List[int]
    bondGrowth: List[int]
    ascensionMaterials: Dict[int, NiceLvlUpMaterial]
    skillMaterials: Dict[int, NiceLvlUpMaterial]
    skills: List[NiceSkill]
    classPassive: List[NiceSkill]
    noblePhantasms: List[NiceTd]
    profile: Optional[NiceLore] = None


class NiceSkillReverse(NiceSkill):
    reverseServants: List[NiceServant] = []
    reverseMC: List[NiceMysticCode] = []


class NiceTdReverse(NiceTd):
    reverseServants: List[NiceServant] = []


class NiceBaseFunctionReverse(NiceBaseFunction):
    reverseSkills: List[NiceSkillReverse] = []
    reverseTds: List[NiceTdReverse] = []


class NiceBuffReverse(NiceBuff):
    reverseFunctions: List[NiceBaseFunctionReverse] = []


class NiceEquip(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    rarity: int
    cost: int
    lvMax: int
    extraAssets: ExtraAssets
    atkBase: int
    atkMax: int
    hpBase: int
    hpMax: int
    growthCurve: int
    atkGrowth: List[int]
    hpGrowth: List[int]
    skills: List[NiceSkill]
    profile: Optional[NiceLore] = None


class NiceCommandCode(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    rarity: int
    extraAssets: ExtraCCAssets
    skills: List[NiceSkill]
    comment: str


class NiceQuestPhase(BaseModelORJson):
    id: int
    phase: int
    name: str
    type: Union[NiceQuestType, int]
    consumeType: Union[NiceConsumeType, int]
    consume: int
    spotId: int
    className: List[SvtClass]
    individuality: List[NiceTrait]
    qp: int
    exp: int
    bond: int
    noticeAt: int
    openedAt: int
    closedAt: int
