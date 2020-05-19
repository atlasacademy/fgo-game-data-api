from enum import IntEnum
from typing import Dict, List, Union

from pydantic import BaseModel


class MstBuff(BaseModel):
    vals: List[int]  # [3004],
    tvals: List[int]  # [5000, 4001],
    ckSelfIndv: List[int]  # [4001],
    ckOpIndv: List[int]  # [2005],
    script: Dict[str, Union[int, str]]  # {"HP_LOWER": 600, "motionName": "MOTION_2101"}
    id: int  # 101,
    buffGroup: int  # 0,
    type: int  # 52,
    name: str  # "Arts Up",
    detail: str  # "Increase Arts Card effectiveness",
    iconId: int  # 313,
    maxRate: int  # 5000


class BuffEntityNoReverse(BaseModel):
    mstBuff: MstBuff


class MstFunc(BaseModel):
    vals: List[int]  # [208],
    expandedVals: List[BuffEntityNoReverse] = []
    tvals: List[int]  # [106],
    questTvals: List[int]  # [94000015],
    effectList: List[int]  # [332],
    popupTextColor: int  # 2,
    id: int  # 657,
    cond: int  # 0,
    funcType: int  # 16,
    targetType: int  # 0,
    applyTarget: int  # 3,
    popupIconId: int  # 302,
    popupText: str  # "STR Up\nvs. Lancer"


class FunctionEntityNoReverse(BaseModel):
    mstFunc: MstFunc


class MstSkill(BaseModel):
    effectList: List[int]  # [323],
    actIndividuality: List[int]  # [401900],
    script: Dict[
        str, Union[str, int]
    ]  # {"cutInId": 90001, "cutInVoices": "ChrVoice_7100400:0_E130:1"}
    id: int  # 263350,
    type: int  # 1,
    name: str  # "Projection C",
    ruby: str  # "Projection",
    maxLv: int  # 10,
    iconId: int  # 317,
    motion: int  # 101


class MstSkillDetail(BaseModel):
    id: int  # 429650,
    detail: str  # "Increase your Critical Strength",
    detailShort: str  # "Increase your Critical Strength"


class MstSvtSkill(BaseModel):
    strengthStatus: int  # 1,
    svtId: int  # 9400920,
    num: int  # 1,
    priority: int  # 1,
    skillId: int  # 990183,
    condQuestId: int  # 0,
    condQuestPhase: int  # 0,
    condLv: int  # 0,
    condLimitCount: int  # 0,
    eventId: int  # 0,
    flag: int  # 0


class MstSkillLv(BaseModel):
    funcId: List[int]  # [366, 216, 434],
    expandedFuncId: List[FunctionEntityNoReverse] = []
    svals: List[str]  # ["[1000,1,-1,3600]", "[1000,1,-1,200]", "[1000]"],
    script: Dict[
        str, Union[int, str, List[str]]
    ]  # {"STAR_HIGHER": 8, "VoiceAssetName": "ChrVoice_7100400", "followerVals": ["[2,30]"]},
    skillId: int  # 440450,
    lv: int  # 4,
    chargeTurn: int  # 7,
    skillDetailId: int  # 440450,
    priority: int  # 0


class SkillEntityNoReverse(BaseModel):
    mstSkill: MstSkill
    mstSkillDetail: List[MstSkillDetail]
    mstSvtSkill: List[MstSvtSkill]
    mstSkillLv: List[MstSkillLv]


class MstTreasureDevice(BaseModel):
    individuality: List[int]  # [3000, 4001, 4007],
    script: Dict[
        str, Union[int, List[int]]
    ]  # {"limitSeqId_12": 800140, "randomWeights_3": [50, 50]},
    id: int  # 500801,
    seqId: int  # 500800,
    name: str  # "Garden of Avalon",
    ruby: str  # " ",
    rank: str  # "C",
    maxLv: int  # 5,
    typeText: str  # "Anti-Personnel",
    attackAttri: int  # 1


class MstTreasureDeviceDetail(BaseModel):
    id: int  # 100101,
    detail: str  # "Deal heavy damage to all enemies [{0}] + restore your NP Gauge <effect increases with Overcharge>",
    detailShort: str  # "Deal heavy damage to all enemies [{0}] + restore your NP Gauge <effect increases with Overcharge>"


class MstSvtTreasureDevice(BaseModel):
    damage: List[int]  # [5, 11, 17, 11, 23, 33],
    strengthStatus: int  # 1,
    svtId: int  # 400900,
    num: int  # 1,
    priority: int  # 101,
    flag: int  # 0,
    imageIndex: int  # 0,
    treasureDeviceId: int  # 400901,
    condQuestId: int  # 0,
    condQuestPhase: int  # 0,
    condLv: int  # 0,
    condFriendshipRank: int  # 0,
    motion: int  # 50,
    cardId: int  # 3


