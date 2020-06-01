from enum import Enum, IntEnum
from typing import Dict


### Servant Type ###


class SvtType(IntEnum):
    NORMAL = 1
    HEROINE = 2
    COMBINE_MATERIAL = 3
    ENEMY = 4
    ENEMY_COLLECTION = 5
    SERVANT_EQUIP = 6
    STATUS_UP = 7
    SVT_EQUIP_MATERIAL = 8
    ENEMY_COLLECTION_DETAIL = 9
    ALL = 10
    COMMAND_CODE = 11


### Function Type ###


class FuncType(IntEnum):
    NONE = 0
    ADD_STATE = 1
    SUB_STATE = 2
    DAMAGE = 3
    DAMAGE_NP = 4
    GAIN_STAR = 5
    GAIN_HP = 6
    GAIN_NP = 7
    LOSS_NP = 8
    SHORTEN_SKILL = 9
    EXTEND_SKILL = 10
    RELEASE_STATE = 11
    LOSS_HP = 12
    INSTANT_DEATH = 13
    DAMAGE_NP_PIERCE = 14
    DAMAGE_NP_INDIVIDUAL = 15
    ADD_STATE_SHORT = 16
    GAIN_HP_PER = 17
    DAMAGE_NP_STATE_INDIVIDUAL = 18
    HASTEN_NPTURN = 19
    DELAY_NPTURN = 20
    DAMAGE_NP_HPRATIO_HIGH = 21
    DAMAGE_NP_HPRATIO_LOW = 22
    CARD_RESET = 23
    REPLACE_MEMBER = 24
    LOSS_HP_SAFE = 25
    DAMAGE_NP_COUNTER = 26
    DAMAGE_NP_STATE_INDIVIDUAL_FIX = 27
    DAMAGE_NP_SAFE = 28
    CALL_SERVANT = 29
    PT_SHUFFLE = 30
    LOSS_STAR = 31
    CHANGE_SERVANT = 32
    CHANGE_BG = 33
    DAMAGE_VALUE = 34
    WITHDRAW = 35
    FIX_COMMANDCARD = 36
    SHORTEN_BUFFTURN = 37
    EXTEND_BUFFTURN = 38
    SHORTEN_BUFFCOUNT = 39
    EXTEND_BUFFCOUNT = 40
    CHANGE_BGM = 41
    DISPLAY_BUFFSTRING = 42
    EXP_UP = 101
    QP_UP = 102
    DROP_UP = 103
    FRIEND_POINT_UP = 104
    EVENT_DROP_UP = 105
    EVENT_DROP_RATE_UP = 106
    EVENT_POINT_UP = 107
    EVENT_POINT_RATE_UP = 108
    TRANSFORM_SERVANT = 109
    QP_DROP_UP = 110
    SERVANT_FRIENDSHIP_UP = 111
    USER_EQUIP_EXP_UP = 112
    CLASS_DROP_UP = 113
    ENEMY_ENCOUNT_COPY_RATE_UP = 114
    ENEMY_ENCOUNT_RATE_UP = 115
    ENEMY_PROB_DOWN = 116


class NiceFuncType(str, Enum):
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


