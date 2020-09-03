from enum import Enum, IntEnum
from typing import Dict

from .gameenums import (
    BUFF_ACTION_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    CLASS_OVERWRITE_NAME,
    COND_TYPE_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    ITEM_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SVT_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    BuffAction,
    FuncType,
    NiceBuffAction,
    NiceBuffType,
    NiceCardType,
    NiceClassRelationOverwriteType,
    NiceCondType,
    NiceConsumeType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceItemType,
    NiceQuestType,
    NiceSvtType,
    NiceSvtVoiceType,
    NiceVoiceCondType,
    SvtType,
    VoiceCondType,
)


### Servant Type ###


SVT_TYPE_NAME_REVERSE: Dict[NiceSvtType, int] = {v: k for k, v in SVT_TYPE_NAME.items()}


### Servant Flag ###


class SvtFlag(IntEnum):
    ONLY_USE_FOR_NPC = 2
    SVT_EQUIP_FRIEND_SHIP = 4
    IGNORE_COMBINE_LIMIT_SPECIAL = 8
    SVT_EQUIP_EXP = 16
    SVT_EQUIP_CHOCOLATE = 32


class NiceSvtFlag(str, Enum):
    onlyUseForNpc = "onlyUseForNpc"
    svtEquipFriendShip = "svtEquipFriendShip"
    ignoreCombineLimitSpecial = "ignoreCombineLimitSpecial"
    svtEquipExp = "svtEquipExp"
    svtEquipChocolate = "svtEquipChocolate"
    # Not in the code
    normal = "normal"
    goetia = "goetia"


SVT_FLAG_NAME: Dict[int, NiceSvtFlag] = {
    0: NiceSvtFlag.normal,
    2: NiceSvtFlag.onlyUseForNpc,
    4: NiceSvtFlag.svtEquipFriendShip,
    8: NiceSvtFlag.ignoreCombineLimitSpecial,
    16: NiceSvtFlag.svtEquipExp,
    32: NiceSvtFlag.svtEquipChocolate,
    63: NiceSvtFlag.goetia,
}


SVT_FLAG_NAME_REVERSE: Dict[NiceSvtFlag, int] = {v: k for k, v in SVT_FLAG_NAME.items()}


### Skill Type ###


class NiceSkillType(str, Enum):
    active = "active"
    passive = "passive"


SKILL_TYPE_NAME: Dict[int, NiceSkillType] = {
    1: NiceSkillType.active,
    2: NiceSkillType.passive,
}


SKILL_TYPE_NAME_REVERSE: Dict[NiceSkillType, int] = {
    v: k for k, v in SKILL_TYPE_NAME.items()
}


### Function Type ###


FUNC_VALS_NOT_BUFF = {
    FuncType.SUB_STATE,
    FuncType.EVENT_DROP_UP,
    FuncType.GAIN_NP_BUFF_INDIVIDUAL_SUM,
}


FUNC_TYPE_NAME_REVERSE: Dict[NiceFuncType, int] = {
    v: k for k, v in FUNC_TYPE_NAME.items()
}


### Func Apply Target ###


class FuncApplyTarget(str, Enum):
    player = "player"
    enemy = "enemy"
    playerAndEnemy = "playerAndEnemy"


FUNC_APPLYTARGET_NAME: Dict[int, FuncApplyTarget] = {
    1: FuncApplyTarget.player,
    2: FuncApplyTarget.enemy,
    3: FuncApplyTarget.playerAndEnemy,
}


FUNC_APPLYTARGET_NAME_REVERSE: Dict[FuncApplyTarget, int] = {
    v: k for k, v in FUNC_APPLYTARGET_NAME.items()
}


### Func Target Type ###


FUNC_TARGETTYPE_NAME_REVERSE: Dict[NiceFuncTargetType, int] = {
    v: k for k, v in FUNC_TARGETTYPE_NAME.items()
}


### Building enemy func signature ###

