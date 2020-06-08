from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, HttpUrl

from ..enums import (
    Attribute,
    CardType,
    FuncApplyTarget,
    Gender,
    NiceBuffType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceItemType,
    SvtClass,
    Trait,
)


ASSET_URL: Dict[str, str] = {
    "charaGraph1": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
    "charaGraph2": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
    "charaGraph3": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
    "charaGraph4": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    "charaGraphEquip": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png",
    "charaGraphcostume": "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png",
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


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceAscensionMaterial(BaseModel):
    items: List[NiceItemAmount]
    qp: int


class NiceSkillMaterial(BaseModel):
    items: List[NiceItemAmount]
    qp: int


class Vals(BaseModel):
    Rate: List[int] = []
    Turn: List[int] = []
    Count: List[int] = []
    Value: List[int] = []
    Value2: List[int] = []
    UseRate: List[int] = []
    Target: List[int] = []
    Correction: List[int] = []
    ParamAdd: List[int] = []
    ParamMax: List[int] = []
    HideMiss: List[int] = []
    OnField: List[int] = []
    HideNoEffect: List[int] = []
    Unaffected: List[int] = []
    ShowState: List[int] = []
    AuraEffectId: List[int] = []
    ActSet: List[int] = []
    ActSetWeight: List[int] = []
    ShowQuestNoEffect: List[int] = []
    CheckDead: List[int] = []
    RatioHPHigh: List[int] = []
    RatioHPLow: List[int] = []
    SetPassiveFrame: List[int] = []
    ProcPassive: List[int] = []
    ProcActive: List[int] = []
    HideParam: List[int] = []
    SkillID: List[int] = []
    SkillLV: List[int] = []
    ShowCardOnly: List[int] = []
    EffectSummon: List[int] = []
    RatioHPRangeHigh: List[int] = []
    RatioHPRangeLow: List[int] = []
    TargetList: List[int] = []
    OpponentOnly: List[int] = []
    TargetRarityList: List[str] = []


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
    buffs: List[NiceBuff]
    svals: Vals
    svals2: Optional[Vals] = None
    svals3: Optional[Vals] = None
    svals4: Optional[Vals] = None
    svals5: Optional[Vals] = None


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
    detail: Optional[str] = None
    npNpGain: int
    npDistribution: List[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: List[NiceTrait]
    functions: List[NiceFunction]


class CharaGraph(BaseModel):
    ascension: Optional[Dict[int, HttpUrl]] = None
    costume: Optional[Dict[int, HttpUrl]] = None
    equip: Optional[Dict[int, HttpUrl]] = None


class Faces(BaseModel):
    ascension: Optional[Dict[int, HttpUrl]] = None
    costume: Optional[Dict[int, HttpUrl]] = None


class ExtraAssets(BaseModel):
    charaGraph: CharaGraph
    faces: Faces


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


class NiceServant(BaseModel):
    id: int
    collectionNo: int
    name: str
    className: SvtClass
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
    npGain: NpGain
    hitsDistribution: HitsDistribution
    atkBase: int
    atkMax: int
    hpBase: int
    hpMax: int
    growthCurve: int
    atkGrowth: List[int]
    hpGrowth: List[int]
    bondGrowth: List[int]
    ascensionMaterials: Dict[int, NiceAscensionMaterial]
    skillMaterials: Dict[int, NiceSkillMaterial]
    skills: List[NiceSkill]
    classPassive: List[NiceSkill]
    noblePhantasms: List[NiceTd]


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
