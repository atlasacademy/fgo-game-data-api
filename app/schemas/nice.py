from decimal import Decimal
from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

from .base import BaseModelORJson
from .basic import (
    BasicQuest,
    BasicReversedBuff,
    BasicReversedFunction,
    BasicReversedSkillTd,
    BasicServant,
)
from .common import (
    MCAssets,
    NiceBuffScript,
    NiceCostume,
    NiceTrait,
    NiceValentineScript,
    ScriptLink,
    StageLink,
)
from .enums import (
    AiTiming,
    AiType,
    Attribute,
    EnemyDeathType,
    EnemyRoleType,
    FuncApplyTarget,
    NiceDetailMissionCondLinkType,
    NiceItemBGType,
    NiceItemUse,
    NiceSkillType,
    ServantPersonality,
    ServantPolicy,
    SvtClass,
)
from .gameenums import (
    NiceAiActNum,
    NiceAiActTarget,
    NiceAiActType,
    NiceAiCond,
    NiceBuffType,
    NiceCardType,
    NiceCommonConsumeType,
    NiceCondType,
    NiceConsumeType,
    NiceEventRewardSceneFlag,
    NiceEventType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceGiftType,
    NiceItemType,
    NiceMissionProgressType,
    NiceMissionRewardType,
    NiceMissionType,
    NicePayType,
    NicePurchaseType,
    NiceQuestAfterClearType,
    NiceQuestFlag,
    NiceQuestType,
    NiceShopType,
    NiceStatusRank,
    NiceSvtFlag,
    NiceSvtType,
    NiceSvtVoiceType,
    NiceTdEffectFlag,
    NiceVoiceCondType,
    NiceWarFlag,
    NiceWarOverwriteType,
    NiceWarStartType,
)


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
    eventUi = "{base_url}/{region}/EventUI/{event}.png"
    eventReward = "{base_url}/{region}/EventReward/{fname}.png"
    mapImg = "{base_url}/{region}/Terminal/MapImgs/img_questmap_{map_id:0>6}/img_questmap_{map_id:0>6}.png"
    mapGimmickImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/gimmick_{gimmick_id:0>6}.png"
    spotImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/spot_{spot_id:0>6}.png"
    spotRoadImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/img_road{war_asset_id:0>4}_00.png"
    script = "{base_url}/{region}/Script/{script_path}.txt"
    bgmLogo = "{base_url}/{region}/MyRoomSound/soundlogo_{logo_id:0>3}.png"
    servantModel = "{base_url}/{region}/Servants/{item_id}/manifest.json"


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
    priority: int
    dropPriority: int


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: list[NiceItemAmount]
    qp: int


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
    AllowSubBgmPlaying: int | None = None
    NotAccompanyWhenLinkedTargetMoveState: int | None = None
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


