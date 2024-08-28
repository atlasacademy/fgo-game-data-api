from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl

from .base import BaseModelORJson, DecimalSerializer
from .basic import (
    BasicQuest,
    BasicReversedBuff,
    BasicReversedFunction,
    BasicReversedSkillTd,
    BasicServant,
)
from .common import (
    BuffScript,
    MCAssets,
    NiceCostume,
    NiceTrait,
    NiceValentineScript,
    ScriptLink,
    StageLink,
)
from .enums import (
    AiTiming,
    AiType,
    EnemyRoleType,
    EventPointActivityObjectType,
    FuncApplyTarget,
    NiceDetailMissionCondLinkType,
    NiceItemBGType,
    NiceItemUse,
    NiceSkillType,
    ServantPersonality,
    ServantPolicy,
    SkillScriptCond,
    StageLimitActType,
    SvtClass,
)
from .gameenums import (
    Attribute,
    NiceAiActNum,
    NiceAiActTarget,
    NiceAiActType,
    NiceAiAllocationSvtFlag,
    NiceAiCond,
    NiceBattleFieldEnvironmentGrantType,
    NiceBattlePointFlag,
    NiceBuffType,
    NiceCardType,
    NiceClassBoardSkillType,
    NiceClassBoardSquareFlag,
    NiceCombineAdjustTarget,
    NiceCommandCardAttackType,
    NiceCommonConsumeType,
    NiceCondType,
    NiceConsumeType,
    NiceEventCombineCalc,
    NiceEventFortificationSvtType,
    NiceEventOverwriteType,
    NiceEventRewardSceneFlag,
    NiceEventSvtType,
    NiceEventType,
    NiceEventWorkType,
    NiceFrequencyType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGachaFlag,
    NiceGender,
    NiceGiftType,
    NiceItemType,
    NiceMissionProgressType,
    NiceMissionRewardType,
    NiceMissionType,
    NiceNpcFollowerEntityFlag,
    NiceNpcServantFollowerFlag,
    NicePayType,
    NicePurchaseType,
    NiceQuestAfterClearType,
    NiceQuestFlag,
    NiceQuestType,
    NiceRestrictionRangeType,
    NiceRestrictionType,
    NiceServantOverwriteType,
    NiceShopType,
    NiceSpotOverwriteType,
    NiceStatusRank,
    NiceSvtClassSupportGroupType,
    NiceSvtDeadType,
    NiceSvtFlag,
    NiceSvtFlagOriginal,
    NiceSvtType,
    NiceSvtVoiceType,
    NiceTdEffectFlag,
    NiceVoiceCondType,
    NiceWarBoardStageSquareType,
    NiceWarBoardTreasureRarity,
    NiceWarFlag,
    NiceWarOverwriteType,
    NiceWarStartType,
)
from .raw import MstSvtScriptExtendData


class AssetURL:
    back = "{base_url}/{region}/Back/back{bg_id}.png"
    charaGraph = {
        1: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
        2: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
        3: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
        4: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    }
    charaGraphChange = {
        0: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}{suffix}@1.png",
        1: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}{suffix}@2.png",
        3: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}{suffix}@1.png",
        4: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}{suffix}@2.png",
    }
    charaGraphEx = {
        1: "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}a@1.png",
        2: "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}a@2.png",
        3: "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}b@1.png",
        4: "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}b@2.png",
    }
    charaGraphExEquip = (
        "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}a.png"
    )
    charaGraphExCostume = (
        "{base_url}/{region}/CharaGraph/CharaGraphEx/{item_id}/{item_id}a.png"
    )
    commands = "{base_url}/{region}/Servants/Commands/{item_id}/card_servant_{i}.png"
    commandFile = "{base_url}/{region}/Servants/Commands/{item_id}/{file_name}.png"
    status = "{base_url}/{region}/Servants/Status/{item_id}/status_servant_{i}.png"
    charaGraphDefault = "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png"
    charaGraphName = "{base_url}/{region}/CharaGraph/{item_id}/{item_id}name@{i}.png"
    charaFigure = "{base_url}/{region}/CharaFigure/{item_id}{i}/{item_id}{i}_merged.png"
    charaFigureId = (
        "{base_url}/{region}/CharaFigure/{charaFigure}/{charaFigure}_merged.png"
    )
    charaFigureForm = "{base_url}/{region}/CharaFigure/Form/{form_id}/{svtScript_id}/{svtScript_id}_merged.png"
    narrowFigure = {
        1: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png",
        2: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@1.png",
        3: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@2.png",
        4: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}_2@0.png",
    }
    narrowFigureChange = {
        0: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}{suffix}@0.png",
        1: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}{suffix}@1.png",
        3: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}{suffix}@2.png",
        4: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}_2{suffix}@0.png",
    }
    image = "{base_url}/{region}/Image/{image}/{image}.png"
    narrowFigureDefault = "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png"
    skillIcon = "{base_url}/{region}/SkillIcons/skill_{item_id:05}.png"
    buffIcon = "{base_url}/{region}/BuffIcons/bufficon_{item_id}.png"
    items = "{base_url}/{region}/Items/{item_id}.png"
    coins = "{base_url}/{region}/Coins/{item_id}.png"
    face = "{base_url}/{region}/Faces/f_{item_id}{i}.png"
    faceChange = "{base_url}/{region}/Faces/f_{item_id}{i}{suffix}.png"
    equipFace = "{base_url}/{region}/EquipFaces/f_{item_id}{i}.png"
    enemy = "{base_url}/{region}/Enemys/{item_id}{i}.png"
    mcitem = "{base_url}/{region}/Items/masterequip{item_id:05}.png"
    mc = {
        "item": "{base_url}/{region}/Items/masterequip{item_id:05}.png",
        "masterFace": "{base_url}/{region}/MasterFace/equip{item_id:05}.png",
        "masterFaceImage": "{base_url}/{region}/MasterFace/image{item_id:05}.png",
        "masterFigure": "{base_url}/{region}/MasterFigure/equip{item_id:05}.png",
    }
    commandCode = "{base_url}/{region}/CommandCodes/c_{item_id}.png"
    commandGraph = "{base_url}/{region}/CommandGraph/{item_id}a.png"
    audio = "{base_url}/{region}/Audio/{folder}/{id}.mp3"
    banner = "{base_url}/{region}/Banner/{banner}.png"
    event = "{base_url}/{region}/Event/{event}.png"
    eventUi = "{base_url}/{region}/EventUI/{event}.png"
    eventReward = "{base_url}/{region}/EventReward/{fname}.png"
    mapImg = "{base_url}/{region}/Terminal/MapImgs/img_questmap_{map_id:0>6}/img_questmap_{map_id:0>6}.png"
    mapGimmickImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/gimmick_{gimmick_id:0>6}.png"
    spotImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/spot_{spot_id:0>6}.png"
    spotRoadImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/img_road{war_asset_id:0>4}_00.png"
    script = "{base_url}/{region}/Script/{script_path}.txt"
    bgmLogo = "{base_url}/{region}/MyRoomSound/soundlogo_{logo_id:0>3}.png"
    servantModel = "{base_url}/{region}/Servants/{item_id}/manifest.json"
    movie = "{base_url}/{region}/Movie/{item_id}.mp4"
    commandSpell = "{base_url}/{region}/CommandSpell/cs_{item_id:0>4}.png"
    enemyMasterFace = "{base_url}/{region}/EnemyMasterFace/enemyMstFace{item_id}.png"
    enemyMasterFigure = "{base_url}/{region}/EnemyMasterFigure/figure{item_id}.png"
    classBoardIcon = "{base_url}/{region}/ClassBoard/Icon/{item_id}.png"
    classBoardBg = "{base_url}/{region}/ClassBoard/Bg/{item_id}.png"


COSTUME_LIMIT_NO_LESS_THAN = 11
LIMIT_TO_FACE_ID = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3}
LIMIT_TO_FIGURE_ID = {0: 0, 1: 1, 2: 1, 3: 2, 4: 2}


class NiceBaseGift(BaseModelORJson):
    id: int
    type: NiceGiftType
    objectId: int
    priority: int
    num: int


class NiceGiftAdd(BaseModelORJson):
    priority: int
    replacementGiftIcon: HttpUrl
    condType: NiceCondType
    targetId: int
    targetNum: int
    replacementGifts: list[NiceBaseGift]


class NiceGift(NiceBaseGift):
    giftAdds: list[NiceGiftAdd]


class NiceItemSelect(BaseModelORJson):
    idx: int
    gifts: list[NiceGift]
    requireNum: int
    detail: str


class NiceItem(BaseModelORJson):
    id: int
    name: str
    originalName: str
    type: NiceItemType
    uses: list[NiceItemUse]
    detail: str
    individuality: list[NiceTrait]
    icon: HttpUrl
    background: NiceItemBGType
    value: int
    eventId: int
    eventGroupId: int
    priority: int
    dropPriority: int
    startedAt: int
    endedAt: int
    itemSelects: list[NiceItemSelect]


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: list[NiceItemAmount]
    qp: int


class NiceCommonRelease(BaseModelORJson):
    id: int
    priority: int
    condGroup: int
    condType: NiceCondType
    condId: int
    condNum: int


class NiceBuff(BaseModelORJson):
    id: int = Field(..., title="Buff ID", description="Buff ID.")
    name: str = Field(..., title="Buff name", description="Buff name.")
    originalName: str
    detail: str = Field(
        ..., title="Buff detailed description", description="Buff detailed description."
    )
    icon: Optional[HttpUrl] = Field(
        None, title="Buff icon URL", description="Buff icon URL."
    )
    type: NiceBuffType = Field(..., title="Buff type", description="Buff type.")
    buffGroup: int = Field(
        ...,
        title="Buff group",
        description="Buff group."
        "See https://github.com/atlasacademy/fgo-docs#unstackable-buffs "
        "for how this field is used.",
    )
    script: BuffScript = Field(
        ...,
        title="Buff script",
        description="Random stuffs that get added to the buff entry. "
        "See each field description for more details.",
    )
    originalScript: dict[str, Any] = Field({}, title="Original Buff script")
    vals: list[NiceTrait] = Field(
        ...,
        title="Buff individualities",
        description="Buff traits/individualities. "
        "For example, buff removal uses this field to target the buffs.",
    )
    tvals: list[NiceTrait] = Field(
        ...,
        title="Buff tvals",
        description="Buff tvals: I'm quite sure this field is used for "
        "visual purposes only and not gameplay.",
    )
    ckSelfIndv: list[NiceTrait] = Field(
        ...,
        title="Check self individualities",
        description="Buff holder's required individuality for the buff's effect to apply.",
    )
    ckOpIndv: list[NiceTrait] = Field(
        ...,
        title="Check oponent individualities",
        description="Target's required individuality for the buff's effect to apply.",
    )
    maxRate: int = Field(
        ...,
        title="Buff max rate",
        description="Buff max rate. "
        "See https://github.com/atlasacademy/fgo-docs#lower-and-upper-bounds-of-buffs "
        "for how this field is used.",
    )


class NiceFuncGroup(BaseModelORJson):
    eventId: int
    baseFuncId: int
    nameTotal: str
    name: str
    icon: Optional[HttpUrl] = None
    priority: int
    isDispValue: bool


class FunctionScript(BaseModel):
    overwriteTvals: list[list[NiceTrait]] | None = None
    funcIndividuality: list[NiceTrait] | None = None


