from decimal import Decimal
from typing import Any, Optional

from pydantic import Field

from .base import BaseModelORJson
from .common import NiceCostume, NiceValentineScript, StageLink
from .enums import SERVANT_TYPES, AiType
from .gameenums import SvtType


class MstConstant(BaseModelORJson):
    name: str  # "IS_IOS_EXAMINATION"
    value: int  # 0
    createdAt: int = 0  # 946652400


class MstCommonRelease(BaseModelORJson):
    id: int
    priority: int
    condGroup: int
    condType: int
    condId: int
    condNum: int


class MstBuff(BaseModelORJson):
    vals: list[int]  # [3004],
    tvals: list[int]  # [5000, 4001],
    ckSelfIndv: list[int]  # [4001],
    ckOpIndv: list[int]  # [2005],
    script: dict[str, Any]  # {"HP_LOWER": 600, "motionName": "MOTION_2101"}
    id: int  # 101,
    buffGroup: int  # 0,
    type: int  # 52,
    name: str  # "Arts Up",
    detail: str  # "Increase Arts Card effectiveness",
    iconId: int  # 313,
    maxRate: int  # 5000


class BuffEntityNoReverse(BaseModelORJson):
    mstBuff: MstBuff


class MstFunc(BaseModelORJson):
    vals: list[int]  # [208],
    expandedVals: list[BuffEntityNoReverse] = []
    tvals: list[int]  # [106],
    questTvals: list[int]  # [94000015],
    effectList: list[int]  # [332],
    popupTextColor: int  # 2,
    id: int  # 657,
    cond: int = 0  # 0,
    funcType: int  # 16,
    targetType: int  # 0,
    applyTarget: int  # 3,
    popupIconId: int  # 302,
    popupText: str  # "STR Up\nvs. Lancer"


class MstFuncGroup(BaseModelORJson):
    funcId: int  # 97
    eventId: int  # 80044
    baseFuncId: int  # 0
    nameTotal: str  # "{1}\nTotal Bond Bonus"
    name: str  # "Increase Bond gained"
    iconId: int  # 1009
    priority: int  # 1
    isDispValue: bool  # true


class FunctionEntityNoReverse(BaseModelORJson):
    mstFunc: MstFunc
    mstFuncGroup: list[MstFuncGroup]


class MstSkill(BaseModelORJson):
    effectList: list[int]  # [323],
    actIndividuality: list[int]  # [401900],
    script: dict[str, Any]
    id: int  # 263350,
    type: int  # 1,
    name: str  # "Projection C",
    ruby: str  # "Projection",
    maxLv: int  # 10,
    iconId: int  # 317,
    motion: int  # 101


class MstSkillDetail(BaseModelORJson):
    id: int  # 429650,
    detail: str  # "Increase your Critical Strength",
    detailShort: str  # "Increase your Critical Strength"


class MstSvtSkill(BaseModelORJson):
    script: Optional[dict[str, Any]] = None
    strengthStatus: int  # 1,
    svtId: int  # 9400920,
    num: int  # 1,
    priority: int  # 1,
    skillId: int  # 990183,
    condQuestId: int  # 0,
    condQuestPhase: int  # 0,
    condLv: int = 0  # 0,
    condLimitCount: int  # 0,
    eventId: int  # 0,
    flag: int  # 0


class MstSvtPassiveSkill(BaseModelORJson):
    svtId: int
    num: int
    priority: int
    skillId: int
    condQuestId: int
    condQuestPhase: int
    condLv: int = 0
    condLimitCount: int = 0
    condFriendshipRank: int
    eventId: int
    flag: int = 0
    commonReleaseId: Optional[int] = None
    startedAt: int
    endedAt: int


class SkillLvScript(BaseModelORJson):
    HP_PER_LOWER: Optional[int] = None
    HP_VAL_HIGHER: Optional[int] = None
    NP_HIGHER: Optional[int] = None
    PlayVoiceNo: Optional[str] = None
    PlayVoiceWait: Optional[int] = None
    STAR_HIGHER: Optional[int] = None
    VoiceAssetName: Optional[str] = None
    aress: Optional[int] = None
    down: Optional[int] = None
    followerVals: Optional[list[str]] = None
    revivalUnder: Optional[int] = None
    revivalUp: Optional[int] = None
    up: Optional[int] = None


class MstSkillLv(BaseModelORJson):
    funcId: list[int]  # [366, 216, 434],
    expandedFuncId: Optional[list[FunctionEntityNoReverse]] = None
    svals: list[str]  # ["[1000,1,-1,3600]", "[1000,1,-1,200]", "[1000]"],
    # script: SkillLvScript
    # Doesn't use the SkillLvScript model so it's easier to build the nice script object
    script: dict[str, Any]
    skillId: int  # 440450,
    lv: int  # 4,
    chargeTurn: int  # 7,
    skillDetailId: int  # 440450,
    priority: int  # 0


class MstSkillAdd(BaseModelORJson):
    skillId: int
    priority: int
    commonReleaseId: int
    name: str
    ruby: str


class SkillEntityNoReverse(BaseModelORJson):
    mstSkill: MstSkill
    mstSkillDetail: list[MstSkillDetail]
    mstSvtSkill: list[MstSvtSkill]
    mstSkillAdd: list[MstSkillAdd]
    mstCommonRelease: list[MstCommonRelease]
    mstSkillLv: list[MstSkillLv]
    aiIds: Optional[dict[AiType, list[int]]] = None


class MstSvtAppendPassiveSkill(BaseModelORJson):
    svtId: int
    num: int
    priority: int
    skillId: int


class MstSvtAppendPassiveSkillUnlock(BaseModelORJson):
    svtId: int
    num: int
    itemIds: list[int]
    itemNums: list[int]


class MstCombineAppendPassiveSkill(BaseModelORJson):
    svtId: int
    num: int
    skillLv: int
    qp: int
    itemIds: list[int]
    itemNums: list[int]


class MstSvtCoin(BaseModelORJson):
    svtId: int
    summonNum: int
    itemId: int


class MstSvtAdd(BaseModelORJson):
    svtId: int
    script: dict[str, Any]


# Dummy ID that is used when enemy servant does an extra attack instead of NP
EXTRA_ATTACK_TD_ID = 100


