from enum import IntEnum, StrEnum

from .gameenums import (
    AI_ACT_NUM_NAME,
    AI_ACT_TARGET_NAME,
    AI_ACT_TYPE_NAME,
    AI_COND_NAME,
    BUFF_ACTION_NAME,
    BUFF_LIMIT_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    CLASS_OVERWRITE_NAME,
    COMBINE_ADJUST_TARGET_TYPE_NAME,
    COND_TYPE_NAME,
    EVENT_LOTTERY_FLAG_NAME,
    EVENT_TYPE_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    GENDER_TYPE_NAME,
    GIFT_TYPE_NAME,
    ITEM_TYPE_NAME,
    MISSION_PROGRESS_TYPE_NAME,
    MISSION_REWARD_TYPE_NAME,
    MISSION_TYPE_NAME,
    PAY_TYPE_NAME,
    PURCHASE_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SHOP_TYPE_NAME,
    STATUS_RANK_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    WAR_OVERWRITE_TYPE_NAME,
    WAR_START_TYPE_NAME,
    FuncType,
    NiceBuffType,
    NiceCardType,
    NiceCombineAdjustTarget,
    NiceEventType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NicePayType,
    NiceQuestFlag,
    NiceQuestType,
    NiceShopType,
    NiceSvtFlag,
    NiceSvtType,
    Quest_FLAG_NAME,
    SvtType,
)


### Servant Type ###


SERVANT_TYPES = [
    SvtType.NORMAL,
    SvtType.HEROINE,
    SvtType.ENEMY_COLLECTION_DETAIL,
]

NICE_SERVANT_TYPES = [
    NiceSvtType.normal,
    NiceSvtType.heroine,
    NiceSvtType.enemyCollectionDetail,
]


SVT_TYPE_NAME_REVERSE: dict[NiceSvtType, int] = {v: k for k, v in SVT_TYPE_NAME.items()}


### Servant Flag ###


SVT_FLAG_NAME_REVERSE: dict[NiceSvtFlag, int] = {v: k for k, v in SVT_FLAG_NAME.items()}


### Item Use Type ###


class NiceItemUse(StrEnum):
    """Item Use Enum"""

    skill = "skill"
    appendSkill = "appendSkill"
    ascension = "ascension"
    costume = "costume"


### Skill Type ###


class NiceSkillType(StrEnum):
    """Skill Type Enum"""

    active = "active"
    passive = "passive"


SKILL_TYPE_NAME: dict[int, NiceSkillType] = {
    1: NiceSkillType.active,
    2: NiceSkillType.passive,
}


SKILL_TYPE_NAME_REVERSE: dict[NiceSkillType, int] = {
    v: k for k, v in SKILL_TYPE_NAME.items()
}


### Function Type ###

# The vals attribute of these func types are not buff IDs.
FUNC_VALS_NOT_BUFF = {
    FuncType.SUB_STATE,
    FuncType.EVENT_DROP_UP,
    FuncType.GAIN_NP_BUFF_INDIVIDUAL_SUM,
    FuncType.GAIN_NP_INDIVIDUAL_SUM,
}


FUNC_TYPE_NAME_REVERSE: dict[NiceFuncType, int] = {
    v: k for k, v in FUNC_TYPE_NAME.items()
}


### Func Apply Target ###


class FuncApplyTarget(StrEnum):
    """Function Target Team Enum"""

    player = "player"
    enemy = "enemy"
    playerAndEnemy = "playerAndEnemy"


FUNC_APPLYTARGET_NAME: dict[int, FuncApplyTarget] = {
    1: FuncApplyTarget.player,
    2: FuncApplyTarget.enemy,
    3: FuncApplyTarget.playerAndEnemy,
}


FUNC_APPLYTARGET_NAME_REVERSE: dict[FuncApplyTarget, int] = {
    v: k for k, v in FUNC_APPLYTARGET_NAME.items()
}


### Func Target Type ###


FUNC_TARGETTYPE_NAME_REVERSE: dict[NiceFuncTargetType, int] = {
    v: k for k, v in FUNC_TARGETTYPE_NAME.items()
}


### Building enemy func signature ###

TARGETTYPE_WITH_ENEMY_APPLYTARGET = (
    NiceFuncTargetType.self_,
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
    (target_type, FuncApplyTarget.player)
    for target_type in TARGETTYPE_WITH_PLAYER_APPLYTARGET
}
ENEMY_FUNC_TARGETING_ENEMY_TEAM = {
    (target_type, FuncApplyTarget.enemy)
    for target_type in TARGETTYPE_WITH_ENEMY_APPLYTARGET
}
ENEMY_FUNC_SIGNATURE = (
    ENEMY_FUNC_TARGETING_PLAYER_TEAM | ENEMY_FUNC_TARGETING_ENEMY_TEAM
)


### Buff Type ###


BUFF_TYPE_NAME_REVERSE: dict[NiceBuffType, int] = {
    v: k for k, v in BUFF_TYPE_NAME.items()
}


### Item BG Type ###


class NiceItemBGType(StrEnum):
    """Item Background Type Enum"""

    zero = "zero"  # qp, friendpoint
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    questClearQPReward = "questClearQPReward"
    aquaBlue = "aquaBlue"
    six = "six"
    unknown = "unknown"


ITEM_BG_TYPE_NAME: dict[int, NiceItemBGType] = {
    0: NiceItemBGType.zero,
    1: NiceItemBGType.bronze,
    2: NiceItemBGType.silver,
    3: NiceItemBGType.gold,
    4: NiceItemBGType.questClearQPReward,
    5: NiceItemBGType.aquaBlue,
    6: NiceItemBGType.six,
}


