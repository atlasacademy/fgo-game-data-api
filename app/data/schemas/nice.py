from decimal import Decimal
from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl
from pydantic.generics import GenericModel

from ..enums import (
    Attribute,
    FuncApplyTarget,
    NiceBuffType,
    NiceCardType,
    NiceClassRelationOverwriteType,
    NiceCondType,
    NiceConsumeType,
    NiceEventType,
    NiceFuncTargetType,
    NiceFuncType,
    NiceGender,
    NiceItemBGType,
    NiceItemType,
    NiceQuestType,
    NiceSkillType,
    NiceStatusRank,
    NiceSvtFlag,
    NiceSvtType,
    NiceSvtVoiceType,
    NiceVoiceCondType,
    NiceWarStartType,
    SvtClass,
)
from .base import BaseModelORJson
from .basic import BasicReversedBuff, BasicReversedFunction, BasicReversedSkillTd
from .common import MCAssets, NiceTrait


class AssetURL:
    charaGraph = {
        1: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@1.png",
        2: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a@2.png",
        3: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@1.png",
        4: "{base_url}/{region}/CharaGraph/{item_id}/{item_id}b@2.png",
    }
    commands = "{base_url}/{region}/Servants/Commands/{item_id}/card_servant_{i}.png"
    status = "{base_url}/{region}/Servants/Status/{item_id}/status_servant_{i}.png"
    charaGraphDefault = "{base_url}/{region}/CharaGraph/{item_id}/{item_id}a.png"
    charaFigure = "{base_url}/{region}/CharaFigure/{item_id}{i}/{item_id}{i}_merged.png"
    charaFigureForm = "{base_url}/{region}/CharaFigure/Form/{form_id}/{svtScript_id}/{svtScript_id}_merged.png"
    narrowFigure = {
        1: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png",
        2: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@1.png",
        3: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@2.png",
        4: "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}_2@0.png",
    }
    narrowFigureDefault = "{base_url}/{region}/NarrowFigure/{item_id}/{item_id}@0.png"
    skillIcon = "{base_url}/{region}/SkillIcons/skill_{item_id:05}.png"
    buffIcon = "{base_url}/{region}/BuffIcons/bufficon_{item_id}.png"
    items = "{base_url}/{region}/Items/{item_id}.png"
    face = "{base_url}/{region}/Faces/f_{item_id}{i}.png"
    equipFace = "{base_url}/{region}/EquipFaces/f_{item_id}{i}.png"
    enemy = "{base_url}/{region}/Enemys/{item_id}{i}.png"
    mcitem = "{base_url}/{region}/Items/masterequip{item_id:05}.png"
    mc = {
        "item": "{base_url}/{region}/Items/masterequip{item_id:05}.png",
        "masterFace": "{base_url}/{region}/MasterFace/equip{item_id:05}.png",
        "masterFigure": "{base_url}/{region}/MasterFigure/equip{item_id:05}.png",
    }
    commandCode = "{base_url}/{region}/CommandCodes/c_{item_id}.png"
    commandGraph = "{base_url}/{region}/CommandGraph/{item_id}a.png"
    audio = "{base_url}/{region}/Audio/{folder}/{id}.mp3"
    banner = "{base_url}/{region}/Banner/{banner}.png"
    mapImg = "{base_url}/{region}/Terminal/MapImgs/img_questmap_{map_id:0>6}/img_questmap_{map_id:0>6}.png"
    spotImg = "{base_url}/{region}/Terminal/QuestMap/Capter{war_asset_id:0>4}/QMap_Cap{war_asset_id:0>4}_Atlas/spot_{spot_id:0>6}.png"


class NiceItem(BaseModelORJson):
    id: int
    name: str
    type: NiceItemType
    detail: str
    icon: HttpUrl
    background: NiceItemBGType


class NiceItemAmount(BaseModel):
    item: NiceItem
    amount: int


