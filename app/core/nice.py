import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Union

import orjson
from fastapi import HTTPException
from sqlalchemy.engine import Connection

from ..config import Settings
from ..data.gamedata import masters
from ..data.translations import TRANSLATIONS
from ..schemas.basic import (
    BasicReversedBuff,
    BasicReversedFunction,
    BasicReversedSkillTd,
)
from ..schemas.common import Language, Region, ReverseData, ReverseDepth
from ..schemas.enums import (
    AI_ACT_NUM_NAME,
    AI_ACT_TARGET_NAME,
    AI_ACT_TYPE_NAME,
    AI_COND_NAME,
    AI_TIMING_NAME,
    ATTRIBUTE_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    CLASS_NAME,
    CLASS_OVERWRITE_NAME,
    COND_TYPE_NAME,
    EVENT_TYPE_NAME,
    FUNC_APPLYTARGET_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    FUNC_VALS_NOT_BUFF,
    GENDER_TYPE_NAME,
    GIFT_TYPE_NAME,
    ITEM_BG_TYPE_NAME,
    ITEM_TYPE_NAME,
    PAY_TYPE_NAME,
    PURCHASE_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SHOP_TYPE_NAME,
    SKILL_TYPE_NAME,
    STATUS_RANK_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    WAR_START_TYPE_NAME,
    AiTiming,
    AiType,
    FuncType,
    NiceAiActNum,
    NiceItemUse,
    NiceStatusRank,
    PayType,
    SvtClass,
    SvtType,
    SvtVoiceType,
    VoiceCondType,
    WarEntityFlag,
)
from ..schemas.nice import (
    AssetURL,
    NiceAi,
    NiceAiAct,
    NiceAiFull,
    NiceBaseFunctionReverse,
    NiceBgm,
    NiceBuffReverse,
    NiceCommandCode,
    NiceCostume,
    NiceEquip,
    NiceEvent,
    NiceFuncGroup,
    NiceGift,
    NiceItem,
    NiceItemAmount,
    NiceLoreComment,
    NiceMap,
    NiceMysticCode,
    NiceQuest,
    NiceQuestPhase,
    NiceQuestRelease,
    NiceReversedBuff,
    NiceReversedBuffType,
    NiceReversedFunction,
    NiceReversedFunctionType,
    NiceReversedSkillTd,
    NiceReversedSkillTdType,
    NiceServant,
    NiceServantChange,
    NiceShop,
    NiceSkillReverse,
    NiceSpot,
    NiceStage,
    NiceTdReverse,
    NiceVoiceCond,
    NiceVoiceGroup,
    NiceVoiceLine,
    NiceWar,
)
from ..schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    BuffEntityNoReverse,
    FunctionEntityNoReverse,
    GlobalNewMstSubtitle,
    MstAiAct,
    MstClassRelationOverwrite,
    MstFuncGroup,
    MstMap,
    MstQuestRelease,
    MstShop,
    MstSpot,
    MstStage,
    MstSvtChange,
    MstSvtComment,
    MstSvtCostume,
    MstSvtVoice,
    OneAiEntity,
    QuestEntity,
    QuestPhaseEntity,
    ScriptJson,
    ScriptJsonCond,
    SkillEntityNoReverse,
    TdEntityNoReverse,
)
from . import raw
from .basic import (
    get_basic_cc,
    get_basic_function,
    get_basic_mc,
    get_basic_servant,
    get_basic_skill,
    get_basic_td,
)
from .utils import get_nice_trait, get_safe, get_traits_list


FORMATTING_BRACKETS = {"[g][o]": "", "[/o][/g]": "", " [{0}] ": " ", "[{0}]": ""}

MASH_SVT_ID = 800100
MASH_VALENTINE_EQUIP = {
    Region.NA: [9800700, 9806620],
    Region.JP: [9800700, 9806620, 9807240],
}

settings = Settings()


def strip_formatting_brackets(detail_string: str) -> str:
    for k, v in FORMATTING_BRACKETS.items():
        detail_string = detail_string.replace(k, v)
    return detail_string


def get_nice_status_rank(rank_number: int) -> NiceStatusRank:
    return STATUS_RANK_NAME.get(rank_number, NiceStatusRank.unknown)


def nullable_to_string(nullable: Optional[str]) -> str:
    if nullable is None:
        return ""
    else:
        return nullable


def remove_brackets(val_string: str) -> str:
    if val_string[0] == "[":
        val_string = val_string[1:]
    if val_string[-1] == "]":
        val_string = val_string[:-1]
    return val_string


EVENT_DROP_FUNCTIONS = {
    FuncType.EVENT_POINT_UP,
    FuncType.EVENT_POINT_RATE_UP,
    FuncType.EVENT_DROP_UP,
    FuncType.EVENT_DROP_RATE_UP,
}
EVENT_FUNCTIONS = EVENT_DROP_FUNCTIONS | {
    FuncType.ENEMY_ENCOUNT_COPY_RATE_UP,
    FuncType.ENEMY_ENCOUNT_RATE_UP,
}
FRIEND_SUPPORT_FUNCTIONS = {
    FuncType.SERVANT_FRIENDSHIP_UP,
    FuncType.USER_EQUIP_EXP_UP,
    FuncType.EXP_UP,
    FuncType.QP_DROP_UP,
    FuncType.QP_UP,
}


def parse_dataVals(
    datavals: str, functype: int, region: Region
) -> Dict[str, Union[int, str, List[int]]]:
    error_message = f"Can't parse datavals: {datavals}"

    output: Dict[str, Union[int, str, List[int]]] = {}
    if datavals != "[]":
        datavals = remove_brackets(datavals)
        array = re.split(r",\s*(?![^\[\]]*])", datavals)
        for i, arrayi in enumerate(array):
            text = ""
            value = -98765
            try:
                value = int(arrayi)
                if functype in {
                    FuncType.DAMAGE_NP_INDIVIDUAL,
                    FuncType.DAMAGE_NP_STATE_INDIVIDUAL,
                    FuncType.DAMAGE_NP_STATE_INDIVIDUAL_FIX,
                    FuncType.DAMAGE_NP_INDIVIDUAL_SUM,
                    FuncType.DAMAGE_NP_RARE,
                }:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Target"
                    elif i == 3:
                        text = "Correction"
                elif functype in {FuncType.ADD_STATE, FuncType.ADD_STATE_SHORT}:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Turn"
                    elif i == 2:
                        text = "Count"
                    elif i == 3:
                        text = "Value"
                    elif i == 4:
                        text = "UseRate"
                    elif i == 5:
                        text = "Value2"
                elif functype == FuncType.SUB_STATE:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Value2"
                elif functype in EVENT_FUNCTIONS:
                    if i == 0:
                        text = "Individuality"
                    elif i == 3:
                        text = "EventId"
                    else:
                        text = "aa" + str(i)
                elif functype == FuncType.CLASS_DROP_UP:
                    if i == 2:
                        text = "EventId"
                    else:
                        text = "aa" + str(i)
                elif functype == FuncType.ENEMY_PROB_DOWN:
                    if i == 0:
                        text = "Individuality"
                    elif i == 1:
                        text = "RateCount"
                    elif i == 2:
                        text = "EventId"
                elif functype in FRIEND_SUPPORT_FUNCTIONS:
                    if i == 2:
                        text = "Individuality"
                    else:
                        text = "aa" + str(i)
                elif functype in {
                    FuncType.FRIEND_POINT_UP,
                    FuncType.FRIEND_POINT_UP_DUPLICATE,
                }:
                    if i == 0:
                        text = "AddCount"
                else:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Target"
            except ValueError:
                array2 = re.split(r":\s*(?![^\[\]]*])", arrayi)
                if len(array2) > 1:
                    if array2[0] == "DependFuncId1":
                        output["DependFuncId"] = int(remove_brackets(array2[1]))
                    elif array2[0] == "DependFuncVals1":
                        # This assumes DependFuncId is parsed before.
                        # If DW ever make it more complicated than this, consider
                        # using "aa" + ... and parse it later
                        func_type = masters[region].mstFuncId[output["DependFuncId"]].funcType  # type: ignore
                        vals_value = parse_dataVals(array2[1], func_type, region)
                        output["DependFuncVals"] = vals_value  # type: ignore
                    elif array2[0] in {
                        "TargetList",
                        "TargetRarityList",
                        "AndCheckIndividualityList",
                    }:
                        try:
                            output[array2[0]] = [int(i) for i in array2[1].split("/")]
                        except ValueError:
                            raise HTTPException(status_code=500, detail=error_message)
                    else:
                        try:
                            text = array2[0]
                            value = int(array2[1])
                        except ValueError:
                            raise HTTPException(status_code=500, detail=error_message)
                else:
                    raise HTTPException(status_code=500, detail=error_message)

            if text:
                output[text] = value

    if functype in EVENT_FUNCTIONS:
        if output["aa1"] == 1:
            output["AddCount"] = output["aa2"]
        elif output["aa1"] == 2:
            output["RateCount"] = output["aa2"]
    elif functype in {FuncType.CLASS_DROP_UP} | FRIEND_SUPPORT_FUNCTIONS:
        if output["aa0"] == 1:
            output["AddCount"] = output["aa1"]
        elif output["aa0"] == 2:
            output["RateCount"] = output["aa1"]

    return output


