from decimal import Decimal
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, HttpUrl
from pydantic.generics import GenericModel

from ..enums import (
    Attribute,
    FuncApplyTarget,
    NiceBuffType,
    NiceCardType,
    NiceClassRelationOverwriteType,
    NiceCondType,
    NiceConsumeType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceItemBGType,
    NiceItemType,
    NiceQuestType,
    NiceSkillType,
    NiceStatusRank,
    NiceSvtFlag,
    NiceSvtType,
    NiceSvtVoiceType,
    NiceVoiceCondType,
    SvtClass,
)
from .base import BaseModelORJson
from .basic import BasicReversedBuff, BasicReversedFunction, BasicReversedSkillTd
from .common import MCAssets, NiceTrait


class AssetURL:
    charaGraph: dict[int, str] = {
        1: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
        2: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
        3: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
        4: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    }
    commands: str = "{base_url}/{region}/Servants/Commands/{item_id}/card_servant_{i}.png"
    status: str = "{base_url}/{region}/Servants/Status/{item_id}/status_servant_{i}.png"
    charaGraphDefault: str = "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png"
    charaFigure: str = "{base_url}/{region}/CharaFigure/{item_id}{i}/{item_id}{i}_merged.png"
    narrowFigure: dict[int, str] = {
        1: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png",
        2: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@1.png",
        3: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@2.png",
        4: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}_2@0.png",
    }
    narrowFigureDefault: str = "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png"
    skillIcon: str = "{base_url}/{region}/SkillIcons/skill_{item_id:05}.png"
    buffIcon: str = "{base_url}/{region}/BuffIcons/bufficon_{item_id}.png"
    items: str = "{base_url}/{region}/Items/{item_id}.png"
    face: str = "{base_url}/{region}/Faces/f_{item_id}{i}.png"
    equipFace: str = "{base_url}/{region}/EquipFaces/f_{item_id}{i}.png"
    enemy: str = "{base_url}/{region}/Enemys/{item_id}{i}.png"
    mcitem: str = "{base_url}/{region}/Items/masterequip{item_id:05}.png"
    mc: dict[str, str] = {
        "item": "{base_url}/{region}/Items/masterequip{item_id:05}.png",
        "masterFace": "{base_url}/{region}/MasterFace/equip{item_id:05}.png",
        "masterFigure": "{base_url}/{region}/MasterFigure/equip{item_id:05}.png",
    }
    commandCode: str = "{base_url}/{region}/CommandCodes/c_{item_id}.png"
    commandGraph: str = "{base_url}/{region}/CommandGraph/{item_id}a.png"
    audio: str = "{base_url}/{region}/Audio/{folder}/{id}.mp3"


class NiceItem(BaseModelORJson):
    id: int
    name: str
    type: NiceItemType
    icon: HttpUrl
    background: NiceItemBGType


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: list[NiceItemAmount]
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
    TargetList: Optional[list[int]] = None
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
    TargetRarityList: Optional[list[int]] = None
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
    AndCheckIndividualityList: Optional[list[int]] = None
    WinBattleNotRelatedSurvivalStatus: Optional[int] = None
    ForceSelfInstantDeath: Optional[int] = None
    ChangeMaxBreakGauge: Optional[int] = None
    ParamAddMaxValue: Optional[int] = None
    ParamAddMaxCount: Optional[int] = None
    LossHpChangeDamage: Optional[int] = None
    IncludePassiveIndividuality: Optional[int] = None
    MotionChange: Optional[int] = None
    PopLabelDelay: Optional[int] = None
    # These are not DataVals but guesses from SkillLvEntity and EventDropUpValInfo
    Individuality: Optional[int] = None
    EventId: Optional[int] = None
    AddCount: Optional[int] = None
    RateCount: Optional[int] = None
    # aa0: Optional[int] = None
    # aa1: Optional[int] = None
    # aa2: Optional[int] = None
    # aa3: Optional[int] = None
    # aa4: Optional[int] = None


class Vals(BaseVals):
    DependFuncVals: Optional[BaseVals] = None


class RelationOverwriteDetail(BaseModelORJson):
    damageRate: int
    type: NiceClassRelationOverwriteType


class NiceBuffRelationOverwrite(BaseModelORJson):
    atkSide: dict[SvtClass, dict[SvtClass, RelationOverwriteDetail]]
    defSide: dict[SvtClass, dict[SvtClass, RelationOverwriteDetail]]


class NiceBuffScript(BaseModelORJson):
    relationId: Optional[NiceBuffRelationOverwrite] = None
    ReleaseText: Optional[str] = None
    DamageRelease: Optional[int] = None