class MstTreasureDevice(BaseModelORJson):
    individuality: list[int]  # [3000, 4001, 4007],
    script: dict[str, Any]  # {"limitSeqId_12": 800140, "randomWeights_3": [50, 50]},
    id: int  # 500801,
    seqId: int  # 500800,
    name: str  # "Garden of Avalon",
    ruby: str  # " ",
    rank: str  # "C",
    maxLv: int  # 5,
    typeText: str  # "Anti-Personnel",
    attackAttri: int  # 1
    effectFlag: int


class MstTreasureDeviceDetail(BaseModelORJson):
    id: int  # 100101,
    detail: str  # "Deal heavy damage to all enemies [{0}] + restore your NP Gauge <effect increases with Overcharge>",
    detailShort: str  # "Deal heavy damage to all enemies [{0}] + restore your NP Gauge <effect increases with Overcharge>"


class MstSvtTreasureDevice(BaseModelORJson):
    damage: list[int]  # [5, 11, 17, 11, 23, 33],
    strengthStatus: int  # 1,
    svtId: int  # 400900,
    num: int  # 1,
    priority: int  # 101,
    flag: int  # 0,
    imageIndex: int  # 0,
    treasureDeviceId: int  # 400901,
    condQuestId: int  # 0,
    condQuestPhase: int  # 0,
    condLv: int = 0  # 0,
    condFriendshipRank: int = 0  # 0,
    motion: int  # 50,
    cardId: int  # 3


class MstTreasureDeviceLv(BaseModelORJson):
    funcId: list[int]  # [13, 174, 432],
    expandedFuncId: Optional[list[FunctionEntityNoReverse]] = None
    svals: list[str]  # ["[1000,6000]", "[1000,3,-1,100]", "[5000,3,-1]"],
    svals2: list[str]  # ["[1000,6000]", "[1000,3,-1,150]", "[5000,3,-1]"],
    svals3: list[str]  # ["[1000,6000]", "[1000,3,-1,200]", "[5000,3,-1]"],
    svals4: list[str]  # ["[1000,6000]", "[1000,3,-1,250]", "[5000,3,-1]"],
    svals5: list[str]  # ["[1000,6000]", "[1000,3,-1,300]", "[5000,3,-1]"],
    treaureDeviceId: int  # 301102,
    lv: int  # 1,
    script: Optional[dict[str, Any]] = None
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
    mstTreasureDeviceDetail: list[MstTreasureDeviceDetail]
    mstSvtTreasureDevice: list[MstSvtTreasureDevice]
    mstTreasureDeviceLv: list[MstTreasureDeviceLv]


class MstSvt(BaseModelORJson):
    relateQuestIds: list[int]  # [91500701, 94004103, 94014414],
    individuality: list[int]  # [5000, 500800],
    classPassive: list[int]  # [83350, 80350, 320650],
    expandedClassPassive: list[SkillEntityNoReverse] = []
    cardIds: list[int]  # [3, 1, 1, 1, 2],
    script: dict[str, Any]  # { "cameraActionId: 80 },
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
    flag: int

    def isServant(self) -> bool:
        return self.type in SERVANT_TYPES

    def isEquip(self) -> bool:
        return self.type == SvtType.SERVANT_EQUIP


class MstSvtIndividuality(BaseModelORJson):
    individuality: list[int]
    svtId: int
    idx: int
    limitCount: int
    condType: Optional[int] = None
    condId: Optional[int] = None
    condNum: Optional[int] = None
    startedAt: Optional[int] = None
    eventId: Optional[int] = None
    endedAt: Optional[int] = None


class MstSvtExtra(BaseModelORJson):
    svtId: int
    zeroLimitOverwriteName: Optional[str] = None
    bondEquip: int
    bondEquipOwner: Optional[int] = None
    valentineEquip: list[int]
    valentineScript: list[NiceValentineScript]
    valentineEquipOwner: Optional[int] = None
    costumeLimitSvtIdMap: dict[int, NiceCostume] = {}  # Map<costume limit, NiceCostume>


class MstSvtCard(BaseModelORJson):
    normalDamage: list[int]  # [4, 9, 14, 19, 23, 31],
    singleDamage: list[int]  # [4, 9, 14, 19, 23, 31],
    trinityDamage: list[int]  # [4, 9, 14, 19, 23, 31],
    unisonDamage: list[int]  # [4, 9, 14, 19, 23, 31],
    grandDamage: list[int]  # [4, 9, 14, 19, 23, 31],
    attackIndividuality: list[int]  # [3000],
    svtId: int  # 5009941050,
    cardId: int  # 5001,
    motion: int  # 50010,
    attackType: int  # 5001


class BasicMstSvtLimit(BaseModelORJson):
    rarity: int
    hpMax: int
    atkMax: int


class MstSvtLimit(BaseModelORJson):
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


class MstSvtComment(BaseModelORJson):
    condValues: Optional[list[int]]  # Can be `null` explicitly
    script: Optional[dict[str, Any]] = None
    svtId: int  # 1000100
    id: int  # 2
    priority: int  # 0
    condMessage: str  # ""
    comment: str  # ""
    condType: int  # 9
    condValue2: int  # 0


class MstSvtCommentAdd(BaseModelORJson):
    svtId: int
    id: int
    priority: int
    idx: int
    condType: int
    condValues: list[int]
    condValue2: int


class MstSvtScriptExtendDataCond(BaseModelORJson):
    condType: int
    value: int


class MstSvtScriptExtendData(BaseModelORJson):
    faceSize: Optional[int] = None
    combineResultMultipleForm: Optional[int] = None
    myroomForm: Optional[int] = None
    conds: Optional[list[MstSvtScriptExtendDataCond]] = None


class MstSvtScript(BaseModelORJson):
    extendData: dict[str, Any]
    id: int  # 4037000
    form: int  # 0
    faceX: int  # 376
    faceY: int  # 163
    bgImageId: int = 0  # 0
    scale: Decimal  # 1.0
    offsetX: int  # -4
    offsetY: int  # 102
    offsetXMyroom: int  # 283
    offsetYMyroom: int  # 119
    svtId: Optional[int]
    limitCount: Optional[int]


