from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, HttpUrl

from ..enums import (
    Attribute,
    CardType,
    FuncApplyTarget,
    Gender,
    NiceBuffType,
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


ASSET_URL: Dict[str, str] = {
    "charaGraph1": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
    "charaGraph2": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
    "charaGraph3": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
    "charaGraph4": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    "charaGraphDefault": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png",
    "skillIcon": "{base_url}/{region}/SkillIcons/skill_{item_id:05}.png",
    "buffIcon": "{base_url}/{region}/BuffIcons/bufficon_{item_id}.png",
    "items": "{base_url}/{region}/Items/{item_id}.png",
    "face": "{base_url}/{region}/Faces/f_{item_id}{i}.png",
    "mcitem": "{base_url}/{region}/Items/masterequip{item_id:05}.png",
    "mcmasterFace": "{base_url}/{region}/MasterFigure/equip{item_id:05}.png",
    "mcmasterFigure": "{base_url}/{region}/MasterFace/equip{item_id:05}.png",
}


class Language(str, Enum):
    en = "en"


class NiceItem(BaseModel):
    id: int
    name: str
    type: NiceItemType
    icon: HttpUrl
    background: NiceItemBGType


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: List[NiceItemAmount]
    qp: int


class Vals(BaseModel):
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
    TargetRarityList: Optional[str] = None


class NiceTrait(BaseModel):
    id: int
    name: Trait


class NiceBuff(BaseModel):
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


class NiceFunction(BaseModel):
    funcId: int
    funcType: Union[NiceFuncType, int]
    funcTargetType: Union[NiceFuncTargetType, int]
    funcTargetTeam: Union[FuncApplyTarget, int]
    funcPopupText: str
    funcPopupIcon: Optional[HttpUrl] = None
    functvals: List[NiceTrait]
    funcquestTvals: List[int]
    buffs: List[NiceBuff]
    svals: List[Vals]
    svals2: Optional[List[Vals]] = None
    svals3: Optional[List[Vals]] = None
    svals4: Optional[List[Vals]] = None
    svals5: Optional[List[Vals]] = None


class NiceSkill(BaseModel):
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


class NiceTd(BaseModel):
    id: int
    num: int
    card: CardType
    name: str
    rank: str
    type: str
    detail: Optional[str] = None
    npNpGain: int
    npDistribution: List[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: List[NiceTrait]
    functions: List[NiceFunction]


class ExtraAssetsUrl(BaseModel):
    ascension: Optional[Dict[int, HttpUrl]] = None
    costume: Optional[Dict[int, HttpUrl]] = None
    equip: Optional[Dict[int, HttpUrl]] = None


class ExtraAssets(BaseModel):
    charaGraph: ExtraAssetsUrl
    faces: ExtraAssetsUrl


class NpGain(BaseModel):
    buster: int
    arts: int
    quick: int
    extra: int
    defence: int


class HitsDistribution(BaseModel):
    buster: List[int]
    arts: List[int]
    quick: List[int]
    extra: List[int]


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
    stats: Optional[NiceLoreStats] = None
    comments: List[NiceLoreComment]


class NiceServant(BaseModel):
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
    cards: List[CardType]
    npGain: Optional[NpGain] = None
    hitsDistribution: HitsDistribution
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


class NiceEquip(BaseModel):
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


class MCAssets(BaseModel):
    male: HttpUrl
    female: HttpUrl


class ExtraMCAssets(BaseModel):
    item: MCAssets
    masterFace: MCAssets
    masterFigure: MCAssets


class NiceMysticCode(BaseModel):
    id: int
    name: str
    detail: str
    maxLv: int
    extraAssets: ExtraMCAssets
    skills: List[NiceSkill]
    expRequired: List[int]


class NiceQuestPhase(BaseModel):
    id: int
    phase: int
    name: str
    type: NiceQuestType
    consumeType: NiceConsumeType
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