ITEM_BG_TYPE_REVERSE = {v: k for k, v in ITEM_BG_TYPE_NAME.items()}


### Item Type ###


ITEM_TYPE_REVERSE = {v: k for k, v in ITEM_TYPE_NAME.items()}


### Card Type ###


CARD_TYPE_NAME_REVERSE: dict[NiceCardType, int] = {
    v: k for k, v in CARD_TYPE_NAME.items()
}


### Gender ###


GENDER_TYPE_NAME_REVERSE: dict[NiceGender, int] = {
    v: k for k, v in GENDER_TYPE_NAME.items()
}


### Quest Type ###


QUEST_TYPE_REVERSE: dict[NiceQuestType, int] = {
    v: k for k, v in QUEST_TYPE_NAME.items()
}


### Quest Flag ###

QUEST_FLAG_REVERSE: dict[NiceQuestFlag, int] = {
    v: k for k, v in Quest_FLAG_NAME.items()
}


### Event Type Flag ###

EVENT_TYPE_REVERSE: dict[NiceEventType, int] = {
    v: k for k, v in EVENT_TYPE_NAME.items()
}


### Event Campaign Target Flag ###

COMBINE_ADJUST_TARGET_REVERSE: dict[NiceCombineAdjustTarget, int] = {
    v: k for k, v in COMBINE_ADJUST_TARGET_TYPE_NAME.items()
}


### Stage Turn Limit Action Type ###


class StageLimitActType(StrEnum):
    win = "win"
    lose = "lose"


STAGE_LIMIT_ACT_TYPE_NAME: dict[int, StageLimitActType] = {
    1: StageLimitActType.win,
    2: StageLimitActType.lose,
}


### Attribute ###


class Attribute(StrEnum):
    """Servant Attribute Enum"""

    human = "human"
    sky = "sky"
    earth = "earth"
    star = "star"
    beast = "beast"
    void = "void"


ATTRIBUTE_NAME: dict[int, Attribute] = {
    1: Attribute.human,
    2: Attribute.sky,
    3: Attribute.earth,
    4: Attribute.star,
    5: Attribute.beast,
    10: Attribute.void,
}


ATTRIBUTE_NAME_REVERSE: dict[Attribute, int] = {v: k for k, v in ATTRIBUTE_NAME.items()}


### Servant Class ###


class SvtClass(StrEnum):
    """Servant Class"""

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
    pretender = "pretender"
    grandCaster = "grandCaster"
    beastII = "beastII"
    ushiChaosTide = "ushiChaosTide"
    beastI = "beastI"
    beastILost = "beastILost"
    beastIIIR = "beastIIIR"
    beastIIIL = "beastIIIL"
    beastIV = "beastIV"
    beastUnknown = "beastUnknown"
    unknown = "unknown"
    agarthaPenth = "agarthaPenth"
    cccFinaleEmiyaAlter = "cccFinaleEmiyaAlter"
    salemAbby = "salemAbby"
    uOlgaMarie = "uOlgaMarie"
    uOlgaMarieAlienGod = "uOlgaMarieAlienGod"
    beast = "beast"
    beastVI = "beastVI"
    beastVIBoss = "beastVIBoss"
    uOlgaMarieFlare = "uOlgaMarieFlare"
    uOlgaMarieAqua = "uOlgaMarieAqua"
    uOlgaMarieFlareCollection = "uOlgaMarieFlareCollection"
    uOlgaMarieAquaCollection = "uOlgaMarieAquaCollection"
    atlasUnmappedClass = "atlasUnmappedClass"
    # OTHER = "OTHER"
    ALL = "ALL"
    # EXTRA = "EXTRA"
    # MIX = "MIX"


CLASS_NAME: dict[int, SvtClass] = {
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
    # 13
    # 14
    # 15
    # 16
    17: SvtClass.grandCaster,
    # 18
    # 19
    20: SvtClass.beastII,
    21: SvtClass.ushiChaosTide,
    22: SvtClass.beastI,
    23: SvtClass.moonCancer,
    24: SvtClass.beastIIIR,
    25: SvtClass.foreigner,
    26: SvtClass.beastIIIL,
    27: SvtClass.beastUnknown,  # LB 5.2 beast
    28: SvtClass.pretender,
    29: SvtClass.beastIV,
    30: SvtClass.beastILost,
    31: SvtClass.uOlgaMarieAlienGod,
    32: SvtClass.uOlgaMarie,
    33: SvtClass.beast,
    34: SvtClass.beastVI,
    35: SvtClass.beastVIBoss,
    36: SvtClass.uOlgaMarieFlare,
    37: SvtClass.uOlgaMarieAqua,
    97: SvtClass.unknown,
    # 98
    # 99
    # 100
    107: SvtClass.agarthaPenth,
    124: SvtClass.cccFinaleEmiyaAlter,
    125: SvtClass.salemAbby,
    # 1000: SvtClass.OTHER,
    # For Support List
    1001: SvtClass.ALL,
    # 1002: SvtClass.EXTRA,
    # 1003: SvtClass.MIX,
    # 1004: SvtClass.EXTRA1,
    # 1005: SvtClass.EXTRA2,
    9001: SvtClass.uOlgaMarieFlareCollection,
    9002: SvtClass.uOlgaMarieAquaCollection,
}


def get_class_name(class_id: int) -> SvtClass | str:
    if class_id in CLASS_NAME:
        return CLASS_NAME[class_id]
    else:
        return str(class_id)