TARGETTYPE_WITH_ENEMY_APPLYTARGET = (
    NiceFuncTargetType.self,
    NiceFuncTargetType.ptOne,
    NiceFuncTargetType.ptAnother,
    NiceFuncTargetType.ptAll,
    NiceFuncTargetType.ptFull,
    NiceFuncTargetType.ptOther,
    NiceFuncTargetType.ptOneOther,
    NiceFuncTargetType.ptRandom,
    NiceFuncTargetType.ptOtherFull,
    NiceFuncTargetType.ptselectOneSub,
    NiceFuncTargetType.ptselectSub,
    NiceFuncTargetType.ptOneAnotherRandom,
    NiceFuncTargetType.ptSelfAnotherRandom,
    NiceFuncTargetType.ptSelfAnotherFirst,
    NiceFuncTargetType.ptSelfBefore,
    NiceFuncTargetType.ptSelfAfter,
    NiceFuncTargetType.ptSelfAnotherLast,
    NiceFuncTargetType.commandTypeSelfTreasureDevice,
)


TARGETTYPE_WITH_PLAYER_APPLYTARGET = (
    NiceFuncTargetType.enemy,
    NiceFuncTargetType.enemyAnother,
    NiceFuncTargetType.enemyAll,
    NiceFuncTargetType.enemyFull,
    NiceFuncTargetType.enemyOther,
    NiceFuncTargetType.enemyRandom,
    NiceFuncTargetType.enemyOtherFull,
    NiceFuncTargetType.enemyOneAnotherRandom,
)


ENEMY_FUNC_TARGETING_PLAYER_TEAM = {
    (item, FuncApplyTarget.player) for item in TARGETTYPE_WITH_PLAYER_APPLYTARGET
}
ENEMY_FUNC_TARGETING_ENEMY_TEAM = {
    (item, FuncApplyTarget.enemy) for item in TARGETTYPE_WITH_ENEMY_APPLYTARGET
}
ENEMY_FUNC_SIGNATURE = (
    ENEMY_FUNC_TARGETING_PLAYER_TEAM | ENEMY_FUNC_TARGETING_ENEMY_TEAM
)


### Buff Type ###


BUFF_TYPE_NAME_REVERSE: Dict[NiceBuffType, int] = {
    v: k for k, v in BUFF_TYPE_NAME.items()
}


### Buff Limit ###


class BuffLimit(IntEnum):
    NONE = 0
    UPPER = 1
    LOWER = 2
    NORMAL = 3


class NiceBuffLimit(str, Enum):
    none = "none"
    upper = "upper"  # type: ignore # str has upper and lower methods
    lower = "lower"  # type: ignore
    normal = "normal"


BUFF_LIMIT_NAME: Dict[int, NiceBuffLimit] = {
    0: NiceBuffLimit.none,
    1: NiceBuffLimit.upper,
    2: NiceBuffLimit.lower,
    3: NiceBuffLimit.normal,
}


### Item BG Type ###


class NiceItemBGType(str, Enum):
    zero = "zero"  # qp, friendpoint
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    questClearQPReward = "questClearQPReward"


ITEM_BG_TYPE_NAME: Dict[int, NiceItemBGType] = {
    0: NiceItemBGType.zero,
    1: NiceItemBGType.bronze,
    2: NiceItemBGType.silver,
    3: NiceItemBGType.gold,
    4: NiceItemBGType.questClearQPReward,
}


### Card Type ###


CARD_TYPE_NAME_REVERSE: Dict[NiceCardType, int] = {
    v: k for k, v in CARD_TYPE_NAME.items()
}


### Gender ###