def get_nice_buff(buffEntity: BuffEntityNoReverse, region: Region) -> Dict[str, Any]:
    buffInfo: Dict[str, Any] = {
        "id": buffEntity.mstBuff.id,
        "name": buffEntity.mstBuff.name,
        "detail": buffEntity.mstBuff.detail,
        "type": BUFF_TYPE_NAME[buffEntity.mstBuff.type],
        "buffGroup": buffEntity.mstBuff.buffGroup,
        "vals": get_traits_list(buffEntity.mstBuff.vals),
        "tvals": get_traits_list(buffEntity.mstBuff.tvals),
        "ckSelfIndv": get_traits_list(buffEntity.mstBuff.ckSelfIndv),
        "ckOpIndv": get_traits_list(buffEntity.mstBuff.ckOpIndv),
        "maxRate": buffEntity.mstBuff.maxRate,
    }

    iconId = buffEntity.mstBuff.iconId
    if iconId != 0:
        buffInfo["icon"] = AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    script: Dict[str, Any] = {}
    if "relationId" in buffEntity.mstBuff.script:
        relationOverwrite: List[MstClassRelationOverwrite] = masters[
            region
        ].mstClassRelationOverwriteId.get(buffEntity.mstBuff.script["relationId"], [])
        relationId: Dict[str, Dict[SvtClass, Dict[SvtClass, Any]]] = {
            "atkSide": defaultdict(dict),
            "defSide": defaultdict(dict),
        }
        for relation in relationOverwrite:
            if relation.atkSide == 1:
                side = "atkSide"
            else:
                side = "defSide"
            atkClass = CLASS_NAME[relation.atkClass]
            defClass = CLASS_NAME[relation.defClass]
            relationDetail = {
                "damageRate": relation.damageRate,
                "type": CLASS_OVERWRITE_NAME[relation.type],
            }
            relationId[side][atkClass][defClass] = relationDetail
        script["relationId"] = relationId

    for script_item in ("ReleaseText", "DamageRelease"):
        if script_item in buffEntity.mstBuff.script:
            script[script_item] = buffEntity.mstBuff.script[script_item]

    if "INDIVIDUALITIE" in buffEntity.mstBuff.script:
        script["INDIVIDUALITIE"] = get_nice_trait(
            buffEntity.mstBuff.script["INDIVIDUALITIE"]
        )

    buffInfo["script"] = script

    return buffInfo


def get_func_group_icon(region: Region, funcType: int, iconId: int) -> Optional[str]:
    if iconId == 0:
        return None

    base_settings = {"base_url": settings.asset_url, "region": region}
    if funcType in EVENT_DROP_FUNCTIONS:
        return AssetURL.items.format(**base_settings, item_id=iconId)
    else:
        return AssetURL.eventUi.format(
            **base_settings, event=f"func_group_icon_{iconId}"
        )


def get_nice_func_group(
    region: Region, funcGroup: MstFuncGroup, funcType: int
) -> NiceFuncGroup:
    return NiceFuncGroup(
        eventId=funcGroup.eventId,
        baseFuncId=funcGroup.baseFuncId,
        nameTotal=funcGroup.nameTotal,
        name=funcGroup.name,
        icon=get_func_group_icon(region, funcType, funcGroup.iconId),
        priority=funcGroup.priority,
        isDispValue=funcGroup.isDispValue,
    )


def get_nice_base_function(
    function: FunctionEntityNoReverse, region: Region
) -> Dict[str, Any]:
    functionInfo: Dict[str, Any] = {
        "funcId": function.mstFunc.id,
        "funcPopupText": function.mstFunc.popupText,
        "funcquestTvals": get_traits_list(function.mstFunc.questTvals),
        "functvals": get_traits_list(function.mstFunc.tvals),
        "funcType": FUNC_TYPE_NAME[function.mstFunc.funcType],
        "funcTargetTeam": FUNC_APPLYTARGET_NAME[function.mstFunc.applyTarget],
        "funcTargetType": FUNC_TARGETTYPE_NAME[function.mstFunc.targetType],
        "funcGroup": [
            get_nice_func_group(region, func_group, function.mstFunc.funcType)
            for func_group in function.mstFuncGroup
        ],
        "buffs": [
            get_nice_buff(buff, region) for buff in function.mstFunc.expandedVals
        ],
    }

    if function.mstFunc.funcType in FUNC_VALS_NOT_BUFF:
        functionInfo["traitVals"] = get_traits_list(function.mstFunc.vals)

    funcPopupIconId = function.mstFunc.popupIconId
    if funcPopupIconId != 0:
        functionInfo["funcPopupIcon"] = AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=funcPopupIconId
        )
    return functionInfo


def get_ai_id_from_skill(region: Region, skill_id: int) -> Dict[AiType, List[int]]:
    return {
        AiType.svt: sorted(
            set(
                ai.id
                for ai_act_id in masters[region].skillToAiAct.get(skill_id, [])
                for ai in masters[region].aiActToAiSvt.get(ai_act_id, [])
            )
        ),
        AiType.field: sorted(
            set(
                ai.id
                for ai_act_id in masters[region].skillToAiAct.get(skill_id, [])
                for ai in masters[region].aiActToAiField.get(ai_act_id, [])
            )
        ),
    }


