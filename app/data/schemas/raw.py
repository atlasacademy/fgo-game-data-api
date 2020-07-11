from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from ..enums import SvtType
from .base import BaseModelORJson


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


class BuffEntityNoReverse(BaseModelORJson):
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


class FunctionEntityNoReverse(BaseModelORJson):
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


class SkillEntityNoReverse(BaseModelORJson):
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


class TdEntityNoReverse(BaseModelORJson):
    mstTreasureDevice: MstTreasureDevice
    mstTreasureDeviceDetail: List[MstTreasureDeviceDetail]
    mstSvtTreasureDevice: List[MstSvtTreasureDevice]
    mstTreasureDeviceLv: List[MstTreasureDeviceLv]


def is_servant(svt_type: int) -> bool:
    return svt_type in {
        SvtType.NORMAL,
        SvtType.HEROINE,
        SvtType.ENEMY_COLLECTION_DETAIL,
    }


def is_equip(svt_type: int) -> bool:
    return svt_type == SvtType.SERVANT_EQUIP


class MstSvt(BaseModelORJson):
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

    def isServant(self) -> bool:
        return is_servant(self.type)

    def isEquip(self) -> bool:
        return is_equip(self.type)


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


class MstSvtComment(BaseModel):
    condValues: Optional[List[int]]  # [1]
    svtId: int  # 1000100
    id: int  # 2
    priority: int  # 0
    condMessage: str  # ""
    comment: str  # ""
    condType: int  # 9
    condValue2: int  # 0


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


class MstEquip(BaseModel):
    id: int  # 20
    name: str  # "Mystic Code: Chaldea Combat Uniform"
    detail: str  # "Created by the tech team at the Chaldea Security Organization"
    condUserLv: int  # 1
    maxLv: int  # 10
    maleImageId: int  # 21
    femaleImageId: int  # 22
    imageId: int  # 20
    maleSpellId: int  # 1
    femaleSpellId: int  # 2


class MstEquipExp(BaseModel):
    equipId: int  # 160
    lv: int  # 5
    exp: int  # 1218000
    skillLv1: int  # 5
    skillLv2: int  # 5
    skillLv3: int  # 5


class MstEquipSkill(BaseModel):
    equipId: int  # 1
    num: int  # 1
    skillId: int  # 980001
    condLv: int  # 0


class MstCommandCode(BaseModel):
    id: int  # 8400110
    collectionNo: int  # 11
    name: str  # "Lucky Beast"
    ruby: str  # "Lucky Beast"
    rarity: int  # 3
    sellQp: int  # 500
    sellMana: int  # 1
    sellRarePri: int  # 0


class MstCommandCodeSkill(BaseModel):
    commandCodeId: int  # 8400080
    num: int  # 1
    priority: int  # 1
    skillId: int  # 991380
    startedAt: int  # 946684800
    endedAt: int  # 1893456000


class MstCommandCodeComment(BaseModel):
    commandCodeId: int  # 8400040
    comment: str
    illustratorId: int  # 81


class MstItem(BaseModel):
    individuality: List[int]  # [],
    script: Dict[str, Union[int, str]]  # {},
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


class ItemEntity(BaseModel):
    mstItem: MstItem


class MstSvtLimitAdd(BaseModel):
    individuality: List[int]  # [],
    script: Dict[str, Union[int, str]]  # {},
    svtId: int  # 102900,
    limitCount: int  # 11,
    battleCharaId: int  # 102930,
    fileConvertLimitCount: int  # 0,
    battleCharaLimitCount: int  # 2,
    battleCharaOffsetX: int  # 0,
    battleCharaOffsetY: int  # 0,
    svtVoiceId: int  # 102900,
    voicePrefix: int  # 11


class MstFriendship(BaseModel):
    itemIds: List[int] = []  # [1000]
    itemNums: List[int] = []  # [1]
    id: int  # 1001
    rank: int  # 12
    friendship: int  # 4700000
    qp: int = -1  # 12000000


class MstQuest(BaseModel):
    afterActionVals: List[str]  # []
    id: int  # 94024618
    name: str  # "Automata Hunt - Pride Rank"
    nameRuby: str  # ""
    type: int  # 5
    consumeType: int  # 1
    actConsume: int  # 40
    chaldeaGateCategory: int  # 1
    spotId: int  # 999999
    giftId: int  # 304
    priority: int  # 802482
    bannerType: int  # 0
    bannerId: int  # 94003603
    iconId: int  # 94024608
    charaIconId: int  # 0
    giftIconId: int  # 0
    forceOperation: int  # 0
    afterClear: int  # 3
    displayHours: int  # 0
    intervalHours: int  # 0
    chapterId: int  # 0
    chapterSubId: int  # 0
    chapterSubStr: str  # ""
    recommendLv: str  # "90"
    hasStartAction: int  # 1
    flag: int  # 0
    scriptQuestId: int  # 0
    noticeAt: int  # 1590984000
    openedAt: int  # 1590984000
    closedAt: int  # 1591156799


