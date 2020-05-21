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


class Func(str, Enum):
    none = "none"
    addState = "addState"
    subState = "subState"
    damage = "damage"
    damageNp = "damageNp"
    gainStar = "gainStar"
    gainHp = "gainHp"
    gainNp = "gainNp"
    lossNp = "lossNp"
    shortenSkill = "shortenSkill"
    extendSkill = "extendSkill"
    releaseState = "releaseState"
    lossHp = "lossHp"
    instantDeath = "instantDeath"
    damageNpPierce = "damageNpPierce"
    damageNpIndividual = "damageNpIndividual"
    addStateShort = "addStateShort"
    gainHpPer = "gainHpPer"
    damageNpStateIndividual = "damageNpStateIndividual"
    hastenNpturn = "hastenNpturn"
    delayNpturn = "delayNpturn"
    damageNpHpratioHigh = "damageNpHpratioHigh"
    damageNpHpratioLow = "damageNpHpratioLow"
    cardReset = "cardReset"
    replaceMember = "replaceMember"
    lossHpSafe = "lossHpSafe"
    damageNpCounter = "damageNpCounter"
    damageNpStateIndividualFix = "damageNpStateIndividualFix"
    damageNpSafe = "damageNpSafe"
    callServant = "callServant"
    ptShuffle = "ptShuffle"
    lossStar = "lossStar"
    changeServant = "changeServant"
    changeBg = "changeBg"
    damageValue = "damageValue"
    withdraw = "withdraw"
    fixCommandcard = "fixCommandcard"
    shortenBuffturn = "shortenBuffturn"
    extendBuffturn = "extendBuffturn"
    shortenBuffcount = "shortenBuffcount"
    extendBuffcount = "extendBuffcount"
    changeBgm = "changeBgm"
    displayBuffstring = "displayBuffstring"
    expUp = "expUp"
    qpUp = "qpUp"
    dropUp = "dropUp"
    friendPointUp = "friendPointUp"
    eventDropUp = "eventDropUp"
    eventDropRateUp = "eventDropRateUp"
    eventPointUp = "eventPointUp"
    eventPointRateUp = "eventPointRateUp"
    transformServant = "transformServant"
    qpDropUp = "qpDropUp"
    servantFriendshipUp = "servantFriendshipUp"
    userEquipExpUp = "userEquipExpUp"
    classDropUp = "classDropUp"
    enemyEncountCopyRateUp = "enemyEncountCopyRateUp"
    enemyEncountRateUp = "enemyEncountRateUp"
    enemyProbDown = "enemyProbDown"