def get_nice_skill(
    skillEntity: SkillEntityNoReverse, svtId: int, region: Region
) -> Dict[str, Any]:
    nice_skill: Dict[str, Any] = {
        "id": skillEntity.mstSkill.id,
        "name": skillEntity.mstSkill.name,
        "ruby": skillEntity.mstSkill.ruby,
        "type": SKILL_TYPE_NAME[skillEntity.mstSkill.type],
        "actIndividuality": get_traits_list(skillEntity.mstSkill.actIndividuality),
    }

    iconId = skillEntity.mstSkill.iconId
    if iconId != 0:
        nice_skill["icon"] = AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    if skillEntity.mstSkillDetail:
        nice_skill["detail"] = strip_formatting_brackets(
            skillEntity.mstSkillDetail[0].detail
        )

    # .mstSvtSkill returns the list of SvtSkill with the same skill_id
    if skillEntity.mstSvtSkill:
        chosenSvt = next(
            svt_skill
            for svt_skill in skillEntity.mstSvtSkill
            if svt_skill.svtId == svtId
        )
        if chosenSvt:
            # Wait for 3.9 for PEP 584 to use |=
            nice_skill.update(
                {
                    "strengthStatus": chosenSvt.strengthStatus,
                    "num": chosenSvt.num,
                    "priority": chosenSvt.priority,
                    "condQuestId": chosenSvt.condQuestId,
                    "condQuestPhase": chosenSvt.condQuestPhase,
                    "condLv": chosenSvt.condLv,
                    "condLimitCount": chosenSvt.condLimitCount,
                }
            )

    aiIds = get_ai_id_from_skill(region, skillEntity.mstSkill.id)
    if aiIds[AiType.svt] or aiIds[AiType.field]:
        nice_skill["aiIds"] = aiIds

    nice_skill["coolDown"] = [
        skill_lv.chargeTurn for skill_lv in skillEntity.mstSkillLv
    ]

    nice_skill["script"] = {
        scriptKey: [skillLv.script[scriptKey] for skillLv in skillEntity.mstSkillLv]
        for scriptKey in skillEntity.mstSkillLv[0].script
    }

    nice_skill["functions"] = []
    for funci, _ in enumerate(skillEntity.mstSkillLv[0].funcId):
        function = skillEntity.mstSkillLv[0].expandedFuncId[funci]
        functionInfo = get_nice_base_function(function, region)
        functionInfo["svals"] = [
            parse_dataVals(skill_lv.svals[funci], function.mstFunc.funcType, region)
            for skill_lv in skillEntity.mstSkillLv
        ]
        if "followerVals" in skillEntity.mstSkillLv[0].script:
            functionInfo["followerVals"] = [
                parse_dataVals(
                    skill_lv.script["followerVals"][funci],
                    function.mstFunc.funcType,
                    region,
                )
                for skill_lv in skillEntity.mstSkillLv
            ]
        nice_skill["functions"].append(functionInfo)

    return nice_skill


def get_nice_td(
    tdEntity: TdEntityNoReverse, svtId: int, region: Region
) -> Dict[str, Any]:
    nice_td: Dict[str, Any] = {
        "id": tdEntity.mstTreasureDevice.id,
        "name": tdEntity.mstTreasureDevice.name,
        "ruby": tdEntity.mstTreasureDevice.ruby,
        "rank": tdEntity.mstTreasureDevice.rank,
        "type": tdEntity.mstTreasureDevice.typeText,
        "individuality": get_traits_list(tdEntity.mstTreasureDevice.individuality),
    }

    if tdEntity.mstTreasureDeviceDetail:
        nice_td["detail"] = strip_formatting_brackets(
            tdEntity.mstTreasureDeviceDetail[0].detail
        )

    nice_td["npGain"] = {
        "buster": [td_lv.tdPointB for td_lv in tdEntity.mstTreasureDeviceLv],
        "arts": [td_lv.tdPointA for td_lv in tdEntity.mstTreasureDeviceLv],
        "quick": [td_lv.tdPointQ for td_lv in tdEntity.mstTreasureDeviceLv],
        "extra": [td_lv.tdPointEx for td_lv in tdEntity.mstTreasureDeviceLv],
        "np": [td_lv.tdPoint for td_lv in tdEntity.mstTreasureDeviceLv],
        "defence": [td_lv.tdPointDef for td_lv in tdEntity.mstTreasureDeviceLv],
    }

    chosenSvt = next(
        svt_td for svt_td in tdEntity.mstSvtTreasureDevice if svt_td.svtId == svtId
    )
    if chosenSvt:
        imageId = chosenSvt.imageIndex
        base_settings_id = {
            "base_url": settings.asset_url,
            "region": region,
            "item_id": svtId,
        }
        if imageId < 2:
            file_i = "np"
        else:
            file_i = "np" + str(imageId // 2)
        nice_td.update(
            {
                "icon": AssetURL.commands.format(**base_settings_id, i=file_i),
                "strengthStatus": chosenSvt.strengthStatus,
                "num": chosenSvt.num,
                "priority": chosenSvt.priority,
                "condQuestId": chosenSvt.condQuestId,
                "condQuestPhase": chosenSvt.condQuestPhase,
                "card": CARD_TYPE_NAME[chosenSvt.cardId],
                "npDistribution": chosenSvt.damage,
            }
        )

    nice_td["functions"] = []

    for funci, _ in enumerate(tdEntity.mstTreasureDeviceLv[0].funcId):
        function = tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci]
        functionInfo = get_nice_base_function(function, region)
        for sval in ["svals", "svals2", "svals3", "svals4", "svals5"]:
            functionInfo[sval] = [
                parse_dataVals(
                    getattr(mst_td, sval)[funci], function.mstFunc.funcType, region
                )
                for mst_td in tdEntity.mstTreasureDeviceLv
            ]
        nice_td["functions"].append(functionInfo)

    return nice_td


def get_nice_servant_change(change: MstSvtChange) -> NiceServantChange:
    return NiceServantChange(
        beforeTreasureDeviceIds=change.beforeTreasureDeviceIds,
        afterTreasureDeviceIds=change.afterTreasureDeviceIds,
        svtId=change.svtId,
        priority=change.priority,
        condType=COND_TYPE_NAME[change.condType],
        condTargetId=change.condTargetId,
        condValue=change.condValue,
        name=change.name,
        svtVoiceId=change.svtVoiceId,
        limitCount=change.limitCount,
        flag=change.flag,
        battleSvtId=change.battleSvtId,
    )


def get_item_use(region: Region, item_id: int) -> List[NiceItemUse]:
    item_uses: List[NiceItemUse] = []

    for use_type, use_table in (
        (NiceItemUse.skill, masters[region].mstCombineSkillItem),
        (NiceItemUse.ascension, masters[region].mstCombineLimitItem),
        (NiceItemUse.costume, masters[region].mstCombineCostumeItem),
    ):
        if item_id in use_table:
            item_uses.append(use_type)

    return item_uses


def get_nice_item(region: Region, item_id: int) -> NiceItem:
    raw_data = masters[region].mstItemId[item_id]
    return NiceItem(
        id=item_id,
        name=raw_data.name,
        type=ITEM_TYPE_NAME[raw_data.type],
        uses=get_item_use(region, item_id),
        detail=raw_data.detail,
        individuality=get_traits_list(raw_data.individuality),
        icon=AssetURL.items.format(
            base_url=settings.asset_url, region=region, item_id=raw_data.imageId
        ),
        background=ITEM_BG_TYPE_NAME[raw_data.bgImageId],
        priority=raw_data.priority,
        dropPriority=raw_data.dropPriority,
    )


def get_nice_item_amount(
    region: Region, item_list: List[int], amount_list: List[int]
) -> List[NiceItemAmount]:
    return [
        NiceItemAmount(item=get_nice_item(region, item_id), amount=amount)
        for item_id, amount in zip(item_list, amount_list)
    ]


def get_nice_comment(comment: MstSvtComment) -> NiceLoreComment:
    return NiceLoreComment(
        id=comment.id,
        priority=comment.priority,
        condMessage=comment.condMessage,
        comment=comment.comment,
        condType=COND_TYPE_NAME[comment.condType],
        condValues=comment.condValues,
        condValue2=comment.condValue2,
    )


def get_illustrator_name(region: Region, illustratorId: int) -> str:
    if illustratorId in masters[region].mstIllustratorId:
        return masters[region].mstIllustratorId[illustratorId].name
    else:
        return ""


def get_cv_name(region: Region, cvId: int) -> str:
    if cvId in masters[region].mstCvId:
        return masters[region].mstCvId[cvId].name
    else:
        return ""


def get_nice_costume(costume: MstSvtCostume) -> NiceCostume:
    return NiceCostume(**costume.dict())