CLASS_NAME_REVERSE: dict[SvtClass, int] = {v: k for k, v in CLASS_NAME.items()}


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
    SvtClass.pretender,
]


### AI Type ###


class AiType(StrEnum):
    """AI Type: where the AI is used"""

    svt = "svt"
    field = "field"


### AI Timing ###


class AiTiming(StrEnum):
    """Field AI timing Enum"""

    dead = "dead"
    turnEnemyStart = "turnEnemyStart"
    turnEnemyEnd = "turnEnemyEnd"
    turnPlayerStart = "turnPlayerStart"
    turnPlayerEnd = "turnPlayerEnd"
    waveStart = "waveStart"
    turnStart = "turnStart"
    unknown = "unknown"


AI_TIMING_NAME: dict[int, AiTiming] = {
    -6: AiTiming.dead,
    -1: AiTiming.unknown,
    1: AiTiming.waveStart,
    2: AiTiming.turnStart,
    3: AiTiming.turnPlayerStart,
    4: AiTiming.turnPlayerEnd,
    5: AiTiming.turnEnemyStart,
    6: AiTiming.turnEnemyEnd,
}


### Enemy role type ###


class EnemyRoleType(StrEnum):
    NORMAL = "normal"
    DANGER = "danger"
    SERVANT = "servant"


ENEMY_ROLE_TYPE_NAME: dict[int, EnemyRoleType] = {
    2: EnemyRoleType.DANGER,
    3: EnemyRoleType.SERVANT,
}


### Event Reward Scene Type ###


class EventRewardSceneType(IntEnum):
    EVENT_SHOP = 1
    BOX_GACHA = 2
    EVENT_POINT = 3
    EVENT_MISSION = 4
    DAMAGE_POINT = 5
    RANKING = 6
    TOWER = 7
    FATIGUE_RECOVERY = 8
    BOARD_GAME_TOKEN = 9
    TREASURE_BOX = 10
    RANDOM_MISSION = 11


### Event Shop


SHOP_TYPE_NAME_REVERSE: dict[NiceShopType, int] = {
    v: k for k, v in SHOP_TYPE_NAME.items()
}

PAY_TYPE_NAME_REVERSE: dict[NicePayType, int] = {v: k for k, v in PAY_TYPE_NAME.items()}


### EventPointActivity.objectType ###


class EventPointActivityObjectType(StrEnum):
    QUEST_ID = "questId"
    SKILL_ID = "skillId"
    SHOP_ID = "shopId"


EVENT_POINT_ACTIVITY_OBJECT_NAME: dict[int, EventPointActivityObjectType] = {
    1: EventPointActivityObjectType.QUEST_ID,
    2: EventPointActivityObjectType.SKILL_ID,
    3: EventPointActivityObjectType.SHOP_ID,
}


### Mission Cond Detail Type ###


class DetailMissionCondType(IntEnum):
    ENEMY_KILL_NUM = 1
    ENEMY_INDIVIDUALITY_KILL_NUM = 2
    ITEM_GET_TOTAL = 3
    BATTLE_SVT_IN_DECK = 4  # Unused
    BATTLE_SVT_EQUIP_IN_DECK = 5  # Unused
    TARGET_QUEST_ENEMY_KILL_NUM = 6
    TARGET_QUEST_ENEMY_INDIVIDUALITY_KILL_NUM = 7
    TARGET_QUEST_ITEM_GET_TOTAL = 8
    QUEST_CLEAR_ONCE = 9
    QUEST_CLEAR_NUM_1 = 10
    ITEM_GET_BATTLE = 12
    DEFEAT_ENEMY_INDIVIDUALITY = 13
    DEFEAT_ENEMY_CLASS = 14
    DEFEAT_SERVANT_CLASS = 15
    DEFEAT_ENEMY_NOT_SERVANT_CLASS = 16
    BATTLE_SVT_INDIVIDUALITY_IN_DECK = 17  # Clear one quest with servant having trait
    BATTLE_SVT_CLASS_IN_DECK = 18  # Filter by svt class
    SVT_GET_BATTLE = 19  # Embers are svt instead of items
    FRIEND_POINT_SUMMON = 21
    BATTLE_SVT_ID_IN_DECK_1 = 22  # Filter by svt ID
    BATTLE_SVT_ID_IN_DECK_2 = 23
    QUEST_CLEAR_NUM_2 = 24  # Not sure what's the difference QUEST_CLEAR_NUM_1
    DICE_USE = 25  # Probably Fate/Requiem event
    SQUARE_ADVANCED = 26
    MORE_FRIEND_FOLLOWER = 27  # 5th Anniversary missions
    QUEST_TYPE_CLEAR = 28  # 22M Download Campaign
    QUEST_CLEAR_NUM_INCLUDING_GRAILFRONT = 31
    WAR_MAIN_QUEST_CLEAR = 32


class DetailMissionCondLinkType(IntEnum):
    EVENT_START = 1
    MISSION_START = 2
    MASTER_MISSION_START = 3
    RANDOM_MISSION_START = 4


class NiceDetailMissionCondLinkType(StrEnum):
    """Mission Condition Detail Condition Link Type Enum"""

    eventStart = "eventStart"
    missionStart = "missionStart"
    masterMissionStart = "masterMissionStart"
    randomMissionStart = "randomMissionStart"