class Gender(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


GENDER_NAME: Dict[int, Gender] = {1: Gender.male, 2: Gender.female, 3: Gender.unknown}

GENDER_NAME_REVERSE: Dict[Gender, int] = {v: k for k, v in GENDER_NAME.items()}


### Attribute ###


class Attribute(str, Enum):
    human = "human"
    sky = "sky"
    earth = "earth"
    star = "star"
    beast = "beast"


ATTRIBUTE_NAME: Dict[int, Attribute] = {
    1: Attribute.human,
    2: Attribute.sky,
    3: Attribute.earth,
    4: Attribute.star,
    5: Attribute.beast,
}


ATTRIBUTE_NAME_REVERSE: Dict[Attribute, int] = {v: k for k, v in ATTRIBUTE_NAME.items()}


### Servant Class ###


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
    demonGodPillar = "demonGodPillar"
    moonCancer = "moonCancer"
    foreigner = "foreigner"
    grandCaster = "grandCaster"
    beastII = "beastII"
    beastI = "beastI"
    beastIIIR = "beastIIIR"
    beastIIIL = "beastIIIL"
    beastUnknown = "beastUnknown"
    unknown = "unknown"
    # OTHER = "OTHER"
    ALL = "ALL"
    # EXTRA = "EXTRA"
    # ALLCLASS = "ALLCLASS"


CLASS_NAME: Dict[int, SvtClass] = {
    1: SvtClass.saber,
    2: SvtClass.archer,
    3: SvtClass.lancer,
    4: SvtClass.rider,
    5: SvtClass.caster,
    6: SvtClass.assassin,
    7: SvtClass.berserker,
    8: SvtClass.shielder,
    9: SvtClass.ruler,
    10: SvtClass.alterEgo,
    11: SvtClass.avenger,
    12: SvtClass.demonGodPillar,
    23: SvtClass.moonCancer,
    25: SvtClass.foreigner,
    17: SvtClass.grandCaster,
    20: SvtClass.beastII,
    22: SvtClass.beastI,
    24: SvtClass.beastIIIR,
    26: SvtClass.beastIIIL,
    27: SvtClass.beastUnknown,  # LB 5.2 beast
    97: SvtClass.unknown,
    # 1000: SvtClass.OTHER,
    1001: SvtClass.ALL,
    # 1002: SvtClass.EXTRA,
    # 1003: SvtClass.ALLCLASS,
}


CLASS_NAME_REVERSE: Dict[SvtClass, int] = {v: k for k, v in CLASS_NAME.items()}


PLAYABLE_CLASS_LIST = [
    SvtClass.saber,
    SvtClass.archer,
    SvtClass.lancer,
    SvtClass.rider,
    SvtClass.caster,
    SvtClass.assassin,
    SvtClass.berserker,
    SvtClass.shielder,
    SvtClass.ruler,
    SvtClass.alterEgo,
    SvtClass.avenger,
    SvtClass.moonCancer,
    SvtClass.foreigner,
]


### Status Rank Type ###


class StatusRank(IntEnum):
    A = 11
    A_PLUS = 12
    A_PLUS2 = 13
    A_MINUS = 14
    A_PLUS3 = 15
    B = 21
    B_PLUS = 22
    B_PLUS2 = 23
    B_MINUS = 24
    B_PLUS3 = 25
    C = 31
    C_PLUS = 32
    C_PLUS2 = 33
    C_MINUS = 34
    C_PLUS3 = 35
    D = 41
    D_PLUS = 42
    D_PLUS2 = 43
    D_MINUS = 44
    D_PLUS3 = 45
    E = 51
    E_PLUS = 52
    E_PLUS2 = 53
    E_MINUS = 54
    E_PLUS3 = 55
    EX = 61
    QUESTION = 98
    NONE = 99


class NiceStatusRank(str, Enum):
    a = "A"
    aPlus = "A+"
    aPlus2 = "A++"
    aMinus = "A-"
    aPlus3 = "A+++"
    b = "B"
    bPlus = "B+"
    bPlus2 = "B++"
    bMinus = "B-"
    bPlus3 = "B+++"
    c = "C"
    cPlus = "C+"
    cPlus2 = "C++"
    cMinus = "C-"
    cPlus3 = "C+++"
    d = "D"
    dPlus = "D+"
    dPlus2 = "D++"
    dMinus = "D-"
    dPlus3 = "D+++"
    e = "E"
    ePlus = "E+"
    ePlus2 = "E++"
    eMinus = "E-"
    ePlus3 = "E+++"
    ex = "EX"
    question = "?"
    none = "None"
    unknown = "Unknown"


STATUS_RANK_NAME: Dict[int, NiceStatusRank] = {
    11: NiceStatusRank.a,
    12: NiceStatusRank.aPlus,
    13: NiceStatusRank.aPlus2,
    14: NiceStatusRank.aMinus,
    15: NiceStatusRank.aPlus3,
    21: NiceStatusRank.b,
    22: NiceStatusRank.bPlus,
    23: NiceStatusRank.bPlus2,
    24: NiceStatusRank.bMinus,
    25: NiceStatusRank.bPlus3,
    31: NiceStatusRank.c,
    32: NiceStatusRank.cPlus,
    33: NiceStatusRank.cPlus2,
    34: NiceStatusRank.cMinus,
    35: NiceStatusRank.cPlus3,
    41: NiceStatusRank.d,
    42: NiceStatusRank.dPlus,
    43: NiceStatusRank.dPlus2,
    44: NiceStatusRank.dMinus,
    45: NiceStatusRank.dPlus3,
    51: NiceStatusRank.e,
    52: NiceStatusRank.ePlus,
    53: NiceStatusRank.ePlus2,
    54: NiceStatusRank.eMinus,
    55: NiceStatusRank.ePlus3,
    61: NiceStatusRank.ex,
    98: NiceStatusRank.question,
    99: NiceStatusRank.none,
}


### Trait ###


class Trait(str, Enum):
    unknown = "unknown"
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
    classBeastUnknown = "classBeastUnknown"
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
    hominidaeServant = "hominidaeServant"
    blessedByKur = "blessedByKur"
    beastServant = "beastServant"
    canBeInBattle = "canBeInBattle"
    notBasedOnServant = "notBasedOnServant"
    livingHuman = "livingHuman"
    cardArts = "cardArts"
    cardBuster = "cardBuster"
    cardQuick = "cardQuick"
    cardExtra = "cardExtra"
    buffPositiveEffect = "buffPositiveEffect"
    buffNegativeEffect = "buffNegativeEffect"
    buffIncreaseDamage = "buffIncreaseDamage"
    buffIncreaseDefence = "buffIncreaseDefence"
    buffDecreaseDamage = "buffDecreaseDamage"
    buffDecreaseDefence = "buffDecreaseDefence"
    buffMentalEffect = "buffMentalEffect"
    buffPoison = "buffPoison"
    buffCharm = "buffCharm"
    buffPetrify = "buffPetrify"
    buffStun = "buffStun"
    buffBurn = "buffBurn"
    buffSpecialResistUp = "buffSpecialResistUp"
    buffSpecialResistDown = "buffSpecialResistDown"
    buffEvadeAndInvincible = "buffEvadeAndInvincible"
    buffSureHit = "buffSureHit"
    buffNpSeal = "buffNpSeal"
    buffEvade = "buffEvade"
    buffInvincible = "buffInvincible"
    buffTargetFocus = "buffTargetFocus"
    buffGuts = "buffGuts"
    skillSeal = "skillSeal"
    buffCurse = "buffCurse"
    buffAtkUp = "buffAtkUp"
    buffPowerModStrUp = "buffPowerModStrUp"
    buffDamagePlus = "buffDamagePlus"
    buffNpDamageUp = "buffNpDamageUp"
    buffCritDamageUp = "buffCritDamageUp"
    buffCritRateUp = "buffCritRateUp"
    buffAtkDown = "buffAtkDown"
    buffPowerModStrDown = "buffPowerModStrDown"
    buffDamageMinus = "buffDamageMinus"
    buffNpDamageDown = "buffNpDamageDown"
    buffCritDamageDown = "buffCritDamageDown"
    buffCritRateDown = "buffCritRateDown"
    buffDeathResistDown = "buffDeathResistDown"
    buffDefenceUp = "buffDefenceUp"
    buffMaxHpUpPercent = "buffMaxHpUpPercent"
    buffMaxHpDownPercent = "buffMaxHpDownPercent"
    buffMaxHpUp = "buffMaxHpUp"
    buffMaxHpDown = "buffMaxHpDown"
    buffStunLike = "buffStunLike"
    buffIncreasePoisonEffectiveness = "buffIncreasePoisonEffectiveness"
    buffPigify = "buffPigify"
    buffCurseEffectUp = "buffCurseEffectUp"
    buffTerrorStunChanceAfterTurn = "buffTerrorStunChanceAfterTurn"
    buffConfusion = "buffConfusion"
    buffOffensiveMode = "buffOffensiveMode"
    buffDefensiveMode = "buffDefensiveMode"
    buffLockCardsDeck = "buffLockCardsDeck"
    buffDisableColorCard = "buffDisableColorCard"
    buffChangeField = "buffChangeField"
    buffIncreaseDefenceAgainstIndividuality = "buffIncreaseDefenceAgainstIndividuality"
    buffInvinciblePierce = "buffInvinciblePierce"
    buffHpRecoveryPerTurn = "buffHpRecoveryPerTurn"
    buffNegativeEffectImmunity = "buffNegativeEffectImmunity"
    buffNegativeEffectAtTurnEnd = "buffNegativeEffectAtTurnEnd"
    normalAttack0 = "normalAttack0"
    normalAttack1 = "normalAttack1"
    normalAttack2 = "normalAttack2"
    criticalHit = "criticalHit"
    playerCards = "playerCards"
    cardNP = "cardNP"
    kingproteaGrowth = "kingproteaGrowth"
    kingproteaProliferation = "kingproteaProliferation"
    kingproteaProliferationNPDefense = "kingproteaProliferationNPDefense"
    fieldSunlight = "fieldSunlight"
    fieldShore = "fieldShore"
    fieldForest = "fieldForest"
    fieldBurning = "fieldBurning"
    fieldCity = "fieldCity"
    shadowServant = "shadowServant"
    aoeNP = "aoeNP"
    giant = "giant"
    childServant = "childServant"
    buffSpecialInvincible = "buffSpecialInvincible"
    buffSkillRankUp = "buffSkillRankUp"
    buffSleep = "buffSleep"


TRAIT_NAME: Dict[int, Trait] = {
    1: Trait.genderMale,
    2: Trait.genderFemale,
    3: Trait.genderUnknown,
    100: Trait.classSaber,
    101: Trait.classLancer,
    102: Trait.classArcher,
    103: Trait.classrider,
    104: Trait.classCaster,
    105: Trait.classAssassin,
    106: Trait.classBerserker,
    107: Trait.classShielder,
    108: Trait.classRuler,
    109: Trait.classAlterEgo,
    110: Trait.classAvenger,
    111: Trait.classDemonGodPillar,
    112: Trait.classGrandCaster,
    113: Trait.classBeastI,
    114: Trait.classBeastII,
    115: Trait.classMoonCancer,
    116: Trait.classBeastIIIR,
    117: Trait.classForeigner,
    118: Trait.classBeastIIIL,
    119: Trait.classBeastUnknown,
    200: Trait.attributeSky,
    201: Trait.attributeEarth,
    202: Trait.attributeHuman,
    203: Trait.attributeStar,
    204: Trait.attributeBeast,
    300: Trait.alignmentLawful,
    301: Trait.alignmentChaotic,
    302: Trait.alignmentNeutral,
    303: Trait.alignmentGood,
    304: Trait.alignmentEvil,
    305: Trait.alignmentBalanced,
    306: Trait.alignmentMadness,
    308: Trait.alignmentSummer,
    1000: Trait.basedOnServant,  # can be NPC or enemy but use a servant's data
    1001: Trait.human,  # Sanson's 3rd skill
    1002: Trait.undead,  # Scathach's 3rd skill
    1003: Trait.artificialDemon,
    1004: Trait.demonBeast,
    1005: Trait.daemon,
    1100: Trait.soldier,
    1101: Trait.amazoness,
    1102: Trait.skeleton,
    1103: Trait.zombie,
    1104: Trait.ghost,
    1105: Trait.automata,
    1106: Trait.golem,
    1107: Trait.spellBook,
    1108: Trait.homunculus,
    1110: Trait.lamia,
    1111: Trait.centaur,
    1112: Trait.werebeast,
    1113: Trait.chimera,
    1117: Trait.wyvern,
    1118: Trait.dragonType,
    1119: Trait.gazer,
    1120: Trait.handOrDoor,
    1121: Trait.demonGodPillar,
    1122: Trait.shadowServant,
    1132: Trait.oni,
    1133: Trait.hand,
    1134: Trait.door,
    1172: Trait.threatToHumanity,
    2000: Trait.divine,
    2001: Trait.humanoid,
    2002: Trait.dragon,
    2003: Trait.dragonSlayer,
    2004: Trait.roman,
    2005: Trait.wildbeast,
    2006: Trait.atalante,
    2007: Trait.saberface,
    2008: Trait.weakToEnumaElish,
    2009: Trait.riding,
    2010: Trait.arthur,
    2011: Trait.skyOrEarth,  # Tesla's NP
    2012: Trait.brynhildsBeloved,
    2018: Trait.undeadOrDaemon,  # Amakusa bond Ce
    2019: Trait.demonic,
    2037: Trait.skyOrEarthExceptPseudoAndDemi,  # Raikou's 3rd skill
    2038: Trait.fieldSunlight,
    2039: Trait.fieldShore,
    2040: Trait.divineOrDaemonOrUndead,  # Ruler Martha's 3rd skill
    2073: Trait.fieldForest,
    2074: Trait.blessedByKur,  # Eresh's 3rd skill add this individuality
    2075: Trait.saberClassServant,  # MHXA NP
    2076: Trait.superGiant,
    2113: Trait.king,
    2114: Trait.greekMythologyMales,
    2121: Trait.fieldBurning,
    2355: Trait.illya,
    2356: Trait.genderUnknownServant,  # Teach's 3rd skill
    2386: Trait.kingproteaProliferation,
    2387: Trait.kingproteaGrowth,
    2392: Trait.fieldCity,
    2466: Trait.argonaut,
    2615: Trait.genderCaenisServant,  # Phantom's 2nd skill
    2631: Trait.hominidaeServant,  # used in TamaVitch's fight
    2632: Trait.beastServant,  # used in TamaVitch's fight
    2654: Trait.livingHuman,  # Voyager's NP
    2664: Trait.kingproteaProliferationNPDefense,
    2666: Trait.giant,
    2667: Trait.childServant,  # Summer Illya's 2nd skill
    # 2xxx: CQ or Story quests buff
    3000: Trait.normalAttack0,  # Normal attack, including NP
    3001: Trait.normalAttack1,  # Haven't figured out the difference between the 3
    3002: Trait.normalAttack2,  #
    3004: Trait.buffPositiveEffect,
    3005: Trait.buffNegativeEffect,  # mutually exclusive with 3004
    3006: Trait.buffIncreaseDamage,  # catch all damage: atk, np, powermod, ...
    3007: Trait.buffIncreaseDefence,  # catch all defence, including evade
    3008: Trait.buffDecreaseDamage,
    3009: Trait.buffDecreaseDefence,  # including death resit down and card color resist down
    3010: Trait.buffMentalEffect,  # charm, terror, confusion
    3011: Trait.buffPoison,
    3012: Trait.buffCharm,
    3013: Trait.buffPetrify,
    3014: Trait.buffStun,  # including Pigify
    3015: Trait.buffBurn,
    3016: Trait.buffSpecialResistUp,  # Unused stuffs
    3017: Trait.buffSpecialResistDown,  # Unused stuffs
    3018: Trait.buffEvadeAndInvincible,
    3019: Trait.buffSureHit,
    3020: Trait.buffNpSeal,
    3021: Trait.buffEvade,
    3022: Trait.buffInvincible,
    3023: Trait.buffTargetFocus,
    3024: Trait.buffGuts,
    3025: Trait.skillSeal,
    3026: Trait.buffCurse,
    3027: Trait.buffAtkUp,  # Likely not the best name for this
    3028: Trait.buffPowerModStrUp,
    3029: Trait.buffDamagePlus,
    3030: Trait.buffNpDamageUp,
    3031: Trait.buffCritDamageUp,
    3032: Trait.buffCritRateUp,
    3033: Trait.buffAtkDown,
    3034: Trait.buffPowerModStrDown,
    3035: Trait.buffDamageMinus,
    3036: Trait.buffNpDamageDown,
    3037: Trait.buffCritDamageDown,
    3038: Trait.buffCritRateDown,
    3039: Trait.buffDeathResistDown,
    3040: Trait.buffDefenceUp,
    3041: Trait.buffMaxHpUpPercent,
    3042: Trait.buffMaxHpDownPercent,
    3043: Trait.buffMaxHpUp,
    3044: Trait.buffMaxHpDown,
    3045: Trait.buffStunLike,  # Including Petrify, Bound, Pigify, Stun
    3046: Trait.buffIncreasePoisonEffectiveness,
    3047: Trait.buffPigify,
    3048: Trait.buffCurseEffectUp,
    3049: Trait.buffTerrorStunChanceAfterTurn,
    3052: Trait.buffConfusion,
    3053: Trait.buffOffensiveMode,  # Unused
    3054: Trait.buffDefensiveMode,  # Unused
    3055: Trait.buffLockCardsDeck,  # Summer BB
    3056: Trait.buffDisableColorCard,
    3057: Trait.buffChangeField,
    3058: Trait.buffIncreaseDefenceAgainstIndividuality,  # Unsure
    3059: Trait.buffInvinciblePierce,
    3060: Trait.buffHpRecoveryPerTurn,
    3061: Trait.buffNegativeEffectImmunity,
    3063: Trait.buffNegativeEffectAtTurnEnd,
    3064: Trait.buffSpecialInvincible,
    3065: Trait.buffSkillRankUp,
    3066: Trait.buffSleep,
    # 6016: No detail
    # 6021: No detail
    # 6022: No detail
    # 10xxx: CCC Kiara buff
    4001: Trait.cardArts,
    4002: Trait.cardBuster,
    4003: Trait.cardQuick,
    4004: Trait.cardExtra,
    4007: Trait.cardNP,
    4008: Trait.playerCards,  # Normal Buster, Arts, Quick, Extra Attack
    4100: Trait.criticalHit,
    4101: Trait.aoeNP,
    5000: Trait.canBeInBattle,  # can be NPC, enemy or playable servant i.e. not CE
    5010: Trait.notBasedOnServant,
}


TRAIT_NAME_REVERSE: Dict[Trait, int] = {v: k for k, v in TRAIT_NAME.items()}


ALL_ENUMS = {
    "NiceSvtType": SVT_TYPE_NAME,
    "NiceSvtFlag": SVT_FLAG_NAME,
    "NiceSkillType": SKILL_TYPE_NAME,
    "NiceFuncType": FUNC_TYPE_NAME,
    "FuncApplyTarget": FUNC_APPLYTARGET_NAME,
    "NiceFuncTargetType": FUNC_TARGETTYPE_NAME,
    "NiceBuffType": BUFF_TYPE_NAME,
    "NiceBuffAction": BUFF_ACTION_NAME,
    "NiceBuffLimit": BUFF_LIMIT_NAME,
    "NiceClassRelationOverwriteType": CLASS_OVERWRITE_NAME,
    "NiceItemType": ITEM_TYPE_NAME,
    "NiceItemBGType": ITEM_BG_TYPE_NAME,
    "NiceCardType": CARD_TYPE_NAME,
    "Gender": GENDER_NAME,
    "Attribute": ATTRIBUTE_NAME,
    "SvtClass": CLASS_NAME,
    "NiceStatusRank": STATUS_RANK_NAME,
    "NiceCondType": COND_TYPE_NAME,
    "NiceVoiceCondType": VOICE_COND_NAME,
    "NiceSvtVoiceType": VOICE_TYPE_NAME,
    "NiceQuestType": QUEST_TYPE_NAME,
    "NiceConsumeType": QUEST_CONSUME_TYPE_NAME,
    "Trait": TRAIT_NAME,
}


__all__ = [
    "NiceSvtFlag",
    "SVT_FLAG_NAME",
    "SVT_FLAG_NAME_REVERSE",
    "SKILL_TYPE_NAME",
    "SKILL_TYPE_NAME_REVERSE",
    "FUNC_VALS_NOT_BUFF",
    "FUNC_TYPE_NAME_REVERSE",
    "FUNC_APPLYTARGET_NAME",
    "FUNC_APPLYTARGET_NAME_REVERSE",
    "FUNC_TARGETTYPE_NAME_REVERSE",
    "BUFF_TYPE_NAME_REVERSE",
    "NiceBuffLimit",
    "BUFF_LIMIT_NAME",
    "NiceItemBGType",
    "ITEM_BG_TYPE_NAME",
    "CARD_TYPE_NAME_REVERSE",
    "Gender",
    "GENDER_NAME",
    "GENDER_NAME_REVERSE",
    "Attribute",
    "ATTRIBUTE_NAME",
    "ATTRIBUTE_NAME_REVERSE",
    "SvtClass",
    "CLASS_NAME",
    "CLASS_NAME_REVERSE",
    "PLAYABLE_CLASS_LIST",
    "NiceStatusRank",
    "STATUS_RANK_NAME",
    "Trait",
    "TRAIT_NAME",
    "TRAIT_NAME_REVERSE",
    "SvtType",
    "NiceSvtType",
    "SVT_TYPE_NAME",
    "FuncType",
    "NiceFuncType",
    "FUNC_TYPE_NAME",
    "NiceFuncTargetType",
    "FUNC_TARGETTYPE_NAME",
    "NiceBuffType",
    "BUFF_TYPE_NAME",
    "BuffAction",
    "NiceBuffAction",
    "BUFF_ACTION_NAME",
    "NiceClassRelationOverwriteType",
    "CLASS_OVERWRITE_NAME",
    "NiceItemType",
    "ITEM_TYPE_NAME",
    "NiceCardType",
    "CARD_TYPE_NAME",
    "NiceCondType",
    "COND_TYPE_NAME",
    "VoiceCondType",
    "NiceVoiceCondType",
    "VOICE_COND_NAME",
    "NiceSvtVoiceType",
    "VOICE_TYPE_NAME",
    "NiceQuestType",
    "QUEST_TYPE_NAME",
    "NiceConsumeType",
    "QUEST_CONSUME_TYPE_NAME",
]
