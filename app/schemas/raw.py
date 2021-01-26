from decimal import Decimal
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel

from .base import BaseModelORJson
from .enums import SvtType


class MstConstant(BaseModelORJson):
    name: str  # "IS_IOS_EXAMINATION"
    value: int  # 0
    createdAt: int  # 946652400


class MstBuff(BaseModel):
    vals: List[int]  # [3004],
    tvals: List[int]  # [5000, 4001],
    ckSelfIndv: List[int]  # [4001],
    ckOpIndv: List[int]  # [2005],
    script: Dict[str, Any]  # {"HP_LOWER": 600, "motionName": "MOTION_2101"}
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


class MstFuncGroup(BaseModel):
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
    mstFuncGroup: List[MstFuncGroup]


class MstSkill(BaseModel):
    effectList: List[int]  # [323],
    actIndividuality: List[int]  # [401900],
    script: Dict[str, Any]
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


class SkillLvScript(BaseModel):
    HP_PER_LOWER: Optional[int] = None
    HP_VAL_HIGHER: Optional[int] = None
    NP_HIGHER: Optional[int] = None
    PlayVoiceNo: Optional[str] = None
    PlayVoiceWait: Optional[int] = None
    STAR_HIGHER: Optional[int] = None
    VoiceAssetName: Optional[str] = None
    aress: Optional[int] = None
    down: Optional[int] = None
    followerVals: Optional[List[str]] = None
    revivalUnder: Optional[int] = None
    revivalUp: Optional[int] = None
    up: Optional[int] = None


class MstSkillLv(BaseModel):
    funcId: List[int]  # [366, 216, 434],
    expandedFuncId: List[FunctionEntityNoReverse] = []
    svals: List[str]  # ["[1000,1,-1,3600]", "[1000,1,-1,200]", "[1000]"],
    # script: SkillLvScript
    # Doesn't use the SkillLvScript model so it's easier to build the nice script object
    script: Dict[str, Any]
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
    script: Dict[str, Any]  # {"limitSeqId_12": 800140, "randomWeights_3": [50, 50]},
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
    script: Dict[str, Any]  # { "cameraActionId: 80 },
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


class MstSvtScriptExtendDataCond(BaseModel):
    condType: int
    value: int


class MstSvtScriptExtendData(BaseModel):
    faceSize: Optional[int] = None
    combineResultMultipleForm: Optional[int] = None
    myroomForm: Optional[int] = None
    conds: Optional[List[MstSvtScriptExtendDataCond]] = None


class MstSvtScript(BaseModel):
    extendData: Dict[str, Any]
    id: int  # 4037000
    form: int  # 0
    faceX: int  # 376
    faceY: int  # 163
    bgImageId: int  # 0
    scale: int  # 1.0
    offsetX: int  # -4
    offsetY: int  # 102
    offsetXMyroom: int  # 283
    offsetYMyroom: int  # 119


class MstCv(BaseModel):
    id: int  # 93
    name: str  # "Satoshi Hino"
    comment: str  # ""


class MstIllustrator(BaseModel):
    id: int  # 2
    name: str  # "Takashi Takeuchi"
    comment: str  # ""


class MstSvtExp(BaseModel):
    type: int  # 20,
    lv: int  # 15,
    exp: int  # 68000,
    curve: int  # 141


# The materials here doesn't mean anything, probably leftover from the old days
BAD_COMBINE_SVT_LIMIT = 4


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


class MstCombineCostume(BaseModel):
    itemIds: List[int]  # [6512, 6524, 6501, 6506]
    itemNums: List[int]  # [10, 5, 5, 5]
    svtId: int  # 100100
    costumeId: int  # 11
    qp: int  # 3000000


class MstCombineMaterial(BaseModel):
    id: int  # 1
    lv: int  # 1
    value: int  # 3000
    createdAt: int  # 1893423600


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


class CommandCodeEntity(BaseModelORJson):
    mstCommandCode: MstCommandCode
    mstSkill: List[SkillEntityNoReverse]
    mstCommandCodeComment: MstCommandCodeComment


class MstItem(BaseModel):
    individuality: List[int]  # [],
    script: Dict[str, Any]  # {},
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


class ItemEntity(BaseModelORJson):
    mstItem: MstItem