class Buff(str, Enum):
    none = "none"
    upCommandatk = "upCommandatk"
    upStarweight = "upStarweight"
    upCriticalpoint = "upCriticalpoint"
    downCriticalpoint = "downCriticalpoint"
    regainNp = "regainNp"
    regainStar = "regainStar"
    regainHp = "regainHp"
    reduceHp = "reduceHp"
    upAtk = "upAtk"
    downAtk = "downAtk"
    upDamage = "upDamage"
    downDamage = "downDamage"
    addDamage = "addDamage"
    subDamage = "subDamage"
    upNpdamage = "upNpdamage"
    downNpdamage = "downNpdamage"
    upDropnp = "upDropnp"
    upCriticaldamage = "upCriticaldamage"
    downCriticaldamage = "downCriticaldamage"
    upSelfdamage = "upSelfdamage"
    downSelfdamage = "downSelfdamage"
    addSelfdamage = "addSelfdamage"
    subSelfdamage = "subSelfdamage"
    avoidance = "avoidance"
    breakAvoidance = "breakAvoidance"
    invincible = "invincible"
    upGrantstate = "upGrantstate"
    downGrantstate = "downGrantstate"
    upTolerance = "upTolerance"
    downTolerance = "downTolerance"
    avoidState = "avoidState"
    donotAct = "donotAct"
    donotSkill = "donotSkill"
    donotNoble = "donotNoble"
    donotRecovery = "donotRecovery"
    disableGender = "disableGender"
    guts = "guts"
    upHate = "upHate"
    addIndividuality = "addIndividuality"
    subIndividuality = "subIndividuality"
    upDefence = "upDefence"
    downDefence = "downDefence"
    upCommandstar = "upCommandstar"
    upCommandnp = "upCommandnp"
    upCommandall = "upCommandall"
    downCommandall = "downCommandall"
    downStarweight = "downStarweight"
    reduceNp = "reduceNp"
    downDropnp = "downDropnp"
    upGainHp = "upGainHp"
    downGainHp = "downGainHp"
    downCommandatk = "downCommandatk"
    downCommanstar = "downCommanstar"
    downCommandnp = "downCommandnp"
    upCriticalrate = "upCriticalrate"
    downCriticalrate = "downCriticalrate"
    pierceInvincible = "pierceInvincible"
    avoidInstantdeath = "avoidInstantdeath"
    upResistInstantdeath = "upResistInstantdeath"
    upNonresistInstantdeath = "upNonresistInstantdeath"
    delayFunction = "delayFunction"
    regainNpUsedNoble = "regainNpUsedNoble"
    deadFunction = "deadFunction"
    upMaxhp = "upMaxhp"
    downMaxhp = "downMaxhp"
    addMaxhp = "addMaxhp"
    subMaxhp = "subMaxhp"
    battlestartFunction = "battlestartFunction"
    wavestartFunction = "wavestartFunction"
    selfturnendFunction = "selfturnendFunction"
    upGivegainHp = "upGivegainHp"
    downGivegainHp = "downGivegainHp"
    commandattackFunction = "commandattackFunction"
    deadattackFunction = "deadattackFunction"
    upSpecialdefence = "upSpecialdefence"
    downSpecialdefence = "downSpecialdefence"
    upDamagedropnp = "upDamagedropnp"
    downDamagedropnp = "downDamagedropnp"
    entryFunction = "entryFunction"
    upChagetd = "upChagetd"
    reflectionFunction = "reflectionFunction"
    upGrantSubstate = "upGrantSubstate"
    downGrantSubstate = "downGrantSubstate"
    upToleranceSubstate = "upToleranceSubstate"
    downToleranceSubstate = "downToleranceSubstate"
    upGrantInstantdeath = "upGrantInstantdeath"
    downGrantInstantdeath = "downGrantInstantdeath"
    gutsRatio = "gutsRatio"
    damageFunction = "damageFunction"
    upDefencecommandall = "upDefencecommandall"
    downDefencecommandall = "downDefencecommandall"
    overwriteBattleclass = "overwriteBattleclass"
    overwriteClassrelatioAtk = "overwriteClassrelatioAtk"
    overwriteClassrelatioDef = "overwriteClassrelatioDef"
    upDamageIndividuality = "upDamageIndividuality"
    downDamageIndividuality = "downDamageIndividuality"
    upDamageIndividualityActiveonly = "upDamageIndividualityActiveonly"
    downDamageIndividualityActiveonly = "downDamageIndividualityActiveonly"
    upNpturnval = "upNpturnval"
    downNpturnval = "downNpturnval"
    multiattack = "multiattack"
    upGiveNp = "upGiveNp"
    downGiveNp = "downGiveNp"
    upResistanceDelayNpturn = "upResistanceDelayNpturn"
    downResistanceDelayNpturn = "downResistanceDelayNpturn"
    pierceDefence = "pierceDefence"
    upGutsHp = "upGutsHp"
    downGutsHp = "downGutsHp"
    upFuncgainNp = "upFuncgainNp"
    downFuncgainNp = "downFuncgainNp"
    upFuncHpReduce = "upFuncHpReduce"
    downFuncHpReduce = "downFuncHpReduce"
    upDefencecommanDamage = "upDefencecommanDamage"
    downDefencecommanDamage = "downDefencecommanDamage"
    npattackPrevBuff = "npattackPrevBuff"
    fixCommandcard = "fixCommandcard"
    donotGainnp = "donotGainnp"
    fieldIndividuality = "fieldIndividuality"
    donotActCommandtype = "donotActCommandtype"
    upDamageEventPoint = "upDamageEventPoint"


CARD_TYPE_NAME: Dict[int, CardType] = {
    1: CardType.arts,
    2: CardType.buster,
    3: CardType.quick,
    4: CardType.extra,
}


GENDER_NAME: Dict[int, Gender] = {1: Gender.male, 2: Gender.female, 3: Gender.unknown}


ATTRIBUTE_NAME: Dict[int, Attribute] = {
    1: Attribute.human,
    2: Attribute.sky,
    3: Attribute.earth,
    4: Attribute.star,
    5: Attribute.beast,
}


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
    23: SvtClass.moonCancer,
    25: SvtClass.foreigner,
}


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
    119: Trait.classBeastMaybe,
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
    2040: Trait.divineOrDaemonOrUndead,  # Ruler Martha's 3rd skill
    2075: Trait.saberClassServant,  # MHXA NP
    2076: Trait.superGiant,
    2113: Trait.king,
    2114: Trait.greekMythologyMales,
    2355: Trait.illya,
    2356: Trait.genderUnknownServant,  # Teach's 3rd skill
    2466: Trait.argonaut,
    2615: Trait.genderCaenisServant,  # Phantom's 2nd skill
    2631: Trait.humanoidServant,  # used in TamaVitch's fight
    2632: Trait.beastServant,  # used in TamaVitch's fight
    5000: Trait.canBeInBattle,  # can be NPC, enemy or playable servant i.e. not CE
    5010: Trait.notBasedOnServant,
}