DETAIL_MISSION_LINK_TYPE: dict[int, NiceDetailMissionCondLinkType] = {
    1: NiceDetailMissionCondLinkType.eventStart,
    2: NiceDetailMissionCondLinkType.missionStart,
    3: NiceDetailMissionCondLinkType.masterMissionStart,
    4: NiceDetailMissionCondLinkType.randomMissionStart,
}


### Servant Policy ###


class ServantPolicy(StrEnum):
    """Servant Policy Enum"""

    none = "none"
    neutral = "neutral"
    lawful = "lawful"
    chaotic = "chaotic"
    unknown = "unknown"


SERVANT_POLICY_NAME = {
    0: ServantPolicy.none,
    1: ServantPolicy.neutral,
    2: ServantPolicy.chaotic,
    3: ServantPolicy.lawful,
}


### Servant Personality ###


class ServantPersonality(StrEnum):
    """Servant Personality Enum"""

    none = "none"
    good = "good"
    madness = "madness"
    balanced = "balanced"
    summer = "summer"
    evil = "evil"
    goodAndEvil = "goodAndEvil"
    bride = "bride"
    unknown = "unknown"


SERVANT_PERSONALITY_NAME = {
    0: ServantPersonality.none,
    1: ServantPersonality.good,
    2: ServantPersonality.evil,
    4: ServantPersonality.madness,
    5: ServantPersonality.balanced,
    6: ServantPersonality.goodAndEvil,
    7: ServantPersonality.bride,
    8: ServantPersonality.summer,
}


### Skill Script Cond ###


class SkillScriptCond(StrEnum):
    """Skill Script Condition Type"""

    NONE = "NONE"
    NP_HIGHER = "NP_HIGHER"
    NP_LOWER = "NP_LOWER"
    STAR_HIGHER = "STAR_HIGHER"
    STAR_LOWER = "STAR_LOWER"
    HP_VAL_HIGHER = "HP_VAL_HIGHER"
    HP_VAL_LOWER = "HP_VAL_LOWER"
    HP_PER_HIGHER = "HP_PER_HIGHER"
    HP_PER_LOWER = "HP_PER_LOWER"


### Trait ###