class MstCv(BaseModelORJson):
    id: int  # 93
    name: str  # "Satoshi Hino"
    comment: str = ""  # ""


class MstIllustrator(BaseModelORJson):
    id: int  # 2
    name: str  # "Takashi Takeuchi"
    comment: str = ""  # ""


class MstSvtExp(BaseModelORJson):
    type: int  # 20,
    lv: int  # 15,
    exp: int  # 68000,
    curve: int  # 141


# The materials here doesn't mean anything, probably leftover from the old days
BAD_COMBINE_SVT_LIMIT = 4


class MstCombineLimit(BaseModelORJson):
    itemIds: list[int]  # [7002]
    itemNums: list[int]  # [4]
    id: int  # 202100
    svtLimit: int  # 0
    qp: int  # 50000


class MstCombineSkill(BaseModelORJson):
    itemIds: list[int]  # [6505, 6521]
    itemNums: list[int]  # [16, 3]
    id: int  # 502300
    skillLv: int  # 7
    qp: int  # 5000000


class MstCombineCostume(BaseModelORJson):
    itemIds: list[int]  # [6512, 6524, 6501, 6506]
    itemNums: list[int]  # [10, 5, 5, 5]
    svtId: int  # 100100
    costumeId: int  # 11
    qp: int  # 3000000


class MstCombineMaterial(BaseModelORJson):
    id: int  # 1
    lv: int  # 1
    value: int  # 3000
    createdAt: int = 0  # 1893423600


class MstEquip(BaseModelORJson):
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


class MstEquipExp(BaseModelORJson):
    equipId: int  # 160
    lv: int  # 5
    exp: int  # 1218000
    skillLv1: int  # 5
    skillLv2: int  # 5
    skillLv3: int  # 5


class MstEquipSkill(BaseModelORJson):
    equipId: int  # 1
    num: int  # 1
    skillId: int  # 980001
    condLv: int = 0  # 0


class MstEquipAdd(BaseModelORJson):
    id: int
    equipId: int
    commonReleaseId: int
    maleImageId: int
    femaleImageId: int


class MstCommandCode(BaseModelORJson):
    id: int  # 8400110
    collectionNo: int  # 11
    name: str  # "Lucky Beast"
    ruby: str  # "Lucky Beast"
    rarity: int  # 3
    sellQp: int  # 500
    sellMana: int  # 1
    sellRarePri: int = 0  # 0


class MstCommandCodeSkill(BaseModelORJson):
    commandCodeId: int  # 8400080
    num: int  # 1
    priority: int  # 1
    skillId: int  # 991380
    startedAt: int  # 946684800
    endedAt: int  # 1893456000


class MstCommandCodeComment(BaseModelORJson):
    commandCodeId: int  # 8400040
    comment: str
    illustratorId: int  # 81


class CommandCodeEntity(BaseModelORJson):
    mstCommandCode: MstCommandCode
    mstSkill: list[SkillEntityNoReverse]
    mstCommandCodeComment: MstCommandCodeComment
    mstIllustrator: Optional[MstIllustrator] = None


class MstGift(BaseModelORJson):
    sort_id: int = 0
    id: int  # 94024900
    type: int  # 6
    objectId: int  # 403000
    priority: int  # 0
    num: int  # 1
    lv: Optional[int]
    limitCount: Optional[int]


class MstGiftAdd(BaseModelORJson):
    priorGiftIconIds: list[int]
    giftId: int
    priority: int | None = None
    condType: int
    targetId: int
    targetNum: int
    priorGiftId: int
    script: str


class MstItemSelect(BaseModelORJson):
    itemId: int
    idx: int
    candidateGiftId: int
    requireNum: int
    detail: str


class MstItem(BaseModelORJson):
    individuality: list[int]  # [],
    script: dict[str, Any]  # {},
    eventId: int = 0  # 0,
    eventGroupId: int = 0  # 0,
    isPresent: bool = False
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
    useSkill: bool = False
    useAppendSkill: bool = False
    useAscension: bool = False
    useCostume: bool = False
    mstItemSelect: list[MstItemSelect] = []
    mstGift: list[MstGift] = []
    mstGiftAdd: list[MstGiftAdd] = []


class MstSetItem(BaseModelORJson):
    id: int
    purchaseType: int
    targetId: int
    setNum: int
    createdAt: int = 0


class ItemEntity(BaseModelORJson):
    mstItem: MstItem


class MstSvtLimitAdd(BaseModelORJson):
    individuality: list[int]  # [],
    script: dict[str, Any]  # {},
    svtId: int  # 102900,
    limitCount: int  # 11,
    battleCharaId: int  # 102930,
    fileConvertLimitCount: int  # 0,
    battleCharaLimitCount: int  # 2,
    battleCharaOffsetX: int  # 0,
    battleCharaOffsetY: int  # 0,
    battleCharaOffsetZ: int
    svtVoiceId: int  # 102900,
    voicePrefix: int  # 11


class MstSvtLimitImage(BaseModelORJson):
    svtId: int
    limitCount: int
    priority: int
    defaultLimitCount: int
    condType: int
    condTargetId: int
    condNum: int


class MstSvtCostume(BaseModelORJson):
    svtId: int  # 702700,
    id: int  # 11,
    groupIndex: int
    name: str  # "簡易霊衣：アマゾネスCEOセット",
    shortName: str  # "アマゾネスCEOセット",
    detail: str  # "霊基接触の影響か、この霊衣で\n戦闘すると言動に謎の変化が見られる",
    itemGetInfo: str  # "クエスト「エピローグ」クリアで開放",
    releaseInfo: str  # "最終再臨かつLv.MAXで開放",
    costumeReleaseDetail: str  # "簡易霊衣「アマゾネスCEOセット」開放権を\n獲得できます。",
    priority: int  # 1,
    flag: int  # 0,
    costumeCollectionNo: int  # 32,
    iconId: Optional[int] = None
    openedAt: int  # 1579683600,
    endedAt: int  # 1893596399
    script: Optional[str] = None