class NiceBaseFunction(BaseModelORJson):
    funcId: int = Field(..., title="Function ID", description="Function ID")
    funcType: NiceFuncType = Field(
        ..., title="Function type", description="Function type"
    )
    funcTargetType: NiceFuncTargetType = Field(
        ...,
        title="Function target type",
        description="Determines the number of targets and the pool of applicable targets.",
    )
    funcTargetTeam: FuncApplyTarget = Field(
        ...,
        title="Function target team",
        description="Determines whether the function applies to only player's servants, "
        "only quest enemies or both. "
        "Note that this is independent of `funcTargetType`. "
        "You need to look at both fields to check if the function applies.",
    )
    funcPopupText: str = Field(
        ..., title="Function pop-up text", description="Function pop-up text"
    )
    funcPopupIcon: Optional[HttpUrl] = Field(
        None, title="Function pop-up icon URL", description="Function pop-up icon URL."
    )
    functvals: list[NiceTrait] = Field(
        ...,
        title="Function tvals",
        description="Function tvals: If available, function's targets or their buffs "
        "need to satisfy the traits given here.",
    )
    overWriteTvalsList: list[list[NiceTrait]] = Field(
        ...,
        title="Overwrite Tvals List",
        description="Overwrite functvals if given. Two-dimensional list, the inner trait list acts as a combined trait in functvals",
    )
    funcquestTvals: list[NiceTrait] = Field(
        ...,
        title="Function quest traits",
        description="Function quest traits. "
        "The current quest needs this traits for the function to works.",
    )
    script: FunctionScript = Field(
        ...,
        title="Function script",
    )
    funcGroup: list[NiceFuncGroup] = Field(
        ...,
        title="Function group details",
        description="Some more details for event drop up, bond point up functions",
    )
    traitVals: list[NiceTrait] = Field(
        [],
        title="Trait details",
        description="Trait details to be used by buff removal functions.",
    )
    buffs: list[NiceBuff] = Field(
        ...,
        title="Buff details",
        description="Buff details to be used by apply buff functions."
        "Even though this is a list, it is safe to assume it only contains 1 buff if applicable"
        "e.g. you can get the buff by buffs[0]. `buffs[0]` is also what the game hardcoded.",
    )


class ValCheckBattlePointPhaseRange(BaseModel):
    battlePointId: int
    range: list[str]


class ValDamageRateBattlePointPhase(BaseModel):
    battlePointPhase: int
    value: int


class BaseVals(BaseModel):
    Rate: Optional[int] = None
    Turn: Optional[int] = None
    Count: Optional[int] = None
    Value: Optional[int] = None
    Value2: Optional[int] = None
    UseRate: Optional[int] = None
    Target: Optional[int] = None
    Correction: Optional[int] = None
    ParamAdd: Optional[int] = None
    ParamMax: Optional[int] = None
    HideMiss: Optional[int] = None
    OnField: Optional[int] = None
    HideNoEffect: Optional[int] = None
    Unaffected: Optional[int] = None
    ShowState: Optional[int] = None
    AuraEffectId: Optional[int] = None
    ActSet: Optional[int] = None
    ActSetWeight: Optional[int] = None
    ShowQuestNoEffect: Optional[int] = None
    CheckDead: Optional[int] = None
    RatioHPHigh: Optional[int] = None
    RatioHPLow: Optional[int] = None
    SetPassiveFrame: Optional[int] = None
    ProcPassive: Optional[int] = None
    ProcActive: Optional[int] = None
    HideParam: Optional[int] = None
    SkillID: Optional[int] = None
    SkillLV: Optional[int] = None
    ShowCardOnly: Optional[int] = None
    EffectSummon: Optional[int] = None
    RatioHPRangeHigh: Optional[int] = None
    RatioHPRangeLow: Optional[int] = None
    TargetList: Optional[list[int]] = None
    OpponentOnly: Optional[int] = None
    StatusEffectId: Optional[int] = None
    EndBattle: Optional[int] = None
    LoseBattle: Optional[int] = None
    AddIndividualty: Optional[int] = None
    AddLinkageTargetIndividualty: Optional[int] = None
    SameBuffLimitTargetIndividuality: Optional[int] = None
    SameBuffLimitNum: Optional[int] = None
    CheckDuplicate: Optional[int] = None
    OnFieldCount: Optional[int] = None
    TargetRarityList: Optional[list[int]] = None
    DependFuncId: Optional[int] = None
    InvalidHide: Optional[int] = None
    OutEnemyNpcId: Optional[int] = None
    InEnemyNpcId: Optional[int] = None
    OutEnemyPosition: Optional[int] = None
    IgnoreIndividuality: Optional[int] = None
    StarHigher: Optional[int] = None
    ChangeTDCommandType: Optional[int] = None
    ShiftNpcId: Optional[int] = None
    DisplayLastFuncInvalidType: Optional[int] = None
    AndCheckIndividualityList: Optional[list[int]] = None
    WinBattleNotRelatedSurvivalStatus: Optional[int] = None
    ForceSelfInstantDeath: Optional[int] = None
    ChangeMaxBreakGauge: Optional[int] = None
    ParamAddMaxValue: Optional[int] = None
    ParamAddMaxCount: Optional[int] = None
    LossHpChangeDamage: Optional[int] = None
    IncludePassiveIndividuality: Optional[int] = None
    MotionChange: Optional[int] = None
    PopLabelDelay: Optional[int] = None
    NoTargetNoAct: Optional[int] = None
    CardIndex: Optional[int] = None
    CardIndividuality: Optional[int] = None
    WarBoardTakeOverBuff: Optional[int] = None
    ParamAddSelfIndividuality: Optional[list[int]] = None
    ParamAddOpIndividuality: Optional[list[int]] = None
    ParamAddFieldIndividuality: Optional[list[int]] = None
    ParamAddValue: Optional[int] = None
    MultipleGainStar: Optional[int] = None
    NoCheckIndividualityIfNotUnit: Optional[int] = None
    ForcedEffectSpeedOne: Optional[int] = None
    SetLimitCount: Optional[int] = None
    CheckEnemyFieldSpace: Optional[int] = None
    TriggeredFuncPosition: Optional[int] = None
    DamageCount: Optional[int] = None
    DamageRates: Optional[list[int]] = None
    OnPositions: Optional[list[int]] = None
    OffPositions: Optional[list[int]] = None
    TargetIndiv: Optional[int] = None
    IncludeIgnoreIndividuality: Optional[int] = None
    EvenIfWinDie: Optional[int] = None
    CallSvtEffectId: Optional[int] = None
    ForceAddState: Optional[int] = None
    UnSubState: Optional[int] = None
    ForceSubState: Optional[int] = None
    IgnoreIndivUnreleaseable: Optional[int] = None
    OnParty: Optional[int] = None
    CounterId: int | None = None
    CounterLv: int | None = None
    CounterOc: int | None = None
    UseTreasureDevice: int | None = None
    SkillReaction: int | None = None
    BehaveAsFamilyBuff: int | None = None
    UnSubStateWhileLinkedToOthers: int | None = Field(
        default=None,
        description="The buff with this dataVal is removed if the linked buff is removed.",
    )
    NotAccompanyWhenLinkedTargetMoveState: int | None = None
    NotTargetSkillIdArray: list[int] | None = None
    ShortTurn: int | None = None
    FieldIndividuality: list[int] | None = None
    BGId: int | None = None
    BGType: int | None = None
    BgmId: int | None = None
    TakeOverFieldState: int | None = None
    TakeOverNextWaveBGAndBGM: int | None = None
    RemoveFieldBuffActorDeath: int | None = None
    FieldBuffGrantType: int | None = None
    Priority: int | None = None
    AddIndividualityEx: int | None = None
    IgnoreResistance: int | None = None
    GainNpTargetPassiveIndividuality: int | None = None
    HpReduceToRegainIndiv: int | None = None
    DisplayActualRecoveryHpFlag: int | None = None
    ShiftDeckIndex: int | None = None
    PopValueText: str | None = None
    IsLossHpPerNow: int | None = None
    CopyTargetFunctionType: list[int] | None = None
    CopyFunctionTargetPTOnly: int | None = None
    IgnoreValueUp: int | None = None
    ApplyValueUp: list[str] | None = None
    ActNoDamageBuff: int | None = None
    ActSelectIndex: int | None = None
    CopyTargetBuffType: list[int] | None = None
    NotSkillCopyTargetFuncIds: list[int] | None = None
    NotSkillCopyTargetIndividualities: list[int] | None = None
    ClassIconAuraEffectId: int | None = None
    ActMasterGenderType: int | None = None
    IntervalTurn: int | None = None
    IntervalCount: int | None = None
    TriggeredFieldCountTarget: int | None = None
    TriggeredFieldCountRange: list[int] | None = None
    TargetEnemyRange: list[int] | None = None
    TriggeredFuncPositionSameTarget: int | None = None
    TriggeredFuncPositionAll: int | None = None
    TriggeredTargetHpRange: str | None = None
    TriggeredTargetHpRateRange: str | None = None
    ExcludeUnSubStateIndiv: int | None = None
    ProgressTurnOnBoard: int | None = None
    CheckTargetResurrectable: int | None = None
    CancelTransform: int | None = None
    UnSubStateWhenContinue: int | None = None
    CheckTargetHaveDefeatPoint: int | None = None
    NPFixedDamageValue: int | None = None
    IgnoreShiftSafeDamage: int | None = None
    ActAttackFunction: int | None = None
    DelayRemoveBuffExpiredOnPlayerTurn: int | None = None
    AllowRemoveBuff: int | None = None
    NotExecFunctionIfKeepAliveOnWarBoard: int | None = None
    SnapShotParamAddSelfIndv: list[int] | None = None
    SnapShotParamAddOpIndv: list[int] | None = None
    SnapShotParamAddFieldIndv: list[int] | None = None
    SnapShotParamAddValue: int | None = None
    SnapShotParamAddMaxValue: int | None = None
    SnapShotParamAddMaxCount: int | None = None
    NotExecOnTransform: int | None = None
    NotRemoveOnTransform: int | None = None
    PriorityBgm: int | None = None
    BgmAllowSubPlaying: int | None = None
    BgPriority: int | None = None
    PriorityBg: int | None = None
    ResetPriorityBgmAtWaveStart: int | None = None
    ControlOtherBgmAtOverStageBgm_Priority: int | None = None
    ControlOtherBgmAtOverStageBgm_Target: int | None = None
    ExtendBuffHalfTurnInOpponentTurn: int | None = None
    ShortenBuffHalfTurnInOpponentTurn: int | None = None
    ExtendBuffHalfTurnInPartyTurn: int | None = None
    ShortenBuffHalfTurnInPartyTurn: int | None = None
    LinkageBuffGrantSuccessEvenIfOtherFailed: int | None = None
    DisplayNoEffectCauses: str | None = None
    BattlePointId: int | None = None
    BattlePointValue: int | None = None
    BattlePointUiUpdateType: int | None = None
    BattlePointOverwrite: int | None = None
    CheckOverChargeStageRange: list[str] | None = None
    CheckBattlePointPhaseRange: list[ValCheckBattlePointPhaseRange] | None = None
    StartingPosition: list[int] | None = None
    FriendShipAbove: int | None = None
    DamageRateBattlePointPhase: list[ValDamageRateBattlePointPhase] | None = None
    ParamAddBattlePointPhaseId: int | None = None
    ParamAddBattlePointPhaseValue: int | None = None
    ShortenMaxCountEachSkill: list[int] | None = None
    # Extra dataval from SkillLvEntty.DIC_KEY_APPLY_SUPPORT_SVT
    ApplySupportSvt: Optional[int] = None
    # These are not DataVals but guesses from SkillLvEntity and EventDropUpValInfo
    Individuality: Optional[int] = None
    EventId: Optional[int] = None
    AddCount: Optional[int] = None
    RateCount: Optional[int] = None
    DropRateCount: Optional[int] = None
    # aa0: Optional[int] = None
    # aa1: Optional[int] = None
    # aa2: Optional[int] = None
    # aa3: Optional[int] = None
    # aa4: Optional[int] = None
    DependFunc: NiceBaseFunction | None = None


class Vals(BaseVals):
    DependFuncVals: Optional[BaseVals] = None