class MstSvtLimitAdd(BaseModel):
    individuality: List[int]  # [],
    script: Dict[str, Any]  # {},
    svtId: int  # 102900,
    limitCount: int  # 11,
    battleCharaId: int  # 102930,
    fileConvertLimitCount: int  # 0,
    battleCharaLimitCount: int  # 2,
    battleCharaOffsetX: int  # 0,
    battleCharaOffsetY: int  # 0,
    svtVoiceId: int  # 102900,
    voicePrefix: int  # 11


class MstSvtCostume(BaseModel):
    svtId: int  # 702700,
    id: int  # 11,
    # groupIndex: int  # NA doesn't have this
    name: str  # "簡易霊衣：アマゾネスCEOセット",
    shortName: str  # "アマゾネスCEOセット",
    detail: str  # "霊基接触の影響か、この霊衣で\n戦闘すると言動に謎の変化が見られる",
    itemGetInfo: str  # "クエスト「エピローグ」クリアで開放",
    releaseInfo: str  # "最終再臨かつLv.MAXで開放",
    costumeReleaseDetail: str  # "簡易霊衣「アマゾネスCEOセット」開放権を\n獲得できます。",
    priority: int  # 1,
    flag: int  # 0,
    costumeCollectionNo: int  # 32,
    openedAt: int  # 1579683600,
    endedAt: int  # 1893596399


class MstVoice(BaseModel):
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


class ScriptJsonInfo(BaseModel):
    id: str  # "0_S010"
    face: int  # 0
    delay: Decimal  # 0.0
    text: Optional[str]  # "I ask of you, are you my Master?"
    form: int  # 0
    changeEffect: int = 0  # 0


class ScriptJsonCond(BaseModel):
    condType: int  # 1
    value: int  # 0
    eventId: int  # 0


class ScriptJson(BaseModel):
    overwriteName: Optional[str]
    infos: List[ScriptJsonInfo]
    conds: List[ScriptJsonCond]


class MstSvtVoice(BaseModel):
    scriptJson: List[ScriptJson]
    id: int
    voicePrefix: int
    type: int


class MstSvtChange(BaseModel):
    beforeTreasureDeviceIds: List[int]  # [202100]
    afterTreasureDeviceIds: List[int]  # [202101]
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


class MstSvtVoiceRelation(BaseModel):
    svtId: int  # 502500
    relationSvtId: int  # 9010002
    ascendOrder: int  # 0


class MstSvtGroup(BaseModel):
    id: int
    svtId: int


class GlobalNewMstSubtitle(BaseModel):
    id: str
    serif: str


class MstFriendship(BaseModel):
    itemIds: List[int] = []  # [1000]
    itemNums: List[int] = []  # [1]
    id: int  # 1001
    rank: int  # 12
    friendship: int  # 4700000
    qp: int = -1  # 12000000


class MstClassRelationOverwrite(BaseModel):
    id: int  # 100
    atkSide: int  # 1
    atkClass: int  # 2
    defClass: int  # 9
    damageRate: int  # 1300
    type: int  # 0


class MstGift(BaseModel):
    id: int  # 94024900
    type: int  # 6
    objectId: int  # 403000
    priority: int  # 0
    num: int  # 1


class MstBgm(BaseModel):
    id: int  # 1
    fileName: str  # "BGM_BATTLE_1"
    name: str  # "集いし英雄\n～BATTLE 1～"
    priority: int  # 1012
    detail: str  # ""
    flag: int  # 0
    shopId: int  # 7000001
    logoId: int  # 1


class MstShop(BaseModel):
    itemIds: List[int]  # [94025003]
    prices: List[int]  # [20]
    targetIds: List[int]  # [7106]
    script: Dict[Any, Any]  # {}
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


class MstEvent(BaseModel):
    script: List[Dict[str, str]]  # []
    id: int  # 10083
    baseEventId: int  # 0
    type: int  # 20
    openType: int  # 1
    name: str  # "劇場版「Fate/stay night [Heaven's Feel]」公開記念キャンペーン"
    shortName: str  # ""
    detail: str  # "劇場版「Fate/stay night [Heaven's Feel]」公開記念キャンペーン"
    noticeBannerId: int  # 0
    bannerId: int  # 0
    iconId: int  # 0
    bannerPriority: int  # 0
    openHours: int  # 0
    intervalHours: int  # 0
    noticeAt: int  # 1509116400
    startedAt: int  # 1509116400
    endedAt: int  # 1509721199
    finishedAt: int  # 1509721199
    materialOpenedAt: int  # 1751295600
    linkType: int  # 1
    linkBody: str  # "/summon/detail_summon_1.html"
    deviceType: int  # 0
    myroomBgId: int  # 0
    myroomBgmId: int  # 0
    createdAt: int  # 1435676400