def get_voice_folder(voice_type: int) -> str:
    if voice_type == SvtVoiceType.BATTLE:
        return "Servants_"
    elif voice_type == SvtVoiceType.TREASURE_DEVICE:
        return "NoblePhantasm_"
    else:
        return "ChrVoice_"


def get_voice_url(region: Region, svt_id: int, voice_type: int, voice_id: str) -> str:
    folder = get_voice_folder(voice_type) + str(svt_id)
    return AssetURL.audio.format(
        base_url=settings.asset_url, region=region, folder=folder, id=voice_id
    )


def get_nice_voice_cond(
    region: Region, cond: ScriptJsonCond, costume_ids: Dict[int, int]
) -> NiceVoiceCond:
    cond_value = (
        costume_ids[cond.value]
        if cond.condType == VoiceCondType.COSTUME
        else cond.value
    )

    cond_value_list = (
        [group.svtId for group in masters[region].mstSvtGroupId[cond.value]]
        if cond.condType == VoiceCondType.SVT_GROUP
        else []
    )

    voice_cond = NiceVoiceCond(
        condType=VOICE_COND_NAME[cond.condType],
        eventId=cond.eventId,
        value=cond_value,
        valueList=cond_value_list,
    )

    return voice_cond


def get_nice_voice_line(
    region: Region,
    script: ScriptJson,
    svt_id: int,
    voice_type: int,
    costume_ids: Dict[int, int],
    subtitle_ids: Dict[str, str],
) -> NiceVoiceLine:
    first_voice_id = script.infos[0].id

    voice_line = NiceVoiceLine(
        overwriteName=nullable_to_string(script.overwriteName),
        id=(info.id for info in script.infos),
        audioAssets=(
            get_voice_url(region, svt_id, voice_type, info.id) for info in script.infos
        ),
        delay=(info.delay for info in script.infos),
        face=(info.face for info in script.infos),
        form=(info.form for info in script.infos),
        text=(nullable_to_string(info.text) for info in script.infos),
        conds=(get_nice_voice_cond(region, info, costume_ids) for info in script.conds),
        subtitle=subtitle_ids.get(str(svt_id) + "_" + first_voice_id, ""),
    )

    # Some voice lines have the first info id ending with xxx1 or xxx2 and we want xxx0
    voice_id = first_voice_id.split("_")[1][:-1] + "0"
    if voice_id in masters[region].mstVoiceId:
        mstVoice = masters[region].mstVoiceId[voice_id]
        voice_line.name = mstVoice.name
        voice_line.condType = COND_TYPE_NAME[mstVoice.condType]
        voice_line.condValue = mstVoice.condValue
        voice_line.priority = mstVoice.priority
        voice_line.svtVoiceType = VOICE_TYPE_NAME[mstVoice.svtVoiceType]

    return voice_line


def get_nice_voice_group(
    region: Region,
    voice: MstSvtVoice,
    costume_ids: Dict[int, int],
    subtitles: List[GlobalNewMstSubtitle],
) -> NiceVoiceGroup:

    subtitle_ids = {subtitle.id: subtitle.serif for subtitle in subtitles}

    return NiceVoiceGroup(
        svtId=voice.id,
        voicePrefix=voice.voicePrefix,
        type=VOICE_TYPE_NAME[voice.type],
        voiceLines=(
            get_nice_voice_line(
                region, script, voice.id, voice.type, costume_ids, subtitle_ids
            )
            for script in voice.scriptJson
        ),
    )


def get_valentine_equip(region: Region, svt_id: int) -> List[int]:
    if svt_id == MASH_SVT_ID:
        return MASH_VALENTINE_EQUIP[region]
    else:
        return masters[region].valentineEquip.get(svt_id, [])