class MstVoice(BaseModelORJson):
    id: str  # "A010",
    priority: int  # 2100,
    svtVoiceType: int  # 8,
    name: str  # "聖晶片受け取り 1",
    nameDefault: str  # "？？？",
    condType: int  # 0,
    condValue: int  # 0,
    voicePlayedValue: int  # 0,
    firstPlayPriority: int  # 0,
    closedType: int  # 1,
    flag: int  # 0


class ScriptJsonInfo(BaseModelORJson):
    id: str  # "0_S010"
    face: int  # 0
    delay: Decimal  # 0.0
    text: Optional[str]  # "I ask of you, are you my Master?"
    form: int = 0  # 0
    changeEffect: int = 0  # 0
    multiFace: Optional[list[int]] = None
    multiForm: Optional[list[int]] = None

    def get_voice_id(self) -> str:
        # Some voice lines have the first info id ending with xxx1 or xxx2 and we want xxx0
        splitted = self.id.split("_")  # TW has lines with odd ids: 御主任務 2021年4月 2
        if len(splitted) >= 2:
            return self.id.split("_")[1][:-1] + "0"
        return self.id


class ScriptJsonCond(BaseModelORJson):
    condType: int  # 1
    value: int  # 0
    eventId: int = 0  # 0


class ScriptJson(BaseModelORJson):
    summonScript: Optional[str]
    overwriteName: Optional[str]
    overwritePriority: Optional[int]
    infos: list[ScriptJsonInfo] = []
    conds: list[ScriptJsonCond] | None = []
    condAddItem: int = 0
    materialOverwriteName: Optional[str] = None


class MstSvtVoice(BaseModelORJson):
    scriptJson: list[ScriptJson]
    scriptJsonAdditory: Optional[list[ScriptJson]]
    id: int
    voicePrefix: int
    type: int


class MstVoicePlayCond(BaseModelORJson):
    svtId: int
    script: dict[str, Any] | None = None
    voicePrefix: int
    voiceId: str
    idx: int
    condGroup: int
    condType: int
    targetId: int
    condValues: list[int]


class MstSvtChange(BaseModelORJson):
    beforeTreasureDeviceIds: list[int]  # [202100]
    afterTreasureDeviceIds: list[int]  # [202101]
    svtId: int  # 202100
    priority: int  # 1
    condType: int  # 36
    condTargetId: int  # 2000306
    condValue: int  # 4
    name: str  # "Archer of Inferno"
    ruby: str  # "Archer of Inferno"
    battleName: str  # "Archer of Inferno"
    svtVoiceId: int  # 202110
    limitCount: int  # 2
    flag: int  # 0
    battleSvtId: int  # 202100


class MstSvtVoiceRelation(BaseModelORJson):
    svtId: int  # 502500
    relationSvtId: int  # 9010002
    ascendOrder: int  # 0


class MstSvtGroup(BaseModelORJson):
    id: int
    svtId: int


class MstSvtMultiPortrait(BaseModelORJson):
    commonPosition: list[int]
    summonPosition: list[int]
    svtId: int
    limitCount: int
    idx: int
    portraitImageId: int
    displayPriority: int


def get_subtitle_svtId(sub_id: str) -> int:
    svt = sub_id.split("_")[0]
    try:
        return int(svt)
    except ValueError:
        return -1


class GlobalNewMstSubtitle(BaseModelORJson):
    id: str
    serif: str

    def get_svtId(self) -> int:
        return get_subtitle_svtId(self.id)


class MstFriendship(BaseModelORJson):
    itemIds: list[int] = []  # [1000]
    itemNums: list[int] = []  # [1]
    id: int  # 1001
    rank: int  # 12
    friendship: int  # 4700000
    qp: int = -1  # 12000000


class MstClassRelationOverwrite(BaseModelORJson):
    id: int  # 100
    atkSide: int  # 1
    atkClass: int  # 2
    defClass: int  # 9
    damageRate: int  # 1300
    type: int  # 0


class MstBgm(BaseModelORJson):
    id: int  # 1
    fileName: str  # "BGM_BATTLE_1"
    name: str  # "集いし英雄\n～BATTLE 1～"
    priority: int  # 1012
    detail: str = ""  # ""
    flag: int  # 0
    shopId: int  # 7000001
    logoId: int  # 1


class MstBgmRelease(BaseModelORJson):
    targetIds: list[int]
    vals: list[int]
    bgmId: int
    id: int
    priority: int
    type: int
    condGroup: int
    closedMessageId: int


class MstShop(BaseModelORJson):
    itemIds: list[int]  # [94025003]
    prices: list[int]  # [20]
    targetIds: list[int]  # [7106]
    script: dict[Any, Any]  # {}
    anotherPayType: Optional[int] = None
    anotherItemIds: Optional[list[int]] = None
    useAnotherPayCommonReleaseId: Optional[int] = None
    freeShopCondId: Optional[int] = None
    freeShopCondMessage: Optional[str] = None
    hideWarningMessageCondId: Optional[int] = None
    freeShopReleaseDate: Optional[int] = None
    id: int  # 80107019
    baseShopId: int  # 80107019
    eventId: int  # 80107
    slot: int  # 1
    flag: int  # 0
    priority: int  # 330
    purchaseType: int  # 1
    setNum: int  # 1
    payType: int  # 6
    shopType: int  # 1
    limitNum: int  # 20
    defaultLv: int  # 0
    defaultLimitCount: int  # 0
    name: str  # "アサシンモニュメント"
    detail: str  # "【霊基再臨素材】へ交換"
    infoMessage: str  # ""
    warningMessage: str  # ""
    imageId: int  # 0
    bgImageId: int  # 80107
    openedAt: int  # 1528880400
    closedAt: int  # 1530676799


class MstShopScript(BaseModelORJson):
    ignoreEventIds: list[int]
    shopId: int
    priority: int
    name: str
    scriptId: str
    frequencyType: int
    eventId: int
    svtId: int
    limitCount: int
    materialFolderId: int


class MstShopRelease(BaseModelORJson):
    condValues: list[int]
    shopId: int
    condType: int
    condNum: int
    priority: int
    isClosedDisp: bool
    closedMessage: str
    closedItemName: str


class MstEventReward(BaseModelORJson):
    eventId: int  # 80305
    groupId: int  # 0
    point: int  # 300000
    type: int  # 1
    giftId: int  # 10084
    bgImageId: int  # 8030502
    presentMessageId: int  # 800410