class MstWar(BaseModel):
    coordinates: List[List[int]]
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
    materialParentWarId: int  # 0
    flag: int  # 32
    emptyMessage: str  # "クエストがありません"
    bgmId: int  # 8
    scriptId: str  # "NONE"
    startType: int  # 0
    targetId: int  # 0
    eventId: int  # 80112
    lastQuestId: int  # 0
    assetId: int  # 0


class MstMap(BaseModel):
    script: Dict[str, Any]
    id: int  # 100
    warId: int  # 100
    mapImageId: int  # 100
    mapImageW: int  # 1920
    mapImageH: int  # 1240
    headerImageId: int  # 5
    bgmId: int  # 7


class MstSpot(BaseModel):
    joinSpotIds: List[int]  # []
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
    nextOfsX: int  # 0
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


class MstQuestRelease(BaseModel):
    questId: int  # 94026514
    type: int  # 7
    targetId: int  # 100100
    value: int  # 4
    openLimit: int  # 0
    closedMessageId: int  # 2
    imagePriority: int  # 3000


class MstQuestConsumeItem(BaseModel):
    itemIds: List[int]  # [94032205, 94032206]
    nums: List[int]  # [160, 220]
    questId: int  # 94032410


class MstClosedMessage(BaseModel):
    id: int
    message: str


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
    giftId: Optional[int] = None


class MstStage(BaseModel):
    npcDeckIds: List[int]  # [2, 1000]
    script: Dict[str, Any]  # {}
    questId: int  # 1000000
    questPhase: int  # 1
    wave: int  # 1
    enemyInfo: int  # 1
    bgmId: int  # 1
    startEffectId: int  # 1


class MstAi(BaseModel):
    id: int
    idx: int
    actNum: int
    priority: int
    probability: int
    cond: int
    vals: List[int]
    aiActId: int
    avals: List[int]
    infoText: str
    timing: Optional[int] = None  # only in mstAiField


class MstAiAct(BaseModel):
    targetIndividuality: List[int]  # [0]
    skillVals: List[int]  # [961075, 1]
    id: int  # 94016184
    type: int  # 40
    target: int  # 0
    createdAt: int  # 946652400


class MysticCodeEntity(BaseModelORJson):
    mstEquip: MstEquip
    mstSkill: List[SkillEntityNoReverse]
    mstEquipExp: List[MstEquipExp]


