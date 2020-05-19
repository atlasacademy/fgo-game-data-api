from enum import Enum
from typing import List, Dict, Union

from pydantic import BaseModel


class Gender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


class SvtClass(str, Enum):
    saber = "saber"
    archer = "archer"
    lancer = "lancer"
    rider = "rider"
    caster = "caster"
    assassin = "assassin"
    berserker = "berserker"
    shielder = "shielder"
    ruler = "ruler"
    alterEgo = "alterEgo"
    avenger = "avenger"
    moonCancer = "moonCancer"
    foreigner = "foreigner"


class Trait(str, Enum):
    genderMale = "genderMale"
    genderFemale = "genderFemale"
    genderUnknown = "genderUnknown"
    classSaber = "classSaber"
    classLancer = "classLancer"
    classArcher = "classArcher"
    classrider = "classrider"
    classCaster = "classCaster"
    classAssassin = "classAssassin"
    classBerserker = "classBerserker"
    classShielder = "classShielder"
    classRuler = "classRuler"
    classAlterEgo = "classAlterEgo"
    classAvenger = "classAvenger"
    classDemonGodPillar = "classDemonGodPillar"
    classGrandCaster = "classGrandCaster"
    classBeastI = "classBeastI"
    classBeastII = "classBeastII"
    classMoonCancer = "classMoonCancer"
    classBeastIIIR = "classBeastIIIR"
    classForeigner = "classForeigner"
    classBeastIIIL = "classBeastIIIL"
    classBeastMaybe = "classBeastMaybe"
    attributeSky = "attributeSky"
    attributeEarth = "attributeEarth"
    attributeHuman = "attributeHuman"
    attributeStar = "attributeStar"
    attributeBeast = "attributeBeast"
    alignmentLawful = "alignmentLawful"
    alignmentChaotic = "alignmentChaotic"
    alignmentNeutral = "alignmentNeutral"
    alignmentGood = "alignmentGood"
    alignmentEvil = "alignmentEvil"
    alignmentBalanced = "alignmentBalanced"
    alignmentMadness = "alignmentMadness"
    alignmentSummer = "alignmentSummer"
    basedOnServant = "basedOnServant"
    human = "human"
    undead = "undead"
    artificialDemon = "artificialDemon"
    demonBeast = "demonBeast"
    daemon = "daemon"
    soldier = "soldier"
    amazoness = "amazoness"
    skeleton = "skeleton"
    zombie = "zombie"
    ghost = "ghost"
    automata = "automata"
    golem = "golem"
    spellBook = "spellBook"
    homunculus = "homunculus"
    lamia = "lamia"
    centaur = "centaur"
    werebeast = "werebeast"
    chimera = "chimera"
    wyvern = "wyvern"
    dragonType = "dragonType"
    gazer = "gazer"
    handOrDoor = "handOrDoor"
    demonGodPillar = "demonGodPillar"
    oni = "oni"
    hand = "hand"
    door = "door"
    threatToHumanity = "threatToHumanity"
    divine = "divine"
    humanoid = "humanoid"
    dragon = "dragon"
    dragonSlayer = "dragonSlayer"
    roman = "roman"
    wildbeast = "wildbeast"
    atalante = "atalante"
    saberface = "saberface"
    weakToEnumaElish = "weakToEnumaElish"
    riding = "riding"
    arthur = "arthur"
    skyOrEarth = "skyOrEarth"
    brynhildsBeloved = "brynhildsBeloved"
    undeadOrDaemon = "undeadOrDaemon"
    demonic = "demonic"
    skyOrEarthExceptPseudoAndDemi = "skyOrEarthExceptPseudoAndDemi"
    divineOrDaemonOrUndead = "divineOrDaemonOrUndead"
    saberClassServant = "saberClassServant"
    superGiant = "superGiant"
    king = "king"
    greekMythologyMales = "greekMythologyMales"
    illya = "illya"
    genderUnknownServant = "genderUnknownServant"
    argonaut = "argonaut"
    genderCaenisServant = "genderCaenisServant"
    humanoidServant = "humanoidServant"
    beastServant = "beastServant"
    canBeInBattle = "canBeInBattle"
    notBasedOnServant = "notBasedOnServant"
    unknown = "unknown"


class CardType(str, Enum):
    arts = "arts"
    buster = "buster"
    quick = "quick"
    extra = "extra"


class Attribute(str, Enum):
    human = "human"
    sky = "sky"
    earth = "earth"
    star = "star"
    beast = "beast"


class NiceItemAmount(BaseModel):
    id: int
    name: str
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


class NiceBuff(BaseModel):
    id: int
    name: str
    detail: str
    type: int
    vals: List[Union[Trait, int]]
    tvals: List[Union[Trait, int]]
    ckSelfIndv: List[Union[Trait, int]]


class NiceFunction(BaseModel):
    funcId: int
    funcPopupText: str
    funcPopupIconId: int
    functvals: List[Union[Trait, int]]
    buffs: List[NiceBuff]
    svals: Vals


class NiceSkill(BaseModel):
    id: int
    name: str
    iconId: int
    detail: str
    strengthStatus: int = -1
    num: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    coolDown: List[int]
    functions: List[NiceFunction]


class NiceServant(BaseModel):
    collectionNo: int
    name: str
    className: SvtClass
    cost: int
    gender: Gender
    attribute: Attribute
    traits: List[Trait]
    busterNpGain: float
    artsNpGain: float
    quickNpGain: float
    extraNpGain: float
    npNpGain: float
    defenceNpGain: float
    starAbsorb: int
    starGen: float
    instantDeathChance: float
    atkMax: int
    atkBase: int
    hpMax: int
    hpBase: int
    growthCurve: int
    atkGrowth: List[int]
    hpGrowth: List[int]
    cards: List[CardType]
    busterDistribution: List[int]
    artsDistribution: List[int]
    quickDistribution: List[int]
    extraDistribution: List[int]
    ascenionMaterials: Dict[int, NiceAscensionMaterial]
    skillMaterials: Dict[int, NiceSkillMaterial]
    skills: List[NiceSkill]
    classPassive: List[NiceSkill]
    # npDistribution: List[int]