class MstEventPointGroup(BaseModelORJson):
    eventId: int
    groupId: int
    name: str
    iconId: int


class MstEventPointBuff(BaseModelORJson):
    funcIds: list[int]
    id: int
    eventId: int
    groupId: int = 0
    eventPoint: int
    name: str
    detail: str
    imageId: int
    bgImageId: int
    value: int


class MstMasterMission(BaseModelORJson):
    id: int
    priority: int = 0
    startedAt: int
    endedAt: int
    closedAt: int
    imageId: int = 0
    name: str


class MstEventRewardScene(BaseModelORJson):
    guideImageIds: list[int]
    guideLimitCounts: list[int]
    guideFaceIds: list[int]
    guideDisplayNames: list[str]
    guideWeights: list[int]
    guideUnselectedMax: list[int]
    eventId: int
    slot: int
    groupId: int
    type: int
    tabImageId: int
    imageId: int
    bgId: int
    bgmId: int
    afterBgmId: int
    flag: int


class MstEventVoicePlay(BaseModelORJson):
    voiceIds: list[str]
    confirmVoiceIds: list[str]
    eventId: int
    slot: int
    idx: int
    guideImageId: int
    condType: int
    condValue: int
    startedAt: int
    endedAt: int


class MstEventMission(BaseModelORJson):
    id: int
    flag: int
    type: int
    missionTargetId: int
    dispNo: int
    name: str
    detail: str
    startedAt: int
    endedAt: int
    closedAt: int
    rewardType: int
    giftId: int
    bannerGroup: int
    priority: int
    rewardRarity: int
    notfyPriority: int
    presentMessageId: int


class MstEventMissionCondition(BaseModelORJson):
    missionId: int
    missionProgressType: int
    priority: int
    id: int
    missionTargetId: int
    condGroup: int
    condType: int
    targetIds: list[int]
    targetNum: int
    conditionMessage: str
    closedMessage: str
    flag: int


class MstEventMissionConditionDetail(BaseModelORJson):
    id: int
    missionTargetId: int
    missionCondType: int
    logicType: int
    targetIds: list[int]
    addTargetIds: list[int]
    targetQuestIndividualities: list[int]
    conditionLinkType: int
    targetEventIds: list[int]


class MstEventTower(BaseModelORJson):
    eventId: int
    towerId: int
    name: str
    topFloor: int
    floorLabel: str
    openEffectId: int
    flag: int


class MstEventTowerReward(BaseModelORJson):
    eventId: int
    towerId: int
    floor: int
    giftId: int
    iconId: int = 0
    presentMessageId: int
    boardMessage: str
    boardImageId: int


class MstBoxGacha(BaseModelORJson):
    baseIds: list[int]
    pickupIds: Optional[list[int]]
    talkIds: list[int]
    script: Optional[dict[str, Any]] = None
    id: int
    eventId: int
    slot: int
    guideDisplayName: str
    payType: int
    payTargetId: int
    payValue: int
    detailUrl: str
    priority: int
    flag: int
    presentMessageId: Optional[int]
    changeMaxDrawAtOnceResetNum: Optional[int]
    maxRequiredPresentBoxSpace: Optional[int]


class MstBoxGachaBase(BaseModelORJson):
    id: int
    no: int
    type: int
    targetId: int
    isRare: bool
    iconId: int
    bannerId: int
    priority: int
    maxNum: int
    detail: str


class MstBoxGachaTalk(BaseModelORJson):
    befVoiceIds: list[str]
    aftVoiceIds: list[str]
    id: int
    guideImageId: int
    no: int
    isRare: bool


class MstEventRewardSet(BaseModelORJson):
    rewardSetType: int
    eventId: int
    id: int
    iconId: int
    name: str
    detail: str
    bgImageId: int


class MstTreasureBox(BaseModelORJson):
    id: int
    eventId: int
    slot: int
    idx: int
    iconId: int
    treasureBoxGiftId: int
    maxDrawNumOnce: int
    commonConsumeId: int
    extraGiftId: int


class MstTreasureBoxGift(BaseModelORJson):
    id: int
    idx: int
    giftId: int
    collateralUpperLimit: int


class MstEventDigging(BaseModelORJson):
    eventId: int
    sizeX: int
    sizeY: int
    bgImageId: int
    eventPointItemId: int
    resettableDiggedNum: int
    script: dict[str, Any]


class MstEventDiggingBlock(BaseModelORJson):
    id: int
    eventId: int
    imageId: int
    commonConsumeId: int
    objectId: int
    diggingEventPoint: int
    script: dict[str, Any]
    consumeHintImageIds: list[int]
    consumeHintItemNums: list[int]
    hintEventPoints: list[int]


class MstEventDiggingReward(BaseModelORJson):
    id: int
    eventId: int
    giftId: int
    iconId: int
    rewardSize: int
    script: dict[str, Any]


class MstEventCooltimeReward(BaseModelORJson):
    eventId: int
    spotId: int
    lv: int
    name: str
    commonReleaseId: int
    cooltime: int
    addEventPointRate: int
    giftId: int
    upperLimitGiftNum: int


class MstEventQuestCooltime(BaseModelORJson):
    eventId: int
    questId: int
    phase: int
    cooltime: int
    isEnabledInitial: bool


class MstEventBulletinBoard(BaseModelORJson):
    id: int
    eventId: int
    message: str
    probability: int | None = None


class MstEventBulletinBoardRelease(BaseModelORJson):
    bulletinBoardId: int
    condType: int
    condTargetId: int
    condNum: int
    condGroup: int


class MstCommonConsume(BaseModelORJson):
    id: int
    priority: int
    type: int
    objectId: int
    num: int