class Trait(StrEnum):
    """Trait/Individuality Enum"""

    unknown = "unknown"
    genderMale = "genderMale"
    genderFemale = "genderFemale"
    genderUnknown = "genderUnknown"
    classSaber = "classSaber"
    classLancer = "classLancer"
    classArcher = "classArcher"
    classRider = "classRider"
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
    classPretender = "classPretender"
    classUOlgaMarie = "classUOlgaMarie"
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
    demon = "demon"
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
    skyOrEarthServant = "skyOrEarthServant"
    brynhildsBeloved = "brynhildsBeloved"
    undeadOrDaemon = "undeadOrDaemon"
    undeadOrDemon = "undeadOrDemon"
    demonic = "demonic"
    skyOrEarthExceptPseudoAndDemi = "skyOrEarthExceptPseudoAndDemi"
    skyOrEarthExceptPseudoAndDemiServant = "skyOrEarthExceptPseudoAndDemiServant"
    divineOrDaemonOrUndead = "divineOrDaemonOrUndead"
    divineOrDemonOrUndead = "divineOrDemonOrUndead"
    saberClassServant = "saberClassServant"
    superGiant = "superGiant"
    king = "king"
    greekMythologyMales = "greekMythologyMales"
    illya = "illya"
    feminineLookingServant = "feminineLookingServant"
    argonaut = "argonaut"
    associatedToTheArgo = "associatedToTheArgo"
    genderCaenisServant = "genderCaenisServant"
    hominidaeServant = "hominidaeServant"
    blessedByKur = "blessedByKur"
    demonicBeastServant = "demonicBeastServant"
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
    buffImmobilize = "buffImmobilize"
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
    buffDefUp = "buffDefUp"
    buffInvinciblePierce = "buffInvinciblePierce"
    buffHpRecoveryPerTurn = "buffHpRecoveryPerTurn"
    buffNegativeEffectImmunity = "buffNegativeEffectImmunity"
    buffNegativeEffectAtTurnEnd = "buffNegativeEffectAtTurnEnd"
    attackPhysical = "attackPhysical"
    attackProjectile = "attackProjectile"
    attackMagical = "attackMagical"
    criticalHit = "criticalHit"
    faceCard = "faceCard"
    cardNP = "cardNP"
    kingproteaGrowth = "kingproteaGrowth"
    kingproteaInfiniteProliferation = "kingproteaInfiniteProliferation"
    kingproteaProliferation = "kingproteaProliferation"
    kingproteaProliferationNPDefense = "kingproteaProliferationNPDefense"
    fieldSunlight = "fieldSunlight"
    fieldShore = "fieldShore"
    fieldForest = "fieldForest"
    fieldBurning = "fieldBurning"
    fieldCity = "fieldCity"
    shadowServant = "shadowServant"
    aoeNP = "aoeNP"
    stNP = "stNP"
    giant = "giant"
    childServant = "childServant"
    buffSpecialInvincible = "buffSpecialInvincible"
    buffSkillRankUp = "buffSkillRankUp"
    buffSleep = "buffSleep"
    nobunaga = "nobunaga"
    fieldImaginarySpace = "fieldImaginarySpace"
    existenceOutsideTheDomain = "existenceOutsideTheDomain"
    curse = "curse"
    fieldShoreOrImaginarySpace = "fieldShoreOrImaginarySpace"
    shutenOnField = "shutenOnField"
    shuten = "shuten"
    genji = "genji"
    vengeance = "vengeance"
    enemyGardenOfSinnersLivingCorpse = "enemyGardenOfSinnersLivingCorpse"
    enemyGardenOfSinnersApartmentGhostAndSkeleton = (
        "enemyGardenOfSinnersApartmentGhostAndSkeleton"
    )
    enemyGardenOfSinnersBaseModel = "enemyGardenOfSinnersBaseModel"
    enemyGardenOfSinnersVengefulSpiritOfSevenPeople = (
        "enemyGardenOfSinnersVengefulSpiritOfSevenPeople"
    )
    enemySaberEliWerebeastAndHomunculusAndKnight = (
        "enemySaberEliWerebeastAndHomunculusAndKnight"
    )
    enemySaberEliSkeletonAndGhostAndLamia = "enemySaberEliSkeletonAndGhostAndLamia"
    enemySaberEliBugAndGolem = "enemySaberEliBugAndGolem"
    enemySeraphEater = "enemySeraphEater"
    enemySeraphShapeshifter = "enemySeraphShapeshifter"
    enemySeraphTypeI = "enemySeraphTypeI"
    enemySeraphTypeSakura = "enemySeraphTypeSakura"
    enemyHimejiCastleKnightAndGazerAndMassProduction = (
        "enemyHimejiCastleKnightAndGazerAndMassProduction"
    )
    enemyHimejiCastleDronesAndHomunculusAndAutomata = (
        "enemyHimejiCastleDronesAndHomunculusAndAutomata"
    )
    enemyHimejiCastleSkeletonAndScarecrow = "enemyHimejiCastleSkeletonAndScarecrow"
    enemyGuda3MiniNobu = "enemyGuda3MiniNobu"
    enemyDavinciTrueEnemy = "enemyDavinciTrueEnemy"
    enemyDavinciFalseEnemy = "enemyDavinciFalseEnemy"
    enemyCaseFilesRareEnemy = "enemyCaseFilesRareEnemy"
    enemyLasVegasBonusEnemy = "enemyLasVegasBonusEnemy"
    enemySummerCampRareEnemy = "enemySummerCampRareEnemy"
    enemyLittleBigTenguTsuwamonoEnemy = "enemyLittleBigTenguTsuwamonoEnemy"
    eventSaberWars = "eventSaberWars"
    eventRashomon = "eventRashomon"
    eventOnigashima = "eventOnigashima"
    eventOnigashimaRaid = "eventOnigashimaRaid"
    eventPrisma = "eventPrisma"
    eventPrismaWorldEndMatch = "eventPrismaWorldEndMatch"
    eventNeroFest2 = "eventNeroFest2"
    eventGuda2 = "eventGuda2"
    eventNeroFest3 = "eventNeroFest3"
    eventSetsubun = "eventSetsubun"
    eventApocrypha = "eventApocrypha"
    eventBattleInNewYork1 = "eventBattleInNewYork1"
    eventOniland = "eventOniland"
    eventOoku = "eventOoku"
    eventGuda4 = "eventGuda4"
    eventLasVegas = "eventLasVegas"
    eventBattleInNewYork2 = "eventBattleInNewYork2"
    eventSaberWarsII = "eventSaberWarsII"
    eventSummerCamp = "eventSummerCamp"
    eventGuda5 = "eventGuda5"
    cursedBook = "cursedBook"
    buffCharmFemale = "buffCharmFemale"
    mechanical = "mechanical"
    fae = "fae"
    hasCostume = "hasCostume"
    weakPointsRevealed = "weakPointsRevealed"
    chenGongNpBlock = "chenGongNpBlock"
    knightsOfTheRound = "knightsOfTheRound"
    divineSpirit = "divineSpirit"
    buffNullifyBuff = "buffNullifyBuff"
    enemyGudaMiniNobu = "enemyGudaMiniNobu"
    burningLove = "burningLove"
    buffStrongAgainstWildBeast = "buffStrongAgainstWildBeast"
    buffStrongAgainstDragon = "buffStrongAgainstDragon"
    fairyTaleServant = "fairyTaleServant"
    classBeastIV = "classBeastIV"
    havingAnimalsCharacteristics = "havingAnimalsCharacteristics"
    like = "like"
    exaltation = "exaltation"
    gubijin = "gubijin"
    yuMeiren = "yuMeiren"
    milleniumCastle = "milleniumCastle"
    protoMerlinNPChargeBlock = "protoMerlinNPChargeBlock"
    valkyrie = "valkyrie"
    immuneToPigify = "immuneToPigify"
    summerModeServant = "summerModeServant"
    shinsengumiServant = "shinsengumiServant"
    ryozanpaku = "ryozanpaku"
    demonUnused = "demonUnused"
    levitating = "levitating"
    obstacleMaker = "obstacleMaker"
    defender = "defender"
    hasGoddessMetamorphosis = "hasGoddessMetamorphosis"
    servantsWithSkyAttribute = "servantsWithSkyAttribute"
    moon = "moon"
    cardWeak = "cardWeak"
    cardStrong = "cardStrong"
    servant = "servant"
    shadow = "shadow"
    chenGongNp = "chenGongNp"
    cantBeSacrificed = "cantBeSacrificed"
    gutsBlock = "gutsBlock"
    classBeastILost = "classBeastILost"
    holdingHolyGrail = "holdingHolyGrail"
    standardClassServant = "standardClassServant"
    classBeast = "classBeast"
    classBeastVI = "classBeastVI"
    classBeastVIBoss = "classBeastVIBoss"
    buffBound = "buffBound"
    buffDamageCut = "buffDamageCut"
    marking = "marking"
    manuscriptComplete = "manuscriptComplete"
    myFairSoldier = "myFairSoldier"
    zeroStarServant = "zeroStarServant"
    oneStarServant = "oneStarServant"
    twoStarServant = "twoStarServant"
    threeStarServant = "threeStarServant"
    fourStarServant = "fourStarServant"
    fiveStarServant = "fiveStarServant"
    wrathOfTheEnshrinedDeity = "wrathOfTheEnshrinedDeity"
    caitCuCerpriestessAscension0To2 = "caitCuCerpriestessAscension0To2"
    caitCuCerpriestessAscension3To4 = "caitCuCerpriestessAscension3To4"
    fieldAir = "fieldAir"
    caitCuCerpriestessOnTheField = "caitCuCerpriestessOnTheField"
    buffNpPerTurn = "buffNpPerTurn"
    buffStarPerTurn = "buffStarPerTurn"
    burnEffectivenessUp = "burnEffectivenessUp"
    murasamaAscension0 = "murasamaAscension0"
    classUOlgaMarieFlare = "classUOlgaMarieFlare"
    elementalsWrath = "elementalsWrath"
    buffBuffSuccessRateUp = "buffBuffSuccessRateUp"
    groupServant = "groupServant"
    takeruDummyTrait = "takeruDummyTrait"
    artsBuff = "artsBuff"
    busterBuff = "busterBuff"
    quickBuff = "quickBuff"
    FSNServant = "FSNServant"
    fieldDarkness = "fieldDarkness"
    magicBullet = "magicBullet"
    protagonistCorrection = "protagonistCorrection"
    normalAokoBuff = "normalAokoBuff"
    magicBulletAtkBuff = "magicBulletAtkBuff"
    demeritFunction = "demeritFunction"
    extraBuff = "extraBuff"
    robinCounter = "robinCounter"
    kuonjiAliceHasSkill3 = "kuonjiAliceHasSkill3"
    kuonjiAliceStage3 = "kuonjiAliceStage3"
    instantDeathFunction = "instantDeathFunction"
    forceInstantDeathFunction = "forceInstantDeathFunction"
    buffGutsOnInstantDeath = "buffGutsOnInstantDeath"
    robinAllGone = "robinAllGone"