class MstTreasureDeviceLv(BaseModel):
    funcId: List[int]  # [13, 174, 432],
    expandedFuncId: List[FunctionEntityNoReverse] = []
    svals: List[str]  # ["[1000,6000]", "[1000,3,-1,100]", "[5000,3,-1]"],
    svals2: List[str]  # ["[1000,6000]", "[1000,3,-1,150]", "[5000,3,-1]"],
    svals3: List[str]  # ["[1000,6000]", "[1000,3,-1,200]", "[5000,3,-1]"],
    svals4: List[str]  # ["[1000,6000]", "[1000,3,-1,250]", "[5000,3,-1]"],
    svals5: List[str]  # ["[1000,6000]", "[1000,3,-1,300]", "[5000,3,-1]"],
    treaureDeviceId: int  # 301102,
    lv: int  # 1,
    gaugeCount: int  # 1,
    detailId: int  # 301102,
    tdPoint: int  # 55,
    tdPointQ: int  # 55,
    tdPointA: int  # 55,
    tdPointB: int  # 55,
    tdPointEx: int  # 55,
    tdPointDef: int  # 400,
    qp: int  # 40000


class TdEntityNoReverse(BaseModel):
    mstTreasureDevice: MstTreasureDevice
    mstTreasureDeviceDetail: List[MstTreasureDeviceDetail]
    mstSvtTreasureDevice: List[MstSvtTreasureDevice]
    mstTreasureDeviceLv: List[MstTreasureDeviceLv]


class MstSvt(BaseModel):
    relateQuestIds: List[int]  # [91500701, 94004103, 94014414],
    individuality: List[int]  # [5000, 500800],
    classPassive: List[int]  # [83350, 80350, 320650],
    expandedClassPassive: List[SkillEntityNoReverse] = []
    cardIds: List[int]  # [3, 1, 1, 1, 2],
    script: Dict[str, int]  # { "cameraActionId: 80 },
    id: int  # 500800,
    baseSvtId: int  # 500800,
    name: str  # "Merlin",
    ruby: str  # "Merlin",
    battleName: str  # "Merlin",
    classId: int  # 5,
    type: int  # 1,
    limitMax: int  # 4,
    rewardLv: int  # 90,
    friendshipId: int  # 1049,
    maxFriendshipRank: int  # 10,
    genderType: int  # 1,
    attri: int  # 3,
    combineSkillId: int  # 500800,
    combineLimitId: int  # 500800,
    sellQp: int  # 5000,
    sellMana: int  # 9,
    sellRarePri: int  # 5,
    expType: int  # 30,
    combineMaterialId: int  # 5,
    cost: int  # 16,
    battleSize: int  # 2,
    hpGaugeY: int  # -250,
    starRate: int  # 108,
    deathRate: int  # 360,
    attackAttri: int  # 3,
    illustratorId: int  # 22,
    cvId: int  # 62,
    collectionNo: int  # 150,
    materialStoryPriority: int  # 1000


class MstSvtCard(BaseModel):
    normalDamage: List[int]  # [4, 9, 14, 19, 23, 31],
    singleDamage: List[int]  # [4, 9, 14, 19, 23, 31],
    trinityDamage: List[int]  # [4, 9, 14, 19, 23, 31],
    unisonDamage: List[int]  # [4, 9, 14, 19, 23, 31],
    grandDamage: List[int]  # [4, 9, 14, 19, 23, 31],
    attackIndividuality: List[int]  # [3000],
    svtId: int  # 5009941050,
    cardId: int  # 5001,
    motion: int  # 50010,
    attackType: int  # 5001


class MstSvtLimit(BaseModel):
    weaponColor: int  # 16777215
    svtId: int  # 9403170
    limitCount: int  # 1
    rarity: int  # 5
    lvMax: int  # 40
    weaponGroup: int  # 104
    weaponScale: int  # 2
    effectFolder: int  # 1
    hpBase: int  # 0
    hpMax: int  # 0
    atkBase: int  # 500
    atkMax: int  # 2000
    criticalWeight: int  # 0
    power: int  # 99
    defense: int  # 99
    agility: int  # 99
    magic: int  # 99
    luck: int  # 99
    treasureDevice: int  # 99
    policy: int  # 0
    personality: int  # 0
    deity: int  # 99
    stepProbability: int  # 1000
    strParam: str  #  "{\"Attack_s1\":285}"