class NiceFunction(NiceBaseFunction):
    svals: list[Vals] = Field(
        ...,
        title="Parameter values by skill level or NP level",
        description="Parameter values by skill level or NP level",
    )
    svals2: Optional[list[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 2",
        description="Parameter values for NP Overcharge level 2 by NP level",
    )
    svals3: Optional[list[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 3",
        description="Parameter values for NP Overcharge level 3 by NP level",
    )
    svals4: Optional[list[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 4",
        description="Parameter values for NP Overcharge level 4 by NP level",
    )
    svals5: Optional[list[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 5",
        description="Parameter values for NP Overcharge level 5 by NP level",
    )
    followerVals: Optional[list[Vals]] = Field(
        None,
        title="Parameter values when used by a support servant",
        description="Parameter values when used by a support servant. "
        "If the function comes from a support servant, the values here will be "
        "used if available, e.g. Chaldea Teatime.",
    )


class ExtraPassive(BaseModel):
    num: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    condLv: int
    condLimitCount: int
    condFriendshipRank: int
    eventId: int
    flag: int
    releaseConditions: list[NiceCommonRelease] = []
    startedAt: int
    endedAt: int


class NiceSelectAddInfoBtnCond(BaseModel):
    cond: SkillScriptCond
    value: int | None = None


class NiceSelectAddInfoBtn(BaseModel):
    name: str
    conds: list[NiceSelectAddInfoBtnCond]


class NiceSelectAddInfo(BaseModel):
    title: str
    btn: list[NiceSelectAddInfoBtn]


class TdChangeByBattlePoint(BaseModel):
    battlePointId: int
    phase: int
    noblePhantasmId: int


class SelectTreasureDeviceInfoTreasureDevice(BaseModel):
    id: int
    type: NiceCardType
    message: str


class SelectTreasureDeviceInfo(BaseModel):
    dialogType: int
    treasureDevices: list[SelectTreasureDeviceInfoTreasureDevice]
    title: str
    messageOnSelected: str


class NiceSkillScript(BaseModel):
    NP_HIGHER: Optional[list[int]] = None
    NP_LOWER: Optional[list[int]] = None
    STAR_HIGHER: Optional[list[int]] = None
    STAR_LOWER: Optional[list[int]] = None
    HP_VAL_HIGHER: Optional[list[int]] = None
    HP_VAL_LOWER: Optional[list[int]] = None
    HP_PER_HIGHER: Optional[list[int]] = None
    HP_PER_LOWER: Optional[list[int]] = None
    additionalSkillId: Optional[list[int]] = None
    additionalSkillActorType: Optional[list[int]] = None
    tdTypeChangeIDs: list[int] | None = None
    excludeTdChangeTypes: list[int] | None = None
    actRarity: list[list[int]] | None = None
    battleStartRemainingTurn: list[int] | None = None
    SelectAddInfo: list[NiceSelectAddInfo] | None = None
    IgnoreValueUp: list[bool] | None = None
    IgnoreBattlePointUp: list[list[int]] | None = None
    tdChangeByBattlePoint: list[TdChangeByBattlePoint] | None = None
    selectTreasureDeviceInfo: list[SelectTreasureDeviceInfo] | None = None


class NiceSkillAdd(BaseModelORJson):
    priority: int
    releaseConditions: list[NiceCommonRelease]
    name: str
    originalName: str
    ruby: str


class NiceSkillGroupOverwrite(BaseModelORJson):
    level: int
    skillGroupId: int
    startedAt: int
    endedAt: int
    icon: Optional[HttpUrl] = None
    detail: str
    unmodifiedDetail: str
    functions: list[NiceFunction] = Field(
        ...,
        description="Since each skill level has their own group overwrite, the svals field only contains data for 1 level.",
    )


class NiceSvtSkillRelease(BaseModelORJson):
    # svtId: int
    # num: int
    # priority: int
    idx: int
    condType: NiceCondType
    condTargetId: int
    condNum: int
    condGroup: int


class NiceSkillSvt(BaseModelORJson):
    svtId: int  # 9400920,
    num: int  # 1,
    priority: int  # 1,
    script: Optional[dict[str, Any]] = None
    strengthStatus: int  # 1,
    condQuestId: int  # 0,
    condQuestPhase: int  # 0,
    condLv: int = 0  # 0,
    condLimitCount: int  # 0,
    eventId: int  # 0,
    flag: int  # 0
    releaseConditions: list[NiceSvtSkillRelease]


class NiceSkill(BaseModelORJson):
    id: int
    num: int = 0
    name: str
    originalName: str
    ruby: str
    detail: Optional[str] = None
    unmodifiedDetail: Optional[str] = None
    type: NiceSkillType
    svtId: int
    strengthStatus: int = 0
    priority: int = 0
    condQuestId: int = 0
    condQuestPhase: int = 0
    condLv: int = 0
    condLimitCount: int = 0
    icon: Optional[HttpUrl] = None
    coolDown: list[int]
    actIndividuality: list[NiceTrait]
    script: NiceSkillScript
    extraPassive: list[ExtraPassive]
    skillAdd: list[NiceSkillAdd]
    skillSvts: list[NiceSkillSvt] = []
    aiIds: Optional[dict[AiType, list[int]]] = None
    groupOverwrites: list[NiceSkillGroupOverwrite] | None = None
    functions: list[NiceFunction]


class NpGain(BaseModel):
    buster: list[int]
    arts: list[int]
    quick: list[int]
    extra: list[int]
    defence: list[int]
    np: list[int]


class NiceTdSvt(BaseModelORJson):
    svtId: int
    num: int
    npNum: int
    priority: int
    damage: list[int]
    strengthStatus: int
    flag: int
    imageIndex: int
    condQuestId: int
    condQuestPhase: int
    condLv: int = 0
    condFriendshipRank: int = 0
    motion: int
    card: NiceCardType
    releaseConditions: list[NiceSvtSkillRelease] = []


class NiceTd(BaseModelORJson):
    id: int
    num: int
    npNum: int
    card: NiceCardType
    name: str
    originalName: str
    ruby: str
    icon: Optional[HttpUrl] = None
    rank: str
    type: str
    effectFlags: list[NiceTdEffectFlag]
    detail: Optional[str] = None
    unmodifiedDetail: Optional[str] = None
    npGain: NpGain
    npDistribution: list[int]
    svtId: int
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    releaseConditions: list[NiceSvtSkillRelease] = []
    individuality: list[NiceTrait]
    npSvts: list[NiceTdSvt]
    script: NiceSkillScript
    functions: list[NiceFunction]


class ExtraMCAssets(BaseModel):
    item: MCAssets
    masterFace: MCAssets
    masterFigure: MCAssets


class NiceMysticCodeCostume(BaseModel):
    id: int
    releaseConditions: list[NiceCommonRelease]
    extraAssets: ExtraMCAssets


class NiceMysticCode(BaseModelORJson):
    id: int
    name: str
    shortName: str
    originalName: str
    detail: str
    maxLv: int
    extraAssets: ExtraMCAssets
    skills: list[NiceSkill]
    expRequired: list[int]
    costumes: list[NiceMysticCodeCostume]


class NiceEnemyMasterBattle(BaseModelORJson):
    id: int
    face: HttpUrl
    figure: HttpUrl
    commandSpellIcon: HttpUrl
    maxCommandSpell: int
    offsetX: int
    offsetY: int
    cutin: list[HttpUrl] | None = None


class NiceEnemyMaster(BaseModelORJson):
    id: int
    name: str
    battles: list[NiceEnemyMasterBattle]


class NiceBattleMasterImage(BaseModelORJson):
    id: int
    type: NiceGender
    faceIcon: HttpUrl
    skillCutin: HttpUrl
    skillCutinOffsetX: int
    skillCutinOffsetY: int
    commandSpellCutin: HttpUrl
    commandSpellCutinOffsetX: int
    commandSpellCutinOffsetY: int
    resultImage: HttpUrl
    releaseConditions: list[NiceCommonRelease]


def get_community_limit(limit_count: int) -> int:
    return limit_count + 1 if limit_count < 2 else limit_count


class ExtraAssetsUrl(BaseModel):
    ascension: Optional[dict[int, HttpUrl]] = None
    story: Optional[dict[int, HttpUrl]] = None
    costume: Optional[dict[int, HttpUrl]] = None
    equip: Optional[dict[int, HttpUrl]] = None
    cc: Optional[dict[int, HttpUrl]] = None

    def set_limit_asset(
        self, limit_count: int, url: HttpUrl, costume_ids: dict[int, int]
    ) -> None:
        if limit_count > 10 and limit_count in costume_ids:
            if self.costume is None:
                self.costume = {costume_ids[limit_count]: url}
            else:
                self.costume[costume_ids[limit_count]] = url
        else:
            community_limit = get_community_limit(limit_count)
            if self.ascension is None:
                self.ascension = {community_limit: url}
            else:
                self.ascension[community_limit] = url


class ExtraCCAssets(BaseModel):
    charaGraph: ExtraAssetsUrl
    faces: ExtraAssetsUrl


class ExtraAssets(ExtraCCAssets):
    charaGraphEx: ExtraAssetsUrl
    charaGraphName: ExtraAssetsUrl
    narrowFigure: ExtraAssetsUrl
    charaFigure: ExtraAssetsUrl
    charaFigureForm: dict[int, ExtraAssetsUrl]
    charaFigureMulti: dict[int, ExtraAssetsUrl]
    charaFigureMultiCombine: dict[int, ExtraAssetsUrl]
    charaFigureMultiLimitUp: dict[int, ExtraAssetsUrl]
    commands: ExtraAssetsUrl
    status: ExtraAssetsUrl
    equipFace: ExtraAssetsUrl
    image: ExtraAssetsUrl = Field(
        ...,
        title="Story images",
        description="Images that are used in the game scripts. Only the story field will be filled."
        "Since the list comes from JP, the NA asset might not exist and returns 404.",
    )
    spriteModel: ExtraAssetsUrl
    charaGraphChange: ExtraAssetsUrl
    narrowFigureChange: ExtraAssetsUrl
    facesChange: ExtraAssetsUrl


class NiceCardDetail(BaseModel):
    hitsDistribution: list[int]
    attackIndividuality: list[NiceTrait]
    attackType: NiceCommandCardAttackType
    damageRate: int | None = None
    attackNpRate: int | None = None
    defenseNpRate: int | None = None
    dropStarRate: int | None = None


AscensionAddData = TypeVar("AscensionAddData")


class AscensionAddEntry(BaseModel, Generic[AscensionAddData]):
    ascension: dict[int, AscensionAddData] = Field(
        ...,
        title="Ascension changes",
        description="Mapping <Ascension level, Ascension level data>.",
    )
    costume: dict[int, AscensionAddData] = Field(
        ..., title="Costume changes", description="Mapping <Costume ID, Costume data>."
    )


# AscensionAddEntry[list[NiceTrait]] can't be pickled
class AscensionAddEntryTrait(BaseModel):
    ascension: dict[int, list[NiceTrait]] = Field(
        ...,
        title="Ascension changes",
        description="Mapping <Ascension level, Ascension level data>.",
    )
    costume: dict[int, list[NiceTrait]] = Field(
        ..., title="Costume changes", description="Mapping <Costume ID, Costume data>."
    )


class AscensionAddEntryCommonRelease(BaseModel):
    ascension: dict[int, list[NiceCommonRelease]] = Field(
        ...,
        title="Ascension changes",
        description="Mapping <Ascension level, Ascension level data>.",
    )
    costume: dict[int, list[NiceCommonRelease]] = Field(
        ..., title="Costume changes", description="Mapping <Costume ID, Costume data>."
    )


AscensionAddEntryInt = AscensionAddEntry[int]
AscensionAddEntryStr = AscensionAddEntry[str]
AscensionAddEntryHttpUrl = AscensionAddEntry[HttpUrl]
AscensionAddEntryAttribte = AscensionAddEntry[Attribute]


class AscensionAdd(BaseModel):
    attribute: AscensionAddEntryAttribte
    individuality: AscensionAddEntryTrait = Field(
        ...,
        title="Individuality changes",
        description="Some servants add or remove traits as they ascend.",
    )
    voicePrefix: AscensionAddEntryInt = Field(
        ...,
        title="Voice prefix changes",
        description="Some servants change voice lines as they ascennd.",
    )
    overWriteServantName: AscensionAddEntryStr = Field(
        ..., title="Servant name changes"
    )
    originalOverWriteServantName: AscensionAddEntryStr
    overWriteServantBattleName: AscensionAddEntryStr = Field(
        ..., title="Servant battle name changes"
    )
    originalOverWriteServantBattleName: AscensionAddEntryStr
    overWriteTDName: AscensionAddEntryStr = Field(..., title="NP name changes")
    originalOverWriteTDName: AscensionAddEntryStr
    overWriteTDRuby: AscensionAddEntryStr = Field(..., title="NP ruby changes")
    overWriteTDFileName: AscensionAddEntryHttpUrl = Field(
        ..., title="NP image URL changes"
    )
    overWriteTDRank: AscensionAddEntryStr = Field(..., title="NP rank changes")
    overWriteTDTypeText: AscensionAddEntryStr = Field(..., title="NP type changes")
    lvMax: AscensionAddEntryInt = Field(..., title="Max level")
    rarity: AscensionAddEntryInt
    charaGraphChange: AscensionAddEntryHttpUrl
    charaGraphChangeCommonRelease: AscensionAddEntryCommonRelease
    faceChange: AscensionAddEntryHttpUrl
    faceChangeCommonRelease: AscensionAddEntryCommonRelease


class NiceServantChange(BaseModel):
    beforeTreasureDeviceIds: list[int]
    afterTreasureDeviceIds: list[int]
    svtId: int
    priority: int
    condType: NiceCondType
    condTargetId: int
    condValue: int
    name: str
    ruby: str
    battleName: str
    svtVoiceId: int
    limitCount: int
    flag: int
    battleSvtId: int


class NiceServantLimitImage(BaseModel):
    limitCount: int
    priority: int
    defaultLimitCount: int
    condType: NiceCondType
    condTargetId: int
    condNum: int


class NiceServantAppendPassiveSkill(BaseModel):
    num: int
    priority: int
    skill: NiceSkill
    unlockMaterials: list[NiceItemAmount]


class NiceServantCoin(BaseModel):
    summonNum: int
    item: NiceItem


class NiceServantTrait(BaseModel):
    idx: int
    trait: list[NiceTrait]
    limitCount: int
    condType: Optional[NiceCondType] = None
    condId: Optional[int] = None
    condNum: Optional[int] = None
    eventId: int | None = None
    startedAt: int | None = None
    endedAt: int | None = None


class NiceLoreCommentAdd(BaseModel):
    idx: int
    condType: NiceCondType
    condValues: list[int]
    condValue2: int = Field(
        ...,
        title="condValue2",
        description="This field can be safely ignored. All values are 0.",
    )


class NiceLoreComment(BaseModel):
    id: int
    priority: int
    condMessage: str
    comment: str
    condType: NiceCondType
    condValues: Optional[list[int]] = None
    condValue2: int
    additionalConds: list[NiceLoreCommentAdd]


class NiceSvtOverwriteValue(BaseModel):
    noblePhantasm: NiceTd | None = None


class NiceSvtOverwrite(BaseModel):
    type: NiceServantOverwriteType
    priority: int
    condType: NiceCondType
    condTargetId: int
    condValue: int
    overwriteValue: NiceSvtOverwriteValue


class NiceLoreStats(BaseModel):
    strength: NiceStatusRank  # power
    endurance: NiceStatusRank  # defense
    agility: NiceStatusRank
    magic: NiceStatusRank
    luck: NiceStatusRank
    np: NiceStatusRank  # treasureDevice
    policy: ServantPolicy
    personality: ServantPersonality
    deity: NiceStatusRank


class NiceSvtLimit(BaseModelORJson):
    limitCount: int
    rarity: int
    lvMax: int
    hpBase: int
    hpMax: int
    atkBase: int
    atkMax: int
    criticalWeight: int
    strength: NiceStatusRank
    endurance: NiceStatusRank
    agility: NiceStatusRank
    magic: NiceStatusRank
    luck: NiceStatusRank
    np: NiceStatusRank
    deity: NiceStatusRank
    policy: ServantPolicy
    personality: ServantPersonality


class NiceBattlePointPhase(BaseModelORJson):
    phase: int
    value: int
    name: str
    effectId: int


class NiceBattlePoint(BaseModelORJson):
    id: int
    flags: list[NiceBattlePointFlag]
    phases: list[NiceBattlePointPhase]


class NiceSvtScript(BaseModelORJson):
    id: int
    form: int
    faceX: int
    faceY: int
    extendData: MstSvtScriptExtendData
    bgImageId: int = 0
    scale: Annotated[Decimal, DecimalSerializer]
    offsetX: int
    offsetY: int
    offsetXMyroom: int
    offsetYMyroom: int
    svtId: Optional[int] = None
    limitCount: Optional[int] = None


class NiceVoiceCond(BaseModel):
    condType: NiceVoiceCondType = Field(
        ..., title="Voice Cond Type", description="Voice Condition Type Enum"
    )
    value: int = Field(
        ..., title="Voice Cond Value", description="Threshold value for the condition."
    )
    valueList: list[int] = Field(
        [],
        title="Voice Cond Value list",
        description="If the voice cond is `svtGroup`, "
        "this list will hold the applicable servant IDs.",
    )
    eventId: int = Field(..., title="Event ID", description="Event ID.")


class NiceVoicePlayCond(BaseModel):
    condGroup: int = Field(
        ...,
        title="Voice play condition group",
        description="To play a voice line, at least one condition group needs to be statisfied."
        "Within one condition group, all conditions need to be statisfied."
        "i.e. (group_1_cond_1 AND group_1_cond_2) OR (group_2_cond_1)",
    )
    condType: NiceCondType = Field(..., title="Voice play condition type")
    targetId: int = Field(..., title="Voice play condition target ID")
    condValue: int = Field(
        ...,
        title="[DEPRECATED, use condValues] Voice play condition target value."
        "Use condValues since condValues in other places can have multiple values."
        "This value is the first element of condValues.",
    )
    condValues: list[int] = Field(..., title="Voice play condition target values")


class NiceVoiceLine(BaseModelORJson):
    name: Optional[str] = Field(
        default=None,
        title="Voice line default name",
        description="Voice line default name.",
    )
    condType: Optional[NiceCondType] = Field(
        default=None,
        title="Voice line default condition type",
        description="Voice line default condition type.",
    )
    condValue: Optional[int] = Field(
        default=None,
        title="Voice line default condition value",
        description="Voice line default condition threshold value.",
    )
    priority: Optional[int] = Field(
        default=None,
        title="Voice line default priority",
        description="Voice line default priority.",
    )
    svtVoiceType: Optional[NiceSvtVoiceType] = Field(
        default=None,
        title="Voice line default type",
        description="Voice line default type.",
    )
    overwriteName: str = Field(
        ..., title="Voice line overwrite name", description="Voice line overwrite name."
    )
    summonScript: Optional[ScriptLink] = Field(
        default=None, title="Script to be played when summoning"
    )
    id: list[str] = Field(..., title="Voice line IDs", description="Voice line IDs.")
    audioAssets: list[str] = Field(
        ..., title="Voice line mp3 URLs", description="Voice line mp3 URLs."
    )
    delay: list[Annotated[Decimal, DecimalSerializer]] = Field(
        ...,
        title="Voice line delays",
        description="Delays in seconds before playing the audio file.",
    )
    face: list[int] = Field(
        ...,
        title="Voice line faces",
        description="CharaFigure faces to be used when playing the voice line.",
    )
    form: list[int] = Field(
        ...,
        title="Voice line forms",
        description="CharaFigure forms to be used when playing the voice line.",
    )
    text: list[str] = Field(
        ...,
        title="Voice line texts",
        description="Texts used for summoning subtitles. "
        "Only summoning lines have data for this fields.",
    )
    subtitle: str = Field(
        ...,
        title="Voice line subtitles",
        description="English subtitle for the voice line, only applicable to NA data.",
    )
    conds: list[NiceVoiceCond] = Field(
        ...,
        title="Voice line conditions",
        description="Conditions to unlock the voice line.",
    )
    playConds: list[NiceVoicePlayCond] = Field(
        ...,
        title="Voice line play conditions",
        description="Conditions to play the voice line."
        "For example, there are male and female versions of a bond 5 voice line."
        "The voice line is unlocked at bond 5 but only one of the line is played in my room.",
    )


class NiceVoiceGroup(BaseModel):
    svtId: int
    voicePrefix: int
    type: NiceSvtVoiceType
    voiceLines: list[NiceVoiceLine]


class NiceLore(BaseModel):
    cv: str
    illustrator: str
    stats: Optional[NiceLoreStats] = None
    costume: dict[int, NiceCostume] = Field(
        ...,
        title="Costume Details",
        description="Mapping <Costume BattleCharaID, Costume Detail>.",
    )
    comments: list[NiceLoreComment]
    voices: list[NiceVoiceGroup]


class NiceServantScript(BaseModel):
    SkillRankUp: Optional[dict[int, list[int]]] = Field(
        None,
        title="SkillRankUp",
        description="Mapping <Skill IDs, list[Skill IDs]>. "
        "Summer Kiara 1st skill additional data. "
        "The keys are the base skill IDs and the values are the rank-up skill IDs.",
    )
    svtBuffTurnExtend: bool | None = Field(
        None,
        title="Servant Buff Turn Extend",
        description="Bazett's effect. Extend buff's duration from end of player turn to end of enemy turn.",
    )
    maleImage: ExtraAssets | None = None


class NiceCommandCode(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    originalName: str
    ruby: str
    rarity: int
    extraAssets: ExtraCCAssets
    skills: list[NiceSkill]
    illustrator: str
    comment: str


class NiceServant(BaseModelORJson):
    id: int = Field(
        ...,
        title="Servant ID",
        description="svt's internal ID. "
        'Note that this is different from the 1~300 IDs shown in "Spirit Origin list", '
        "which is `.collectionNo`. "
        "This ID is unique accross svt items (servants, CEs, EXPs, enemies, …)",
    )
    collectionNo: int = Field(
        ...,
        title="Collection No",
        description='The ID number shown in "Spirit Origin list". '
        "The community usually means this number when they talk about servant or CE IDs.",
    )
    name: str = Field(..., title="svt's name", description="svt's name")
    originalName: str = Field(
        ..., title="untranslated svt name", description="untranslated svt name"
    )
    ruby: str = Field(
        ..., title="svt's name ruby text", description="svt's name ruby text"
    )
    battleName: str = Field(
        ..., title="svt's battle name", description="Name that appears in battle"
    )
    originalBattleName: str = Field(
        ...,
        title="untranslated svt's battle name",
        description="untranslated svt's battle name",
    )
    classId: int = Field(..., title="svt's class ID")
    className: SvtClass | str = Field(
        ...,
        title="svt's class",
        description="svt's class. "
        "Because enemies also use this model, you can see some non-playable classes "
        "as possible values.",
    )
    type: NiceSvtType = Field(..., title="svt's type", description="svt's type.")
    flag: NiceSvtFlag = Field(
        ...,
        title="svt's flag",
        description="[DEPRECATED] Use the `flags` field. Some random flags given to the svt items.",
    )
    flags: list[NiceSvtFlagOriginal]
    rarity: int = Field(..., title="svt's rarity", description="svt's rarity.")
    cost: int = Field(
        ..., title="svt's cost", description="Cost to put the item in a party."
    )
    lvMax: int = Field(
        ...,
        title="svt's max level",
        description="Max level of the item without grailing.",
    )
    extraAssets: ExtraAssets = Field(
        ..., title="Image assets", description="Image assets."
    )
    gender: NiceGender = Field(..., title="svt's gender", description="svt's gender.")
    attribute: Attribute = Field(
        ..., title="svt's attribute", description="svt's attribute."
    )
    traits: list[NiceTrait] = Field(
        ...,
        title="list of traits",
        description="list of individualities, or commonly refered to as traits.",
    )
    starAbsorb: int = Field(..., title="Star weight", description="Star weight.")
    starGen: int = Field(..., title="Star rate", description="Star generation rate.")
    instantDeathChance: int = Field(
        ..., title="Instant death chance", description="Instant death chance."
    )
    cards: list[NiceCardType] = Field(..., title="Card deck", description="Card deck.")
    hitsDistribution: dict[NiceCardType, list[int]] = Field(
        ...,
        title="Hits distribution",
        description="Mapping <Card type, Hits distribution>.",
    )
    cardDetails: dict[NiceCardType, NiceCardDetail] = Field(
        ...,
        title="Card detail",
        description="Mapping <Card type, Card detail>, containing attack traits.",
    )
    atkBase: int = Field(..., title="Base ATK", description="Base ATK.")
    atkMax: int = Field(..., title="Max ATK", description="Max ATK (without grailing).")
    hpBase: int = Field(..., title="Base HP", description="Base HP.")
    hpMax: int = Field(..., title="Max HP", description="Max HP (without grailing).")
    relateQuestIds: list[int] = Field(
        ...,
        title="Related quest IDs",
        description="IDs of related quests: rank-ups or interludes.",
    )
    trialQuestIds: list[int] = Field(..., title="Trial quest IDs")
    growthCurve: int = Field(
        ..., title="Growth curve type", description="Growth curve type"
    )
    atkGrowth: list[int] = Field(
        ...,
        title="ATK value per level",
        description="ATK value per level, including grail levels.",
    )
    hpGrowth: list[int] = Field(
        ...,
        title="HP value per level",
        description="HP value per level, including grail levels.",
    )
    bondGrowth: list[int] = Field(
        ...,
        title="Bond EXP needed per bond level",
        description="Bond EXP needed per bond level",
    )
    expGrowth: list[int] = Field(
        ...,
        title="Accumulated EXP",
        description="Total EXP needed per level. "
        'Equivalent to the "Accumulated EXP" value when feeding CE into another CE.',
    )
    expFeed: list[int] = Field(
        ...,
        title="Base EXP",
        description="Base EXP per level. "
        'Will show up as "Base EXP" when feeding the item into something else.',
    )
    bondEquip: int = Field(
        0,
        title="Bond CE",
        description="Bond CE ID (not collectionNo). Defaults to 0 if the svt doesn't have a bond CE.",
    )
    valentineEquip: list[int] = Field(
        [], title="Valentine CE", description="Valentine CE ID (not collectionNo)."
    )
    valentineScript: list[NiceValentineScript] = Field(
        [],
        title="Valentine Script",
        description="Index matched with the `valentineEquip` field.",
    )
    bondEquipOwner: Optional[int] = Field(
        None,
        title="Bond Servant ID",
        description="Servant ID if this CE is a bond CE",
    )
    valentineEquipOwner: Optional[int] = Field(
        None,
        title="Valentine Servant ID",
        description="Servant ID if this CE is a valentine CE",
    )
    limits: list[NiceSvtLimit] = Field(
        ...,
        title="Svt Limit",
        description="Ascension and Costume data.",
    )
    ascensionAdd: AscensionAdd = Field(
        ...,
        title="Ascension Add",
        description="Attributes that change when servants ascend.",
    )
    traitAdd: list[NiceServantTrait] = Field(
        ...,
        title="Extra Conditional Individuality",
        description="Traits used for event bonus or in special quests.",
    )
    svtChange: list[NiceServantChange] = Field(
        ..., title="Servant Change", description="EOR servants' hidden name details."
    )
    ascensionImage: list[NiceServantLimitImage] = Field(
        ..., title="Servant Limit Image"
    )
    overwrites: list[NiceSvtOverwrite] = Field(..., title="Servant Overwrites")
    ascensionMaterials: dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Ascension Materials",
        description="Mapping <Ascension level, Materials to ascend servants>.",
    )
    skillMaterials: dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Skill Materials",
        description="Mapping <Skill level, Materials to level up skills>.",
    )
    appendSkillMaterials: dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Append Skill Materials",
        description="Mapping <Append Skill level, Materials to level up append skills>.",
    )
    costumeMaterials: dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Costume Materials",
        description="Mapping <Costume svt ID, Materials to unlock the costume>. "
        "Costume details can be found in `.profile.costume`",
    )
    coin: Optional[NiceServantCoin] = Field(None, title="Servant Coin")
    script: NiceServantScript = Field(
        ...,
        title="Servant Script",
        description="Random stuffs that get added to the servant entry. "
        "See each field description for more details.",
    )
    charaScripts: list[NiceSvtScript]
    battlePoints: list[NiceBattlePoint]
    skills: list[NiceSkill] = Field(
        ..., title="Skills", description="List of servant or CE skills."
    )
    classPassive: list[NiceSkill] = Field(
        ..., title="Passive Skills", description="list of servant's passive skills."
    )
    extraPassive: list[NiceSkill] = Field(
        ...,
        title="Event Passive Skills",
        description="List of servant's extra event passive skills, (bond bonus, damage bonus, etc).",
    )
    appendPassive: list[NiceServantAppendPassiveSkill] = Field(
        ...,
        title="Append Passive skills",
        description="List of skills that can be added to servant and the number of materials required.",
    )
    noblePhantasms: list[NiceTd] = Field(
        ..., title="Noble Phantasm", description="List of servant's noble phantasms."
    )
    profile: Optional[NiceLore] = Field(
        None,
        title="Profile Details",
        description="Will be returned if `lore` query parameter is set to `true`",
    )


class NiceEquip(BaseModelORJson):
    id: int = Field(
        ...,
        title="Servant ID",
        description="svt's internal ID. "
        'Note that this is different from the 1~300 IDs shown in "Spirit Origin list", '
        "which is `.collectionNo`. "
        "This ID is unique accross svt items (servants, CEs, EXPs, enemies, …)",
    )
    collectionNo: int = Field(
        ...,
        title="Collection No",
        description='The ID number shown in "Spirit Origin list". '
        "The community usually means this number when they talk about servant or CE IDs.",
    )
    name: str = Field(..., title="svt's name", description="svt's name")
    originalName: str = Field(
        ..., title="untranslated svt name", description="untranslated svt name"
    )
    ruby: str = Field(
        ..., title="svt's name ruby text", description="svt's name ruby text"
    )
    type: NiceSvtType = Field(..., title="svt's type", description="svt's type.")
    flag: NiceSvtFlag = Field(
        ...,
        title="svt's flag",
        description="[DEPRECATED] Use the `flags` field. Some random flags given to the svt items.",
    )
    flags: list[NiceSvtFlagOriginal]
    rarity: int = Field(..., title="svt's rarity", description="svt's rarity.")
    cost: int = Field(
        ..., title="svt's cost", description="Cost to put the item in a party."
    )
    lvMax: int = Field(
        ...,
        title="svt's max level",
        description="Max level of the item without grailing.",
    )
    extraAssets: ExtraAssets = Field(
        ..., title="Image assets", description="Image assets."
    )
    atkBase: int = Field(..., title="Base ATK", description="Base ATK.")
    atkMax: int = Field(..., title="Max ATK", description="Max ATK (without grailing).")
    hpBase: int = Field(..., title="Base HP", description="Base HP.")
    hpMax: int = Field(..., title="Max HP", description="Max HP (without grailing).")
    growthCurve: int = Field(
        ..., title="Growth curve type", description="Growth curve type"
    )
    atkGrowth: list[int] = Field(
        ...,
        title="ATK value per level",
        description="ATK value per level, including grail levels.",
    )
    hpGrowth: list[int] = Field(
        ...,
        title="HP value per level",
        description="HP value per level, including grail levels.",
    )
    expGrowth: list[int] = Field(
        ...,
        title="Accumulated EXP",
        description="Total EXP needed per level. "
        'Equivalent to the "Accumulated EXP" value when feeding CE into another CE.',
    )
    expFeed: list[int] = Field(
        ...,
        title="Base EXP",
        description="Base EXP per level. "
        'Will show up as "Base EXP" when feeding the item into something else.',
    )
    bondEquipOwner: Optional[int] = Field(
        None,
        title="Bond Servant ID",
        description="Servant ID if this CE is a bond CE",
    )
    valentineEquipOwner: Optional[int] = Field(
        None,
        title="Valentine Servant ID",
        description="Servant ID if this CE is a valentine CE",
    )
    valentineScript: list[NiceValentineScript] = Field(
        [], title="Valentine Script", description="Array of length 1"
    )
    ascensionAdd: AscensionAdd = Field(
        ...,
        title="Ascension Add",
        description="Attributes that change when servants ascend.",
    )
    script: NiceServantScript = Field(
        ...,
        title="Servant Script",
        description="Random stuffs that get added to the servant entry. "
        "See each field description for more details.",
    )
    skills: list[NiceSkill] = Field(
        ..., title="Skills", description="list of servant or CE skills."
    )
    profile: Optional[NiceLore] = Field(
        None,
        title="Profile Details",
        description="Will be returned if `lore` query parameter is set to `true`",
    )


class NiceReversedSkillTd(BaseModelORJson):
    servant: list[NiceServant] = []
    MC: list[NiceMysticCode] = []
    CC: list[NiceCommandCode] = []


class NiceReversedSkillTdType(BaseModelORJson):
    nice: Optional[NiceReversedSkillTd] = None
    basic: Optional[BasicReversedSkillTd] = None


class NiceSkillReverse(NiceSkill):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceTdReverse(NiceTd):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceReversedFunction(BaseModelORJson):
    skill: list[NiceSkillReverse] = []
    NP: list[NiceTdReverse] = []


class NiceReversedFunctionType(BaseModelORJson):
    nice: Optional[NiceReversedFunction] = None
    basic: Optional[BasicReversedFunction] = None


class NiceBaseFunctionReverse(NiceBaseFunction):
    reverse: Optional[NiceReversedFunctionType] = None


class NiceReversedBuff(BaseModelORJson):
    function: list[NiceBaseFunctionReverse] = []


class NiceReversedBuffType(BaseModelORJson):
    nice: Optional[NiceReversedBuff] = None
    basic: Optional[BasicReversedBuff] = None


class NiceBuffReverse(NiceBuff):
    reverse: Optional[NiceReversedBuffType] = None


class NiceItemSet(BaseModelORJson):
    id: int
    purchaseType: NicePurchaseType
    targetId: int
    setNum: int
    gifts: list[NiceGift]


class NiceCommonConsume(BaseModelORJson):
    id: int
    priority: int
    type: NiceCommonConsumeType
    objectId: int
    num: int


class NiceShopRelease(BaseModelORJson):
    condValues: list[int]
    shopId: int
    condType: NiceCondType
    condNum: int
    priority: int
    isClosedDisp: bool
    closedMessage: str
    closedItemName: str


class NiceShop(BaseModelORJson):
    id: int
    baseShopId: int
    shopType: NiceShopType
    releaseConditions: list[NiceShopRelease]
    eventId: int
    slot: int = Field(..., title="Slot", description="Tab number in the shop")
    priority: int = Field(..., title="Priority", description="Sort order in the shop")
    name: str
    detail: str
    infoMessage: str
    warningMessage: str
    payType: NicePayType = Field(
        ..., title="Payment Type", description="Type of items to be used as payment."
    )
    cost: NiceItemAmount
    consumes: list[NiceCommonConsume] = Field(
        ..., title="Common Consume", description="If payType is commonConsume"
    )
    freeShopConds: list[NiceCommonRelease] = Field(..., title="Free Shop Conditions")
    freeShopReleaseDate: int | None = None
    freeShopCondMessage: str | None = None
    purchaseType: NicePurchaseType = Field(
        ..., title="Reward Type", description="Type of items to be received."
    )
    targetIds: list[int]
    itemSet: list[NiceItemSet] = Field(
        ...,
        title="List if item in the item set",
        description="If purchaseType is itemSet, this field will contain the item in the set.",
    )
    setNum: int = Field(
        ..., title="Set Number", description="Number of items per buying unit"
    )
    limitNum: int = Field(
        ..., title="Limit Number", description="Maximum number of buying units"
    )
    gifts: list[NiceGift] = Field(
        ..., title="Gift", description="If purchaseType is gift"
    )
    defaultLv: int
    defaultLimitCount: int
    scriptName: Optional[str] = None
    scriptId: Optional[str] = None
    script: Optional[HttpUrl] = None
    image: HttpUrl | None = None
    openedAt: int
    closedAt: int


class NiceBgmRelease(BaseModelORJson):
    id: int
    type: NiceCondType
    condGroup: int = Field(
        ...,
        title="Condition Group",
        description="To play the BGM, at least one condition group needs to be statisfied."
        "Within one condition group, all conditions need to be statisfied.",
    )
    targetIds: list[int]
    vals: list[int]
    priority: int
    closedMessage: str


class NiceBgm(BaseModelORJson):
    id: int
    name: str
    originalName: str
    fileName: str
    notReleased: bool
    audioAsset: Optional[HttpUrl] = None


class NiceBgmEntity(NiceBgm):
    priority: int
    detail: str
    shop: Optional[NiceShop] = None
    logo: HttpUrl
    releaseConditions: list[NiceBgmRelease]


class NiceEventQuest(BaseModelORJson):
    questId: int
    # phase: int


class NiceEventCampaign(BaseModelORJson):
    targetIds: list[int]
    warIds: list[int]
    target: NiceCombineAdjustTarget
    idx: int
    value: int
    calcType: NiceEventCombineCalc
    entryCondMessage: str


class NiceEventReward(BaseModelORJson):
    groupId: int
    point: int
    gifts: list[NiceGift]
    bgImagePoint: HttpUrl
    bgImageGet: HttpUrl


class NiceEventPointGroup(BaseModelORJson):
    groupId: int
    name: str
    icon: HttpUrl


class NiceEventPointBuff(BaseModelORJson):
    id: int
    funcIds: list[int]
    groupId: int
    eventPoint: int
    name: str
    detail: str
    icon: HttpUrl
    background: NiceItemBGType
    skillIcon: HttpUrl | None = None
    lv: int | None = None
    value: int


class NiceEventPointActivity(BaseModelORJson):
    groupId: int
    point: int
    objectType: EventPointActivityObjectType
    objectId: int
    objectValue: int


class NiceEventMissionConditionDetail(BaseModelORJson):
    id: int
    missionTargetId: int
    missionCondType: int
    logicType: int
    targetIds: list[int]
    addTargetIds: list[int]
    targetQuestIndividualities: list[NiceTrait]
    conditionLinkType: NiceDetailMissionCondLinkType
    targetEventIds: Optional[list[int]] = None


class NiceEventMissionCondition(BaseModelORJson):
    id: int
    missionProgressType: NiceMissionProgressType
    priority: int
    missionTargetId: int
    condGroup: int
    condType: NiceCondType
    targetIds: list[int]
    targetNum: int
    conditionMessage: str
    closedMessage: str
    flag: int
    details: list[NiceEventMissionConditionDetail] | None = None


class NiceEventMission(BaseModelORJson):
    id: int
    flag: int
    type: NiceMissionType
    missionTargetId: int
    dispNo: int
    name: str
    detail: str
    startedAt: int
    endedAt: int
    closedAt: int
    rewardType: NiceMissionRewardType
    gifts: list[NiceGift]
    bannerGroup: int
    priority: int
    rewardRarity: int
    notfyPriority: int
    presentMessageId: int
    conds: list[NiceEventMissionCondition]


class NiceEventMissionGroup(BaseModelORJson):
    id: int
    missionIds: list[int]


class NiceEventRandomMission(BaseModelORJson):
    missionId: int
    missionRank: int
    condType: NiceCondType
    condId: int
    condNum: int


class NiceEventTowerReward(BaseModelORJson):
    floor: int
    gifts: list[NiceGift]
    boardMessage: str
    rewardGet: HttpUrl
    banner: HttpUrl


class NiceEventTower(BaseModelORJson):
    towerId: int
    name: str
    rewards: list[NiceEventTowerReward]


class NiceEventLotteryBox(BaseModelORJson):
    id: int
    boxIndex: int
    talkId: int
    no: int
    type: int
    gifts: list[NiceGift]
    maxNum: int
    isRare: bool
    priority: int
    detail: str
    icon: HttpUrl
    banner: HttpUrl


class NiceEventLotteryTalk(BaseModelORJson):
    talkId: int
    no: int
    guideImageId: int
    beforeVoiceLines: list[NiceVoiceLine]
    afterVoiceLines: list[NiceVoiceLine]
    isRare: bool


class NiceEventLottery(BaseModelORJson):
    id: int
    slot: int
    payType: NicePayType
    cost: NiceItemAmount
    priority: int
    limited: bool
    boxes: list[NiceEventLotteryBox]
    talks: list[NiceEventLotteryTalk]


class NiceEventTreasureBoxGift(BaseModelORJson):
    id: int
    idx: int
    gifts: list[NiceGift]
    collateralUpperLimit: int


class NiceEventTreasureBox(BaseModelORJson):
    slot: int
    id: int
    idx: int
    treasureBoxGifts: list[NiceEventTreasureBoxGift]
    maxDrawNumOnce: int
    extraGifts: list[NiceGift]
    consumes: list[NiceCommonConsume]


class NiceEventDiggingBlock(BaseModelORJson):
    id: int
    eventId: int
    image: HttpUrl
    consumes: list[NiceCommonConsume]
    objectId: int
    diggingEventPoint: int
    blockNum: int


class NiceEventDiggingReward(BaseModelORJson):
    id: int
    # icon: Optional[HttpUrl] = None
    gifts: list[NiceGift]
    rewardSize: int


class NiceEventDigging(BaseModelORJson):
    sizeX: int
    sizeY: int
    bgImage: HttpUrl
    eventPointItem: NiceItem
    resettableDiggedNum: int
    blocks: list[NiceEventDiggingBlock]
    rewards: list[NiceEventDiggingReward]


class NiceEventCooltimeReward(BaseModelORJson):
    spotId: int
    lv: int
    name: str
    releaseConditions: list[NiceCommonRelease]
    cooltime: int
    addEventPointRate: int
    gifts: list[NiceGift]
    upperLimitGiftNum: int


class NiceEventCooltime(BaseModelORJson):
    rewards: list[NiceEventCooltimeReward]


class NiceEventBulletinBoardRelease(BaseModelORJson):
    condGroup: int
    condType: NiceCondType
    condTargetId: int
    condNum: int


class NiceEventBulletinBoardScript(BaseModelORJson):
    icon: HttpUrl | None = None
    name: str | None = None


class NiceEventBulletinBoard(BaseModelORJson):
    bulletinBoardId: int
    message: str
    probability: int | None = None
    dispOrder: int | None = None
    releaseConditions: list[NiceEventBulletinBoardRelease]
    script: list[NiceEventBulletinBoardScript] = []


class NiceEventRecipeGift(BaseModelORJson):
    idx: int
    displayOrder: int
    topIconId: int
    gifts: list[NiceGift]


class NiceEventRecipe(BaseModelORJson):
    id: int
    icon: HttpUrl
    name: str
    maxNum: int
    eventPointItem: NiceItem
    eventPointNum: int
    consumes: list[NiceCommonConsume]
    releaseConditions: list[NiceCommonRelease]
    closedMessage: str
    recipeGifts: list[NiceEventRecipeGift]


class NiceEventFortificationDetail(BaseModelORJson):
    position: int
    name: str
    className: NiceSvtClassSupportGroupType
    releaseConditions: list[NiceCommonRelease]


class NiceEventFortificationSvt(BaseModelORJson):
    position: int
    type: NiceEventFortificationSvtType
    svtId: int
    limitCount: int
    lv: int
    releaseConditions: list[NiceCommonRelease]


class NiceEventFortification(BaseModelORJson):
    idx: int
    name: str
    x: int
    y: int
    rewardSceneX: int
    rewardSceneY: int
    maxFortificationPoint: int
    workType: NiceEventWorkType
    gifts: list[NiceGift]
    releaseConditions: list[NiceCommonRelease]
    details: list[NiceEventFortificationDetail]
    servants: list[NiceEventFortificationSvt]


class NiceEventTradePickup(BaseModelORJson):
    startedAt: int
    endedAt: int
    # pickupIconId: int
    tradeTimeRate: int


class NiceEventTradeGoods(BaseModelORJson):
    id: int
    name: str
    goodsIcon: HttpUrl
    gifts: list[NiceGift]
    consumes: list[NiceCommonConsume]
    eventPointNum: int
    eventPointItem: NiceItem
    tradeTime: int
    maxNum: int
    maxTradeTime: int
    # presentMessageId: int
    releaseConditions: list[NiceCommonRelease]
    closedMessage: str
    # voiceData: dict[str,Any]
    pickups: list[NiceEventTradePickup]


class NiceEventRewardSceneGuide(BaseModelORJson):
    imageId: int
    limitCount: int
    image: HttpUrl
    faceId: int | None = None
    displayName: str | None = None
    weight: int | None = None
    unselectedMax: int | None = None


class NiceEventRewardScene(BaseModelORJson):
    slot: int
    groupId: int
    type: int = Field(
        ..., description="See Event Reward Scene Type in app/schemas/enums.py"
    )
    guides: list[NiceEventRewardSceneGuide]
    tabOnImage: HttpUrl
    tabOffImage: HttpUrl
    image: HttpUrl | None = None
    bg: HttpUrl
    bgm: NiceBgmEntity
    afterBgm: NiceBgmEntity
    flags: list[NiceEventRewardSceneFlag]


class NiceEventVoicePlay(BaseModelORJson):
    slot: int
    idx: int
    guideImageId: int
    voiceLines: list[NiceVoiceLine]
    confirmVoiceLines: list[NiceVoiceLine]
    condType: NiceCondType
    condValue: int = Field(..., description="Event ID")
    startedAt: int
    endedAt: int


class NiceEventCommandAssist(BaseModelORJson):
    id: int
    priority: int
    lv: int
    name: str
    assistCard: NiceCardType
    image: HttpUrl
    skill: NiceSkill
    skillLv: int
    releaseConditions: list[NiceCommonRelease]


class NiceHeelPortrait(BaseModelORJson):
    id: int
    name: str
    image: HttpUrl
    dispCondType: NiceCondType
    dispCondId: int
    dispCondNum: int
    script: dict[str, Any]


class NiceEventMural(BaseModelORJson):
    id: int
    message: str
    images: list[HttpUrl]
    num: int
    condQuestId: int
    condQuestPhase: int


class NiceEventAdd(BaseModelORJson):
    overwriteType: NiceEventOverwriteType
    priority: int
    overwriteId: int
    overwriteText: str
    overwriteBanner: HttpUrl | None = None
    condType: NiceCondType
    targetId: int
    startedAt: int
    endedAt: int


class NiceEventSvtScript(BaseModelORJson):
    addGetMessage: str | None = None
    addMessageReleaseConditions: list[NiceCommonRelease] | None = None
    isProtectedDuringEvent: bool | None = None
    joinQuestId: int | None = None
    joinShopId: int | None = None
    notPresentAnonymous: bool | None = None
    notPresentRarePri: int | None = None
    ruby: str | None = None


class NiceEventSvt(BaseModelORJson):
    svtId: int
    script: NiceEventSvtScript
    originalScript: dict[str, Any]
    type: NiceEventSvtType
    joinMessage: str
    getMessage: str
    leaveMessage: str
    name: str
    battleName: str
    releaseConditions: list[NiceCommonRelease]
    startedAt: int
    endedAt: int


class NiceWarBoardTreasure(BaseModelORJson):
    warBoardTreasureId: int
    rarity: NiceWarBoardTreasureRarity
    gifts: list[NiceGift]


class NiceWarBoardStageSquare(BaseModelORJson):
    squareIndex: int
    type: NiceWarBoardStageSquareType
    effectId: int
    treasures: list[NiceWarBoardTreasure]


class NiceWarBoardStage(BaseModelORJson):
    warBoardStageId: int
    boardMessage: str
    formationCost: int
    questId: int
    questPhase: int
    squares: list[NiceWarBoardStageSquare]


class NiceWarBoard(BaseModelORJson):
    warBoardId: int
    stages: list[NiceWarBoardStage]


class NiceEvent(BaseModelORJson):
    id: int
    type: NiceEventType
    name: str
    originalName: str
    shortName: str
    detail: str
    noticeBanner: Optional[HttpUrl] = None
    banner: Optional[HttpUrl] = None
    icon: Optional[HttpUrl] = None
    bannerPriority: int
    noticeAt: int
    startedAt: int
    endedAt: int
    finishedAt: int
    materialOpenedAt: int
    warIds: list[int]
    eventAdds: list[NiceEventAdd]
    svts: list[NiceEventSvt]
    shop: list[NiceShop]
    rewards: list[NiceEventReward]
    rewardScenes: list[NiceEventRewardScene]
    pointGroups: list[NiceEventPointGroup]
    pointBuffs: list[NiceEventPointBuff]
    pointActivities: list[NiceEventPointActivity]
    missions: list[NiceEventMission]
    randomMissions: list[NiceEventRandomMission]
    missionGroups: list[NiceEventMissionGroup]
    towers: list[NiceEventTower]
    lotteries: list[NiceEventLottery]
    warBoards: list[NiceWarBoard]
    treasureBoxes: list[NiceEventTreasureBox]
    bulletinBoards: list[NiceEventBulletinBoard]
    recipes: list[NiceEventRecipe]
    digging: NiceEventDigging | None = None
    cooltime: NiceEventCooltime | None = None
    fortifications: list[NiceEventFortification]
    tradeGoods: list[NiceEventTradeGoods]
    campaigns: list[NiceEventCampaign]
    campaignQuests: list[NiceEventQuest]
    commandAssists: list[NiceEventCommandAssist]
    heelPortraits: list[NiceHeelPortrait]
    murals: list[NiceEventMural]
    voicePlays: list[NiceEventVoicePlay]
    voices: list[NiceVoiceGroup] = Field(
        ..., description="All voice lines related to this event"
    )


class NiceCompleteMission(BaseModelORJson):
    # masterMissionId: int
    objectId: int
    presentMessageId: int
    gifts: list[NiceGift]
    bgm: NiceBgm | None = None


class NiceMasterMissionScript(BaseModelORJson):
    missionIconDetailText: str | None = None


class NiceMasterMission(BaseModelORJson):
    id: int
    startedAt: int
    endedAt: int
    closedAt: int
    script: NiceMasterMissionScript
    missions: list[NiceEventMission]
    completeMission: NiceCompleteMission | None = None
    quests: list[BasicQuest]


class NiceQuestRelease(BaseModelORJson):
    type: NiceCondType
    targetId: int
    value: int
    closedMessage: str


class NiceQuestReleaseOverwrite(BaseModelORJson):
    priority: int
    # imagePriority: int
    condType: NiceCondType
    condId: int
    condNum: int
    closedMessage: str
    overlayClosedMessage: str
    eventId: int
    startedAt: int
    endedAt: int


class NiceQuestPhaseScript(BaseModelORJson):
    phase: int
    scripts: list[ScriptLink]


class NiceQuestPhasePresent(BaseModelORJson):
    phase: int
    gifts: list[NiceGift]
    giftIcon: HttpUrl | None = None
    condType: NiceCondType
    condId: int
    condNum: int
    originalScript: dict[str, Any]


class NiceQuest(BaseModelORJson):
    id: int
    name: str
    originalName: str
    type: NiceQuestType
    flags: list[NiceQuestFlag]
    consumeType: NiceConsumeType
    consume: int
    consumeItem: list[NiceItemAmount]
    afterClear: NiceQuestAfterClearType
    recommendLv: str
    spotId: int
    spotName: str
    warId: int
    warLongName: str
    chapterId: int
    chapterSubId: int
    chapterSubStr: str
    giftIcon: HttpUrl | None = None
    gifts: list[NiceGift]
    releaseConditions: list[NiceQuestRelease]
    releaseOverwrites: list[NiceQuestReleaseOverwrite]
    presents: list[NiceQuestPhasePresent]
    phases: list[int]
    phasesWithEnemies: list[int] = Field(
        [],
        title="List of phases with enemies data from Rayshift",
        description="List of phases with enemies data from Rayshift.",
    )
    phasesNoBattle: list[int] = Field(
        [],
        title="List of phases with no battle",
        description="List of phases no battle (Story quest).",
    )
    phaseScripts: list[NiceQuestPhaseScript]
    priority: int
    noticeAt: int
    openedAt: int
    closedAt: int


class EnemyScript(BaseModelORJson):
    deathType: Optional[NiceSvtDeadType] = None
    appear: Optional[bool] = None
    noVoice: Optional[bool] = None
    raid: Optional[int] = None
    superBoss: Optional[int] = None
    hpBarType: Optional[int] = None
    leader: Optional[bool] = Field(None, title="Battle ends if servant is defeated")
    scale: Optional[int] = None
    svtVoiceId: Optional[int] = None
    treasureDeviceVoiceId: Optional[str] = None
    changeAttri: Optional[Attribute] = None
    billBoardGroup: Optional[int] = None
    multiTargetCore: Optional[bool] = None
    multiTargetUp: Optional[bool] = None
    multiTargetUnder: Optional[bool] = None
    startPos: Optional[bool] = None
    deadChangePos: Optional[int] = None
    call: Optional[list[int]] = Field(None, title="Summon these NPC IDs")
    shift: Optional[list[int]] = Field(None, title="Break bar switch to these NPC IDs")
    shiftPosition: Optional[int] = None
    shiftClear: list[NiceTrait] | None = Field(
        None, title="Active buff traits to remove with break bar"
    )
    skillShift: Optional[list[int]] = None
    missionTargetSkillShift: Optional[list[int]] = None
    change: Optional[list[int]] = None
    forceDropItem: Optional[bool] = None
    entryIndex: Optional[int] = None  # Only used for Rashomon raids
    treasureDeviceName: Optional[str] = None
    treasureDeviceRuby: Optional[str] = None
    npInfoEnable: Optional[bool] = None
    npCharge: Optional[int] = None
    NoSkipDead: Optional[bool] = None
    probability_type: int | None = None


class EnemyInfoScript(BaseModelORJson):
    isAddition: bool | None = None


class EnemySkill(BaseModelORJson):
    skillId1: int
    skillId2: int
    skillId3: int
    skill1: Optional[NiceSkill] = None
    skill2: Optional[NiceSkill] = None
    skill3: Optional[NiceSkill] = None
    skillLv1: int
    skillLv2: int
    skillLv3: int


class EnemyPassive(BaseModelORJson):
    classPassive: list[NiceSkill]
    addPassive: list[NiceSkill]
    addPassiveLvs: list[int] | None = None
    appendPassiveSkillIds: list[int] | None = None
    appendPassiveSkillLvs: list[int] | None = None


class EnemyTd(BaseModelORJson):
    noblePhantasmId: int
    noblePhantasm: Optional[NiceTd] = None
    noblePhantasmLv: int
    noblePhantasmLv1: int
    noblePhantasmLv2: int | None = None
    noblePhantasmLv3: int | None = None


class EnemyLimit(BaseModelORJson):
    limitCount: int
    imageLimitCount: int
    dispLimitCount: int
    commandCardLimitCount: int
    iconLimitCount: int
    portraitLimitCount: int
    battleVoice: int
    exceedCount: int


class EnemyServerMod(BaseModelORJson):
    tdRate: int = Field(
        ...,
        title="Attacking NP gain server mod",
        description="`enemyServerMod` when attacking: "
        "https://github.com/atlasacademy/fgo-game-data-docs/blob/master/battle/np.md#attacking-np",
    )
    tdAttackRate: int = Field(
        ...,
        title="Defending NP gain server mod",
        description="`enemyServerMod` when defending: "
        "https://github.com/atlasacademy/fgo-game-data-docs/blob/master/battle/np.md#defending-np",
    )
    starRate: int = Field(
        ...,
        title="Star drop rate server mod",
        description="`serverRate` when attacking: "
        "https://github.com/atlasacademy/fgo-game-data-docs/blob/master/battle/critstars.md",
    )


class EnemyAi(BaseModelORJson):
    aiId: int
    actPriority: int
    maxActNum: int
    minActNum: int | None = None


class EnemyMisc(BaseModelORJson):
    displayType: int
    npcSvtType: int
    passiveSkill: Optional[list[int]] = None
    equipTargetId1: int
    equipTargetIds: Optional[list[int]] = None
    npcSvtClassId: int
    overwriteSvtId: int
    userCommandCodeIds: list[int]
    commandCardParam: Optional[list[int]] = None
    status: int
    hpGaugeType: int | None = None
    imageSvtId: int | None = None
    condVal: int | None = None


class EnemyDrop(BaseModelORJson):
    type: NiceGiftType
    objectId: int
    num: int
    dropCount: int
    runs: int
    dropExpected: float
    dropVariance: float


class DeckType(StrEnum):
    ENEMY = "enemy"
    CALL = "call"
    SHIFT = "shift"
    CHANGE = "change"
    TRANSFORM = "transform"
    SKILL_SHIFT = "skillShift"
    MISSION_TARGET_SKILL_SHIFT = "missionTargetSkillShift"
    AI_NPC = "aiNpc"
    SVT_FOLLOWER = "svtFollower"


class QuestEnemy(BaseModelORJson):
    deck: DeckType
    deckId: int
    userSvtId: int
    uniqueId: int
    npcId: int
    roleType: EnemyRoleType
    name: str
    svt: BasicServant
    drops: list[EnemyDrop]
    lv: int
    exp: int
    atk: int
    hp: int
    adjustAtk: int
    adjustHp: int
    deathRate: int
    criticalRate: int
    recover: int
    chargeTurn: int
    traits: list[NiceTrait]
    skills: EnemySkill
    classPassive: EnemyPassive
    noblePhantasm: EnemyTd
    serverMod: EnemyServerMod
    ai: EnemyAi
    enemyScript: EnemyScript
    originalEnemyScript: dict[str, Any]
    infoScript: EnemyInfoScript
    originalInfoScript: dict[str, Any]
    limit: EnemyLimit
    misc: EnemyMisc


class FieldAi(BaseModelORJson):
    raid: Optional[int] = None
    day: Optional[int] = None
    id: int


class NiceStageStartMovie(BaseModelORJson):
    waveStartMovie: HttpUrl


class NiceStageCutInSkill(BaseModelORJson):
    skill: NiceSkill
    appearCount: int


class NiceStageCutIn(BaseModelORJson):
    runs: int
    skills: list[NiceStageCutInSkill]
    drops: list[EnemyDrop]


class NiceBattleBg(BaseModelORJson):
    id: int
    type: NiceBattleFieldEnvironmentGrantType
    priority: int
    individuality: list[NiceTrait]
    imageId: int


class NiceAiAllocation(BaseModelORJson):
    aiIds: list[int]
    individuality: NiceTrait
    applySvtType: list[NiceAiAllocationSvtFlag]


class NiceStage(BaseModelORJson):
    wave: int
    bgm: NiceBgm
    startEffectId: int
    fieldAis: list[FieldAi] = []
    call: list[int] = Field([], title="Summon these NPC IDs")
    enemyFieldPosCount: int | None = None
    enemyActCount: int | None = None
    turn: int | None = Field(None, title="Turn countdown")
    limitAct: StageLimitActType | None = Field(
        None, title="Action after turn countdown is over"
    )
    battleBg: NiceBattleBg | None = None
    NoEntryIds: list[int] | None = None
    waveStartMovies: list[NiceStageStartMovie] = []
    cutin: NiceStageCutIn | None = None
    aiAllocations: list[NiceAiAllocation] | None = None
    originalScript: dict[str, Any]
    enemies: list[QuestEnemy] = []


class NiceQuestMessage(BaseModelORJson):
    idx: int
    message: str
    condType: NiceCondType
    targetId: int
    targetNum: int


class NiceBattleMessage(BaseModelORJson):
    id: int
    idx: int
    priority: int
    releaseConditions: list[NiceCommonRelease]
    motionId: int
    message: str
    script: dict[str, Any]


class NiceBattleMessageGroup(BaseModelORJson):
    groupId: int
    probability: int
    messages: list[NiceBattleMessage]


class NiceQuestHint(BaseModelORJson):
    title: str
    message: str
    leftIndent: int


class SupportServantRelease(BaseModelORJson):
    type: NiceCondType
    targetId: int
    value: int


class SupportServantLimit(BaseModelORJson):
    limitCount: int


class SupportServantTd(BaseModelORJson):
    noblePhantasmId: int
    noblePhantasm: Optional[NiceTd] = None
    noblePhantasmLv: int


class SupportServantPassiveSkill(BaseModelORJson):
    skillId: int
    skill: NiceSkill | None = None
    skillLv: int | None = None


class SupportServantMisc(BaseModelORJson):
    followerFlag: int
    svtFollowerFlag: int


class SupportServantEquip(BaseModelORJson):
    equip: NiceEquip
    lv: int
    limitCount: int


class SupportServantScript(BaseModelORJson):
    dispLimitCount: Optional[int] = None
    eventDeckIndex: int | None = None


class NpcServant(BaseModelORJson):
    npcId: int
    name: str
    svt: BasicServant
    lv: int
    atk: int
    hp: int
    traits: list[NiceTrait]
    skills: EnemySkill
    noblePhantasm: SupportServantTd
    limit: SupportServantLimit
    flags: list[NiceNpcServantFollowerFlag]


class SupportServant(BaseModelORJson):
    id: int
    npcSvtFollowerId: int
    priority: int
    name: str
    originalName: str
    svt: BasicServant
    releaseConditions: list[SupportServantRelease]
    lv: int
    atk: int
    hp: int
    traits: list[NiceTrait]
    skills: EnemySkill
    noblePhantasm: SupportServantTd
    # passiveSkills: list[SupportServantPassiveSkill]
    flags: list[NiceNpcServantFollowerFlag]
    followerFlags: list[NiceNpcFollowerEntityFlag]
    equips: list[SupportServantEquip]
    script: SupportServantScript
    limit: SupportServantLimit
    misc: SupportServantMisc
    detail: QuestEnemy | None = None


class NiceQuestPhaseAiNpc(BaseModelORJson):
    npc: NpcServant
    detail: QuestEnemy | None = None
    aiIds: list[int]


class NiceQuestPhaseOverwriteEquipSkill(BaseModelORJson):
    lv: int
    id: int
    condId: int | None = None


class NiceQuestPhaseOverwriteEquipSkills(BaseModelORJson):
    iconId: int | None = None
    cutInView: int | None = None  # 1: ShowMasterSkillCutIn
    notDispEquipSkillIconSplit: int | None = None
    skills: list[NiceQuestPhaseOverwriteEquipSkill]


class NiceQuestPhaseExtraDetail(BaseModelORJson):
    questSelect: list[int] | None = None
    singleForceSvtId: int | None = None
    hintTitle: str | None = None
    hintMessage: str | None = None
    aiNpc: NiceQuestPhaseAiNpc | None = None
    aiMultiNpc: list[NiceQuestPhaseAiNpc] | None = None
    overwriteEquipSkills: NiceQuestPhaseOverwriteEquipSkills | None = None
    addEquipSkills: NiceQuestPhaseOverwriteEquipSkills | None = None
    waveSetup: int | None = None  # U Olga Marie Quest
    interruptibleQuest: int | None = None
    masterImageId: int | None = None
    IgnoreBattlePointUp: list[int] | None = None


class NiceRestriction(BaseModelORJson):
    id: int
    name: str
    type: NiceRestrictionType
    rangeType: NiceRestrictionRangeType
    targetVals: list[int]
    targetVals2: list[int]


class NiceQuestPhaseRestriction(BaseModelORJson):
    restriction: NiceRestriction
    frequencyType: NiceFrequencyType
    dialogMessage: str
    noticeMessage: str
    title: str


class NiceQuestPhase(NiceQuest):
    phase: int
    className: list[SvtClass | str]
    individuality: list[NiceTrait]
    qp: int
    exp: int
    bond: int
    isNpcOnly: bool
    battleBgId: int
    enemyHash: str | None = None
    availableEnemyHashes: list[str]
    dropsFromAllHashes: bool | None = None
    battleBg: NiceBattleBg | None = None
    extraDetail: NiceQuestPhaseExtraDetail
    scripts: list[ScriptLink]
    messages: list[NiceQuestMessage]
    hints: list[NiceQuestHint]
    restrictions: list[NiceQuestPhaseRestriction]
    supportServants: list[SupportServant]
    drops: list[EnemyDrop]
    stages: list[NiceStage]


class NiceScript(BaseModelORJson):
    scriptId: str
    scriptSizeBytes: int
    script: HttpUrl
    quests: list[NiceQuest]


class NiceScriptSearchResult(BaseModelORJson):
    scriptId: str
    script: HttpUrl
    score: float
    snippets: list[str]


class NiceSpotRoad(BaseModelORJson):
    id: int
    warId: int
    mapId: int
    image: HttpUrl
    srcSpotId: int
    dstSpotId: int
    dispCondType: NiceCondType
    dispTargetId: int
    dispTargetValue: int
    dispCondType2: NiceCondType
    dispTargetId2: int
    dispTargetValue2: int
    activeCondType: NiceCondType
    activeTargetId: int
    activeTargetValue: int


class NiceMapGimmick(BaseModel):
    id: int
    image: Optional[HttpUrl] = None
    x: int
    y: int
    depthOffset: int
    scale: int
    dispCondType: NiceCondType
    dispTargetId: int
    dispTargetValue: int
    dispCondType2: NiceCondType
    dispTargetId2: int
    dispTargetValue2: int
    actionAnimTime: int
    actionEffectId: int
    startedAt: int
    endedAt: int


class NiceMap(BaseModel):
    id: int
    mapImage: Optional[HttpUrl] = None
    mapImageW: int
    mapImageH: int
    mapGimmicks: list[NiceMapGimmick]
    headerImage: Optional[HttpUrl] = None
    bgm: NiceBgm


class NiceSpotAdd(BaseModel):
    # spotId: int
    priority: int
    overrideType: NiceSpotOverwriteType
    targetId: int
    targetText: str
    condType: NiceCondType
    condTargetId: int
    condNum: int


class NiceSpot(BaseModel):
    id: int
    blankEarth: bool
    joinSpotIds: list[int]
    mapId: int
    name: str
    originalName: str
    image: Optional[HttpUrl] = None
    x: Annotated[Decimal, DecimalSerializer]
    y: Annotated[Decimal, DecimalSerializer]
    imageOfsX: int
    imageOfsY: int
    nameOfsX: int
    nameOfsY: int
    questOfsX: int
    questOfsY: int
    nextOfsX: int
    nextOfsY: int
    closedMessage: str
    spotAdds: list[NiceSpotAdd]
    quests: list[NiceQuest]


class NiceWarAdd(BaseModelORJson):
    warId: int
    type: NiceWarOverwriteType
    priority: int
    overwriteId: int
    overwriteStr: str
    overwriteBanner: Optional[HttpUrl] = None
    condType: NiceCondType
    targetId: int
    value: int
    startedAt: int
    endedAt: int


class NiceWarQuestSelection(BaseModelORJson):
    quest: NiceQuest
    shortcutBanner: HttpUrl | None = None
    priority: int


class NiceWar(BaseModelORJson):
    id: int
    coordinates: list[list[Annotated[Decimal, DecimalSerializer]]]
    age: str
    name: str
    originalName: str
    longName: str
    originalLongName: str
    flags: list[NiceWarFlag]
    banner: Optional[HttpUrl] = None
    headerImage: Optional[HttpUrl] = None
    priority: int
    parentWarId: int
    materialParentWarId: int
    parentBlankEarthSpotId: int
    emptyMessage: str
    bgm: NiceBgm
    scriptId: str = Field(..., description='Could be "NONE".')
    script: HttpUrl
    startType: NiceWarStartType
    targetId: int
    eventId: int
    eventName: str
    lastQuestId: int
    warAdds: list[NiceWarAdd]
    maps: list[NiceMap]
    spots: list[NiceSpot]
    spotRoads: list[NiceSpotRoad]
    questSelections: list[NiceWarQuestSelection]


class NiceAiAct(BaseModelORJson):
    id: int
    type: NiceAiActType
    target: NiceAiActTarget
    targetIndividuality: list[NiceTrait]
    skillId: Optional[int] = None
    skillLv: Optional[int] = None
    skill: Optional[NiceSkill] = None
    noblePhantasmId: Optional[int] = None
    noblePhantasmLv: Optional[int] = None
    noblePhantasmOc: Optional[int] = None
    noblePhantasm: Optional[NiceTd] = None


class NiceAi(BaseModelORJson):
    id: int
    idx: int
    actNumInt: int
    actNum: NiceAiActNum
    priority: int
    probability: int
    cond: NiceAiCond
    condNegative: bool
    vals: list[int]
    aiAct: NiceAiAct
    avals: list[int]
    parentAis: dict[AiType, list[int]]
    infoText: str
    timing: Optional[int] = None
    timingDescription: Optional[AiTiming] = None


class NiceAiCollection(BaseModelORJson):
    mainAis: list[NiceAi]
    relatedAis: list[NiceAi]
    relatedQuests: list[StageLink]


class NiceClassBoardClass(BaseModelORJson):
    classId: int
    className: SvtClass | str
    condType: NiceCondType
    condTargetId: int
    condNum: int


class NiceClassBoardCommandSpell(BaseModelORJson):
    id: int
    commandSpellId: int
    name: str
    detail: str
    functions: list[NiceFunction]


class NiceClassBoardLock(BaseModelORJson):
    id: int
    items: list[NiceItemAmount]
    closedMessage: str
    condType: NiceCondType
    condTargetId: int
    condNum: int


class NiceClassBoardSquare(BaseModelORJson):
    id: int
    icon: HttpUrl | None = None
    items: list[NiceItemAmount]
    posX: int
    posY: int
    skillType: NiceClassBoardSkillType
    targetSkill: NiceSkill | None = None
    upSkillLv: int
    targetCommandSpell: NiceClassBoardCommandSpell | None = None
    lock: NiceClassBoardLock | None = None
    flags: list[NiceClassBoardSquareFlag]
    priority: int


class NiceClassBoardLine(BaseModelORJson):
    id: int
    prevSquareId: int
    nextSquareId: int


class NiceClassBoard(BaseModelORJson):
    id: int
    name: str
    icon: HttpUrl
    dispItems: list[NiceItem]
    closedMessage: str
    condType: NiceCondType
    condTargetId: int
    condNum: int
    classes: list[NiceClassBoardClass]
    squares: list[NiceClassBoardSquare]
    lines: list[NiceClassBoardLine]


class NiceFuncTypeDetail(BaseModelORJson):
    funcType: NiceFuncType
    ignoreValueUp: bool
    individuality: list[NiceTrait] | None = None


class NiceBuffTypeDetail(BaseModelORJson):
    buffType: NiceBuffType
    ignoreValueUp: bool
    script: dict[str, Any]


class GachaStoryAdjust(BaseModelORJson):
    idx: int
    adjustId: int
    condType: NiceCondType
    targetId: int
    value: int
    imageId: int


class NiceGacha(BaseModelORJson):
    id: int
    name: str
    imageId: int
    type: NicePayType
    adjustId: int
    pickupId: int
    drawNum1: int
    drawNum2: int
    maxDrawNum: int
    openedAt: int
    closedAt: int
    detailUrl: str
    flags: list[NiceGachaFlag]
    storyAdjusts: list[GachaStoryAdjust]
    featuredSvtIds: list[int]