TRAIT_NAME: dict[int, Trait] = {
    1: Trait.genderMale,
    2: Trait.genderFemale,
    3: Trait.genderUnknown,
    100: Trait.classSaber,
    101: Trait.classLancer,
    102: Trait.classArcher,
    103: Trait.classRider,
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
    120: Trait.classPretender,
    121: Trait.classBeastIV,
    122: Trait.classBeastILost,
    123: Trait.classUOlgaMarie,
    124: Trait.classBeast,
    125: Trait.classBeastVI,
    126: Trait.classBeastVIBoss,
    127: Trait.classUOlgaMarieFlare,
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
    400: Trait.zeroStarServant,
    401: Trait.oneStarServant,
    402: Trait.twoStarServant,
    403: Trait.threeStarServant,
    404: Trait.fourStarServant,
    405: Trait.fiveStarServant,
    1000: Trait.servant,  # can be NPC or enemy but use a servant's data
    1001: Trait.human,  # Sanson's 3rd skill
    1002: Trait.undead,  # Scathach's 3rd skill
    1003: Trait.artificialDemon,
    1004: Trait.demonBeast,
    1005: Trait.demonUnused,
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
    1119: Trait.demon,
    1120: Trait.handOrDoor,
    1121: Trait.demonGodPillar,
    1122: Trait.shadow,
    1128: Trait.enemyGardenOfSinnersLivingCorpse,
    1129: Trait.enemyGardenOfSinnersApartmentGhostAndSkeleton,
    1130: Trait.enemyGardenOfSinnersBaseModel,
    1131: Trait.enemyGardenOfSinnersVengefulSpiritOfSevenPeople,
    1132: Trait.oni,
    1133: Trait.hand,
    1134: Trait.door,
    1135: Trait.enemySaberEliWerebeastAndHomunculusAndKnight,
    1136: Trait.enemySaberEliSkeletonAndGhostAndLamia,
    1137: Trait.enemySaberEliBugAndGolem,
    1138: Trait.enemySeraphEater,
    1139: Trait.enemySeraphShapeshifter,
    1140: Trait.enemySeraphTypeI,
    1141: Trait.enemySeraphTypeSakura,
    1155: Trait.enemyHimejiCastleKnightAndGazerAndMassProduction,
    1156: Trait.enemyHimejiCastleDronesAndHomunculusAndAutomata,
    1157: Trait.enemyHimejiCastleSkeletonAndScarecrow,
    1171: Trait.enemyGuda3MiniNobu,
    1172: Trait.threatToHumanity,
    1177: Trait.fae,
    2000: Trait.divine,
    2001: Trait.humanoid,
    2002: Trait.dragon,
    2003: Trait.dragonSlayer,
    2004: Trait.roman,
    2005: Trait.wildbeast,
    2006: Trait.moon,
    2007: Trait.saberface,
    2008: Trait.weakToEnumaElish,
    2009: Trait.riding,
    2010: Trait.arthur,
    2011: Trait.skyOrEarthServant,  # Tesla's NP
    2012: Trait.brynhildsBeloved,
    2018: Trait.undeadOrDemon,  # Amakusa bond CE
    2019: Trait.demonic,
    2023: Trait.enemyDavinciTrueEnemy,
    2024: Trait.enemyDavinciFalseEnemy,
    2037: Trait.skyOrEarthExceptPseudoAndDemiServant,  # Raikou's 3rd skill
    2038: Trait.fieldSunlight,
    2039: Trait.fieldShore,
    2040: Trait.divineOrDemonOrUndead,  # Ruler Martha's 3rd skill
    2073: Trait.fieldForest,
    2074: Trait.blessedByKur,  # Eresh's 3rd skill add this individuality
    2075: Trait.saberClassServant,  # MHXA NP
    2076: Trait.superGiant,
    2113: Trait.king,
    2114: Trait.greekMythologyMales,
    2121: Trait.fieldBurning,
    2191: Trait.buffCharmFemale,  # Charm buffs that come from females; Fion 2nd skill
    2221: Trait.enemyGudaMiniNobu,
    2355: Trait.illya,
    2356: Trait.feminineLookingServant,  # Teach's 3rd skill
    2385: Trait.cursedBook,  # Murasaki Valentine
    2386: Trait.kingproteaProliferation,
    2387: Trait.kingproteaInfiniteProliferation,
    2392: Trait.fieldCity,
    2403: Trait.enemyCaseFilesRareEnemy,
    2469: Trait.enemyLasVegasBonusEnemy,
    2466: Trait.associatedToTheArgo,
    2467: Trait.weakPointsRevealed,  # Paris 1st skill
    2615: Trait.genderCaenisServant,  # Phantom's 2nd skill
    2631: Trait.hominidaeServant,  # used in TamaVitch's fight
    2632: Trait.demonicBeastServant,  # used in TamaVitch's fight
    2654: Trait.livingHuman,  # Voyager's NP
    2663: Trait.enemySummerCampRareEnemy,
    2664: Trait.kingproteaProliferationNPDefense,
    2666: Trait.giant,
    2667: Trait.childServant,  # Summer Illya's 2nd skill
    2721: Trait.nobunaga,  # Nobukatsu's skill
    2729: Trait.curse,  # Van Gogh passive
    2730: Trait.fieldImaginarySpace,
    2731: Trait.existenceOutsideTheDomain,
    2732: Trait.fieldShoreOrImaginarySpace,  # Nemo's 3rd skill and bond CE
    2733: Trait.shutenOnField,  # Ibaraki strengthened 2nd skill
    2734: Trait.shuten,  # Ibaraki strengthened 2nd skill
    2735: Trait.genji,
    2749: Trait.enemyLittleBigTenguTsuwamonoEnemy,
    2759: Trait.vengeance,  # Taira 2nd skill and NP
    2780: Trait.hasCostume,
    2781: Trait.mechanical,
    2795: Trait.knightsOfTheRound,
    2797: Trait.divineSpirit,
    2801: Trait.burningLove,  # Summer Kama 3rd skill
    2802: Trait.buffStrongAgainstDragon,
    2803: Trait.buffStrongAgainstWildBeast,
    2810: Trait.fairyTaleServant,
    2821: Trait.havingAnimalsCharacteristics,
    2827: Trait.like,  # Super Bunyan NP
    2828: Trait.exaltation,
    2829: Trait.milleniumCastle,
    2833: Trait.yuMeiren,
    2835: Trait.immuneToPigify,
    2836: Trait.protoMerlinNPChargeBlock,
    2837: Trait.valkyrie,
    2838: Trait.summerModeServant,
    2839: Trait.shinsengumiServant,
    2840: Trait.ryozanpaku,
    2847: Trait.levitating,
    2848: Trait.obstacleMaker,
    2849: Trait.defender,
    2850: Trait.hasGoddessMetamorphosis,
    2851: Trait.servantsWithSkyAttribute,
    2857: Trait.holdingHolyGrail,
    2858: Trait.standardClassServant,
    2871: Trait.murasamaAscension0,
    2872: Trait.manuscriptComplete,
    2873: Trait.myFairSoldier,
    2874: Trait.wrathOfTheEnshrinedDeity,
    2875: Trait.caitCuCerpriestessAscension0To2,
    2876: Trait.caitCuCerpriestessAscension3To4,
    2878: Trait.fieldAir,
    2879: Trait.caitCuCerpriestessOnTheField,
    2880: Trait.elementalsWrath,
    2881: Trait.groupServant,
    2883: Trait.FSNServant,
    2884: Trait.fieldDarkness,
    2885: Trait.magicBullet,
    2886: Trait.robinCounter,
    2887: Trait.robinAllGone,
    2888: Trait.protagonistCorrection,
    2903: Trait.kuonjiAliceStage3,
    2911: Trait.normalAokoBuff,
    2912: Trait.magicBulletAtkBuff,
    2913: Trait.kuonjiAliceHasSkill3,
    2914: Trait.buffGutsOnInstantDeath,
    # 2xxx: CQ or Story quests buff
    3000: Trait.attackPhysical,  # Normal attack, including NP
    3001: Trait.attackProjectile,
    3002: Trait.attackMagical,
    3004: Trait.buffPositiveEffect,
    3005: Trait.buffNegativeEffect,  # mutually exclusive with 3004
    3006: Trait.buffIncreaseDamage,  # catch all damage: atk, np, powermod, ...
    3007: Trait.buffIncreaseDefence,  # catch all defence, including evade
    3008: Trait.buffDecreaseDamage,
    3009: Trait.buffDecreaseDefence,  # including death resist down and card color resist down
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
    3045: Trait.buffImmobilize,  # Including Petrify, Bound, Pigify, Stun
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
    3058: Trait.buffDefUp,
    3059: Trait.buffInvinciblePierce,
    3060: Trait.buffHpRecoveryPerTurn,
    3061: Trait.buffNegativeEffectImmunity,
    3063: Trait.buffNegativeEffectAtTurnEnd,
    3064: Trait.buffSpecialInvincible,
    3065: Trait.buffSkillRankUp,
    3066: Trait.buffSleep,
    3068: Trait.chenGongNp,
    3070: Trait.buffNullifyBuff,
    3076: Trait.cantBeSacrificed,
    3080: Trait.buffNpPerTurn,
    3081: Trait.buffStarPerTurn,
    3085: Trait.buffDamageCut,
    3086: Trait.gutsBlock,
    3087: Trait.buffBound,
    3088: Trait.marking,
    3089: Trait.burnEffectivenessUp,
    3090: Trait.buffBuffSuccessRateUp,
    3091: Trait.takeruDummyTrait,
    3092: Trait.artsBuff,
    3093: Trait.busterBuff,
    3094: Trait.quickBuff,
    3096: Trait.instantDeathFunction,
    3097: Trait.forceInstantDeathFunction,
    3098: Trait.demeritFunction,
    3100: Trait.extraBuff,
    # 6016: No detail
    # 6021: No detail
    # 6022: No detail
    # 10xxx: CCC Kiara buff
    4001: Trait.cardArts,
    4002: Trait.cardBuster,
    4003: Trait.cardQuick,
    4004: Trait.cardExtra,
    4005: Trait.cardWeak,
    4006: Trait.cardStrong,
    4007: Trait.cardNP,
    4008: Trait.faceCard,  # Normal Buster, Arts, Quick, Extra Attack
    4100: Trait.criticalHit,
    4101: Trait.aoeNP,
    4102: Trait.stNP,
    5000: Trait.canBeInBattle,  # can be NPC, enemy or playable servant i.e. not CE
    5010: Trait.notBasedOnServant,
    94000015: Trait.eventSaberWars,
    94000037: Trait.eventRashomon,
    94000045: Trait.eventOnigashima,
    94000046: Trait.eventOnigashimaRaid,
    94000047: Trait.eventPrisma,
    94000048: Trait.eventPrismaWorldEndMatch,
    94000049: Trait.eventNeroFest2,
    94000057: Trait.eventGuda2,
    94000066: Trait.eventNeroFest3,
    94000071: Trait.eventSetsubun,
    94000074: Trait.eventApocrypha,
    94000077: Trait.eventBattleInNewYork1,
    94000078: Trait.eventOniland,
    94000086: Trait.eventOoku,
    94000089: Trait.eventGuda4,
    94000091: Trait.eventLasVegas,
    94000092: Trait.eventBattleInNewYork2,
    94000095: Trait.eventSaberWarsII,
    94000107: Trait.eventSummerCamp,
    94000108: Trait.eventGuda5,
}