class MstEvent(BaseModelORJson):
    script: list[dict[str, str]]  # []
    id: int  # 10083
    baseEventId: int  # 0
    type: int  # 20
    openType: int  # 1
    name: str  # "劇場版「Fate/stay night [Heaven's Feel]」公開記念キャンペーン"
    shortName: str = ""  # ""
    detail: str  # "劇場版「Fate/stay night [Heaven's Feel]」公開記念キャンペーン"
    noticeBannerId: int  # 0
    bannerId: int  # 0
    iconId: int  # 0
    bannerPriority: int  # 0
    openHours: int = 0  # 0
    intervalHours: int = 0  # 0
    noticeAt: int  # 1509116400
    startedAt: int  # 1509116400
    endedAt: int  # 1509721199
    finishedAt: int  # 1509721199
    materialOpenedAt: int  # 1751295600
    linkType: int  # 1
    linkBody: str  # "/summon/detail_summon_1.html"
    deviceType: int = 0  # 0
    myroomBgId: int  # 0
    myroomBgmId: int  # 0
    createdAt: int = 0  # 1435676400
    warIds: list[int] = []


class MstWar(BaseModelORJson):
    coordinates: list[list[Decimal]]
    id: int  # 9046
    age: str  # "-"
    name: str  # "ルルハワ"
    longName: str  # "永久常夏祭壇 ルルハワ"
    bannerId: int  # 9046
    mapImageId: int  # 9046
    mapImageW: int  # 2048
    mapImageH: int  # 2048
    headerImageId: int  # 1000
    priority: int  # 9046
    parentWarId: int  # 0
    materialParentWarId: int = 0  # 0
    flag: int  # 32
    emptyMessage: str  # "クエストがありません"
    bgmId: int  # 8
    scriptId: str  # "NONE"
    startType: int  # 0
    targetId: int  # 0
    eventId: int  # 80112
    eventName: str = ""
    lastQuestId: int  # 0
    assetId: int  # 0


class MstWarAdd(BaseModelORJson):
    script: dict[str, Any]
    warId: int
    type: int
    priority: int
    overwriteId: int
    overwriteStr: str
    condType: int
    targetId: int
    value: int
    startedAt: int
    endedAt: int


class MstMap(BaseModelORJson):
    script: dict[str, Any]
    id: int  # 100
    warId: int  # 100
    mapImageId: int  # 100
    mapImageW: int  # 1920
    mapImageH: int  # 1240
    headerImageId: int  # 5
    bgmId: int  # 7


class MstMapGimmick(BaseModelORJson):
    script: dict[str, Any]
    id: int
    warId: int
    mapId: int
    imageId: int
    x: int
    y: int
    depthOffset: int
    scale: int
    dispCondType: int
    dispTargetId: int
    dispTargetValue: int
    dispCondType2: int
    dispTargetId2: int
    dispTargetValue2: int
    actionAnimTime: int
    actionEffectId: int
    startedAt: int
    endedAt: int


class MstSpot(BaseModelORJson):
    joinSpotIds: list[int] = []  # []
    id: int  # 10001
    warId: int  # 100
    mapId: int  # 100
    name: str  # "未確認座標Ｘ－Ａ"
    imageId: int  # 10001
    x: int  # 678
    y: int  # 400
    imageOfsX: int  # 0
    imageOfsY: int  # 0
    nameOfsX: int  # 0
    nameOfsY: int  # 0
    questOfsX: int  # 38
    questOfsY: int  # -62
    nextOfsX: int = 0  # 0
    nextOfsY: int  # 0
    dispCondType1: int  # 1
    dispTargetId1: int  # 0
    dispTargetValue1: int  # 0
    dispCondType2: int  # 1
    dispTargetId2: int  # 0
    dispTargetValue2: int  # 0
    activeCondType: int  # 1
    activeTargetId: int  # 0
    activeTargetValue: int  # 0
    closedMessage: str  # ""
    flag: int  # 0


class MstSpotRoad(BaseModelORJson):
    id: int
    warId: int
    mapId: int
    srcSpotId: int
    dstSpotId: int
    type: int
    imageId: int
    dispCondType: int
    dispTargetId: int
    dispTargetValue: int
    dispCondType2: int
    dispTargetId2: int
    dispTargetValue2: int
    activeCondType: int
    activeTargetId: int
    activeTargetValue: int


class MstQuest(BaseModelORJson):
    beforeActionVals: list[str]
    afterActionVals: list[str]  # []
    id: int  # 94024618
    name: str  # "Automata Hunt - Pride Rank"
    nameRuby: str = ""  # ""
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
    forceOperation: int = 0  # 0
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


class MstQuestWithWar(MstQuest):
    warId: int
    warLongName: str
    spotName: str


class MstQuestWithPhase(MstQuestWithWar):
    classIds: list[int]  # [7],
    individuality: list[int]  # [2038, 2039, 94000046],
    script: dict[str, Any]  # {"resultBgmId": 61},
    questId: int  # 94004502,
    phase: int  # 1,
    isNpcOnly: bool  # true,
    battleBgId: int  # 13400,
    battleBgType: int  # 0,
    qp: int  # 1900,
    playerExp: int  # 550,
    friendshipExp: int  # 165
    phaseGiftId: Optional[int] = None


class MstQuestRelease(BaseModelORJson):
    questId: int  # 94026514
    type: int  # 7
    targetId: int  # 100100
    value: int  # 4
    openLimit: int = 0  # 0
    closedMessageId: int  # 2
    imagePriority: int  # 3000


class MstQuestConsumeItem(BaseModelORJson):
    itemIds: list[int]  # [94032205, 94032206]
    nums: list[int]  # [160, 220]
    questId: int  # 94032410


class MstClosedMessage(BaseModelORJson):
    id: int
    message: str


class MstQuestPhase(BaseModelORJson):
    classIds: list[int]  # [7],
    individuality: list[int]  # [2038, 2039, 94000046],
    script: dict[str, Any]  # {"resultBgmId": 61},
    questSelect: list[int] | None = None
    questId: int  # 94004502,
    phase: int  # 1,
    isNpcOnly: bool  # true,
    battleBgId: int  # 13400,
    battleBgType: int  # 0,
    qp: int  # 1900,
    playerExp: int  # 550,
    friendshipExp: int  # 165
    giftId: int = 0
    encountSvtIds: Optional[list[int]]


class MstQuestPhaseDetail(BaseModelORJson):
    beforeActionVals: list[str]
    afterActionVals: list[str]
    boardMessage: dict[str, Any]
    questId: int
    phase: int
    spotId: int
    consumeType: int
    actConsume: int
    flag: int
    recommendLv: Optional[str] = None


