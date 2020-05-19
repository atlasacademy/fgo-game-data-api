from enum import Enum
from typing import List, Dict

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


class NiceServantEntity(BaseModel):
    collectionNo: int
    name: str
    className: SvtClass
    cost: int
    gender: Gender
    attribute: Attribute
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
    # npDistribution: List[int]