TRAIT_NAME_REVERSE: dict[Trait, int] = {v: k for k, v in TRAIT_NAME.items()}

OLD_TRAIT_MAPPING = {
    Trait.daemon: 1005,
    Trait.undeadOrDaemon: 2018,
    Trait.divineOrDaemonOrUndead: 2040,
    Trait.argonaut: 2466,
    Trait.skyOrEarth: 2011,
    Trait.skyOrEarthExceptPseudoAndDemi: 2037,
    Trait.kingproteaGrowth: 2387,
    Trait.gubijin: 2833,
    Trait.buffIncreaseDefenceAgainstIndividuality: 3058,
    Trait.atalante: 2006,
    Trait.basedOnServant: 1000,
    Trait.shadowServant: 1122,
    Trait.chenGongNpBlock: 3068,
}

TRAIT_NAME_REVERSE |= OLD_TRAIT_MAPPING


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
    "Gender": GENDER_TYPE_NAME,
    "Attribute": ATTRIBUTE_NAME,
    "SvtClass": CLASS_NAME,
    "NiceStatusRank": STATUS_RANK_NAME,
    "NiceCondType": COND_TYPE_NAME,
    "NiceVoiceCondType": VOICE_COND_NAME,
    "NiceSvtVoiceType": VOICE_TYPE_NAME,
    "NiceQuestType": QUEST_TYPE_NAME,
    "NiceConsumeType": QUEST_CONSUME_TYPE_NAME,
    "NiceEventType": EVENT_TYPE_NAME,
    "Trait": TRAIT_NAME,
    "NiceWarStartType": WAR_START_TYPE_NAME,
    "NiceWarOverwriteType": WAR_OVERWRITE_TYPE_NAME,
    "NiceGiftType": GIFT_TYPE_NAME,
    "NicePayType": PAY_TYPE_NAME,
    "NicePurchaseType": PURCHASE_TYPE_NAME,
    "NiceShopType": SHOP_TYPE_NAME,
    "NiceAiActType": AI_ACT_TYPE_NAME,
    "NiceAiActTarget": AI_ACT_TARGET_NAME,
    "NiceAiActNum": AI_ACT_NUM_NAME,
    "NiceAiCond": AI_COND_NAME,
    "AiTiming": AI_TIMING_NAME,
    "NiceMissionType": MISSION_TYPE_NAME,
    "NiceMissionRewardType": MISSION_REWARD_TYPE_NAME,
    "NiceMissionProgressType": MISSION_PROGRESS_TYPE_NAME,
    "NiceDetailMissionCondLinkType": DETAIL_MISSION_LINK_TYPE,
    "NiceLotteryFlag": EVENT_LOTTERY_FLAG_NAME,
}