class NiceBuff(BaseModelORJson):
    id: int
    name: str
    detail: str
    icon: Optional[HttpUrl] = None
    type: NiceBuffType
    buffGroup: int
    script: NiceBuffScript
    vals: list[NiceTrait]
    tvals: list[NiceTrait]
    ckSelfIndv: list[NiceTrait]
    ckOpIndv: list[NiceTrait]
    maxRate: int


class NiceBaseFunction(BaseModelORJson):
    funcId: int
    funcType: NiceFuncType
    funcTargetType: NiceFuncTargetType
    funcTargetTeam: FuncApplyTarget
    funcPopupText: str
    funcPopupIcon: Optional[HttpUrl] = None
    functvals: list[NiceTrait]
    funcquestTvals: list[NiceTrait]
    traitVals: list[NiceTrait] = []
    buffs: list[NiceBuff]


class NiceFunction(NiceBaseFunction):
    svals: list[Vals]
    svals2: Optional[list[Vals]] = None
    svals3: Optional[list[Vals]] = None
    svals4: Optional[list[Vals]] = None
    svals5: Optional[list[Vals]] = None
    followerVals: Optional[list[Vals]] = None


class NiceSkillScript(BaseModel):
    NP_HIGHER: Optional[list[int]] = None
    NP_LOWER: Optional[list[int]] = None
    STAR_HIGHER: Optional[list[int]] = None
    STAR_LOWER: Optional[list[int]] = None
    HP_VAL_HIGHER: Optional[list[int]] = None
    HP_VAL_LOWER: Optional[list[int]] = None
    HP_PER_HIGHER: Optional[list[int]] = None
    HP_PER_LOWER: Optional[list[int]] = None


class NiceSkill(BaseModelORJson):
    id: int
    num: int = -1
    name: str
    detail: Optional[str] = None
    type: NiceSkillType
    strengthStatus: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    icon: Optional[HttpUrl] = None
    coolDown: list[int]
    actIndividuality: list[NiceTrait]
    script: NiceSkillScript
    functions: list[NiceFunction]


class NpGain(BaseModel):
    buster: list[int]
    arts: list[int]
    quick: list[int]
    extra: list[int]
    defence: list[int]
    np: list[int]