class Master(BaseModel):
    mstConstantId: Dict[str, int]
    mstBuff: List[MstBuff]
    mstFunc: List[MstFunc]
    mstSkill: List[MstSkill]
    # mstSkillDetail: List[MstSkillDetail]
    # mstSkillLv: List[MstSkillLv]
    # mstItem: List[MstItem]
    mstSvt: List[MstSvt]
    # mstSvtCard: List[MstSvtCard]
    # mstSvtSkill: List[MstSvtSkill]
    # mstSvtLimit: List[MstSvtLimit]
    # mstSvtExp: List[MstSvtExp]
    # mstFriendship: List[MstFriendship]
    # mstSvtTreasureDevice: List[MstSvtTreasureDevice]
    # mstSvtLimitAdd: List[MstSvtLimitAdd]
    # mstCombineSkill: List[MstCombineSkill]
    # mstCombineLimit: List[MstCombineLimit]
    mstTreasureDevice: List[MstTreasureDevice]
    # mstTreasureDeviceDetail: List[MstTreasureDeviceDetail]
    # mstTreasureDeviceLv: List[MstTreasureDeviceLv]
    mstSvtId: Dict[int, MstSvt]
    mstBuffId: Dict[int, MstBuff]
    mstFuncId: Dict[int, MstFunc]
    mstFuncGroupId: Dict[int, List[MstFuncGroup]]
    mstSkillId: Dict[int, MstSkill]
    mstItemId: Dict[int, MstItem]
    mstGiftId: Dict[int, List[MstGift]]
    mstShopEventId: Dict[int, List[MstShop]]
    mstTreasureDeviceId: Dict[int, MstTreasureDevice]
    mstSvtServantCollectionNo: Dict[int, int]
    # mstSvtServantName: Dict[str, int]
    mstSvtEquipCollectionNo: Dict[int, int]
    # mstSkillDetailId: Dict[int, List[MstSkillDetail]]
    mstSvtSkillId: Dict[int, List[MstSvtSkill]]
    # mstSvtSkillSvtId: Dict[int, List[MstSvtSkill]]
    mstSkillLvId: Dict[int, List[MstSkillLv]]
    mstTreasureDeviceDetailId: Dict[int, List[MstTreasureDeviceDetail]]
    mstSvtTreasureDeviceId: Dict[int, List[MstSvtTreasureDevice]]
    mstSvtTreasureDeviceSvtId: Dict[int, List[MstSvtTreasureDevice]]
    mstTreasureDeviceLvId: Dict[int, List[MstTreasureDeviceLv]]
    mstCombineSkillId: Dict[int, List[MstCombineSkill]]
    mstCombineLimitId: Dict[int, List[MstCombineLimit]]
    mstCombineCostumeId: Dict[int, List[MstCombineCostume]]
    mstCombineMaterialId: Dict[int, List[MstCombineMaterial]]
    mstCombineSkillItem: Set[int]
    mstCombineLimitItem: Set[int]
    mstCombineCostumeItem: Set[int]
    mstSvtCardId: Dict[int, List[MstSvtCard]]
    mstSvtLimitId: Dict[int, List[MstSvtLimit]]
    mstSvtLimitAddId: Dict[int, List[MstSvtLimitAdd]]
    mstSvtExpId: Dict[int, List[MstSvtExp]]
    mstFriendshipId: Dict[int, List[int]]
    # mstEquip: List[MstEquip]
    mstEquipId: Dict[int, MstEquip]
    mstEquipExp: List[MstEquipExp]
    mstEquipSkill: List[MstEquipSkill]
    mstBgmId: Dict[int, MstBgm]
    mstWarId: Dict[int, MstWar]
    mstMapWarId: Dict[int, List[MstMap]]
    mstWarEventId: Dict[int, List[MstWar]]
    mstSpotWarId: Dict[int, List[MstSpot]]
    mstSpotId: Dict[int, MstSpot]
    mstQuestSpotId: Dict[int, List[MstQuest]]
    mstEventId: Dict[int, MstEvent]
    # mstQuest: List[MstQuest]
    mstQuestId: Dict[int, MstQuest]
    mstQuestConsumeItemId: Dict[int, List[MstQuestConsumeItem]]
    # mstQuestPhase: List[MstQuestPhase]
    mstQuestPhaseId: Dict[int, Dict[int, MstQuestPhase]]
    mstStageId: Dict[int, Dict[int, List[MstStage]]]
    mstQuestReleaseId: Dict[int, List[MstQuestRelease]]
    mstClosedMessageId: Dict[int, str]
    # mstSvtComment: List[MstSvtComment]
    mstSvtCommentId: Dict[int, List[MstSvtComment]]
    mstSvtCostumeId: Dict[int, List[MstSvtCostume]]
    mstSvtChangeId: Dict[int, List[MstSvtChange]]
    mstSvtVoiceRelationId: Dict[int, List[MstSvtVoiceRelation]]
    mstSvtScriptId: Dict[int, List[MstSvtScript]]
    # mstCommandCode: List[MstCommandCode]
    mstCommandCodeId: Dict[int, MstCommandCode]
    mstCommandCodeSkill: List[MstCommandCodeSkill]
    # mstCommandCodeComment: List[MstCommandCodeComment]
    mstCommandCodeCommentId: Dict[int, List[MstCommandCodeComment]]
    mstCvId: Dict[int, MstCv]
    mstIllustratorId: Dict[int, MstIllustrator]
    # mstSvtVoice: List[MstSvtVoice]
    mstSvtVoiceId: Dict[int, List[MstSvtVoice]]
    # mstVoice: List[MstVoice]
    mstVoiceId: Dict[str, MstVoice]
    # mstSvtGroup: List[MstSvtGroup]
    mstSvtGroupId: Dict[int, List[MstSvtGroup]]
    mstSvtGroupSvtId: Dict[int, List[MstSvtGroup]]
    # globalNewMstSubtitle: List[GlobalNewMstSubtitle] = []
    mstSubtitleId: Dict[int, List[GlobalNewMstSubtitle]] = {}
    # mstClassRelationOverwrite: List[MstClassRelationOverwrite]
    mstClassRelationOverwriteId: Dict[int, List[MstClassRelationOverwrite]]
    buffToFunc: Dict[int, Set[int]]
    funcToSkill: Dict[int, Set[int]]
    funcToTd: Dict[int, Set[int]]
    passiveSkillToSvt: Dict[int, Set[int]]
    bondEquip: Dict[int, int]
    valentineEquip: Dict[int, List[int]]
    # mstAiId: Dict[int, List[MstAi]]
    # mstAiFieldId: Dict[int, List[MstAi]]
    # mstAiActId: Dict[int, MstAiAct]
    skillToAiAct: Dict[int, Set[int]]
    aiActToAiSvt: Dict[int, List[MstAi]]
    aiActToAiField: Dict[int, List[MstAi]]
    parentAiSvt: Dict[int, Set[int]]
    parentAiField: Dict[int, Set[int]]