class MstQuestPhase(BaseModel):
    classIds: List[int]  # [7],
    individuality: List[int]  # [2038, 2039, 94000046],
    script: Dict[str, Any]  # {"resultBgmId": 61},
    questId: int  # 94004502,
    phase: int  # 1,
    isNpcOnly: bool  # true,
    battleBgId: int  # 13400,
    battleBgType: int  # 0,
    qp: int  # 1900,
    playerExp: int  # 550,
    friendshipExp: int  # 165


class MysticCodeEntity(BaseModelORJson):
    mstEquip: MstEquip
    mstSkill: List[SkillEntityNoReverse]
    mstEquipExp: List[MstEquipExp]


class Master(BaseModel):
    mstBuff: List[MstBuff]
    mstFunc: List[MstFunc]
    # mstSkill: List[MstSkill]
    # mstSkillDetail: List[MstSkillDetail]
    mstSkillLv: List[MstSkillLv]
    # mstItem: List[MstItem]
    mstSvt: List[MstSvt]
    # mstSvtCard: List[MstSvtCard]
    mstSvtSkill: List[MstSvtSkill]
    # mstSvtLimit: List[MstSvtLimit]
    # mstSvtExp: List[MstSvtExp]
    # mstFriendship: List[MstFriendship]
    mstSvtTreasureDevice: List[MstSvtTreasureDevice]
    # mstSvtLimitAdd: List[MstSvtLimitAdd]
    # mstCombineSkill: List[MstCombineSkill]
    # mstCombineLimit: List[MstCombineLimit]
    # mstTreasureDevice: List[MstTreasureDevice]
    # mstTreasureDeviceDetail: List[MstTreasureDeviceDetail]
    mstTreasureDeviceLv: List[MstTreasureDeviceLv]
    mstSvtId: Dict[int, MstSvt]
    mstBuffId: Dict[int, MstBuff]
    mstFuncId: Dict[int, MstFunc]
    mstSkillId: Dict[int, MstSkill]
    mstItemId: Dict[int, MstItem]
    mstTreasureDeviceId: Dict[int, MstTreasureDevice]
    mstSvtServantCollectionNo: Dict[int, int]
    # mstSvtServantName: Dict[str, int]
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
    mstSvtLimitAddId: Dict[int, List[MstSvtLimitAdd]]
    mstSvtExpId: Dict[int, List[int]]
    mstFriendshipId: Dict[int, List[int]]
    # mstEquip: List[MstEquip]
    mstEquipId: Dict[int, MstEquip]
    mstEquipExp: List[MstEquipExp]
    mstEquipSkill: List[MstEquipSkill]
    # mstQuest: List[MstQuest]
    mstQuestId: Dict[int, MstQuest]
    # mstQuestPhase: List[MstQuestPhase]
    mstQuestPhaseId: Dict[int, Dict[int, MstQuestPhase]]
    # mstSvtComment: List[MstSvtComment]
    mstSvtCommentId: Dict[int, List[MstSvtComment]]
    # mstCommandCode: List[MstCommandCode]
    mstCommandCodeId: Dict[int, MstCommandCode]
    mstCommandCodeSkill: List[MstCommandCodeSkill]
    mstCommandCodeComment: List[MstCommandCodeComment]


class ServantEntity(BaseModelORJson):
    mstSvt: MstSvt
    mstSkill: List[SkillEntityNoReverse]
    mstTreasureDevice: List[TdEntityNoReverse]
    mstSvtCard: List[MstSvtCard]
    mstSvtLimit: List[MstSvtLimit]
    mstCombineSkill: List[MstCombineSkill]
    mstCombineLimit: List[MstCombineLimit]
    mstSvtLimitAdd: List[MstSvtLimitAdd]
    mstSvtComment: List[MstSvtComment] = []


class SkillEntity(SkillEntityNoReverse):
    reverseServants: List[ServantEntity] = []
    reverseMC: List[MysticCodeEntity] = []


class TdEntity(TdEntityNoReverse):
    reverseServants: List[ServantEntity] = []


class FunctionEntity(FunctionEntityNoReverse):
    reverseSkills: List[SkillEntity] = []
    reverseTds: List[TdEntity] = []


class BuffEntity(BuffEntityNoReverse):
    reverseFunctions: List[FunctionEntity] = []


class CommandCodeEntity(BaseModelORJson):
    mstCommandCode: MstCommandCode
    mstSkill: List[SkillEntityNoReverse]
    mstCommandCodeComment: MstCommandCodeComment


class QuestPhaseEntity(BaseModelORJson):
    mstQuest: MstQuest
    mstQuestPhase: MstQuestPhase