class MstQuestMessage(BaseModelORJson):
    questId: int
    phase: int
    idx: int
    message: str
    condType: int
    targetId: int
    targetNum: int
    frequencyType: int
    displayType: int


class MstStage(BaseModelORJson):
    npcDeckIds: list[int]  # [2, 1000]
    script: dict[str, Any]  # {}
    questId: int  # 1000000
    questPhase: int  # 1
    wave: int  # 1
    enemyInfo: int  # 1
    bgmId: int  # 1
    startEffectId: int  # 1


class MstStageRemap(BaseModelORJson):
    questId: int
    questPhase: int
    wave: int
    remapQuestId: int
    remapPhase: int
    remapWave: int


class NpcFollower(BaseModelORJson):
    id: int
    questId: int
    questPhase: int
    priority: int
    leaderSvtId: int
    svtEquipIds: list[int]
    flag: int
    npcScript: str
    openedAt: int = 0
    closedAt: int = 0
    createdAt: int = 0


class NpcFollowerRelease(BaseModelORJson):
    id: int
    questId: int
    questPhase: int
    condType: int
    condTargetId: int
    condValue: int = 0
    createdAt: int = 0


class NpcSvtFollower(BaseModelORJson):
    appendPassiveSkillIds: Optional[list[int]] = None
    appendPassiveSkillLvs: Optional[list[int]] = None
    id: int
    svtId: int
    name: str
    lv: int
    limitCount: int
    hp: int
    atk: int
    individuality: str
    treasureDeviceId: int
    treasureDeviceLv: int
    skillId1: int
    skillId2: int
    skillId3: int
    skillLv1: int
    skillLv2: int
    skillLv3: int
    passiveSkills: Optional[list[int]]
    flag: int
    createdAt: int = 0


class NpcSvtEquip(BaseModelORJson):
    id: int
    svtId: int
    lv: int
    limitCount: int


class MstAi(BaseModelORJson):
    id: int
    idx: int
    actNum: int
    priority: int
    probability: int
    cond: int
    vals: list[int]
    aiActId: int
    avals: list[int]
    infoText: str
    timing: Optional[int] = None  # only in mstAiField
    script: dict[str, Any] | None = None


class MstAiAct(BaseModelORJson):
    targetIndividuality: list[int]  # [0]
    skillVals: list[int]  # [961075, 1]
    id: int  # 94016184
    type: int  # 40
    target: int  # 0
    createdAt: int = 0  # 946652400


class MysticCodeEntity(BaseModelORJson):
    mstEquip: MstEquip
    mstSkill: list[SkillEntityNoReverse]
    mstEquipExp: list[MstEquipExp]
    mstEquipAdd: list[MstEquipAdd]
    mstCommonRelease: list[MstCommonRelease]


class Master(BaseModelORJson):
    skillToAiAct: dict[int, set[int]]
    aiActToAiSvt: dict[int, set[int]]
    aiActToAiField: dict[int, set[int]]


class ServantEntity(BaseModelORJson):
    mstSvt: MstSvt
    mstSkill: list[SkillEntityNoReverse]
    mstTreasureDevice: list[TdEntityNoReverse]
    mstSvtIndividuality: list[MstSvtIndividuality]
    mstSvtCard: list[MstSvtCard]
    mstSvtLimit: list[MstSvtLimit]
    mstCombineSkill: list[MstCombineSkill]
    mstCombineLimit: list[MstCombineLimit]
    mstCombineCostume: list[MstCombineCostume]
    mstCombineMaterial: list[MstCombineMaterial]
    mstSvtLimitAdd: list[MstSvtLimitAdd]
    mstSvtLimitImage: list[MstSvtLimitImage]
    mstSvtChange: list[MstSvtChange]
    mstSvtCostume: list[MstSvtCostume]
    mstSvtScript: list[MstSvtScript]
    mstSvtAdd: Optional[MstSvtAdd] = None
    mstSvtPassiveSkill: list[MstSvtPassiveSkill]
    expandedExtraPassive: list[SkillEntityNoReverse] = []
    mstSvtAppendPassiveSkill: list[MstSvtAppendPassiveSkill]
    expandedAppendPassive: list[SkillEntityNoReverse] = []
    mstSvtAppendPassiveSkillUnlock: list[MstSvtAppendPassiveSkillUnlock]
    mstCombineAppendPassiveSkill: list[MstCombineAppendPassiveSkill]
    mstItem: list[MstItem]
    mstCommonRelease: list[MstCommonRelease]
    mstSvtCoin: Optional[MstSvtCoin] = None
    mstCv: Optional[MstCv] = None
    mstIllustrator: Optional[MstIllustrator] = None
    mstSvtExp: list[MstSvtExp] = []
    mstFriendship: list[MstFriendship] = []
    mstSvtExtra: Optional[MstSvtExtra] = None
    mstSvtComment: list[MstSvtComment] = []
    mstSvtCommentAdd: list[MstSvtCommentAdd] = []
    mstSvtVoice: list[MstSvtVoice] = []
    mstSvtMultiPortrait: list[MstSvtMultiPortrait] = []
    mstVoice: list[MstVoice] = []
    mstSvtGroup: list[MstSvtGroup] = []
    mstSubtitle: list[GlobalNewMstSubtitle] = []
    mstVoicePlayCond: list[MstVoicePlayCond] = []


class ReversedSkillTd(BaseModelORJson):
    servant: list[ServantEntity] = []
    MC: list[MysticCodeEntity] = []
    CC: list[CommandCodeEntity] = []


class ReversedSkillTdType(BaseModelORJson):
    raw: Optional[ReversedSkillTd] = None


class SkillEntity(SkillEntityNoReverse):
    reverse: Optional[ReversedSkillTdType] = None


class TdEntity(TdEntityNoReverse):
    reverse: Optional[ReversedSkillTdType] = None


class ReversedFunction(BaseModelORJson):
    skill: list[SkillEntity] = []
    NP: list[TdEntity] = []


class ReversedFunctionType(BaseModelORJson):
    raw: Optional[ReversedFunction] = None