class NiceTd(BaseModelORJson):
    id: int
    num: int
    card: NiceCardType
    name: str
    icon: Optional[HttpUrl] = None
    rank: str
    type: str
    detail: Optional[str] = None
    npGain: NpGain
    npDistribution: list[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: list[NiceTrait]
    functions: list[NiceFunction]


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
    skills: list[NiceSkill]
    expRequired: list[int]


class ExtraAssetsUrl(BaseModel):
    ascension: Optional[dict[int, HttpUrl]] = None
    costume: Optional[dict[int, HttpUrl]] = None
    equip: Optional[dict[int, HttpUrl]] = None
    cc: Optional[dict[int, HttpUrl]] = None


class ExtraCCAssets(BaseModel):
    charaGraph: ExtraAssetsUrl
    faces: ExtraAssetsUrl


class ExtraAssets(ExtraCCAssets):
    narrowFigure: ExtraAssetsUrl
    charaFigure: ExtraAssetsUrl
    commands: ExtraAssetsUrl
    status: ExtraAssetsUrl
    equipFace: ExtraAssetsUrl


AscensionAddData = TypeVar("AscensionAddData")


class AscensionAddEntry(GenericModel, Generic[AscensionAddData]):
    ascension: dict[int, AscensionAddData]
    costume: dict[int, AscensionAddData]


class AscensionAdd(BaseModel):
    individuality: AscensionAddEntry[list[NiceTrait]]
    voicePrefix: AscensionAddEntry[int]


class NiceServantChange(BaseModel):
    beforeTreasureDeviceIds: list[int]
    afterTreasureDeviceIds: list[int]
    svtId: int
    priority: int
    condType: NiceCondType
    condTargetId: int
    condValue: int
    name: str
    svtVoiceId: int
    limitCount: int
    flag: int
    battleSvtId: int


class NiceLoreComment(BaseModel):
    id: int
    priority: int
    condMessage: str
    comment: str
    condType: NiceCondType
    condValues: Optional[list[int]]
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


class NiceCostume(BaseModel):
    id: int
    costumeCollectionNo: int
    name: str
    shortName: str
    detail: str
    priority: int


class NiceVoiceCond(BaseModel):
    condType: NiceVoiceCondType
    value: int
    valueList: list[int] = []
    eventId: int


class NiceVoiceLine(BaseModel):
    name: Optional[str] = None
    condType: Optional[NiceCondType] = None
    condValue: Optional[int] = None
    priority: Optional[int] = None
    svtVoiceType: Optional[NiceSvtVoiceType] = None
    overwriteName: str
    id: list[str]
    audioAssets: list[str]
    delay: list[Decimal]
    face: list[int]
    form: list[int]
    text: list[str]
    subtitle: str
    conds: list[NiceVoiceCond]


class NiceVoiceGroup(BaseModel):
    svtId: int
    voicePrefix: int
    type: NiceSvtVoiceType
    voiceLines: list[NiceVoiceLine]


class NiceLore(BaseModel):
    cv: str
    illustrator: str
    stats: Optional[NiceLoreStats] = None
    costume: dict[int, NiceCostume]
    comments: list[NiceLoreComment]
    voices: list[NiceVoiceGroup]


class NiceServantScript(BaseModel):
    SkillRankUp: Optional[dict[int, list[int]]] = None


class NiceCommandCode(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    rarity: int
    extraAssets: ExtraCCAssets
    skills: list[NiceSkill]
    comment: str


class NiceServant(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    className: SvtClass
    type: NiceSvtType
    flag: NiceSvtFlag
    rarity: int
    cost: int
    lvMax: int
    extraAssets: ExtraAssets
    gender: NiceGender
    attribute: Attribute
    traits: list[NiceTrait]
    starAbsorb: int
    starGen: int
    instantDeathChance: int
    cards: list[NiceCardType]
    hitsDistribution: dict[NiceCardType, list[int]]
    atkBase: int
    atkMax: int
    hpBase: int
    hpMax: int
    relateQuestIds: list[int]
    growthCurve: int
    atkGrowth: list[int]
    hpGrowth: list[int]
    bondGrowth: list[int]
    bondEquip: int
    ascensionAdd: AscensionAdd
    svtChange: list[NiceServantChange]
    ascensionMaterials: dict[int, NiceLvlUpMaterial]
    skillMaterials: dict[int, NiceLvlUpMaterial]
    costumeMaterials: dict[int, NiceLvlUpMaterial]
    script: NiceServantScript
    skills: list[NiceSkill]
    classPassive: list[NiceSkill]
    noblePhantasms: list[NiceTd]
    profile: Optional[NiceLore] = None


class NiceEquip(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    type: NiceSvtType
    flag: NiceSvtFlag
    rarity: int
    cost: int
    lvMax: int
    extraAssets: ExtraAssets
    atkBase: int
    atkMax: int
    hpBase: int
    hpMax: int
    growthCurve: int
    atkGrowth: list[int]
    hpGrowth: list[int]
    skills: list[NiceSkill]
    profile: Optional[NiceLore] = None


class NiceReversedSkillTd(BaseModelORJson):
    servant: list[NiceServant] = []
    MC: list[NiceMysticCode] = []
    CC: list[NiceCommandCode] = []


class NiceReversedSkillTdType(BaseModelORJson):
    nice: Optional[NiceReversedSkillTd] = None
    basic: Optional[BasicReversedSkillTd] = None


class NiceSkillReverse(NiceSkill):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceTdReverse(NiceTd):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceReversedFunction(BaseModelORJson):
    skill: list[NiceSkillReverse] = []
    NP: list[NiceTdReverse] = []


class NiceReversedFunctionType(BaseModelORJson):
    nice: Optional[NiceReversedFunction] = None
    basic: Optional[BasicReversedFunction] = None


class NiceBaseFunctionReverse(NiceBaseFunction):
    reverse: Optional[NiceReversedFunctionType] = None


class NiceReversedBuff(BaseModelORJson):
    function: list[NiceBaseFunctionReverse] = []


class NiceReversedBuffType(BaseModelORJson):
    nice: Optional[NiceReversedBuff] = None
    basic: Optional[BasicReversedBuff] = None


class NiceBuffReverse(NiceBuff):
    reverse: Optional[NiceReversedBuffType] = None


class NiceQuestRelease(BaseModelORJson):
    type: NiceCondType
    targetId: int
    value: int
    closedMessage: str


class NiceQuest(BaseModelORJson):
    id: int
    name: str
    type: NiceQuestType
    consumeType: NiceConsumeType
    consume: int
    spotId: int
    releaseConditions: list[NiceQuestRelease]
    noticeAt: int
    openedAt: int
    closedAt: int


class NiceQuestPhase(NiceQuest):
    phase: int
    className: list[SvtClass]
    individuality: list[NiceTrait]
    qp: int
    exp: int
    bond: int