def get_nice_servant(
    conn: Connection, region: Region, svt_id: int, lang: Language, lore: bool = False
) -> Dict[str, Any]:
    # Get expanded servant entity to get function and buff details
    raw_data = raw.get_servant_entity(conn, region, svt_id, expand=True, lore=lore)
    nice_data: Dict[str, Any] = {
        "id": raw_data.mstSvt.id,
        "collectionNo": raw_data.mstSvt.collectionNo,
        "name": raw_data.mstSvt.name,
        "ruby": raw_data.mstSvt.ruby,
        "gender": GENDER_TYPE_NAME[raw_data.mstSvt.genderType],
        "attribute": ATTRIBUTE_NAME[raw_data.mstSvt.attri],
        "className": CLASS_NAME[raw_data.mstSvt.classId],
        "type": SVT_TYPE_NAME[raw_data.mstSvt.type],
        "flag": SVT_FLAG_NAME[raw_data.mstSvt.flag],
        "cost": raw_data.mstSvt.cost,
        "instantDeathChance": raw_data.mstSvt.deathRate,
        "starGen": raw_data.mstSvt.starRate,
        "traits": get_traits_list(sorted(raw_data.mstSvt.individuality)),
        "starAbsorb": raw_data.mstSvtLimit[0].criticalWeight,
        "rarity": raw_data.mstSvtLimit[0].rarity,
        "cards": [CARD_TYPE_NAME[card_id] for card_id in raw_data.mstSvt.cardIds],
        "bondGrowth": masters[region].mstFriendshipId.get(
            raw_data.mstSvt.friendshipId, []
        ),
        "bondEquip": masters[region].bondEquip.get(svt_id, 0),
        "valentineEquip": get_valentine_equip(region, svt_id),
        "relateQuestIds": raw_data.mstSvt.relateQuestIds,
    }

    if region == Region.JP and lang == Language.en:
        nice_data["name"] = get_safe(TRANSLATIONS, nice_data["name"])

    charaGraph: Dict[str, Dict[int, str]] = {}
    faces: Dict[str, Dict[int, str]] = {}
    commands: Dict[str, Dict[int, str]] = {}
    status: Dict[str, Dict[int, str]] = {}
    charaFigure: Dict[str, Dict[int, str]] = {}
    charaFigureForm: Dict[int, Dict[str, Dict[int, str]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    narrowFigure: Dict[str, Dict[int, str]] = {}
    equipFace: Dict[str, Dict[int, str]] = {}

    costume_limits = {svt_costume.id for svt_costume in raw_data.mstSvtCostume}
    costume_ids = {
        svt_limit_add.limitCount: svt_limit_add.battleCharaId
        for svt_limit_add in raw_data.mstSvtLimitAdd
        if svt_limit_add.limitCount in costume_limits
    }

    base_settings = {"base_url": settings.asset_url, "region": region}
    base_settings_id = dict(item_id=svt_id, **base_settings)

    if raw_data.mstSvt.type in (
        SvtType.ENEMY_COLLECTION_DETAIL,
        SvtType.COMBINE_MATERIAL,
        SvtType.STATUS_UP,
    ):
        charaGraph["ascension"] = {
            0: AssetURL.charaGraphDefault.format(**base_settings_id)
        }
        faces["ascension"] = {0: AssetURL.face.format(**base_settings_id, i=0)}
    elif raw_data.mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        faces["ascension"] = {
            limit.limitCount: AssetURL.enemy.format(
                **base_settings_id, i=limit.limitCount
            )
            for limit in raw_data.mstSvtLimit
        }
    elif raw_data.mstSvt.isServant():
        charaGraph["ascension"] = {
            i: AssetURL.charaGraph[i].format(**base_settings_id) for i in range(1, 5)
        }
        faces["ascension"] = {
            (i + 1): AssetURL.face.format(**base_settings_id, i=i) for i in range(4)
        }
        commands["ascension"] = {
            i: AssetURL.commands.format(**base_settings_id, i=i) for i in range(1, 4)
        }
        status["ascension"] = {
            i: AssetURL.status.format(**base_settings_id, i=i) for i in range(1, 4)
        }
        charaFigure["ascension"] = {
            (i + 1): AssetURL.charaFigure.format(**base_settings_id, i=i)
            for i in range(3)
        }
        for svtScript in raw_data.mstSvtScript:
            script_form = svtScript.extendData.get("myroomForm", svtScript.form)
            if script_form != 0:
                charaFigureForm[script_form]["ascension"][
                    svtScript.id % 10 + 1
                ] = AssetURL.charaFigureForm.format(
                    **base_settings, form_id=script_form, svtScript_id=svtScript.id
                )
        narrowFigure["ascension"] = {
            i: AssetURL.narrowFigure[i].format(**base_settings_id) for i in range(1, 5)
        }
        if costume_ids:
            charaGraph["costume"] = {
                costume_id: AssetURL.charaGraphDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            faces["costume"] = {
                costume_id: AssetURL.face.format(
                    **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaFigure["costume"] = {
                costume_id: AssetURL.charaFigure.format(
                    **base_settings, item_id=costume_id, i=0
                )
                for costume_id in costume_ids.values()
            }
            charaGraph["costume"] = {
                costume_id: AssetURL.charaGraphDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            narrowFigure["costume"] = {
                costume_id: AssetURL.narrowFigureDefault.format(
                    **base_settings, item_id=costume_id
                )
                for costume_id in costume_ids.values()
            }
            status["costume"] = {
                costume_id: AssetURL.status.format(**base_settings_id, i=limit)
                for limit, costume_id in costume_ids.items()
            }
            commands["costume"] = {
                costume_id: AssetURL.commands.format(**base_settings_id, i=limit)
                for limit, costume_id in costume_ids.items()
            }
    elif raw_data.mstSvt.isEquip():
        charaGraph["equip"] = {
            svt_id: AssetURL.charaGraphDefault.format(**base_settings_id)
        }
        faces["equip"] = {svt_id: AssetURL.face.format(**base_settings_id, i=0)}
        equipFace["equip"] = {
            svt_id: AssetURL.equipFace.format(**base_settings_id, i=0)
        }

    nice_data["extraAssets"] = {
        "charaGraph": charaGraph,
        "faces": faces,
        "charaFigure": charaFigure,
        "charaFigureForm": charaFigureForm,
        "narrowFigure": narrowFigure,
        "commands": commands,
        "status": status,
        "equipFace": equipFace,
    }

    lvMax = max(svt_limit.lvMax for svt_limit in raw_data.mstSvtLimit)
    atkMax = raw_data.mstSvtLimit[0].atkMax
    atkBase = raw_data.mstSvtLimit[0].atkBase
    hpMax = raw_data.mstSvtLimit[0].hpMax
    hpBase = raw_data.mstSvtLimit[0].hpBase
    growthCurve = raw_data.mstSvt.expType
    growthCurveMax = 101 if raw_data.mstSvt.type == SvtType.NORMAL else (lvMax + 1)
    growthCurveValues = masters[region].mstSvtExpId[growthCurve]
    atkGrowth = [
        atkBase + (atkMax - atkBase) * exp.curve // 1000
        for exp in growthCurveValues[1:growthCurveMax]
    ]
    hpGrowth = [
        hpBase + (hpMax - hpBase) * exp.curve // 1000
        for exp in growthCurveValues[1:growthCurveMax]
    ]
    expGrowth = [exp.exp for exp in growthCurveValues[: growthCurveMax - 1]]
    nice_data.update(
        {
            "lvMax": lvMax,
            "growthCurve": growthCurve,
            "atkMax": atkMax,
            "atkBase": atkBase,
            "hpMax": hpMax,
            "hpBase": hpBase,
            "atkGrowth": atkGrowth,
            "hpGrowth": hpGrowth,
            "expGrowth": expGrowth,
        }
    )

    nice_data["expFeed"] = [
        combine.value
        for combine in masters[region].mstCombineMaterialId[
            raw_data.mstSvt.combineMaterialId
        ][: growthCurveMax - 1]
    ]

    nice_data["hitsDistribution"] = {
        CARD_TYPE_NAME[svt_card.cardId]: svt_card.normalDamage
        for svt_card in raw_data.mstSvtCard
    }

    ascensionAddIndividuality = {
        "ascension": {
            limitAdd.limitCount: get_traits_list(
                sorted(set(limitAdd.individuality + raw_data.mstSvt.individuality))
            )
            if limitAdd.individuality
            else []
            for limitAdd in raw_data.mstSvtLimitAdd
            if limitAdd.limitCount not in costume_ids
        },
        "costume": {
            costume_ids[limitAdd.limitCount]: get_traits_list(
                sorted(set(limitAdd.individuality + raw_data.mstSvt.individuality))
            )
            if limitAdd.individuality
            else []
            for limitAdd in raw_data.mstSvtLimitAdd
            if limitAdd.limitCount in costume_ids
        },
    }

    ascensionAddVoicePrefix = {
        "ascension": {
            limitAdd.limitCount: limitAdd.voicePrefix
            for limitAdd in raw_data.mstSvtLimitAdd
            if limitAdd.limitCount not in costume_ids
        },
        "costume": {
            costume_ids[limitAdd.limitCount]: limitAdd.voicePrefix
            for limitAdd in raw_data.mstSvtLimitAdd
            if limitAdd.limitCount in costume_ids
        },
    }

    nice_data["ascensionAdd"] = {
        "individuality": ascensionAddIndividuality,
        "voicePrefix": ascensionAddVoicePrefix,
    }

    nice_data["svtChange"] = [
        get_nice_servant_change(change) for change in raw_data.mstSvtChange
    ]

    nice_data["ascensionMaterials"] = {
        combineLimit.svtLimit: {
            "items": get_nice_item_amount(
                region, combineLimit.itemIds, combineLimit.itemNums
            ),
            "qp": combineLimit.qp,
        }
        for combineLimit in raw_data.mstCombineLimit
        if combineLimit.svtLimit != BAD_COMBINE_SVT_LIMIT
    }

    nice_data["skillMaterials"] = {
        combineSkill.skillLv: {
            "items": get_nice_item_amount(
                region, combineSkill.itemIds, combineSkill.itemNums
            ),
            "qp": combineSkill.qp,
        }
        for combineSkill in raw_data.mstCombineSkill
    }

    nice_data["costumeMaterials"] = {
        costume_ids[combineCostume.costumeId]: {
            "items": get_nice_item_amount(
                region, combineCostume.itemIds, combineCostume.itemNums
            ),
            "qp": combineCostume.qp,
        }
        for combineCostume in raw_data.mstCombineCostume
    }

    script = {}
    if "SkillRankUp" in raw_data.mstSvt.script:
        script["SkillRankUp"] = {
            rank_up_script[0]: rank_up_script[1:]
            for rank_up_script in orjson.loads(raw_data.mstSvt.script["SkillRankUp"])
        }

    nice_data["script"] = script

    nice_data["skills"] = [
        get_nice_skill(skill, svt_id, region) for skill in raw_data.mstSkill
    ]

    nice_data["classPassive"] = [
        get_nice_skill(skill, svt_id, region)
        for skill in raw_data.mstSvt.expandedClassPassive
    ]

    # Filter out dummy TDs that are used by enemy servants
    if raw_data.mstSvt.isServant():
        actualTDs: List[TdEntityNoReverse] = [
            td
            for td in raw_data.mstTreasureDevice
            if td.mstSvtTreasureDevice[0].num == 1
        ]
        for actualTD in actualTDs:
            if "tdTypeChangeIDs" in actualTD.mstTreasureDevice.script:
                tdTypeChangeIDs: List[int] = actualTD.mstTreasureDevice.script[
                    "tdTypeChangeIDs"
                ]
                currentActualTDsIDs = {td.mstTreasureDevice.id for td in actualTDs}
                for td in raw_data.mstTreasureDevice:
                    if (
                        td.mstTreasureDevice.id in tdTypeChangeIDs
                        and td.mstTreasureDevice.id not in currentActualTDsIDs
                    ):
                        actualTDs.append(td)
    else:
        actualTDs = raw_data.mstTreasureDevice

    nice_data["noblePhantasms"] = [
        get_nice_td(td, svt_id, region)
        for td in sorted(actualTDs, key=lambda x: x.mstTreasureDevice.id)
    ]

    if lore:
        nice_data["profile"] = {
            "cv": get_cv_name(region, raw_data.mstSvt.cvId),
            "illustrator": get_illustrator_name(region, raw_data.mstSvt.illustratorId),
            "costume": {
                costume_ids[costume.id]: get_nice_costume(costume)
                for costume in raw_data.mstSvtCostume
            },
            "comments": [
                get_nice_comment(svt_comment) for svt_comment in raw_data.mstSvtComment
            ],
            "voices": [
                get_nice_voice_group(region, voice, costume_ids, raw_data.mstSubtitle)
                for voice in raw_data.mstSvtVoice
            ],
        }

        if raw_data.mstSvtLimit:
            nice_data["profile"]["stats"] = {
                "strength": get_nice_status_rank(raw_data.mstSvtLimit[0].power),
                "endurance": get_nice_status_rank(raw_data.mstSvtLimit[0].defense),
                "agility": get_nice_status_rank(raw_data.mstSvtLimit[0].agility),
                "magic": get_nice_status_rank(raw_data.mstSvtLimit[0].magic),
                "luck": get_nice_status_rank(raw_data.mstSvtLimit[0].luck),
                "np": get_nice_status_rank(raw_data.mstSvtLimit[0].treasureDevice),
            }

    return nice_data


def get_nice_servant_model(
    conn: Connection, region: Region, item_id: int, lang: Language, lore: bool = False
) -> NiceServant:
    return NiceServant.parse_obj(get_nice_servant(conn, region, item_id, lang, lore))


def get_nice_equip_model(
    conn: Connection, region: Region, item_id: int, lang: Language, lore: bool = False
) -> NiceEquip:
    return NiceEquip.parse_obj(get_nice_servant(conn, region, item_id, lang, lore))


def get_nice_buff_alone(
    conn: Connection,
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceBuffReverse:
    raw_data = raw.get_buff_entity_no_reverse(region, buff_id)
    nice_data = NiceBuffReverse.parse_obj(get_nice_buff(raw_data, region))
    if reverse and reverseDepth >= ReverseDepth.function:
        if reverseData == ReverseData.basic:
            basic_buff_reverse = BasicReversedBuff(
                function=(
                    get_basic_function(region, func_id, lang, reverse, reverseDepth)
                    for func_id in raw.buff_to_func(region, buff_id)
                )
            )
            nice_data.reverse = NiceReversedBuffType(basic=basic_buff_reverse)
        else:
            buff_reverse = NiceReversedBuff(
                function=(
                    get_nice_func_alone(
                        conn, region, func_id, lang, reverse, reverseDepth
                    )
                    for func_id in raw.buff_to_func(region, buff_id)
                )
            )
            nice_data.reverse = NiceReversedBuffType(nice=buff_reverse)
    return nice_data


def get_nice_func_alone(
    conn: Connection,
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceBaseFunctionReverse:
    raw_data = raw.get_func_entity_no_reverse(region, func_id, expand=True)
    nice_data = NiceBaseFunctionReverse.parse_obj(
        get_nice_base_function(raw_data, region)
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        if reverseData == ReverseData.basic:
            basic_func_reverse = BasicReversedFunction(
                skill=(
                    get_basic_skill(region, skill_id, lang, reverse, reverseDepth)
                    for skill_id in raw.func_to_skillId(region, func_id)
                ),
                NP=(
                    get_basic_td(region, td_id, lang, reverse, reverseDepth)
                    for td_id in raw.func_to_tdId(region, func_id)
                ),
            )
            nice_data.reverse = NiceReversedFunctionType(basic=basic_func_reverse)
        else:
            func_reverse = NiceReversedFunction(
                skill=(
                    get_nice_skill_alone(
                        conn, region, skill_id, lang, reverse, reverseDepth
                    )
                    for skill_id in raw.func_to_skillId(region, func_id)
                ),
                NP=(
                    get_nice_td_alone(conn, region, td_id, lang, reverse, reverseDepth)
                    for td_id in raw.func_to_tdId(region, func_id)
                ),
            )
            nice_data.reverse = NiceReversedFunctionType(nice=func_reverse)
    return nice_data


def get_nice_skill_alone(
    conn: Connection,
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceSkillReverse:
    raw_data = raw.get_skill_entity_no_reverse(conn, region, skill_id, expand=True)

    svt_list = [svt_skill.svtId for svt_skill in raw_data.mstSvtSkill]
    if svt_list:
        svtId = svt_list[0]
    else:
        svtId = 0
    nice_data = NiceSkillReverse.parse_obj(get_nice_skill(raw_data, svtId, region))

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in raw_data.mstSvtSkill}
        passiveSkills = raw.passive_to_svtId(region, skill_id)
        if reverseData == ReverseData.basic:
            basic_skill_reverse = BasicReversedSkillTd(
                servant=(
                    get_basic_servant(region, svt_id, lang=lang)
                    for svt_id in activeSkills | passiveSkills
                ),
                MC=(
                    get_basic_mc(region, mc_id)
                    for mc_id in raw.skill_to_MCId(region, skill_id)
                ),
                CC=(
                    get_basic_cc(region, cc_id)
                    for cc_id in raw.skill_to_CCId(region, skill_id)
                ),
            )
            nice_data.reverse = NiceReversedSkillTdType(basic=basic_skill_reverse)
        else:
            skill_reverse = NiceReversedSkillTd(
                servant=(
                    get_nice_servant_model(conn, region, svt_id, lang=lang)
                    for svt_id in activeSkills | passiveSkills
                ),
                MC=(
                    get_nice_mystic_code(conn, region, mc_id)
                    for mc_id in raw.skill_to_MCId(region, skill_id)
                ),
                CC=(
                    get_nice_command_code(conn, region, cc_id)
                    for cc_id in raw.skill_to_CCId(region, skill_id)
                ),
            )
            nice_data.reverse = NiceReversedSkillTdType(nice=skill_reverse)
    return nice_data


def get_nice_td_alone(
    conn: Connection,
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceTdReverse:
    raw_data = raw.get_td_entity_no_reverse(region, td_id, expand=True)

    # Yes, all td_id has a svtTd entry
    svtId = next(svt_id.svtId for svt_id in raw_data.mstSvtTreasureDevice)
    nice_data = NiceTdReverse.parse_obj(get_nice_td(raw_data, svtId, region))

    if reverse and reverseDepth >= ReverseDepth.servant:
        if reverseData == ReverseData.basic:
            basic_td_reverse = BasicReversedSkillTd(
                servant=[
                    get_basic_servant(region, svt_id.svtId, lang=lang)
                    for svt_id in raw_data.mstSvtTreasureDevice
                ]
            )
            nice_data.reverse = NiceReversedSkillTdType(basic=basic_td_reverse)
        else:
            td_reverse = NiceReversedSkillTd(
                servant=[
                    get_nice_servant_model(conn, region, svt_id.svtId, lang=lang)
                    for svt_id in raw_data.mstSvtTreasureDevice
                ]
            )
            nice_data.reverse = NiceReversedSkillTdType(nice=td_reverse)
    return nice_data


def get_nice_mystic_code(
    conn: Connection, region: Region, mc_id: int
) -> NiceMysticCode:
    raw_data = raw.get_mystic_code_entity(conn, region, mc_id, expand=True)
    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_mc = NiceMysticCode(
        id=raw_data.mstEquip.id,
        name=raw_data.mstEquip.name,
        detail=raw_data.mstEquip.detail,
        maxLv=raw_data.mstEquip.maxLv,
        extraAssets={
            asset_category: {
                "male": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_data.mstEquip.maleImageId
                ),
                "female": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_data.mstEquip.femaleImageId
                ),
            }
            for asset_category in ("item", "masterFace", "masterFigure")
        },
        expRequired=(
            exp.exp
            for exp in sorted(raw_data.mstEquipExp, key=lambda x: x.lv)
            if exp.exp != -1
        ),
        skills=(get_nice_skill(skill, mc_id, region) for skill in raw_data.mstSkill),
    )

    return nice_mc


def get_nice_command_code(
    conn: Connection, region: Region, cc_id: int
) -> NiceCommandCode:
    raw_data = raw.get_command_code_entity(conn, region, cc_id, expand=True)

    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}
    nice_cc = NiceCommandCode(
        id=raw_data.mstCommandCode.id,
        name=raw_data.mstCommandCode.name,
        collectionNo=raw_data.mstCommandCode.collectionNo,
        rarity=raw_data.mstCommandCode.rarity,
        extraAssets={
            "charaGraph": {
                "cc": {cc_id: AssetURL.commandGraph.format(**base_settings)}
            },
            "faces": {"cc": {cc_id: AssetURL.commandCode.format(**base_settings)}},
        },
        skills=(get_nice_skill(skill, cc_id, region) for skill in raw_data.mstSkill),
        illustrator=get_illustrator_name(
            region, raw_data.mstCommandCodeComment.illustratorId
        ),
        comment=raw_data.mstCommandCodeComment.comment,
    )

    return nice_cc


def get_nice_shop(region: Region, shop: MstShop) -> NiceShop:
    if shop.payType == PayType.FRIEND_POINT:
        shop_item_id = 4
    elif shop.payType == PayType.MANA:
        shop_item_id = 3
    else:
        shop_item_id = shop.itemIds[0]

    return NiceShop(
        id=shop.id,
        baseShopId=shop.baseShopId,
        shopType=SHOP_TYPE_NAME[shop.shopType],
        eventId=shop.eventId,
        slot=shop.slot,
        priority=shop.priority,
        name=shop.name,
        detail=shop.detail,
        infoMessage=shop.infoMessage,
        warningMessage=shop.warningMessage,
        payType=PAY_TYPE_NAME[shop.payType],
        cost=NiceItemAmount(
            item=get_nice_item(region, shop_item_id), amount=shop.prices[0]
        ),
        purchaseType=PURCHASE_TYPE_NAME[shop.purchaseType],
        targetIds=shop.targetIds,
        setNum=shop.setNum,
        limitNum=shop.limitNum,
        defaultLv=shop.defaultLv,
        defaultLimitCount=shop.defaultLimitCount,
        openedAt=shop.openedAt,
        closedAt=shop.closedAt,
    )


def get_nice_event(region: Region, event_id: int) -> NiceEvent:
    raw_data = raw.get_event_entity(region, event_id)

    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_event = NiceEvent(
        id=raw_data.mstEvent.id,
        type=EVENT_TYPE_NAME[raw_data.mstEvent.type],
        name=raw_data.mstEvent.name,
        shortName=raw_data.mstEvent.shortName,
        detail=raw_data.mstEvent.detail,
        noticeBanner=AssetURL.banner.format(
            **base_settings, banner=f"event_war_{raw_data.mstEvent.noticeBannerId}"
        )
        if raw_data.mstEvent.noticeBannerId != 0
        else None,
        banner=AssetURL.banner.format(
            **base_settings, banner=f"event_war_{raw_data.mstEvent.bannerId}"
        )
        if raw_data.mstEvent.bannerId != 0
        else None,
        icon=AssetURL.banner.format(
            **base_settings, banner=f"banner_icon_{raw_data.mstEvent.iconId}"
        )
        if raw_data.mstEvent.iconId != 0
        else None,
        bannerPriority=raw_data.mstEvent.bannerPriority,
        noticeAt=raw_data.mstEvent.noticeAt,
        startedAt=raw_data.mstEvent.startedAt,
        endedAt=raw_data.mstEvent.endedAt,
        finishedAt=raw_data.mstEvent.finishedAt,
        materialOpenedAt=raw_data.mstEvent.materialOpenedAt,
        warIds=(war.id for war in masters[region].mstWarEventId.get(event_id, [])),
        shop=(get_nice_shop(region, shop) for shop in raw_data.mstShop),
    )

    return nice_event


def get_nice_bgm(region: Region, bgm_id: int) -> NiceBgm:
    raw_bgm = masters[region].mstBgmId[bgm_id]
    return NiceBgm(
        id=raw_bgm.id,
        name=raw_bgm.name,
        audioAsset=AssetURL.audio.format(
            base_url=settings.asset_url,
            region=region,
            folder=raw_bgm.fileName,
            id=raw_bgm.fileName,
        )
        if raw_bgm.id != 0
        else None,
    )


def get_nice_gift(region: Region, gift_id: int) -> List[NiceGift]:
    raw_gifts = masters[region].mstGiftId.get(gift_id, [])
    return [
        NiceGift(
            id=raw_gift.id,
            type=GIFT_TYPE_NAME[raw_gift.type],
            objectId=raw_gift.objectId,
            priority=raw_gift.priority,
            num=raw_gift.num,
        )
        for raw_gift in raw_gifts
    ]


def get_nice_quest_release(
    region: Region, raw_quest_release: MstQuestRelease
) -> NiceQuestRelease:
    return NiceQuestRelease(
        type=COND_TYPE_NAME[raw_quest_release.type],
        targetId=raw_quest_release.targetId,
        value=raw_quest_release.value,
        closedMessage=masters[region].mstClosedMessageId.get(
            raw_quest_release.closedMessageId, ""
        ),
    )


def get_nice_stage(region: Region, raw_stage: MstStage) -> NiceStage:
    return NiceStage(bgm=get_nice_bgm(region, raw_stage.bgmId))


def get_nice_quest(
    region: Region, quest_id: int, raw_quest: Union[QuestEntity, QuestPhaseEntity]
) -> Dict[str, Any]:
    nice_data: Dict[str, Any] = {
        "id": raw_quest.mstQuest.id,
        "name": raw_quest.mstQuest.name,
        "type": QUEST_TYPE_NAME[raw_quest.mstQuest.type],
        "consumeType": QUEST_CONSUME_TYPE_NAME[raw_quest.mstQuest.consumeType],
        "consumeItem": [
            nice_item_amount
            for consumeItem in raw_quest.mstQuestConsumeItem
            for nice_item_amount in get_nice_item_amount(
                region, consumeItem.itemIds, consumeItem.nums
            )
        ],
        "consume": raw_quest.mstQuest.actConsume,
        "spotId": raw_quest.mstQuest.spotId,
        "warId": masters[region].mstSpotId[raw_quest.mstQuest.spotId].warId,
        "gifts": get_nice_gift(region, raw_quest.mstQuest.giftId),
        "releaseConditions": [
            get_nice_quest_release(region, release)
            for release in raw_quest.mstQuestRelease
        ],
        "phases": [
            questPhase.phase
            for questPhase in masters[region].mstQuestPhaseId[quest_id].values()
        ],
        "noticeAt": raw_quest.mstQuest.noticeAt,
        "openedAt": raw_quest.mstQuest.openedAt,
        "closedAt": raw_quest.mstQuest.closedAt,
    }
    return nice_data


def get_nice_quest_alone(region: Region, quest_id: int) -> NiceQuest:
    return NiceQuest.parse_obj(
        get_nice_quest(region, quest_id, raw.get_quest_entity(region, quest_id))
    )


def get_nice_quest_phase(region: Region, quest_id: int, phase: int) -> NiceQuestPhase:
    raw_data = raw.get_quest_phase_entity(region, quest_id, phase)
    nice_data = get_nice_quest(region, quest_id, raw_data)
    nice_data.update(
        {
            "phase": raw_data.mstQuestPhase.phase,
            "className": [
                CLASS_NAME[class_id] for class_id in raw_data.mstQuestPhase.classIds
            ],
            "individuality": get_traits_list(raw_data.mstQuestPhase.individuality),
            "qp": raw_data.mstQuestPhase.qp,
            "exp": raw_data.mstQuestPhase.playerExp,
            "bond": raw_data.mstQuestPhase.friendshipExp,
            "stages": [get_nice_stage(region, stage) for stage in raw_data.mstStage],
        }
    )
    return NiceQuestPhase.parse_obj(nice_data)


def get_nice_map(region: Region, raw_map: MstMap) -> NiceMap:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceMap(
        id=raw_map.id,
        mapImage=AssetURL.mapImg.format(**base_settings, map_id=raw_map.mapImageId)
        if raw_map.mapImageId != 0
        else None,
        mapImageW=raw_map.mapImageW,
        mapImageH=raw_map.mapImageH,
        headerImage=AssetURL.banner.format(
            **base_settings, banner=f"img_title_header_{raw_map.headerImageId}"
        )
        if raw_map.headerImageId != 0
        else None,
        bgm=get_nice_bgm(region, raw_map.bgmId),
    )


def get_nice_spot(region: Region, raw_spot: MstSpot, war_asset_id: int) -> NiceSpot:
    return NiceSpot(
        id=raw_spot.id,
        joinSpotIds=raw_spot.joinSpotIds,
        mapId=raw_spot.mapId,
        name=raw_spot.name,
        image=AssetURL.spotImg.format(
            base_url=settings.asset_url,
            region=region,
            war_asset_id=war_asset_id,
            spot_id=raw_spot.imageId,
        )
        if raw_spot.imageId != 0
        else None,
        x=raw_spot.x,
        y=raw_spot.y,
        imageOfsX=raw_spot.imageOfsX,
        imageOfsY=raw_spot.imageOfsY,
        nameOfsX=raw_spot.nameOfsX,
        nameOfsY=raw_spot.nameOfsY,
        questOfsX=raw_spot.questOfsX,
        questOfsY=raw_spot.questOfsY,
        nextOfsX=raw_spot.nextOfsX,
        nextOfsY=raw_spot.nextOfsY,
        closedMessage=raw_spot.closedMessage,
        quests=(
            get_nice_quest_alone(region, quest.id)
            for quest in masters[region].mstQuestSpotId.get(raw_spot.id, [])
        ),
    )


def get_nice_war(region: Region, war_id: int) -> NiceWar:
    raw_war = raw.get_war_entity(region, war_id)

    base_settings = {"base_url": settings.asset_url, "region": region}
    war_asset_id = (
        raw_war.mstWar.assetId if raw_war.mstWar.assetId > 0 else raw_war.mstWar.id
    )

    if raw_war.mstWar.eventId in masters[region].mstEventId:
        event = masters[region].mstEventId[raw_war.mstWar.eventId]
        banner_file = f"event_war_{event.bannerId}"
    elif raw_war.mstWar.flag & WarEntityFlag.MAIN_SCENARIO != 0:
        banner_file = f"questboard_cap{raw_war.mstWar.bannerId:>03}"
    else:
        banner_file = f"chaldea_category_{raw_war.mstWar.bannerId}"

    return NiceWar(
        id=raw_war.mstWar.id,
        coordinates=raw_war.mstWar.coordinates,
        age=raw_war.mstWar.age,
        name=raw_war.mstWar.name,
        longName=raw_war.mstWar.longName,
        banner=AssetURL.banner.format(**base_settings, banner=banner_file)
        if raw_war.mstWar.bannerId != 0
        else None,
        headerImage=AssetURL.banner.format(
            **base_settings, banner=f"img_title_header_{raw_war.mstWar.headerImageId}"
        )
        if raw_war.mstWar.headerImageId != 0
        else None,
        priority=raw_war.mstWar.priority,
        parentWarId=raw_war.mstWar.parentWarId,
        materialParentWarId=raw_war.mstWar.materialParentWarId,
        emptyMessage=raw_war.mstWar.emptyMessage,
        bgm=get_nice_bgm(region, raw_war.mstWar.bgmId),
        scriptId=raw_war.mstWar.scriptId,
        startType=WAR_START_TYPE_NAME[raw_war.mstWar.startType],
        targetId=raw_war.mstWar.targetId,
        eventId=raw_war.mstWar.eventId,
        lastQuestId=raw_war.mstWar.lastQuestId,
        maps=(get_nice_map(region, raw_map) for raw_map in raw_war.mstMap),
        spots=(
            get_nice_spot(region, raw_spot, war_asset_id)
            for raw_spot in raw_war.mstSpot
        ),
    )


def get_nice_ai_act(conn: Connection, region: Region, mstAiAct: MstAiAct) -> NiceAiAct:
    nice_ai_act = NiceAiAct(
        id=mstAiAct.id,
        type=AI_ACT_TYPE_NAME[mstAiAct.type],
        target=AI_ACT_TARGET_NAME[mstAiAct.target],
        targetIndividuality=get_traits_list(mstAiAct.targetIndividuality),
    )
    if len(mstAiAct.skillVals) >= 2:
        nice_ai_act.skillId = mstAiAct.skillVals[0]
        nice_ai_act.skillLv = mstAiAct.skillVals[1]
        nice_ai_act.skill = get_nice_skill_alone(
            conn,
            region,
            mstAiAct.skillVals[0],
            Language.jp if region == Region.JP else Language.en,
        )
    return nice_ai_act


def get_parent_ais(
    region: Region, ai_id: int, field: bool = False
) -> Dict[AiType, List[int]]:
    if field:
        return {
            AiType.svt: [],
            AiType.field: sorted(masters[region].parentAiField.get(ai_id, [])),
        }
    else:
        return {
            AiType.svt: sorted(masters[region].parentAiSvt.get(ai_id, [])),
            AiType.field: [],
        }


def get_nice_ai(
    conn: Connection, region: Region, one_ai: OneAiEntity, field: bool = False
) -> NiceAi:
    nice_ai = NiceAi(
        id=one_ai.mstAi.id,
        idx=one_ai.mstAi.idx,
        actNumInt=one_ai.mstAi.actNum,
        actNum=AI_ACT_NUM_NAME.get(one_ai.mstAi.actNum, NiceAiActNum.unknown),
        priority=one_ai.mstAi.priority,
        probability=one_ai.mstAi.probability,
        cond=AI_COND_NAME[
            one_ai.mstAi.cond if one_ai.mstAi.cond >= 0 else -one_ai.mstAi.cond
        ],
        condNegative=one_ai.mstAi.cond < 0,
        vals=one_ai.mstAi.vals,
        aiAct=get_nice_ai_act(conn, region, one_ai.mstAiAct),
        avals=one_ai.mstAi.avals,
        parentAis=get_parent_ais(region, one_ai.mstAi.id, field),
        infoText=one_ai.mstAi.infoText,
    )
    if one_ai.mstAi.timing:
        nice_ai.timing = one_ai.mstAi.timing
        nice_ai.timingDescription = AI_TIMING_NAME.get(
            one_ai.mstAi.timing, AiTiming.unknown
        )
    return nice_ai


def get_nice_ai_full(
    conn: Connection, region: Region, ai_id: int, field: bool = False
) -> NiceAiFull:
    full_ai = raw.get_ai_entity(conn, ai_id, field)
    return NiceAiFull(
        mainAis=(get_nice_ai(conn, region, ai, field) for ai in full_ai.mainAis),
        relatedAis=(get_nice_ai(conn, region, ai, field) for ai in full_ai.relatedAis),
    )