class Vals(BaseVals):
    DependFuncVals: Optional[BaseVals] = None


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
        description="Buff group. "
        "See https://github.com/atlasacademy/fgo-docs#unstackable-buffs "
        "for how this field is used.",
    )
    script: NiceBuffScript = Field(
        ...,
        title="Buff script",
        description="Random stuffs that get added to the buff entry. "
        "See each field description for more details.",
    )
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
    funcquestTvals: list[NiceTrait] = Field(
        ...,
        title="Function quest traits",
        description="Function quest traits. "
        "The current quest needs this traits for the function to works.",
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
    startedAt: int
    endedAt: int


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


class NiceSkillAdd(BaseModelORJson):
    priority: int
    releaseConditions: list[NiceCommonRelease]
    name: str
    ruby: str


class NiceSkill(BaseModelORJson):
    id: int
    num: int = -1
    name: str
    originalName: str
    ruby: str
    detail: Optional[str] = None
    unmodifiedDetail: Optional[str] = None
    type: NiceSkillType
    strengthStatus: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    condLv: int = -1
    condLimitCount: int = -1
    icon: Optional[HttpUrl] = None
    coolDown: list[int]
    actIndividuality: list[NiceTrait]
    script: NiceSkillScript
    extraPassive: list[ExtraPassive]
    skillAdd: list[NiceSkillAdd]
    aiIds: Optional[dict[AiType, list[int]]] = None
    functions: list[NiceFunction]


class NpGain(BaseModel):
    buster: list[int]
    arts: list[int]
    quick: list[int]
    extra: list[int]
    defence: list[int]
    np: list[int]


class NiceTd(BaseModelORJson):
    id: int
    num: int
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
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: list[NiceTrait]
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
    originalName: str
    detail: str
    maxLv: int
    extraAssets: ExtraMCAssets
    skills: list[NiceSkill]
    expRequired: list[int]
    costumes: list[NiceMysticCodeCostume]


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
    attackIndividuality: list[NiceTrait]


AscensionAddData = TypeVar("AscensionAddData")


class AscensionAddEntry(GenericModel, Generic[AscensionAddData]):
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


class AscensionAdd(BaseModel):
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
    condValues: Optional[list[int]]
    condValue2: int
    additionalConds: list[NiceLoreCommentAdd]


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


class NiceVoiceCond(BaseModel):
    condType: NiceVoiceCondType = Field(
        ..., title="Voice Cond Type", description="Voice Condition Type Enum"
    )
    value: int = Field(
        ..., title="Voice Cond Value", description="Threshold value for the condtion."
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
        title="[DEPRECIATED, use condValues] Voice play condition target value."
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
    delay: list[Decimal] = Field(
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
    className: SvtClass = Field(
        ...,
        title="svt's class",
        description="svt's class. "
        "Because enemies also use this model, you can see some non-playable classes "
        "as possible values.",
    )
    type: NiceSvtType = Field(..., title="svt's type", description="svt's type.")
    flag: NiceSvtFlag = Field(
        ..., title="svt's flag", description="Some random flags given to the svt items."
    )
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
        ..., title="svt's flag", description="Some random flags given to the svt items."
    )
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
    defaultLv: int
    defaultLimitCount: int
    scriptName: Optional[str] = None
    scriptId: Optional[str] = None
    script: Optional[HttpUrl] = None
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


class NiceBgmEntity(BaseModelORJson):
    id: int
    name: str
    originalName: str
    fileName: str
    audioAsset: Optional[HttpUrl] = None
    priority: int
    detail: str
    notReleased: bool
    shop: Optional[NiceShop] = None
    logo: HttpUrl
    releaseConditions: list[NiceBgmRelease]


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
    value: int


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
    detail: Optional[NiceEventMissionConditionDetail] = None


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


class NiceCommonConsume(BaseModelORJson):
    id: int
    priority: int
    type: NiceCommonConsumeType
    objectId: int
    num: int


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
    commonConsume: NiceCommonConsume


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
    shop: list[NiceShop]
    rewards: list[NiceEventReward]
    rewardScenes: list[NiceEventRewardScene]
    pointGroups: list[NiceEventPointGroup]
    pointBuffs: list[NiceEventPointBuff]
    missions: list[NiceEventMission]
    towers: list[NiceEventTower]
    lotteries: list[NiceEventLottery]
    treasureBoxes: list[NiceEventTreasureBox]
    voicePlays: list[NiceEventVoicePlay]
    voices: list[NiceVoiceGroup] = Field(
        ..., description="All voice lines related to this event"
    )


class NiceMasterMission(BaseModelORJson):
    id: int
    startedAt: int
    endedAt: int
    closedAt: int
    missions: list[NiceEventMission]
    quests: list[BasicQuest]


class NiceBgm(BaseModelORJson):
    id: int
    name: str
    fileName: str
    notReleased: bool
    audioAsset: Optional[HttpUrl] = None


class NiceQuestRelease(BaseModelORJson):
    type: NiceCondType
    targetId: int
    value: int
    closedMessage: str


class NiceQuestPhaseScript(BaseModelORJson):
    phase: int
    scripts: list[ScriptLink]


class NiceQuest(BaseModelORJson):
    id: int
    name: str
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
    gifts: list[NiceGift]
    releaseConditions: list[NiceQuestRelease]
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
    noticeAt: int
    openedAt: int
    closedAt: int


class EnemyScript(BaseModelORJson):
    deathType: Optional[EnemyDeathType]
    appear: Optional[bool]
    noVoice: Optional[bool]
    raid: Optional[int]
    superBoss: Optional[int]
    hpBarType: Optional[int]
    leader: Optional[bool] = Field(None, title="Battle ends if servant is defeated")
    scale: Optional[int]
    svtVoiceId: Optional[int]
    treasureDeviceVoiceId: Optional[str]
    changeAttri: Optional[Attribute]
    billBoardGroup: Optional[int]
    multiTargetCore: Optional[bool]
    multiTargetUp: Optional[bool]
    multiTargetUnder: Optional[bool]
    startPos: Optional[bool]
    deadChangePos: Optional[int]
    call: Optional[list[int]] = Field(None, title="Summon these NPC IDs")
    shift: Optional[list[int]] = Field(None, title="Break bar switch to these NPC IDs")
    shiftPosition: Optional[int]
    shiftClear: list[NiceTrait] = Field(
        None, title="Active buff traits to remove with break bar"
    )
    skillShift: Optional[list[int]]
    missionTargetSkillShift: Optional[list[int]]
    change: Optional[list[int]]
    forceDropItem: Optional[bool]
    entryIndex: Optional[int]  # Only used for Rashomon raids
    treasureDeviceName: Optional[str]
    treasureDeviceRuby: Optional[str]
    npInfoEnable: Optional[bool]
    npCharge: Optional[int]
    NoSkipDead: Optional[bool]


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


class EnemyTd(BaseModelORJson):
    noblePhantasmId: int
    noblePhantasm: Optional[NiceTd] = None
    noblePhantasmLv: int
    noblePhantasmLv1: int


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


class EnemyDrop(BaseModelORJson):
    type: NiceGiftType
    objectId: int
    num: int
    dropCount: int
    runs: int
    dropExpected: float
    dropVariance: float


class DeckType(str, Enum):
    ENEMY = "enemy"
    CALL = "call"
    SHIFT = "shift"
    CHANGE = "change"
    TRANSFORM = "transform"
    SKILL_SHIFT = "skillShift"
    MISSION_TARGET_SKILL_SHIFT = "missionTargetSkillShift"


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
    limit: EnemyLimit
    misc: EnemyMisc


class FieldAi(BaseModelORJson):
    raid: Optional[int] = None
    day: Optional[int] = None
    id: int


class NiceStage(BaseModelORJson):
    wave: int
    bgm: NiceBgm
    fieldAis: list[FieldAi] = []
    call: list[int] = Field([], title="Summon these NPC IDs")
    enemies: list[QuestEnemy] = []


class NiceQuestMessage(BaseModelORJson):
    idx: int
    message: str
    condType: NiceCondType
    targetId: int
    targetNum: int


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


class SupportServantMisc(BaseModelORJson):
    followerFlag: int
    svtFollowerFlag: int


class SupportServantEquip(BaseModelORJson):
    equip: NiceEquip
    lv: int
    limitCount: int


class SupportServantScript(BaseModelORJson):
    dispLimitCount: Optional[int] = None


class SupportServant(BaseModelORJson):
    id: int
    priority: int
    name: str
    svt: BasicServant
    releaseConditions: list[SupportServantRelease]
    lv: int
    atk: int
    hp: int
    traits: list[NiceTrait]
    skills: EnemySkill
    noblePhantasm: SupportServantTd
    equips: list[SupportServantEquip]
    script: SupportServantScript
    limit: SupportServantLimit
    misc: SupportServantMisc


class NiceQuestPhaseExtraDetail(BaseModelORJson):
    questSelect: list[int] | None = None
    singleForceSvtId: int | None = None


class NiceQuestPhase(NiceQuest):
    phase: int
    className: list[SvtClass]
    individuality: list[NiceTrait]
    qp: int
    exp: int
    bond: int
    isNpcOnly: bool
    battleBgId: int
    extraDetail: NiceQuestPhaseExtraDetail
    scripts: list[ScriptLink]
    messages: list[NiceQuestMessage]
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
    image: Optional[HttpUrl]
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


class NiceSpot(BaseModel):
    id: int
    joinSpotIds: list[int]
    mapId: int
    name: str
    originalName: str
    image: Optional[HttpUrl] = None
    x: int
    y: int
    imageOfsX: int
    imageOfsY: int
    nameOfsX: int
    nameOfsY: int
    questOfsX: int
    questOfsY: int
    nextOfsX: int
    nextOfsY: int
    closedMessage: str
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


class NiceWar(BaseModelORJson):
    id: int
    coordinates: list[list[Decimal]]
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
    emptyMessage: str
    bgm: NiceBgm
    scriptId: str
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


class NiceAiAct(BaseModelORJson):
    id: int
    type: NiceAiActType
    target: NiceAiActTarget
    targetIndividuality: list[NiceTrait]
    skillId: Optional[int] = None
    skillLv: Optional[int] = None
    skill: Optional[NiceSkill] = None


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