FUNC_TYPE_NAME: Dict[int, Func] = {
    0: Func.none,
    1: Func.addState,
    2: Func.subState,
    3: Func.damage,
    4: Func.damageNp,
    5: Func.gainStar,
    6: Func.gainHp,
    7: Func.gainNp,
    8: Func.lossNp,
    9: Func.shortenSkill,
    10: Func.extendSkill,
    11: Func.releaseState,
    12: Func.lossHp,
    13: Func.instantDeath,
    14: Func.damageNpPierce,
    15: Func.damageNpIndividual,
    16: Func.addStateShort,
    17: Func.gainHpPer,
    18: Func.damageNpStateIndividual,
    19: Func.hastenNpturn,
    20: Func.delayNpturn,
    21: Func.damageNpHpratioHigh,
    22: Func.damageNpHpratioLow,
    23: Func.cardReset,
    24: Func.replaceMember,
    25: Func.lossHpSafe,
    26: Func.damageNpCounter,
    27: Func.damageNpStateIndividualFix,
    28: Func.damageNpSafe,
    29: Func.callServant,
    30: Func.ptShuffle,
    31: Func.lossStar,
    32: Func.changeServant,
    33: Func.changeBg,
    34: Func.damageValue,
    35: Func.withdraw,
    36: Func.fixCommandcard,
    37: Func.shortenBuffturn,
    38: Func.extendBuffturn,
    39: Func.shortenBuffcount,
    40: Func.extendBuffcount,
    41: Func.changeBgm,
    42: Func.displayBuffstring,
    101: Func.expUp,
    102: Func.qpUp,
    103: Func.dropUp,
    104: Func.friendPointUp,
    105: Func.eventDropUp,
    106: Func.eventDropRateUp,
    107: Func.eventPointUp,
    108: Func.eventPointRateUp,
    109: Func.transformServant,
    110: Func.qpDropUp,
    111: Func.servantFriendshipUp,
    112: Func.userEquipExpUp,
    113: Func.classDropUp,
    114: Func.enemyEncountCopyRateUp,
    115: Func.enemyEncountRateUp,
    116: Func.enemyProbDown,
}