class MstSvtExp(BaseModel):
    type: int  # 20,
    lv: int  # 15,
    exp: int  # 68000,
    curve: int  # 141


class MstCombineLimit(BaseModel):
    itemIds: List[int]  # [7002]
    itemNums: List[int]  # [4]
    id: int  # 202100
    svtLimit: int  # 0
    qp: int  # 50000


class MstCombineSkill(BaseModel):
    itemIds: List[int]  # [6505, 6521]
    itemNums: List[int]  # [16, 3]
    id: int  # 502300
    skillLv: int  # 7
    qp: int  # 5000000


class MstItem(BaseModel):
    individuality: List[int]  # [],
    script: Dict[str, int]  # {},
    eventId: int  # 0,
    eventGroupId: int  # 0,
    id: int  # 6505,
    name: str  # "Void's Dust",
    detail: str  # "\"Skill Up & Ascension Material\"\nDust that disperses when hollow shadows disappear.",
    imageId: int  # 6505,
    bgImageId: int  # 1,
    type: int  # 11,
    unit: str  # "",
    value: int  # 0,
    sellQp: int  # 2500,
    isSell: bool  # true,
    priority: int  # 203,
    dropPriority: int  # 8201,
    startedAt: int  # 946684800,
    endedAt: int  # 1910908800


class Master(BaseModel):
    mstBuff: List[MstBuff]
    mstFunc: List[MstFunc]
    mstSkill: List[MstSkill]
    mstSkillDetail: List[MstSkillDetail]
    mstSkillLv: List[MstSkillLv]
    mstItem: List[MstItem]
    mstSvt: List[MstSvt]
    mstSvtCard: List[MstSvtCard]
    mstSvtSkill: List[MstSvtSkill]
    mstSvtLimit: List[MstSvtLimit]
    mstSvtExp: List[MstSvtExp]
    mstSvtTreasureDevice: List[MstSvtTreasureDevice]
    mstCombineSkill: List[MstCombineSkill]
    mstCombineLimit: List[MstCombineLimit]
    mstTreasureDevice: List[MstTreasureDevice]
    mstTreasureDeviceDetail: List[MstTreasureDeviceDetail]
    mstTreasureDeviceLv: List[MstTreasureDeviceLv]
    mstSvtId: Dict[int, MstSvt]
    mstBuffId: Dict[int, MstBuff]
    mstFuncId: Dict[int, MstFunc]
    mstSkillId: Dict[int, MstSkill]
    mstItemId: Dict[int, MstItem]
    mstTreasureDeviceId: Dict[int, MstTreasureDevice]
    mstSvtServantCollectionNo: Dict[int, int]
    mstSvtServantName: Dict[str, int]
    mstSvtEquipCollectionNo: Dict[int, int]
    mstSkillDetailId: Dict[int, List[MstSkillDetail]]
    mstSvtSkillId: Dict[int, List[MstSvtSkill]]
    mstSkillLvId: Dict[int, List[MstSkillLv]]
    mstTreasureDeviceDetailId: Dict[int, List[MstTreasureDeviceDetail]]
    mstSvtTreasureDeviceId: Dict[int, List[MstSvtTreasureDevice]]
    mstTreasureDeviceLvId: Dict[int, List[MstTreasureDeviceLv]]
    mstCombineSkillId: Dict[int, List[MstCombineSkill]]
    mstCombineLimitId: Dict[int, List[MstCombineLimit]]
    mstSvtCardId: Dict[int, List[MstSvtCard]]
    mstSvtLimitId: Dict[int, List[MstSvtLimit]]
    mstSvtExpId: Dict[int, Dict[int, MstSvtExp]]


class ServantEntity(BaseModel):
    mstSvt: MstSvt
    mstSkill: List[SkillEntityNoReverse] = []
    mstTreasureDevice: List[TdEntityNoReverse] = []
    mstSvtCard: List[MstSvtCard]
    mstSvtLimit: List[MstSvtLimit]
    mstCombineSkill: List[MstCombineSkill]
    mstCombineLimit: List[MstCombineLimit]


class SkillEntity(SkillEntityNoReverse):
    reverseServants: List[ServantEntity] = []


class TdEntity(TdEntityNoReverse):
    reverseServants: List[ServantEntity] = []


class FunctionEntity(FunctionEntityNoReverse):
    reverseSkills: List[SkillEntity] = []
    reverseTds: List[TdEntity] = []


class BuffEntity(BuffEntityNoReverse):
    reverseFunctions: List[FunctionEntity] = []


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