class FunctionEntity(FunctionEntityNoReverse):
    reverse: Optional[ReversedFunctionType] = None


class ReversedBuff(BaseModelORJson):
    function: list[FunctionEntity] = []


class ReversedBuffType(BaseModelORJson):
    raw: Optional[ReversedBuff] = None


class BuffEntity(BuffEntityNoReverse):
    reverse: Optional[ReversedBuffType] = None


class ScriptFile(BaseModelORJson):
    scriptFileName: str
    questId: int
    phase: int
    sceneType: int


class ScriptSearchResult(BaseModelORJson):
    scriptId: str
    score: float
    snippets: list[str]


class QuestEntity(BaseModelORJson):
    mstQuest: MstQuest
    mstQuestConsumeItem: list[MstQuestConsumeItem]
    mstQuestRelease: list[MstQuestRelease]
    mstClosedMessage: list[MstClosedMessage]
    mstGift: list[MstGift]
    mstGiftAdd: list[MstGiftAdd]
    phases: list[int]
    phasesWithEnemies: list[int] = []
    phasesNoBattle: list[int] = []
    allScripts: list[ScriptFile]


class QuestPhaseEntity(QuestEntity):
    mstQuestPhase: MstQuestPhase
    mstQuestPhaseDetail: Optional[MstQuestPhaseDetail] = None
    mstQuestMessage: list[MstQuestMessage] = []
    scripts: list[str]
    mstStage: list[MstStage]
    mstBgm: list[MstBgm]
    npcFollower: list[NpcFollower]
    npcFollowerRelease: list[NpcFollowerRelease]
    npcSvtFollower: list[NpcSvtFollower]
    npcSvtEquip: list[NpcSvtEquip]


class ScriptEntity(BaseModelORJson):
    scriptId: str
    scriptSizeBytes: int
    quests: list[QuestEntity]


class BgmEntity(BaseModelORJson):
    mstBgm: MstBgm
    mstBgmRelease: list[MstBgmRelease]
    mstClosedMessage: list[MstClosedMessage]
    mstShop: MstShop | None = None
    mstItem: MstItem | None = None


class EventEntity(BaseModelORJson):
    mstEvent: MstEvent
    mstWar: list[MstWar]
    mstEventRewardScene: list[MstEventRewardScene]
    mstEventVoicePlay: list[MstEventVoicePlay]
    mstGift: list[MstGift]
    mstGiftAdd: list[MstGiftAdd]
    mstShop: list[MstShop]
    mstShopRelease: list[MstShopRelease]
    mstShopScript: list[MstShopScript]
    mstSetItem: list[MstSetItem]
    mstEventReward: list[MstEventReward]
    mstEventRewardSet: list[MstEventRewardSet]
    mstEventPointBuff: list[MstEventPointBuff]
    mstEventPointGroup: list[MstEventPointGroup]
    mstEventMission: list[MstEventMission]
    mstEventMissionCondition: list[MstEventMissionCondition]
    mstEventMissionConditionDetail: list[MstEventMissionConditionDetail]
    mstEventTower: list[MstEventTower]
    mstEventTowerReward: list[MstEventTowerReward]
    mstBoxGacha: list[MstBoxGacha]
    mstBoxGachaBase: list[MstBoxGachaBase]
    mstBoxGachaTalk: list[MstBoxGachaTalk]
    mstTreasureBox: list[MstTreasureBox]
    mstTreasureBoxGift: list[MstTreasureBoxGift]
    mstEventDigging: MstEventDigging | None = None
    mstEventDiggingBlock: list[MstEventDiggingBlock]
    mstEventDiggingReward: list[MstEventDiggingReward]
    mstEventCooltimeReward: list[MstEventCooltimeReward]
    mstEventQuestCooltime: list[MstEventQuestCooltime]
    mstEventBulletinBoard: list[MstEventBulletinBoard]
    mstEventBulletinBoardRelease: list[MstEventBulletinBoardRelease]
    mstItem: list[MstItem]
    mstCommonConsume: list[MstCommonConsume]
    mstCommonRelease: list[MstCommonRelease]
    mstSvtVoice: list[MstSvtVoice]
    mstVoice: list[MstVoice]
    mstSvtGroup: list[MstSvtGroup]
    mstSubtitle: list[GlobalNewMstSubtitle]
    mstVoicePlayCond: list[MstVoicePlayCond]
    mstSvtExtra: list[MstSvtExtra]
    mstBgm: list[BgmEntity]


class WarEntity(BaseModelORJson):
    mstWar: MstWar
    mstEvent: Optional[MstEvent] = None
    mstWarAdd: list[MstWarAdd]
    mstMap: list[MstMap]
    mstBgm: list[MstBgm]
    mstMapGimmick: list[MstMapGimmick]
    mstSpot: list[MstSpot]
    mstQuest: list[QuestEntity]
    mstSpotRoad: list[MstSpotRoad]


class MasterMissionEntity(BaseModelORJson):
    mstMasterMission: MstMasterMission
    mstEventMission: list[MstEventMission]
    mstEventMissionCondition: list[MstEventMissionCondition]
    mstEventMissionConditionDetail: list[MstEventMissionConditionDetail]
    mstGift: list[MstGift]
    mstGiftAdd: list[MstGiftAdd]
    mstQuest: list[MstQuestWithWar]


class AiEntity(BaseModelORJson):
    mstAi: MstAi
    mstAiAct: MstAiAct
    parentAis: dict[AiType, list[int]]


class AiCollection(BaseModelORJson):
    mainAis: list[AiEntity]
    relatedAis: list[AiEntity]
    relatedQuests: list[StageLink]


class AssetStorageLine(BaseModelORJson):
    first: str = Field(
        ...,
        title="First field",
        description="Unused in JP/NA/KR. Download name of the asset in CN/TW.",
    )
    required: str = Field(
        ...,
        title="Whether the asset is required",
        description="SYSTEM=Required DATA0=Not Required. If required, the asset will be downloaded before the title screen.",
    )
    size: int = Field(..., title="Size of the asset in bytes")
    crc32: int = Field(
        ...,
        title="CRC32 of the asset",
        description="CRC32 of the asset as an unsigned 32-bit integer.",
    )
    path: str
    folder: str
    fileName: str