class ServantEntity(BaseModelORJson):
    mstSvt: MstSvt
    mstSkill: List[SkillEntityNoReverse]
    mstTreasureDevice: List[TdEntityNoReverse]
    mstSvtCard: List[MstSvtCard]
    mstSvtLimit: List[MstSvtLimit]
    mstCombineSkill: List[MstCombineSkill]
    mstCombineLimit: List[MstCombineLimit]
    mstCombineCostume: List[MstCombineCostume]
    mstSvtLimitAdd: List[MstSvtLimitAdd]
    mstSvtChange: List[MstSvtChange]
    mstSvtCostume: List[MstSvtCostume]
    mstSvtScript: List[MstSvtScript]
    mstSvtComment: List[MstSvtComment] = []
    mstSvtVoice: List[MstSvtVoice] = []
    mstSubtitle: List[GlobalNewMstSubtitle] = []


class ReversedSkillTd(BaseModelORJson):
    servant: List[ServantEntity] = []
    MC: List[MysticCodeEntity] = []
    CC: List[CommandCodeEntity] = []


class ReversedSkillTdType(BaseModelORJson):
    raw: Optional[ReversedSkillTd] = None


class SkillEntity(SkillEntityNoReverse):
    reverse: Optional[ReversedSkillTdType] = None


class TdEntity(TdEntityNoReverse):
    reverse: Optional[ReversedSkillTdType] = None


class ReversedFunction(BaseModelORJson):
    skill: List[SkillEntity] = []
    NP: List[TdEntity] = []


class ReversedFunctionType(BaseModelORJson):
    raw: Optional[ReversedFunction] = None


class FunctionEntity(FunctionEntityNoReverse):
    reverse: Optional[ReversedFunctionType] = None


class ReversedBuff(BaseModelORJson):
    function: List[FunctionEntity] = []


class ReversedBuffType(BaseModelORJson):
    raw: Optional[ReversedBuff] = None


class BuffEntity(BuffEntityNoReverse):
    reverse: Optional[ReversedBuffType] = None


class QuestEntity(BaseModelORJson):
    mstQuest: MstQuest
    mstQuestConsumeItem: List[MstQuestConsumeItem]
    mstQuestRelease: List[MstQuestRelease]


class QuestPhaseEntity(QuestEntity):
    mstQuestPhase: MstQuestPhase
    mstStage: List[MstStage]


class EventEntity(BaseModelORJson):
    mstEvent: MstEvent
    mstShop: List[MstShop]


class WarEntity(BaseModelORJson):
    mstWar: MstWar
    mstMap: List[MstMap]
    mstSpot: List[MstSpot]


class OneAiEntity(BaseModelORJson):
    mstAi: MstAi
    mstAiAct: MstAiAct


class AiEntity(BaseModelORJson):
    mainAis: List[OneAiEntity]
    relatedAis: List[OneAiEntity]