BUFF_TYPE_NAME: Dict[int, Buff] = {
    0: Buff.none,
    1: Buff.upCommandatk,
    2: Buff.upStarweight,
    3: Buff.upCriticalpoint,
    4: Buff.downCriticalpoint,
    5: Buff.regainNp,
    6: Buff.regainStar,
    7: Buff.regainHp,
    8: Buff.reduceHp,
    9: Buff.upAtk,
    10: Buff.downAtk,
    11: Buff.upDamage,
    12: Buff.downDamage,
    13: Buff.addDamage,
    14: Buff.subDamage,
    15: Buff.upNpdamage,
    16: Buff.downNpdamage,
    17: Buff.upDropnp,
    18: Buff.upCriticaldamage,
    19: Buff.downCriticaldamage,
    20: Buff.upSelfdamage,
    21: Buff.downSelfdamage,
    22: Buff.addSelfdamage,
    23: Buff.subSelfdamage,
    24: Buff.avoidance,
    25: Buff.breakAvoidance,
    26: Buff.invincible,
    27: Buff.upGrantstate,
    28: Buff.downGrantstate,
    29: Buff.upTolerance,
    30: Buff.downTolerance,
    31: Buff.avoidState,
    32: Buff.donotAct,
    33: Buff.donotSkill,
    34: Buff.donotNoble,
    35: Buff.donotRecovery,
    36: Buff.disableGender,
    37: Buff.guts,
    38: Buff.upHate,
    40: Buff.addIndividuality,
    41: Buff.subIndividuality,
    42: Buff.upDefence,
    43: Buff.downDefence,
    50: Buff.upCommandstar,
    51: Buff.upCommandnp,
    52: Buff.upCommandall,
    60: Buff.downCommandall,
    61: Buff.downStarweight,
    62: Buff.reduceNp,
    63: Buff.downDropnp,
    64: Buff.upGainHp,
    65: Buff.downGainHp,
    66: Buff.downCommandatk,
    67: Buff.downCommanstar,
    68: Buff.downCommandnp,
    70: Buff.upCriticalrate,
    71: Buff.downCriticalrate,
    72: Buff.pierceInvincible,
    73: Buff.avoidInstantdeath,
    74: Buff.upResistInstantdeath,
    75: Buff.upNonresistInstantdeath,
    76: Buff.delayFunction,
    77: Buff.regainNpUsedNoble,
    78: Buff.deadFunction,
    79: Buff.upMaxhp,
    80: Buff.downMaxhp,
    81: Buff.addMaxhp,
    82: Buff.subMaxhp,
    83: Buff.battlestartFunction,
    84: Buff.wavestartFunction,
    85: Buff.selfturnendFunction,
    87: Buff.upGivegainHp,
    88: Buff.downGivegainHp,
    89: Buff.commandattackFunction,
    90: Buff.deadattackFunction,
    91: Buff.upSpecialdefence,
    92: Buff.downSpecialdefence,
    93: Buff.upDamagedropnp,
    94: Buff.downDamagedropnp,
    95: Buff.entryFunction,
    96: Buff.upChagetd,
    97: Buff.reflectionFunction,
    98: Buff.upGrantSubstate,
    99: Buff.downGrantSubstate,
    100: Buff.upToleranceSubstate,
    101: Buff.downToleranceSubstate,
    102: Buff.upGrantInstantdeath,
    103: Buff.downGrantInstantdeath,
    104: Buff.gutsRatio,
    86: Buff.damageFunction,
    105: Buff.upDefencecommandall,
    106: Buff.downDefencecommandall,
    107: Buff.overwriteBattleclass,
    108: Buff.overwriteClassrelatioAtk,
    109: Buff.overwriteClassrelatioDef,
    110: Buff.upDamageIndividuality,
    111: Buff.downDamageIndividuality,
    112: Buff.upDamageIndividualityActiveonly,
    113: Buff.downDamageIndividualityActiveonly,
    114: Buff.upNpturnval,
    115: Buff.downNpturnval,
    116: Buff.multiattack,
    117: Buff.upGiveNp,
    118: Buff.downGiveNp,
    119: Buff.upResistanceDelayNpturn,
    120: Buff.downResistanceDelayNpturn,
    121: Buff.pierceDefence,
    122: Buff.upGutsHp,
    123: Buff.downGutsHp,
    124: Buff.upFuncgainNp,
    125: Buff.downFuncgainNp,
    126: Buff.upFuncHpReduce,
    127: Buff.downFuncHpReduce,
    128: Buff.upDefencecommanDamage,
    129: Buff.downDefencecommanDamage,
    130: Buff.npattackPrevBuff,
    131: Buff.fixCommandcard,
    132: Buff.donotGainnp,
    133: Buff.fieldIndividuality,
    134: Buff.donotActCommandtype,
    135: Buff.upDamageEventPoint,
}


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
    iconId: int
    type: Union[Buff, int]
    vals: List[Union[Trait, int]]
    tvals: List[Union[Trait, int]]
    ckOpIndv: List[Union[Trait, int]]
    ckSelfIndv: List[Union[Trait, int]]


class NiceFunction(BaseModel):
    funcId: int
    funcType: Union[Func, int]
    funcPopupText: str
    funcPopupIconId: int
    functvals: List[Union[Trait, int]]
    buffs: List[NiceBuff]
    svals: Vals
    # svals2: Optional[Vals] = None
    # svals3: Optional[Vals] = None
    # svals4: Optional[Vals] = None
    # svals5: Optional[Vals] = None


class NiceFunctionGroup(BaseModel):
    level: List[NiceFunction] = []
    overcharge: List[NiceFunction] = []
    constant: List[NiceFunction] = []
    other: List[NiceFunction] = []


class NiceSkill(BaseModel):
    id: int
    num: int = -1
    name: str
    detail: str
    strengthStatus: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    iconId: int
    coolDown: List[int]
    functions: NiceFunctionGroup


class NiceTd(BaseModel):
    id: int
    num: int
    card: CardType
    name: str
    detail: str
    npNpGain: float
    npDistribution: List[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    functions: NiceFunctionGroup


class NiceServant(BaseModel):
    id: int
    collectionNo: int
    name: str
    className: SvtClass
    cost: int
    gender: Gender
    attribute: Attribute
    traits: List[Union[Trait, int]]
    busterNpGain: float
    artsNpGain: float
    quickNpGain: float
    extraNpGain: float
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
    NPs: List[NiceTd]