FUNC_TYPE_NAME: Dict[int, NiceFuncType] = {
    0: NiceFuncType.none,
    1: NiceFuncType.addState,
    2: NiceFuncType.subState,
    3: NiceFuncType.damage,
    4: NiceFuncType.damageNp,
    5: NiceFuncType.gainStar,
    6: NiceFuncType.gainHp,
    7: NiceFuncType.gainNp,
    8: NiceFuncType.lossNp,
    9: NiceFuncType.shortenSkill,
    10: NiceFuncType.extendSkill,
    11: NiceFuncType.releaseState,
    12: NiceFuncType.lossHp,
    13: NiceFuncType.instantDeath,
    14: NiceFuncType.damageNpPierce,
    15: NiceFuncType.damageNpIndividual,
    16: NiceFuncType.addStateShort,
    17: NiceFuncType.gainHpPer,
    18: NiceFuncType.damageNpStateIndividual,
    19: NiceFuncType.hastenNpturn,
    20: NiceFuncType.delayNpturn,
    21: NiceFuncType.damageNpHpratioHigh,
    22: NiceFuncType.damageNpHpratioLow,
    23: NiceFuncType.cardReset,
    24: NiceFuncType.replaceMember,
    25: NiceFuncType.lossHpSafe,
    26: NiceFuncType.damageNpCounter,
    27: NiceFuncType.damageNpStateIndividualFix,
    28: NiceFuncType.damageNpSafe,
    29: NiceFuncType.callServant,
    30: NiceFuncType.ptShuffle,
    31: NiceFuncType.lossStar,
    32: NiceFuncType.changeServant,
    33: NiceFuncType.changeBg,
    34: NiceFuncType.damageValue,
    35: NiceFuncType.withdraw,
    36: NiceFuncType.fixCommandcard,
    37: NiceFuncType.shortenBuffturn,
    38: NiceFuncType.extendBuffturn,
    39: NiceFuncType.shortenBuffcount,
    40: NiceFuncType.extendBuffcount,
    41: NiceFuncType.changeBgm,
    42: NiceFuncType.displayBuffstring,
    101: NiceFuncType.expUp,
    102: NiceFuncType.qpUp,
    103: NiceFuncType.dropUp,
    104: NiceFuncType.friendPointUp,
    105: NiceFuncType.eventDropUp,
    106: NiceFuncType.eventDropRateUp,
    107: NiceFuncType.eventPointUp,
    108: NiceFuncType.eventPointRateUp,
    109: NiceFuncType.transformServant,
    110: NiceFuncType.qpDropUp,
    111: NiceFuncType.servantFriendshipUp,
    112: NiceFuncType.userEquipExpUp,
    113: NiceFuncType.classDropUp,
    114: NiceFuncType.enemyEncountCopyRateUp,
    115: NiceFuncType.enemyEncountRateUp,
    116: NiceFuncType.enemyProbDown,
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


### Func Target Type ###


class FuncTargetType(IntEnum):
    SELF = 0
    PT_ONE = 1
    PT_ANOTHER = 2
    PT_ALL = 3
    ENEMY = 4
    ENEMY_ANOTHER = 5
    ENEMY_ALL = 6
    PT_FULL = 7
    ENEMY_FULL = 8
    PT_OTHER = 9
    PT_ONE_OTHER = 10
    PT_RANDOM = 11
    ENEMY_OTHER = 12
    ENEMY_RANDOM = 13
    PT_OTHER_FULL = 14
    ENEMY_OTHER_FULL = 15
    PTSELECT_ONE_SUB = 16
    PTSELECT_SUB = 17
    PT_ONE_ANOTHER_RANDOM = 18


class NiceFuncTargetType(str, Enum):
    self = "self"
    ptOne = "ptOne"
    ptAnother = "ptAnother"
    ptAll = "ptAll"
    enemy = "enemy"
    enemyAnother = "enemyAnother"
    enemyAll = "enemyAll"
    ptFull = "ptFull"
    enemyFull = "enemyFull"
    ptOther = "ptOther"
    ptOneOther = "ptOneOther"
    ptRandom = "ptRandom"
    enemyOther = "enemyOther"
    enemyRandom = "enemyRandom"
    ptOtherFull = "ptOtherFull"
    enemyOtherFull = "enemyOtherFull"
    ptselectOneSub = "ptselectOneSub"
    ptselectSub = "ptselectSub"
    ptOneAnotherRandom = "ptOneAnotherRandom"


FUNC_TARGETTYPE_NAME: Dict[int, NiceFuncTargetType] = {
    0: NiceFuncTargetType.self,
    1: NiceFuncTargetType.ptOne,
    2: NiceFuncTargetType.ptAnother,
    3: NiceFuncTargetType.ptAll,
    4: NiceFuncTargetType.enemy,
    5: NiceFuncTargetType.enemyAnother,
    6: NiceFuncTargetType.enemyAll,
    7: NiceFuncTargetType.ptFull,
    8: NiceFuncTargetType.enemyFull,
    9: NiceFuncTargetType.ptOther,
    10: NiceFuncTargetType.ptOneOther,
    11: NiceFuncTargetType.ptRandom,
    12: NiceFuncTargetType.enemyOther,
    13: NiceFuncTargetType.enemyRandom,
    14: NiceFuncTargetType.ptOtherFull,
    15: NiceFuncTargetType.enemyOtherFull,
    16: NiceFuncTargetType.ptselectOneSub,
    17: NiceFuncTargetType.ptselectSub,
    18: NiceFuncTargetType.ptOneAnotherRandom,
}


### Building enemy func signature ###

TARGETTYPE_OWN_TEAM = [
    NiceFuncTargetType.self,
    NiceFuncTargetType.ptOne,
    NiceFuncTargetType.ptAnother,
    NiceFuncTargetType.ptAll,
    NiceFuncTargetType.ptFull,
    NiceFuncTargetType.ptOther,
    NiceFuncTargetType.ptRandom,
    NiceFuncTargetType.ptOtherFull,
    NiceFuncTargetType.ptselectOneSub,
    NiceFuncTargetType.ptselectSub,
    NiceFuncTargetType.ptOneAnotherRandom,
]


TARGETTYPE_OTHER_TEAM = [
    NiceFuncTargetType.enemy,
    NiceFuncTargetType.enemyAnother,
    NiceFuncTargetType.enemyAll,
    NiceFuncTargetType.enemyFull,
    NiceFuncTargetType.enemyRandom,
    NiceFuncTargetType.enemyOtherFull,
]


ENEMY_FUNC_TARGETING_PLAYER_TEAM = [
    (item, FuncApplyTarget.player) for item in TARGETTYPE_OTHER_TEAM
]
ENEMY_FUNC_TARGETING_ENEMY_TEAM = [
    (item, FuncApplyTarget.enemy) for item in TARGETTYPE_OWN_TEAM
]
ENEMY_FUNC_SIGNATURE = (
    ENEMY_FUNC_TARGETING_PLAYER_TEAM + ENEMY_FUNC_TARGETING_ENEMY_TEAM
)


### Buff Type ###


class BuffType(IntEnum):
    NONE = 0
    UP_COMMANDATK = 1
    UP_STARWEIGHT = 2
    UP_CRITICALPOINT = 3
    DOWN_CRITICALPOINT = 4
    REGAIN_NP = 5
    REGAIN_STAR = 6
    REGAIN_HP = 7
    REDUCE_HP = 8
    UP_ATK = 9
    DOWN_ATK = 10
    UP_DAMAGE = 11
    DOWN_DAMAGE = 12
    ADD_DAMAGE = 13
    SUB_DAMAGE = 14
    UP_NPDAMAGE = 15
    DOWN_NPDAMAGE = 16
    UP_DROPNP = 17
    UP_CRITICALDAMAGE = 18
    DOWN_CRITICALDAMAGE = 19
    UP_SELFDAMAGE = 20
    DOWN_SELFDAMAGE = 21
    ADD_SELFDAMAGE = 22
    SUB_SELFDAMAGE = 23
    AVOIDANCE = 24
    BREAK_AVOIDANCE = 25
    INVINCIBLE = 26
    UP_GRANTSTATE = 27
    DOWN_GRANTSTATE = 28
    UP_TOLERANCE = 29
    DOWN_TOLERANCE = 30
    AVOID_STATE = 31
    DONOT_ACT = 32
    DONOT_SKILL = 33
    DONOT_NOBLE = 34
    DONOT_RECOVERY = 35
    DISABLE_GENDER = 36
    GUTS = 37
    UP_HATE = 38
    ADD_INDIVIDUALITY = 40
    SUB_INDIVIDUALITY = 41
    UP_DEFENCE = 42
    DOWN_DEFENCE = 43
    UP_COMMANDSTAR = 50
    UP_COMMANDNP = 51
    UP_COMMANDALL = 52
    DOWN_COMMANDALL = 60
    DOWN_STARWEIGHT = 61
    REDUCE_NP = 62
    DOWN_DROPNP = 63
    UP_GAIN_HP = 64
    DOWN_GAIN_HP = 65
    DOWN_COMMANDATK = 66
    DOWN_COMMANSTAR = 67
    DOWN_COMMANDNP = 68
    UP_CRITICALRATE = 70
    DOWN_CRITICALRATE = 71
    PIERCE_INVINCIBLE = 72
    AVOID_INSTANTDEATH = 73
    UP_RESIST_INSTANTDEATH = 74
    UP_NONRESIST_INSTANTDEATH = 75
    DELAY_FUNCTION = 76
    REGAIN_NP_USED_NOBLE = 77
    DEAD_FUNCTION = 78
    UP_MAXHP = 79
    DOWN_MAXHP = 80
    ADD_MAXHP = 81
    SUB_MAXHP = 82
    BATTLESTART_FUNCTION = 83
    WAVESTART_FUNCTION = 84
    SELFTURNEND_FUNCTION = 85
    UP_GIVEGAIN_HP = 87
    DOWN_GIVEGAIN_HP = 88
    COMMANDATTACK_FUNCTION = 89
    DEADATTACK_FUNCTION = 90
    UP_SPECIALDEFENCE = 91
    DOWN_SPECIALDEFENCE = 92
    UP_DAMAGEDROPNP = 93
    DOWN_DAMAGEDROPNP = 94
    ENTRY_FUNCTION = 95
    UP_CHAGETD = 96
    REFLECTION_FUNCTION = 97
    UP_GRANT_SUBSTATE = 98
    DOWN_GRANT_SUBSTATE = 99
    UP_TOLERANCE_SUBSTATE = 100
    DOWN_TOLERANCE_SUBSTATE = 101
    UP_GRANT_INSTANTDEATH = 102
    DOWN_GRANT_INSTANTDEATH = 103
    GUTS_RATIO = 104
    DAMAGE_FUNCTION = 86
    UP_DEFENCECOMMANDALL = 105
    DOWN_DEFENCECOMMANDALL = 106
    OVERWRITE_BATTLECLASS = 107
    OVERWRITE_CLASSRELATIO_ATK = 108
    OVERWRITE_CLASSRELATIO_DEF = 109
    UP_DAMAGE_INDIVIDUALITY = 110
    DOWN_DAMAGE_INDIVIDUALITY = 111
    UP_DAMAGE_INDIVIDUALITY_ACTIVEONLY = 112
    DOWN_DAMAGE_INDIVIDUALITY_ACTIVEONLY = 113
    UP_NPTURNVAL = 114
    DOWN_NPTURNVAL = 115
    MULTIATTACK = 116
    UP_GIVE_NP = 117
    DOWN_GIVE_NP = 118
    UP_RESISTANCE_DELAY_NPTURN = 119
    DOWN_RESISTANCE_DELAY_NPTURN = 120
    PIERCE_DEFENCE = 121
    UP_GUTS_HP = 122
    DOWN_GUTS_HP = 123
    UP_FUNCGAIN_NP = 124
    DOWN_FUNCGAIN_NP = 125
    UP_FUNC_HP_REDUCE = 126
    DOWN_FUNC_HP_REDUCE = 127
    UP_DEFENCECOMMAN_DAMAGE = 128
    DOWN_DEFENCECOMMAN_DAMAGE = 129
    NPATTACK_PREV_BUFF = 130
    FIX_COMMANDCARD = 131
    DONOT_GAINNP = 132
    FIELD_INDIVIDUALITY = 133
    DONOT_ACT_COMMANDTYPE = 134
    UP_DAMAGE_EVENT_POINT = 135


class NiceBuffType(str, Enum):
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


BUFF_TYPE_NAME: Dict[int, NiceBuffType] = {
    0: NiceBuffType.none,
    1: NiceBuffType.upCommandatk,
    2: NiceBuffType.upStarweight,
    3: NiceBuffType.upCriticalpoint,
    4: NiceBuffType.downCriticalpoint,
    5: NiceBuffType.regainNp,
    6: NiceBuffType.regainStar,
    7: NiceBuffType.regainHp,
    8: NiceBuffType.reduceHp,
    9: NiceBuffType.upAtk,
    10: NiceBuffType.downAtk,
    11: NiceBuffType.upDamage,
    12: NiceBuffType.downDamage,
    13: NiceBuffType.addDamage,
    14: NiceBuffType.subDamage,
    15: NiceBuffType.upNpdamage,
    16: NiceBuffType.downNpdamage,
    17: NiceBuffType.upDropnp,
    18: NiceBuffType.upCriticaldamage,
    19: NiceBuffType.downCriticaldamage,
    20: NiceBuffType.upSelfdamage,
    21: NiceBuffType.downSelfdamage,
    22: NiceBuffType.addSelfdamage,
    23: NiceBuffType.subSelfdamage,
    24: NiceBuffType.avoidance,
    25: NiceBuffType.breakAvoidance,
    26: NiceBuffType.invincible,
    27: NiceBuffType.upGrantstate,
    28: NiceBuffType.downGrantstate,
    29: NiceBuffType.upTolerance,
    30: NiceBuffType.downTolerance,
    31: NiceBuffType.avoidState,
    32: NiceBuffType.donotAct,
    33: NiceBuffType.donotSkill,
    34: NiceBuffType.donotNoble,
    35: NiceBuffType.donotRecovery,
    36: NiceBuffType.disableGender,
    37: NiceBuffType.guts,
    38: NiceBuffType.upHate,
    40: NiceBuffType.addIndividuality,
    41: NiceBuffType.subIndividuality,
    42: NiceBuffType.upDefence,
    43: NiceBuffType.downDefence,
    50: NiceBuffType.upCommandstar,
    51: NiceBuffType.upCommandnp,
    52: NiceBuffType.upCommandall,
    60: NiceBuffType.downCommandall,
    61: NiceBuffType.downStarweight,
    62: NiceBuffType.reduceNp,
    63: NiceBuffType.downDropnp,
    64: NiceBuffType.upGainHp,
    65: NiceBuffType.downGainHp,
    66: NiceBuffType.downCommandatk,
    67: NiceBuffType.downCommanstar,
    68: NiceBuffType.downCommandnp,
    70: NiceBuffType.upCriticalrate,
    71: NiceBuffType.downCriticalrate,
    72: NiceBuffType.pierceInvincible,
    73: NiceBuffType.avoidInstantdeath,
    74: NiceBuffType.upResistInstantdeath,
    75: NiceBuffType.upNonresistInstantdeath,
    76: NiceBuffType.delayFunction,
    77: NiceBuffType.regainNpUsedNoble,
    78: NiceBuffType.deadFunction,
    79: NiceBuffType.upMaxhp,
    80: NiceBuffType.downMaxhp,
    81: NiceBuffType.addMaxhp,
    82: NiceBuffType.subMaxhp,
    83: NiceBuffType.battlestartFunction,
    84: NiceBuffType.wavestartFunction,
    85: NiceBuffType.selfturnendFunction,
    87: NiceBuffType.upGivegainHp,
    88: NiceBuffType.downGivegainHp,
    89: NiceBuffType.commandattackFunction,
    90: NiceBuffType.deadattackFunction,
    91: NiceBuffType.upSpecialdefence,
    92: NiceBuffType.downSpecialdefence,
    93: NiceBuffType.upDamagedropnp,
    94: NiceBuffType.downDamagedropnp,
    95: NiceBuffType.entryFunction,
    96: NiceBuffType.upChagetd,
    97: NiceBuffType.reflectionFunction,
    98: NiceBuffType.upGrantSubstate,
    99: NiceBuffType.downGrantSubstate,
    100: NiceBuffType.upToleranceSubstate,
    101: NiceBuffType.downToleranceSubstate,
    102: NiceBuffType.upGrantInstantdeath,
    103: NiceBuffType.downGrantInstantdeath,
    104: NiceBuffType.gutsRatio,
    86: NiceBuffType.damageFunction,
    105: NiceBuffType.upDefencecommandall,
    106: NiceBuffType.downDefencecommandall,
    107: NiceBuffType.overwriteBattleclass,
    108: NiceBuffType.overwriteClassrelatioAtk,
    109: NiceBuffType.overwriteClassrelatioDef,
    110: NiceBuffType.upDamageIndividuality,
    111: NiceBuffType.downDamageIndividuality,
    112: NiceBuffType.upDamageIndividualityActiveonly,
    113: NiceBuffType.downDamageIndividualityActiveonly,
    114: NiceBuffType.upNpturnval,
    115: NiceBuffType.downNpturnval,
    116: NiceBuffType.multiattack,
    117: NiceBuffType.upGiveNp,
    118: NiceBuffType.downGiveNp,
    119: NiceBuffType.upResistanceDelayNpturn,
    120: NiceBuffType.downResistanceDelayNpturn,
    121: NiceBuffType.pierceDefence,
    122: NiceBuffType.upGutsHp,
    123: NiceBuffType.downGutsHp,
    124: NiceBuffType.upFuncgainNp,
    125: NiceBuffType.downFuncgainNp,
    126: NiceBuffType.upFuncHpReduce,
    127: NiceBuffType.downFuncHpReduce,
    128: NiceBuffType.upDefencecommanDamage,
    129: NiceBuffType.downDefencecommanDamage,
    130: NiceBuffType.npattackPrevBuff,
    131: NiceBuffType.fixCommandcard,
    132: NiceBuffType.donotGainnp,
    133: NiceBuffType.fieldIndividuality,
    134: NiceBuffType.donotActCommandtype,
    135: NiceBuffType.upDamageEventPoint,
}


### Buff Action ###


class BuffAction(IntEnum):
    NONE = 0
    COMMAND_ATK = 1
    COMMAND_DEF = 2
    ATK = 3
    DEFENCE = 4
    DEFENCE_PIERCE = 5
    SPECIALDEFENCE = 6
    DAMAGE = 7
    DAMAGE_INDIVIDUALITY = 8
    DAMAGE_INDIVIDUALITY_ACTIVEONLY = 9
    SELFDAMAGE = 10
    CRITICAL_DAMAGE = 11
    NPDAMAGE = 12
    GIVEN_DAMAGE = 13
    RECEIVE_DAMAGE = 14
    PIERCE_INVINCIBLE = 15
    INVINCIBLE = 16
    BREAK_AVOIDANCE = 17
    AVOIDANCE = 18
    OVERWRITE_BATTLECLASS = 19
    OVERWRITE_CLASSRELATIO_ATK = 20
    OVERWRITE_CLASSRELATIO_DEF = 21
    COMMAND_NP_ATK = 22
    COMMAND_NP_DEF = 23
    DROP_NP = 24
    DROP_NP_DAMAGE = 25
    COMMAND_STAR_ATK = 26
    COMMAND_STAR_DEF = 27
    CRITICAL_POINT = 28
    STARWEIGHT = 29
    TURNEND_NP = 30
    TURNEND_STAR = 31
    TURNEND_HP_REGAIN = 32
    TURNEND_HP_REDUCE = 33
    GAIN_HP = 34
    TURNVAL_NP = 35
    GRANT_STATE = 36
    RESISTANCE_STATE = 37
    AVOID_STATE = 38
    DONOT_ACT = 39
    DONOT_SKILL = 40
    DONOT_NOBLE = 41
    DONOT_RECOVERY = 42
    INDIVIDUALITY_ADD = 43
    INDIVIDUALITY_SUB = 44
    HATE = 45
    CRITICAL_RATE = 46
    AVOID_INSTANTDEATH = 47
    RESIST_INSTANTDEATH = 48
    NONRESIST_INSTANTDEATH = 49
    REGAIN_NP_USED_NOBLE = 50
    FUNCTION_DEAD = 51
    MAXHP_RATE = 52
    MAXHP_VALUE = 53
    FUNCTION_WAVESTART = 54
    FUNCTION_SELFTURNEND = 55
    GIVE_GAIN_HP = 56
    FUNCTION_COMMANDATTACK = 57
    FUNCTION_DEADATTACK = 58
    FUNCTION_ENTRY = 59
    CHAGETD = 60
    GRANT_SUBSTATE = 61
    TOLERANCE_SUBSTATE = 62
    GRANT_INSTANTDEATH = 63
    FUNCTION_DAMAGE = 64
    FUNCTION_REFLECTION = 65
    MULTIATTACK = 66
    GIVE_NP = 67
    RESISTANCE_DELAY_NPTURN = 68
    PIERCE_DEFENCE = 69
    GUTS_HP = 70
    FUNCGAIN_NP = 71
    FUNC_HP_REDUCE = 72
    FUNCTION_NPATTACK = 73
    FIX_COMMANDCARD = 74
    DONOT_GAINNP = 75
    FIELD_INDIVIDUALITY = 76
    DONOT_ACT_COMMANDTYPE = 77
    DAMAGE_EVENT_POINT = 78


class NiceBuffAction(str, Enum):
    none = "none"
    commandAtk = "commandAtk"
    commandDef = "commandDef"
    atk = "atk"
    defence = "defence"
    defencePierce = "defencePierce"
    specialdefence = "specialdefence"
    damage = "damage"
    damageIndividuality = "damageIndividuality"
    damageIndividualityActiveonly = "damageIndividualityActiveonly"
    selfdamage = "selfdamage"
    criticalDamage = "criticalDamage"
    npdamage = "npdamage"
    givenDamage = "givenDamage"
    receiveDamage = "receiveDamage"
    pierceInvincible = "pierceInvincible"
    invincible = "invincible"
    breakAvoidance = "breakAvoidance"
    avoidance = "avoidance"
    overwriteBattleclass = "overwriteBattleclass"
    overwriteClassrelatioAtk = "overwriteClassrelatioAtk"
    overwriteClassrelatioDef = "overwriteClassrelatioDef"
    commandNpAtk = "commandNpAtk"
    commandNpDef = "commandNpDef"
    dropNp = "dropNp"
    dropNpDamage = "dropNpDamage"
    commandStarAtk = "commandStarAtk"
    commandStarDef = "commandStarDef"
    criticalPoint = "criticalPoint"
    starweight = "starweight"
    turnendNp = "turnendNp"
    turnendStar = "turnendStar"
    turnendHpRegain = "turnendHpRegain"
    turnendHpReduce = "turnendHpReduce"
    gainHp = "gainHp"
    turnvalNp = "turnvalNp"
    grantState = "grantState"
    resistanceState = "resistanceState"
    avoidState = "avoidState"
    donotAct = "donotAct"
    donotSkill = "donotSkill"
    donotNoble = "donotNoble"
    donotRecovery = "donotRecovery"
    individualityAdd = "individualityAdd"
    individualitySub = "individualitySub"
    hate = "hate"
    criticalRate = "criticalRate"
    avoidInstantdeath = "avoidInstantdeath"
    resistInstantdeath = "resistInstantdeath"
    nonresistInstantdeath = "nonresistInstantdeath"
    regainNpUsedNoble = "regainNpUsedNoble"
    functionDead = "functionDead"
    maxhpRate = "maxhpRate"
    maxhpValue = "maxhpValue"
    functionWavestart = "functionWavestart"
    functionSelfturnend = "functionSelfturnend"
    giveGainHp = "giveGainHp"
    functionCommandattack = "functionCommandattack"
    functionDeadattack = "functionDeadattack"
    functionEntry = "functionEntry"
    chagetd = "chagetd"
    grantSubstate = "grantSubstate"
    toleranceSubstate = "toleranceSubstate"
    grantInstantdeath = "grantInstantdeath"
    functionDamage = "functionDamage"
    functionReflection = "functionReflection"
    multiattack = "multiattack"
    giveNp = "giveNp"
    resistanceDelayNpturn = "resistanceDelayNpturn"
    pierceDefence = "pierceDefence"
    gutsHp = "gutsHp"
    funcgainNp = "funcgainNp"
    funcHpReduce = "funcHpReduce"
    functionNpattack = "functionNpattack"
    fixCommandcard = "fixCommandcard"
    donotGainnp = "donotGainnp"
    fieldIndividuality = "fieldIndividuality"
    donotActCommandtype = "donotActCommandtype"
    damageEventPoint = "damageEventPoint"


BUFF_ACTION_NAME: Dict[int, NiceBuffAction] = {
    0: NiceBuffAction.none,
    1: NiceBuffAction.commandAtk,
    2: NiceBuffAction.commandDef,
    3: NiceBuffAction.atk,
    4: NiceBuffAction.defence,
    5: NiceBuffAction.defencePierce,
    6: NiceBuffAction.specialdefence,
    7: NiceBuffAction.damage,
    8: NiceBuffAction.damageIndividuality,
    9: NiceBuffAction.damageIndividualityActiveonly,
    10: NiceBuffAction.selfdamage,
    11: NiceBuffAction.criticalDamage,
    12: NiceBuffAction.npdamage,
    13: NiceBuffAction.givenDamage,
    14: NiceBuffAction.receiveDamage,
    15: NiceBuffAction.pierceInvincible,
    16: NiceBuffAction.invincible,
    17: NiceBuffAction.breakAvoidance,
    18: NiceBuffAction.avoidance,
    19: NiceBuffAction.overwriteBattleclass,
    20: NiceBuffAction.overwriteClassrelatioAtk,
    21: NiceBuffAction.overwriteClassrelatioDef,
    22: NiceBuffAction.commandNpAtk,
    23: NiceBuffAction.commandNpDef,
    24: NiceBuffAction.dropNp,
    25: NiceBuffAction.dropNpDamage,
    26: NiceBuffAction.commandStarAtk,
    27: NiceBuffAction.commandStarDef,
    28: NiceBuffAction.criticalPoint,
    29: NiceBuffAction.starweight,
    30: NiceBuffAction.turnendNp,
    31: NiceBuffAction.turnendStar,
    32: NiceBuffAction.turnendHpRegain,
    33: NiceBuffAction.turnendHpReduce,
    34: NiceBuffAction.gainHp,
    35: NiceBuffAction.turnvalNp,
    36: NiceBuffAction.grantState,
    37: NiceBuffAction.resistanceState,
    38: NiceBuffAction.avoidState,
    39: NiceBuffAction.donotAct,
    40: NiceBuffAction.donotSkill,
    41: NiceBuffAction.donotNoble,
    42: NiceBuffAction.donotRecovery,
    43: NiceBuffAction.individualityAdd,
    44: NiceBuffAction.individualitySub,
    45: NiceBuffAction.hate,
    46: NiceBuffAction.criticalRate,
    47: NiceBuffAction.avoidInstantdeath,
    48: NiceBuffAction.resistInstantdeath,
    49: NiceBuffAction.nonresistInstantdeath,
    50: NiceBuffAction.regainNpUsedNoble,
    51: NiceBuffAction.functionDead,
    52: NiceBuffAction.maxhpRate,
    53: NiceBuffAction.maxhpValue,
    54: NiceBuffAction.functionWavestart,
    55: NiceBuffAction.functionSelfturnend,
    56: NiceBuffAction.giveGainHp,
    57: NiceBuffAction.functionCommandattack,
    58: NiceBuffAction.functionDeadattack,
    59: NiceBuffAction.functionEntry,
    60: NiceBuffAction.chagetd,
    61: NiceBuffAction.grantSubstate,
    62: NiceBuffAction.toleranceSubstate,
    63: NiceBuffAction.grantInstantdeath,
    64: NiceBuffAction.functionDamage,
    65: NiceBuffAction.functionReflection,
    66: NiceBuffAction.multiattack,
    67: NiceBuffAction.giveNp,
    68: NiceBuffAction.resistanceDelayNpturn,
    69: NiceBuffAction.pierceDefence,
    70: NiceBuffAction.gutsHp,
    71: NiceBuffAction.funcgainNp,
    72: NiceBuffAction.funcHpReduce,
    73: NiceBuffAction.functionNpattack,
    74: NiceBuffAction.fixCommandcard,
    75: NiceBuffAction.donotGainnp,
    76: NiceBuffAction.fieldIndividuality,
    77: NiceBuffAction.donotActCommandtype,
    78: NiceBuffAction.damageEventPoint,
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


### DataVals Type ###


class DataValsType(IntEnum):
    Rate = 0
    Turn = 1
    Count = 2
    Value = 3
    Value2 = 4
    UseRate = 5
    Target = 6
    Correction = 7
    ParamAdd = 8
    ParamMax = 9
    HideMiss = 10
    OnField = 11
    HideNoEffect = 12
    Unaffected = 13
    ShowState = 14
    AuraEffectId = 15
    ActSet = 16
    ActSetWeight = 17
    ShowQuestNoEffect = 18
    CheckDead = 19
    RatioHPHigh = 20
    RatioHPLow = 21
    SetPassiveFrame = 22
    ProcPassive = 23
    ProcActive = 24
    HideParam = 25
    SkillID = 26
    SkillLV = 27
    ShowCardOnly = 28
    EffectSummon = 29
    RatioHPRangeHigh = 30
    RatioHPRangeLow = 31
    TargetList = 32
    OpponentOnly = 33


### Item Type ###


class ItemType(IntEnum):
    QP = 1
    STONE = 2
    AP_RECOVER = 3
    AP_ADD = 4
    MANA = 5
    KEY = 6
    GACHA_CLASS = 7
    GACHA_RELIC = 8
    GACHA_TICKET = 9
    LIMIT = 10
    SKILL_LV_UP = 11
    TD_LV_UP = 12
    FRIEND_POINT = 13
    EVENT_POINT = 14
    EVENT_ITEM = 15
    QUEST_REWARD_QP = 16
    CHARGE_STONE = 17
    RP_ADD = 18
    BOOST_ITEM = 19
    STONE_FRAGMENTS = 20
    ANONYMOUS = 21
    RARE_PRI = 22
    COSTUME_RELEASE = 23
    ITEM_SELECT = 24


class NiceItemType(str, Enum):
    qp = "qp"
    stone = "stone"
    apRecover = "apRecover"
    apAdd = "apAdd"
    mana = "mana"
    key = "key"
    gachaClass = "gachaClass"
    gachaRelic = "gachaRelic"
    gachaTicket = "gachaTicket"
    limit = "limit"
    skillLvUp = "skillLvUp"
    tdLvUp = "tdLvUp"
    friendPoint = "friendPoint"
    eventPoint = "eventPoint"
    eventItem = "eventItem"
    questRewardQp = "questRewardQp"
    chargeStone = "chargeStone"
    rpAdd = "rpAdd"
    boostItem = "boostItem"
    stoneFragments = "stoneFragments"
    anonymous = "anonymous"
    rarePri = "rarePri"
    costumeRelease = "costumeRelease"
    itemSelect = "itemSelect"


ITEM_TYPE_NAME: Dict[int, NiceItemType] = {
    1: NiceItemType.qp,
    2: NiceItemType.stone,
    3: NiceItemType.apRecover,
    4: NiceItemType.apAdd,
    5: NiceItemType.mana,
    6: NiceItemType.key,
    7: NiceItemType.gachaClass,
    8: NiceItemType.gachaRelic,
    9: NiceItemType.gachaTicket,
    10: NiceItemType.limit,
    11: NiceItemType.skillLvUp,
    12: NiceItemType.tdLvUp,
    13: NiceItemType.friendPoint,
    14: NiceItemType.eventPoint,
    15: NiceItemType.eventItem,
    16: NiceItemType.questRewardQp,
    17: NiceItemType.chargeStone,
    18: NiceItemType.rpAdd,
    19: NiceItemType.boostItem,
    20: NiceItemType.stoneFragments,
    21: NiceItemType.anonymous,
    22: NiceItemType.rarePri,
    23: NiceItemType.costumeRelease,
    24: NiceItemType.itemSelect,
}


### Card Type ###


class CardType(str, Enum):
    arts = "arts"
    buster = "buster"
    quick = "quick"
    extra = "extra"


CARD_TYPE_NAME: Dict[int, CardType] = {
    1: CardType.arts,
    2: CardType.buster,
    3: CardType.quick,
    4: CardType.extra,
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


class PlayableSvtClass(str, Enum):
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
    grandCaster = "grandCaster"
    beastII = "beastII"
    beastI = "beastI"
    beastIIIR = "beastIIIR"
    beastIIIL = "beastIIIL"
    beastUnknown = "beastUnknown"
    ALL = "ALL"


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
    17: SvtClass.grandCaster,
    20: SvtClass.beastII,
    22: SvtClass.beastI,
    24: SvtClass.beastIIIR,
    26: SvtClass.beastIIIL,
    27: SvtClass.beastUnknown,  # LB 5.2 beast
    1001: SvtClass.ALL,
}


CLASS_NAME_REVERSE: Dict[SvtClass, int] = {v: k for k, v in CLASS_NAME.items()}


PLAYABLE_CLASS_NAME: Dict[int, PlayableSvtClass] = {
    1: PlayableSvtClass.saber,
    2: PlayableSvtClass.archer,
    3: PlayableSvtClass.lancer,
    4: PlayableSvtClass.rider,
    5: PlayableSvtClass.caster,
    6: PlayableSvtClass.assassin,
    7: PlayableSvtClass.berserker,
    8: PlayableSvtClass.shielder,
    9: PlayableSvtClass.ruler,
    10: PlayableSvtClass.alterEgo,
    11: PlayableSvtClass.avenger,
    23: PlayableSvtClass.moonCancer,
    25: PlayableSvtClass.foreigner,
}


PLAYABLE_CLASS_NAME_REVERSE: Dict[PlayableSvtClass, int] = {
    v: k for k, v in PLAYABLE_CLASS_NAME.items()
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
    humanoidServant = "humanoidServant"
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
    buffInviciblePierce = "buffInviciblePierce"
    buffHpRecoveryPerTurn = "buffHpRecoveryPerTurn"
    buffNegativeEffectImmunity = "buffNegativeEffectImmunity"
    buffNegativeEffectAtTurnEnd = "buffNegativeEffectAtTurnEnd"
    normalAttack0 = "normalAttack0"
    normalAttack1 = "normalAttack1"
    normalAttack2 = "normalAttack2"
    criticalHit = "criticalHit"
    playerCards = "playerCards"
    cardNP = "cardNP"


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
    2074: Trait.blessedByKur,  # Eresh's 3rd skill add this individuality
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
    2654: Trait.livingHuman,  # Voyager's NP
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
    3059: Trait.buffInviciblePierce,
    3060: Trait.buffHpRecoveryPerTurn,
    3061: Trait.buffNegativeEffectImmunity,
    3063: Trait.buffNegativeEffectAtTurnEnd,
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
    5000: Trait.canBeInBattle,  # can be NPC, enemy or playable servant i.e. not CE
    5010: Trait.notBasedOnServant,
}


TRAIT_NAME_REVERSE: Dict[Trait, int] = {v: k for k, v in TRAIT_NAME.items()}