class NiceLvlUpMaterial(BaseModel):
    items: List[NiceItemAmount]
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
    TargetList: Optional[List[int]] = None
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
    TargetRarityList: Optional[List[int]] = None
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
    AndCheckIndividualityList: Optional[List[int]] = None
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
    # These are not DataVals but guesses from SkillLvEntity and EventDropUpValInfo
    Individuality: Optional[int] = None
    EventId: Optional[int] = None
    AddCount: Optional[int] = None
    RateCount: Optional[int] = None
    # aa0: Optional[int] = None
    # aa1: Optional[int] = None
    # aa2: Optional[int] = None
    # aa3: Optional[int] = None
    # aa4: Optional[int] = None


class Vals(BaseVals):
    DependFuncVals: Optional[BaseVals] = None


class RelationOverwriteDetail(BaseModelORJson):
    damageRate: int
    type: NiceClassRelationOverwriteType


class NiceBuffRelationOverwrite(BaseModelORJson):
    atkSide: Dict[SvtClass, Dict[SvtClass, RelationOverwriteDetail]]
    defSide: Dict[SvtClass, Dict[SvtClass, RelationOverwriteDetail]]


class NiceBuffScript(BaseModelORJson):
    relationId: Optional[NiceBuffRelationOverwrite] = None
    ReleaseText: Optional[str] = None
    DamageRelease: Optional[int] = None
    INDIVIDUALITIE: Optional[NiceTrait] = None


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
    vals: List[NiceTrait] = Field(
        ...,
        title="Buff individualities",
        description="Buff traits/individualities. "
        "For example, buff removal uses this field to target the buffs.",
    )
    tvals: List[NiceTrait] = Field(
        ...,
        title="Buff tvals",
        description="Buff tvals: I'm quite sure this field is used for "
        "visual purposes only and not gameplay.",
    )
    ckSelfIndv: List[NiceTrait] = Field(
        ...,
        title="Check self individualities",
        description="Buff holder's required individuality for the buff's effect to apply.",
    )
    ckOpIndv: List[NiceTrait] = Field(
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
    functvals: List[NiceTrait] = Field(
        ...,
        title="Function tvals",
        description="Function tvals: If available, function's targets or their buffs "
        "need to satisfy the traits given here.",
    )
    funcquestTvals: List[NiceTrait] = Field(
        ...,
        title="Function quest traits",
        description="Function quest traits. "
        "The current quest needs this traits for the function to works.",
    )
    traitVals: List[NiceTrait] = Field(
        [],
        title="Trait details",
        description="Trait details for buff removal functions.",
    )
    buffs: List[NiceBuff] = Field(
        ..., title="Buff details", description="Buff details for apply buff functions."
    )


class NiceFunction(NiceBaseFunction):
    svals: List[Vals] = Field(
        ...,
        title="Parameter values by skill level or NP level",
        description="Parameter values by skill level or NP level",
    )
    svals2: Optional[List[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 2",
        description="Parameter values for NP Overcharge level 2 by NP level",
    )
    svals3: Optional[List[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 3",
        description="Parameter values for NP Overcharge level 3 by NP level",
    )
    svals4: Optional[List[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 4",
        description="Parameter values for NP Overcharge level 4 by NP level",
    )
    svals5: Optional[List[Vals]] = Field(
        None,
        title="Parameter values for NP Overcharge level 5",
        description="Parameter values for NP Overcharge level 5 by NP level",
    )
    followerVals: Optional[List[Vals]] = Field(
        None,
        title="Parameter values when used by a support servant",
        description="Parameter values when used by a support servant. "
        "If the function comes from a support servant, the values here will be "
        "used if available, e.g. Chaldea Teatime.",
    )


class NiceSkillScript(BaseModel):
    NP_HIGHER: Optional[List[int]] = None
    NP_LOWER: Optional[List[int]] = None
    STAR_HIGHER: Optional[List[int]] = None
    STAR_LOWER: Optional[List[int]] = None
    HP_VAL_HIGHER: Optional[List[int]] = None
    HP_VAL_LOWER: Optional[List[int]] = None
    HP_PER_HIGHER: Optional[List[int]] = None
    HP_PER_LOWER: Optional[List[int]] = None


class NiceSkill(BaseModelORJson):
    id: int
    num: int = -1
    name: str
    detail: Optional[str] = None
    type: NiceSkillType
    strengthStatus: int = -1
    priority: int = -1
    condQuestId: int = -1
    condQuestPhase: int = -1
    icon: Optional[HttpUrl] = None
    coolDown: List[int]
    actIndividuality: List[NiceTrait]
    script: NiceSkillScript
    functions: List[NiceFunction]


class NpGain(BaseModel):
    buster: List[int]
    arts: List[int]
    quick: List[int]
    extra: List[int]
    defence: List[int]
    np: List[int]


class NiceTd(BaseModelORJson):
    id: int
    num: int
    card: NiceCardType
    name: str
    icon: Optional[HttpUrl] = None
    rank: str
    type: str
    detail: Optional[str] = None
    npGain: NpGain
    npDistribution: List[int]
    strengthStatus: int
    priority: int
    condQuestId: int
    condQuestPhase: int
    individuality: List[NiceTrait]
    functions: List[NiceFunction]


class ExtraMCAssets(BaseModel):
    item: MCAssets
    masterFace: MCAssets
    masterFigure: MCAssets


class NiceMysticCode(BaseModelORJson):
    id: int
    name: str
    detail: str
    maxLv: int
    extraAssets: ExtraMCAssets
    skills: List[NiceSkill]
    expRequired: List[int]


class ExtraAssetsUrl(BaseModel):
    ascension: Optional[Dict[int, HttpUrl]] = None
    costume: Optional[Dict[int, HttpUrl]] = None
    equip: Optional[Dict[int, HttpUrl]] = None
    cc: Optional[Dict[int, HttpUrl]] = None


class ExtraCCAssets(BaseModel):
    charaGraph: ExtraAssetsUrl
    faces: ExtraAssetsUrl


class ExtraAssets(ExtraCCAssets):
    narrowFigure: ExtraAssetsUrl
    charaFigure: ExtraAssetsUrl
    charaFigureForm: Dict[int, ExtraAssetsUrl]
    commands: ExtraAssetsUrl
    status: ExtraAssetsUrl
    equipFace: ExtraAssetsUrl


AscensionAddData = TypeVar("AscensionAddData")


class AscensionAddEntry(GenericModel, Generic[AscensionAddData]):
    ascension: Dict[int, AscensionAddData] = Field(
        ...,
        title="Ascension changes",
        description="Mapping <Ascension level, Ascension level data>.",
    )
    costume: Dict[int, AscensionAddData] = Field(
        ..., title="Costume changes", description="Mapping <Costume ID, Costume data>."
    )


class AscensionAdd(BaseModel):
    individuality: AscensionAddEntry[List[NiceTrait]] = Field(
        ...,
        title="Individuality changes",
        description="Some servants add or remove traits as they ascend.",
    )
    voicePrefix: AscensionAddEntry[int] = Field(
        ...,
        title="Voice prefix changes",
        description="Some servants change voice lines as they ascennd.",
    )


class NiceServantChange(BaseModel):
    beforeTreasureDeviceIds: List[int]
    afterTreasureDeviceIds: List[int]
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


class NiceLoreComment(BaseModel):
    id: int
    priority: int
    condMessage: str
    comment: str
    condType: NiceCondType
    condValues: Optional[List[int]]
    condValue2: int


class NiceLoreStats(BaseModel):
    strength: NiceStatusRank  # power
    endurance: NiceStatusRank  # defense
    agility: NiceStatusRank
    magic: NiceStatusRank
    luck: NiceStatusRank
    np: NiceStatusRank  # treasureDevice
    # policy: NiceStatusRank
    # personality: NiceStatusRank
    # deity: NiceStatusRank


class NiceCostume(BaseModel):
    id: int
    costumeCollectionNo: int
    name: str
    shortName: str
    detail: str
    priority: int


class NiceVoiceCond(BaseModel):
    condType: NiceVoiceCondType = Field(
        ..., title="Voice Cond Type", description="Voice Condition Type Enum"
    )
    value: int = Field(
        ..., title="Voice Cond Value", description="Threshold value for the condtion."
    )
    valueList: List[int] = Field(
        [],
        title="Voice Cond Value List",
        description="If the voice cond is `svtGroup`, "
        "this list will hold the applicable servant IDs.",
    )
    eventId: int = Field(..., title="Event ID", description="Event ID.")


class NiceVoiceLine(BaseModel):
    name: Optional[str] = Field(
        None, title="Voice line default name", description="Voice line default name."
    )
    condType: Optional[NiceCondType] = Field(
        None,
        title="Voice line default condition type",
        description="Voice line default condition type.",
    )
    condValue: Optional[int] = Field(
        None,
        title="Voice line default condition value",
        description="Voice line default condition threshold value.",
    )
    priority: Optional[int] = Field(
        None,
        title="Voice line default priority",
        description="Voice line default priority.",
    )
    svtVoiceType: Optional[NiceSvtVoiceType] = Field(
        None, title="Voice line default type", description="Voice line default type."
    )
    overwriteName: str = Field(
        ..., title="Voice line overwrite name", description="Voice line overwrite name."
    )
    id: List[str] = Field(..., title="Voice line IDs", description="Voice line IDs.")
    audioAssets: List[str] = Field(
        ..., title="Voice line mp3 URLs", description="Voice line mp3 URLs."
    )
    delay: List[Decimal] = Field(
        ...,
        title="Voice line delays",
        description="Delays in seconds before playing the audio file.",
    )
    face: List[int] = Field(
        ...,
        title="Voice line faces",
        description="CharaFigure faces to be used when playing the voice line.",
    )
    form: List[int] = Field(
        ...,
        title="Voice line forms",
        description="CharaFigure forms to be used when playing the voice line.",
    )
    text: List[str] = Field(
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
    conds: List[NiceVoiceCond] = Field(
        ...,
        title="Voice line conditions",
        description="Conditions to make the voice line available.",
    )


class NiceVoiceGroup(BaseModel):
    svtId: int
    voicePrefix: int
    type: NiceSvtVoiceType
    voiceLines: List[NiceVoiceLine]


class NiceLore(BaseModel):
    cv: str
    illustrator: str
    stats: Optional[NiceLoreStats] = None
    costume: Dict[int, NiceCostume]
    comments: List[NiceLoreComment]
    voices: List[NiceVoiceGroup]


class NiceServantScript(BaseModel):
    SkillRankUp: Optional[Dict[int, List[int]]] = Field(
        None,
        title="SkillRankUp",
        description="Mapping <Skill IDs, List[Skill IDs]>. "
        "Summer Kiara 1st skill additional data. "
        "The keys are the base skill IDs and the values are the rank-up skill IDs.",
    )


class NiceCommandCode(BaseModelORJson):
    id: int
    collectionNo: int
    name: str
    rarity: int
    extraAssets: ExtraCCAssets
    skills: List[NiceSkill]
    illustrator: str
    comment: str


class NiceServant(BaseModelORJson):
    id: int = Field(
        ...,
        title="Servant ID",
        description="svt's internal ID. "
        'Note that this is different from the 1~300 IDs shown in "Spirit Origin List", '
        "which is `.collectionNo`. "
        "This ID is unique accross svt items (servants, CEs, EXPs, enemies, …)",
    )
    collectionNo: int = Field(
        ...,
        title="Collection No",
        description='The ID number shown in "Spirit Origin List". '
        "The community usually means this number when they talk about servant or CE IDs.",
    )
    name: str = Field(..., title="svt's name", description="svt's name")
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
    traits: List[NiceTrait] = Field(
        ...,
        title="List of traits",
        description="List of individualities, or commonly refered to as traits.",
    )
    starAbsorb: int = Field(..., title="Star weight", description="Star weight.")
    starGen: int = Field(..., title="Star rate", description="Star generation rate.")
    instantDeathChance: int = Field(
        ..., title="Instant death chance", description="Instant death chance."
    )
    cards: List[NiceCardType] = Field(..., title="Card deck", description="Card deck.")
    hitsDistribution: Dict[NiceCardType, List[int]] = Field(
        ...,
        title="Hits distribution",
        description="Mapping <Card type, Hits distribution>.",
    )
    atkBase: int = Field(..., title="Base ATK", description="Base ATK.")
    atkMax: int = Field(..., title="Max ATK", description="Max ATK (without grailing).")
    hpBase: int = Field(..., title="Base HP", description="Base HP.")
    hpMax: int = Field(..., title="Max HP", description="Max HP (without grailing).")
    relateQuestIds: List[int] = Field(
        ...,
        title="Related quest IDs",
        description="IDs of related quests: rank-ups or interludes.",
    )
    growthCurve: int = Field(
        ..., title="Growth curve type", description="Growth curve type"
    )
    atkGrowth: List[int] = Field(
        ...,
        title="ATK value per level",
        description="ATK value per level, including grail levels.",
    )
    hpGrowth: List[int] = Field(
        ...,
        title="HP value per level",
        description="HP value per level, including grail levels.",
    )
    bondGrowth: List[int] = Field(
        ...,
        title="Bond EXP needed per bond level",
        description="Bond EXP needed per bond level",
    )
    expGrowth: List[int] = Field(
        ...,
        title="Accumulated EXP",
        description="Total EXP needed per level. "
        'Equivalent to the "Accumulated EXP" value when feeding CE into another CE.',
    )
    expFeed: List[int] = Field(
        ...,
        title="Base EXP",
        description="Base EXP per level. "
        'Will show up as "Base EXP" when feeding the item into something else.',
    )
    bondEquip: int = Field(
        ..., title="Bond CE", description="Bond CE ID (not collectionNo)."
    )
    ascensionAdd: AscensionAdd = Field(
        ...,
        title="Ascension Add",
        description="Attributes that change when servants ascend.",
    )
    svtChange: List[NiceServantChange] = Field(
        ..., title="Servant Change", description="EOR servants' hidden name details."
    )
    ascensionMaterials: Dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Ascension Materials",
        description="Mapping <Ascension level, Materials to ascend servants>.",
    )
    skillMaterials: Dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Skill Materials",
        description="Mapping <Skill level, Materials to level up skills>.",
    )
    costumeMaterials: Dict[int, NiceLvlUpMaterial] = Field(
        ...,
        title="Costume Materials",
        description="Mapping <Costume svt ID, Materials to unlock the costume>. "
        "Costume details can be found in `.profile.costume`",
    )
    script: NiceServantScript = Field(
        ...,
        title="Servant Script",
        description="Random stuffs that get added to the servant entry. "
        "See each field description for more details.",
    )
    skills: List[NiceSkill] = Field(
        ..., title="Skills", description="List of servant or CE skills."
    )
    classPassive: List[NiceSkill] = Field(
        ..., title="Passive Skills", description="List of servant's passive skills."
    )
    noblePhantasms: List[NiceTd] = Field(
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
        'Note that this is different from the 1~300 IDs shown in "Spirit Origin List", '
        "which is `.collectionNo`. "
        "This ID is unique accross svt items (servants, CEs, EXPs, enemies, …)",
    )
    collectionNo: int = Field(
        ...,
        title="Collection No",
        description='The ID number shown in "Spirit Origin List". '
        "The community usually means this number when they talk about servant or CE IDs.",
    )
    name: str = Field(..., title="svt's name", description="svt's name")
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
    atkGrowth: List[int] = Field(
        ...,
        title="ATK value per level",
        description="ATK value per level, including grail levels.",
    )
    hpGrowth: List[int] = Field(
        ...,
        title="HP value per level",
        description="HP value per level, including grail levels.",
    )
    expGrowth: List[int] = Field(
        ...,
        title="Accumulated EXP",
        description="Total EXP needed per level. "
        'Equivalent to the "Accumulated EXP" value when feeding CE into another CE.',
    )
    expFeed: List[int] = Field(
        ...,
        title="Base EXP",
        description="Base EXP per level. "
        'Will show up as "Base EXP" when feeding the item into something else.',
    )
    skills: List[NiceSkill] = Field(
        ..., title="Skills", description="List of servant or CE skills."
    )
    profile: Optional[NiceLore] = Field(
        None,
        title="Profile Details",
        description="Will be returned if `lore` query parameter is set to `true`",
    )


class NiceReversedSkillTd(BaseModelORJson):
    servant: List[NiceServant] = []
    MC: List[NiceMysticCode] = []
    CC: List[NiceCommandCode] = []


class NiceReversedSkillTdType(BaseModelORJson):
    nice: Optional[NiceReversedSkillTd] = None
    basic: Optional[BasicReversedSkillTd] = None


class NiceSkillReverse(NiceSkill):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceTdReverse(NiceTd):
    reverse: Optional[NiceReversedSkillTdType] = None


class NiceReversedFunction(BaseModelORJson):
    skill: List[NiceSkillReverse] = []
    NP: List[NiceTdReverse] = []


class NiceReversedFunctionType(BaseModelORJson):
    nice: Optional[NiceReversedFunction] = None
    basic: Optional[BasicReversedFunction] = None


class NiceBaseFunctionReverse(NiceBaseFunction):
    reverse: Optional[NiceReversedFunctionType] = None


class NiceReversedBuff(BaseModelORJson):
    function: List[NiceBaseFunctionReverse] = []


class NiceReversedBuffType(BaseModelORJson):
    nice: Optional[NiceReversedBuff] = None
    basic: Optional[BasicReversedBuff] = None


class NiceBuffReverse(NiceBuff):
    reverse: Optional[NiceReversedBuffType] = None


class NiceEvent(BaseModelORJson):
    id: int
    type: NiceEventType
    name: str
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
    warIds: List[int]


class NiceBgm(BaseModelORJson):
    id: int
    name: str
    audioAsset: Optional[HttpUrl] = None


class NiceQuestRelease(BaseModelORJson):
    type: NiceCondType
    targetId: int
    value: int
    closedMessage: str


class NiceQuest(BaseModelORJson):
    id: int
    name: str
    type: NiceQuestType
    consumeType: NiceConsumeType
    consume: int
    spotId: int
    warId: int
    releaseConditions: List[NiceQuestRelease]
    phases: List[int]
    noticeAt: int
    openedAt: int
    closedAt: int


class NiceStage(BaseModelORJson):
    bgm: NiceBgm


class NiceQuestPhase(NiceQuest):
    phase: int
    className: List[SvtClass]
    individuality: List[NiceTrait]
    qp: int
    exp: int
    bond: int
    stages: List[NiceStage]


class NiceMap(BaseModel):
    id: int
    mapImage: Optional[HttpUrl] = None
    mapImageW: int
    mapImageH: int
    headerImage: Optional[HttpUrl] = None
    bgm: NiceBgm


class NiceSpot(BaseModel):
    id: int
    joinSpotIds: List[int]
    mapId: int
    name: str
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
    quests: List[NiceQuest]


class NiceWar(BaseModelORJson):
    id: int
    coordinates: List[List[int]]
    age: str
    name: str
    longName: str
    banner: Optional[HttpUrl] = None
    headerImage: Optional[HttpUrl] = None
    priority: int
    parentWarId: int
    materialParentWarId: int
    emptyMessage: str
    bgm: NiceBgm
    scriptId: str
    startType: NiceWarStartType
    targetId: int
    eventId: int
    lastQuestId: int
    maps: List[NiceMap]
    spots: List[NiceSpot]
