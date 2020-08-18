import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import orjson
from fastapi import HTTPException

from ..config import Settings
from .basic import (
    get_basic_cc,
    get_basic_function,
    get_basic_mc,
    get_basic_servant,
    get_basic_skill,
    get_basic_td,
)
from .common import Language, Region, ReverseData, ReverseDepth
from .enums import (
    ATTRIBUTE_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    CLASS_NAME,
    COND_TYPE_NAME,
    FUNC_APPLYTARGET_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    FUNC_VALS_NOT_BUFF,
    GENDER_NAME,
    ITEM_BG_TYPE_NAME,
    ITEM_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SKILL_TYPE_NAME,
    STATUS_RANK_NAME,
    SVT_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    FuncType,
    NiceStatusRank,
    SvtType,
    VoiceCondType,
)
from .gamedata import masters
from .raw import (
    buff_to_func,
    func_to_skillId,
    func_to_tdId,
    get_buff_entity_no_reverse,
    get_command_code_entity,
    get_func_entity_no_reverse,
    get_mystic_code_entity,
    get_quest_phase_entity,
    get_servant_entity,
    get_skill_entity_no_reverse,
    get_td_entity_no_reverse,
    passive_to_svtId,
    skill_to_CCId,
    skill_to_MCId,
)
from .schemas.basic import (
    BasicReversedBuff,
    BasicReversedFunction,
    BasicReversedSkillTd,
)
from .schemas.nice import (
    AssetURL,
    NiceBaseFunctionReverse,
    NiceBuffReverse,
    NiceCommandCode,
    NiceEquip,
    NiceMysticCode,
    NiceReversedBuff,
    NiceReversedBuffType,
    NiceReversedFunction,
    NiceReversedFunctionType,
    NiceReversedSkillTd,
    NiceReversedSkillTdType,
    NiceServant,
    NiceSkillReverse,
    NiceTdReverse,
)
from .schemas.raw import (
    BuffEntityNoReverse,
    FunctionEntityNoReverse,
    GlobalNewMstSubtitle,
    MstSvtComment,
    MstSvtCostume,
    MstSvtVoice,
    ScriptJson,
    ScriptJsonCond,
    SkillEntityNoReverse,
    TdEntityNoReverse,
)
from .translations import SVT_NAME_JP_EN
from .utils import get_safe, get_traits_list


FORMATTING_BRACKETS = {"[g][o]": "", "[/o][/g]": "", " [{0}] ": " ", "[{0}]": ""}


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


def parse_dataVals(
    datavals: str, functype: int, region: Region
) -> Dict[str, Union[int, str, List[int]]]:
    EVENT_FUNCTIONS = {
        FuncType.EVENT_POINT_UP,
        FuncType.EVENT_POINT_RATE_UP,
        FuncType.EVENT_DROP_UP,
        FuncType.EVENT_DROP_RATE_UP,
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

    datavals_exception = HTTPException(
        status_code=500, detail=f"Can't parse datavals: {datavals}"
    )

    output: Dict[str, Union[int, str, List[int]]] = {}
    if datavals != "[]":
        datavals = remove_brackets(datavals)
        array = re.split(r",\s*(?![^\[\]]*\])", datavals)
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
                elif functype in (
                    FuncType.FRIEND_POINT_UP,
                    FuncType.FRIEND_POINT_UP_DUPLICATE,
                ):
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
                array2 = re.split(r":\s*(?![^\[\]]*\])", arrayi)
                if len(array2) > 1:
                    if array2[0] == "DependFuncId1":
                        output["DependFuncId"] = int(remove_brackets(array2[1]))
                    elif array2[0] == "DependFuncVals1":
                        func_type = masters[region].mstFuncId[output["DependFuncId"]].funcType  # type: ignore
                        vals_value = parse_dataVals(array2[1], func_type, region)
                        output["DependFuncVals"] = vals_value  # type: ignore
                    elif array2[0] in (
                        "TargetList",
                        "TargetRarityList",
                        "AndCheckIndividualityList",
                    ):
                        try:
                            list_value = [int(i) for i in array2[1].split("/")]
                            output[array2[0]] = list_value
                        except ValueError:
                            raise datavals_exception
                    else:
                        try:
                            text = array2[0]
                            value = int(array2[1])
                        except ValueError:
                            raise datavals_exception
                else:
                    raise datavals_exception

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
        "type": get_safe(BUFF_TYPE_NAME, buffEntity.mstBuff.type),
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
    return buffInfo


def get_nice_base_function(
    function: FunctionEntityNoReverse, region: Region
) -> Dict[str, Any]:
    functionInfo: Dict[str, Any] = {
        "funcId": function.mstFunc.id,
        "funcPopupText": function.mstFunc.popupText,
        "funcquestTvals": get_traits_list(function.mstFunc.questTvals),
        "functvals": get_traits_list(function.mstFunc.tvals),
        "funcType": get_safe(FUNC_TYPE_NAME, function.mstFunc.funcType),
        "funcTargetTeam": get_safe(FUNC_APPLYTARGET_NAME, function.mstFunc.applyTarget),
        "funcTargetType": get_safe(FUNC_TARGETTYPE_NAME, function.mstFunc.targetType),
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


def get_nice_skill(
    skillEntity: SkillEntityNoReverse, svtId: int, region: Region
) -> Dict[str, Any]:
    nice_skill: Dict[str, Any] = {
        "id": skillEntity.mstSkill.id,
        "name": skillEntity.mstSkill.name,
        "type": SKILL_TYPE_NAME[skillEntity.mstSkill.type],
        "actIndividuality": get_traits_list(skillEntity.mstSkill.actIndividuality),
    }

    iconId = skillEntity.mstSkill.iconId
    if iconId != 0:
        nice_skill["icon"] = AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId,
        )

    if skillEntity.mstSkillDetail:
        nice_skill["detail"] = strip_formatting_brackets(
            skillEntity.mstSkillDetail[0].detail
        )

    # .mstSvtSkill returns the list of SvtSkill with the same skill_id
    if skillEntity.mstSvtSkill:
        chosenSvt = [item for item in skillEntity.mstSvtSkill if item.svtId == svtId]
        if chosenSvt:
            # Wait for 3.9 for PEP 584 to use |=
            nice_skill.update(
                {
                    "strengthStatus": chosenSvt[0].strengthStatus,
                    "num": chosenSvt[0].num,
                    "priority": chosenSvt[0].priority,
                    "condQuestId": chosenSvt[0].condQuestId,
                    "condQuestPhase": chosenSvt[0].condQuestPhase,
                }
            )

    nice_skill["coolDown"] = [item.chargeTurn for item in skillEntity.mstSkillLv]

    nice_skill["script"] = {
        key: [item.script[key] for item in skillEntity.mstSkillLv]
        for key in skillEntity.mstSkillLv[0].script.keys()
    }

    nice_skill["functions"] = []
    for funci, _ in enumerate(skillEntity.mstSkillLv[0].funcId):
        function = skillEntity.mstSkillLv[0].expandedFuncId[funci]
        functionInfo = get_nice_base_function(function, region)
        functionInfo["svals"] = [
            parse_dataVals(item.svals[funci], function.mstFunc.funcType, region)
            for item in skillEntity.mstSkillLv
        ]
        if "followerVals" in skillEntity.mstSkillLv[0].script:
            functionInfo["followerVals"] = [
                parse_dataVals(
                    item.script["followerVals"][funci],
                    function.mstFunc.funcType,
                    region,
                )
                for item in skillEntity.mstSkillLv
            ]
        nice_skill["functions"].append(functionInfo)

    return nice_skill


def get_nice_td(
    tdEntity: TdEntityNoReverse, svtId: int, region: Region
) -> Dict[str, Any]:
    nice_td: Dict[str, Any] = {
        "id": tdEntity.mstTreasureDevice.id,
        "name": tdEntity.mstTreasureDevice.name,
        "rank": tdEntity.mstTreasureDevice.rank,
        "type": tdEntity.mstTreasureDevice.typeText,
        "individuality": get_traits_list(tdEntity.mstTreasureDevice.individuality),
    }

    if tdEntity.mstTreasureDeviceDetail:
        nice_td["detail"] = strip_formatting_brackets(
            tdEntity.mstTreasureDeviceDetail[0].detail
        )

    nice_td["npGain"] = {
        "buster": [item.tdPointB for item in tdEntity.mstTreasureDeviceLv],
        "arts": [item.tdPointA for item in tdEntity.mstTreasureDeviceLv],
        "quick": [item.tdPointQ for item in tdEntity.mstTreasureDeviceLv],
        "extra": [item.tdPointEx for item in tdEntity.mstTreasureDeviceLv],
        "np": [item.tdPoint for item in tdEntity.mstTreasureDeviceLv],
        "defence": [item.tdPointDef for item in tdEntity.mstTreasureDeviceLv],
    }

    chosenSvt = [item for item in tdEntity.mstSvtTreasureDevice if item.svtId == svtId]
    if chosenSvt:
        imageId = chosenSvt[0].imageIndex
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
                "strengthStatus": chosenSvt[0].strengthStatus,
                "num": chosenSvt[0].num,
                "priority": chosenSvt[0].priority,
                "condQuestId": chosenSvt[0].condQuestId,
                "condQuestPhase": chosenSvt[0].condQuestPhase,
                "card": CARD_TYPE_NAME[chosenSvt[0].cardId],
                "npDistribution": chosenSvt[0].damage,
            }
        )

    nice_td["functions"] = []

    for funci, _ in enumerate(tdEntity.mstTreasureDeviceLv[0].funcId):
        function = tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci]
        functionInfo = get_nice_base_function(function, region)
        for sval in ["svals", "svals2", "svals3", "svals4", "svals5"]:
            functionInfo[sval] = [
                parse_dataVals(
                    getattr(item, sval)[funci], function.mstFunc.funcType, region
                )
                for item in tdEntity.mstTreasureDeviceLv
            ]
        nice_td["functions"].append(functionInfo)

    return nice_td


def get_nice_item(region: Region, item_id: int) -> Dict[str, Union[int, str]]:
    raw_data = masters[region].mstItemId[item_id]
    nice_item: Dict[str, Union[int, str]] = {
        "id": item_id,
        "name": raw_data.name,
        "type": get_safe(ITEM_TYPE_NAME, raw_data.type),
        "icon": AssetURL.items.format(
            base_url=settings.asset_url, region=region, item_id=raw_data.imageId
        ),
        "background": ITEM_BG_TYPE_NAME[raw_data.bgImageId],
    }
    return nice_item


def get_nice_item_amount(
    region: Region, item_list: List[int], amount_list: List[int]
) -> List[Dict[str, Any]]:
    return [
        {"item": get_nice_item(region, item), "amount": amount}
        for item, amount in zip(item_list, amount_list)
    ]


def get_nice_comment(comment: MstSvtComment) -> Dict[str, Any]:
    return {
        "id": comment.id,
        "priority": comment.priority,
        "condMessage": comment.condMessage,
        "comment": comment.comment,
        "condType": COND_TYPE_NAME[comment.condType],
        "condValues": comment.condValues,
        "condValue2": comment.condValue2,
    }


def get_nice_costume(costume: MstSvtCostume) -> Dict[str, Union[str, int]]:
    return {
        "id": costume.id,
        "costumeCollectionNo": costume.costumeCollectionNo,
        "name": costume.name,
        "shortName": costume.shortName,
        "detail": costume.detail,
        "priority": costume.priority,
    }


def get_nice_voice_cond(
    region: Region, cond: ScriptJsonCond, costume_ids: Dict[int, int]
) -> Dict[str, Any]:
    voice_cond = {
        "condType": VOICE_COND_NAME[cond.condType],
        "value": cond.value,
        "eventId": cond.eventId,
    }

    if cond.condType == VoiceCondType.COSTUME:
        voice_cond["value"] = costume_ids[cond.value]
    if cond.condType == VoiceCondType.SVT_GROUP:
        voice_cond["valueList"] = masters[region].mstSvtGroupId[cond.value]
    else:
        voice_cond["valueList"] = []

    return voice_cond


def get_nice_voice_line(
    region: Region,
    script: ScriptJson,
    svt_id: int,
    costume_ids: Dict[int, int],
    subtitle_ids: Dict[str, str],
) -> Dict[str, Any]:
    voice_line: Dict[str, Any] = {
        "overwriteName": nullable_to_string(script.overwriteName),
        "id": [item.id for item in script.infos],
        "delay": [item.delay for item in script.infos],
        "face": [item.face for item in script.infos],
        "form": [item.form for item in script.infos],
        "text": [nullable_to_string(item.text) for item in script.infos],
        "conds": [
            get_nice_voice_cond(region, item, costume_ids) for item in script.conds
        ],
    }

    first_voice_id = script.infos[0].id
    voice_line["subtitle"] = subtitle_ids.get(str(svt_id) + "_" + first_voice_id, "")

    # Some voice lines have info starting at xxx1 or xxx2 and we want xxx0
    voice_id = first_voice_id.split("_")[1][:-1] + "0"
    if voice_id in masters[region].mstVoiceId:
        mstVoice = masters[region].mstVoiceId[voice_id]
        voice_line.update(
            {
                "name": mstVoice.name,
                "condType": COND_TYPE_NAME[mstVoice.condType],
                "condValue": mstVoice.condValue,
                "priority": mstVoice.priority,
                "svtVoiceType": VOICE_TYPE_NAME[mstVoice.svtVoiceType],
            }
        )

    return voice_line


def get_nice_voice_group(
    region: Region,
    voice: MstSvtVoice,
    svt_id: int,
    costume_ids: Dict[int, int],
    subtitles: List[GlobalNewMstSubtitle],
) -> Dict[str, Any]:

    subtitle_ids = {item.id: item.serif for item in subtitles}

    return {
        "type": VOICE_TYPE_NAME[voice.type],
        "voiceLines": [
            get_nice_voice_line(region, item, svt_id, costume_ids, subtitle_ids)
            for item in voice.scriptJson
        ],
    }


@lru_cache(maxsize=settings.lru_cache_size)
def get_nice_servant(
    region: Region, item_id: int, lang: Language, lore: bool = False
) -> Dict[str, Any]:
    # Get expanded servant entity to get function and buff details
    raw_data = get_servant_entity(region, item_id, expand=True, lore=lore)
    nice_data: Dict[str, Any] = {
        "id": raw_data.mstSvt.id,
        "collectionNo": raw_data.mstSvt.collectionNo,
        "name": raw_data.mstSvt.name,
        "gender": GENDER_NAME[raw_data.mstSvt.genderType],
        "attribute": ATTRIBUTE_NAME[raw_data.mstSvt.attri],
        "className": CLASS_NAME[raw_data.mstSvt.classId],
        "type": SVT_TYPE_NAME[raw_data.mstSvt.type],
        "cost": raw_data.mstSvt.cost,
        "instantDeathChance": raw_data.mstSvt.deathRate,
        "starGen": raw_data.mstSvt.starRate,
        "traits": get_traits_list(sorted(raw_data.mstSvt.individuality)),
        "starAbsorb": raw_data.mstSvtLimit[0].criticalWeight,
        "rarity": raw_data.mstSvtLimit[0].rarity,
        "cards": [CARD_TYPE_NAME[item] for item in raw_data.mstSvt.cardIds],
        "bondGrowth": masters[region].mstFriendshipId.get(
            raw_data.mstSvt.friendshipId, []
        ),
        "bondEquip": masters[region].bondEquip.get(item_id, 0),
    }

    if region == Region.JP and lang == Language.en:
        nice_data["name"] = get_safe(SVT_NAME_JP_EN, nice_data["name"])

    charaGraph: Dict[str, Dict[int, str]] = {}
    faces: Dict[str, Dict[int, str]] = {}
    commands: Dict[str, Dict[int, str]] = {}
    status: Dict[str, Dict[int, str]] = {}
    charaFigure: Dict[str, Dict[int, str]] = {}
    narrowFigure: Dict[str, Dict[int, str]] = {}
    equipFace: Dict[str, Dict[int, str]] = {}

    costume_limits = {item.id for item in raw_data.mstSvtCostume}
    costume_ids = {
        item.limitCount: item.battleCharaId
        for item in raw_data.mstSvtLimitAdd
        if item.limitCount in costume_limits
    }

    base_settings = {"base_url": settings.asset_url, "region": region}
    base_settings_id = dict(item_id=item_id, **base_settings)

    if raw_data.mstSvt.type == SvtType.ENEMY_COLLECTION_DETAIL:
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
            item_id: AssetURL.charaGraphDefault.format(**base_settings_id)
        }
        faces["equip"] = {item_id: AssetURL.face.format(**base_settings_id, i=0)}
        equipFace["equip"] = {
            item_id: AssetURL.equipFace.format(**base_settings_id, i=0)
        }

    nice_data["extraAssets"] = {
        "charaGraph": charaGraph,
        "faces": faces,
        "charaFigure": charaFigure,
        "narrowFigure": narrowFigure,
        "commands": commands,
        "status": status,
        "equipFace": equipFace,
    }

    lvMax = max([item.lvMax for item in raw_data.mstSvtLimit])
    nice_data["lvMax"] = lvMax
    if raw_data.mstSvt.type == SvtType.NORMAL:
        lvMax = 100
    atkMax = raw_data.mstSvtLimit[0].atkMax
    atkBase = raw_data.mstSvtLimit[0].atkBase
    hpMax = raw_data.mstSvtLimit[0].hpMax
    hpBase = raw_data.mstSvtLimit[0].hpBase
    growthCurve = raw_data.mstSvt.expType
    growthCurveValues = masters[region].mstSvtExpId[growthCurve][1 : lvMax + 1]
    atkGrowth = [
        atkBase + (atkMax - atkBase) * curve // 1000 for curve in growthCurveValues
    ]
    hpGrowth = [
        hpBase + (hpMax - hpBase) * curve // 1000 for curve in growthCurveValues
    ]
    nice_data.update(
        {
            "growthCurve": growthCurve,
            "atkMax": atkMax,
            "atkBase": atkBase,
            "hpMax": hpMax,
            "hpBase": hpBase,
            "atkGrowth": atkGrowth,
            "hpGrowth": hpGrowth,
        }
    )

    nice_data["hitsDistribution"] = {
        CARD_TYPE_NAME[item.cardId]: item.normalDamage for item in raw_data.mstSvtCard
    }

    ascensionAddIndividuality = {
        "ascension": {
            item.limitCount: get_traits_list(sorted(item.individuality))
            for item in raw_data.mstSvtLimitAdd
            if item.limitCount not in costume_ids
        },
        "costume": {
            costume_ids[item.limitCount]: get_traits_list(sorted(item.individuality))
            for item in raw_data.mstSvtLimitAdd
            if item.limitCount in costume_ids
        },
    }

    nice_data["ascensionAdd"] = {"individuality": ascensionAddIndividuality}

    # Filter out dummy TDs that are probably used by enemy servants that don't use their NPs
    actualTDs: List[TdEntityNoReverse] = [
        item
        for item in raw_data.mstTreasureDevice
        if item.mstSvtTreasureDevice[0].num == 1
    ]
    if actualTDs and "tdTypeChangeIDs" in actualTDs[0].mstTreasureDevice.script:
        for actualTD in actualTDs:
            tdTypeChangeIDs: List[int] = actualTD.mstTreasureDevice.script[
                "tdTypeChangeIDs"
            ]
            currentActualTDsIDs = {item.mstTreasureDevice.id for item in actualTDs}
            for td in raw_data.mstTreasureDevice:
                if (
                    td.mstTreasureDevice.id in tdTypeChangeIDs
                    and td.mstTreasureDevice.id not in currentActualTDsIDs
                ):
                    actualTDs.append(td)

    nice_data["ascensionMaterials"] = {
        combineLimit.svtLimit: {
            "items": get_nice_item_amount(
                region, combineLimit.itemIds, combineLimit.itemNums
            ),
            "qp": combineLimit.qp,
        }
        for combineLimit in raw_data.mstCombineLimit
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
            item[0]: item[1:]
            for item in orjson.loads(raw_data.mstSvt.script["SkillRankUp"])
        }

    nice_data["script"] = script

    nice_data["skills"] = [
        get_nice_skill(skill, item_id, region) for skill in raw_data.mstSkill
    ]
    nice_data["classPassive"] = [
        get_nice_skill(skill, item_id, region)
        for skill in raw_data.mstSvt.expandedClassPassive
    ]
    nice_data["noblePhantasms"] = [get_nice_td(td, item_id, region) for td in actualTDs]

    if lore:
        if raw_data.mstSvt.cvId in masters[region].mstCvId:
            cv = masters[region].mstCvId[raw_data.mstSvt.cvId].name
        else:
            cv = ""

        if raw_data.mstSvt.illustratorId in masters[region].mstIllustratorId:
            illustrator = (
                masters[region].mstIllustratorId[raw_data.mstSvt.illustratorId].name
            )
        else:
            illustrator = ""

        nice_data["profile"] = {
            "cv": cv,
            "illustrator": illustrator,
            "costume": {
                costume_ids[costume.id]: get_nice_costume(costume)
                for costume in raw_data.mstSvtCostume
            },
            "comments": [get_nice_comment(item) for item in raw_data.mstSvtComment],
            "voices": [
                get_nice_voice_group(
                    region, item, item_id, costume_ids, raw_data.mstSubtitle
                )
                for item in raw_data.mstSvtVoice
            ],
        }

        if raw_data.mstSvt.isServant():
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
    region: Region, item_id: int, lang: Language, lore: bool = False
) -> NiceServant:
    return NiceServant.parse_obj(get_nice_servant(region, item_id, lang, lore))


def get_nice_equip_model(
    region: Region, item_id: int, lang: Language, lore: bool = False
) -> NiceEquip:
    return NiceEquip.parse_obj(get_nice_servant(region, item_id, lang, lore))


@lru_cache(maxsize=settings.lru_cache_size)
def get_nice_buff_alone(
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceBuffReverse:
    raw_data = get_buff_entity_no_reverse(region, buff_id)
    nice_data = NiceBuffReverse.parse_obj(get_nice_buff(raw_data, region))
    if reverse and reverseDepth >= ReverseDepth.function:
        if reverseData == ReverseData.basic:
            basic_buff_reverse = BasicReversedBuff(
                function=[
                    get_basic_function(region, func_id, lang, reverse, reverseDepth)
                    for func_id in buff_to_func(region, buff_id)
                ]
            )
            nice_data.reverse = NiceReversedBuffType(basic=basic_buff_reverse)
        else:
            buff_reverse = NiceReversedBuff(
                function=[
                    get_nice_func_alone(region, func_id, lang, reverse, reverseDepth)
                    for func_id in buff_to_func(region, buff_id)
                ]
            )
            nice_data.reverse = NiceReversedBuffType(nice=buff_reverse)
    return nice_data


@lru_cache(maxsize=settings.lru_cache_size)
def get_nice_func_alone(
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceBaseFunctionReverse:
    raw_data = get_func_entity_no_reverse(region, func_id, expand=True)
    nice_data = NiceBaseFunctionReverse.parse_obj(
        get_nice_base_function(raw_data, region)
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        if reverseData == ReverseData.basic:
            basic_func_reverse = BasicReversedFunction(
                skill=[
                    get_basic_skill(region, skill_id, lang, reverse, reverseDepth)
                    for skill_id in func_to_skillId(region, func_id)
                ],
                NP=[
                    get_basic_td(region, td_id, lang, reverse, reverseDepth)
                    for td_id in func_to_tdId(region, func_id)
                ],
            )
            nice_data.reverse = NiceReversedFunctionType(basic=basic_func_reverse)
        else:
            func_reverse = NiceReversedFunction(
                skill=[
                    get_nice_skill_alone(region, skill_id, lang, reverse, reverseDepth)
                    for skill_id in func_to_skillId(region, func_id)
                ],
                NP=[
                    get_nice_td_alone(region, td_id, lang, reverse, reverseDepth)
                    for td_id in func_to_tdId(region, func_id)
                ],
            )
            nice_data.reverse = NiceReversedFunctionType(nice=func_reverse)
    return nice_data


@lru_cache(maxsize=settings.lru_cache_size)
def get_nice_skill_alone(
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceSkillReverse:
    raw_data = get_skill_entity_no_reverse(region, skill_id, expand=True)

    svt_list = [item.svtId for item in raw_data.mstSvtSkill]
    if svt_list:
        svtId = svt_list[0]
    else:
        svtId = 0
    nice_data = NiceSkillReverse.parse_obj(get_nice_skill(raw_data, svtId, region))

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {item.svtId for item in raw_data.mstSvtSkill}
        passiveSkills = passive_to_svtId(region, skill_id)
        if reverseData == ReverseData.basic:
            basic_skill_reverse = BasicReversedSkillTd(
                servant=[
                    get_basic_servant(region, item, lang=lang)
                    for item in activeSkills | passiveSkills
                ],
                MC=[
                    get_basic_mc(region, item)
                    for item in skill_to_MCId(region, skill_id)
                ],
                CC=[
                    get_basic_cc(region, item)
                    for item in skill_to_CCId(region, skill_id)
                ],
            )
            nice_data.reverse = NiceReversedSkillTdType(basic=basic_skill_reverse)
        else:
            skill_reverse = NiceReversedSkillTd(
                servant=[
                    get_nice_servant_model(region, item, lang=lang)
                    for item in activeSkills | passiveSkills
                ],
                MC=[
                    get_nice_mystic_code(region, item)
                    for item in skill_to_MCId(region, skill_id)
                ],
                CC=[
                    get_nice_command_code(region, item)
                    for item in skill_to_CCId(region, skill_id)
                ],
            )
            nice_data.reverse = NiceReversedSkillTdType(nice=skill_reverse)
    return nice_data


@lru_cache(maxsize=settings.lru_cache_size)
def get_nice_td_alone(
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    reverseData: ReverseData = ReverseData.nice,
) -> NiceTdReverse:
    raw_data = get_td_entity_no_reverse(region, td_id, expand=True)

    svt_list = [item.svtId for item in raw_data.mstSvtTreasureDevice]
    svtId = svt_list[0]  # Yes, all td_id has a svtTd entry
    nice_data = NiceTdReverse.parse_obj(get_nice_td(raw_data, svtId, region))

    if reverse and reverseDepth >= ReverseDepth.servant:
        if reverseData == ReverseData.basic:
            basic_td_reverse = BasicReversedSkillTd(
                servant=[
                    get_basic_servant(region, item.svtId, lang=lang)
                    for item in raw_data.mstSvtTreasureDevice
                ]
            )
            nice_data.reverse = NiceReversedSkillTdType(basic=basic_td_reverse)
        else:
            td_reverse = NiceReversedSkillTd(
                servant=[
                    get_nice_servant_model(region, item.svtId, lang=lang)
                    for item in raw_data.mstSvtTreasureDevice
                ]
            )
            nice_data.reverse = NiceReversedSkillTdType(nice=td_reverse)
    return nice_data


def get_nice_mystic_code(region: Region, mc_id: int) -> NiceMysticCode:
    raw_data = get_mystic_code_entity(region, mc_id, expand=True)
    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_data: Dict[str, Any] = {
        "id": raw_data.mstEquip.id,
        "name": raw_data.mstEquip.name,
        "detail": raw_data.mstEquip.detail,
        "maxLv": raw_data.mstEquip.maxLv,
        "extraAssets": {
            asset_category: {
                "male": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_data.mstEquip.maleImageId,
                ),
                "female": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_data.mstEquip.femaleImageId,
                ),
            }
            for asset_category in ("item", "masterFace", "masterFigure")
        },
    }

    raw_exp = sorted(raw_data.mstEquipExp, key=lambda x: x.lv)
    nice_data["expRequired"] = [exp.exp for exp in raw_exp if exp.exp != -1]

    nice_data["skills"] = [
        get_nice_skill(skill, mc_id, region) for skill in raw_data.mstSkill
    ]
    return NiceMysticCode.parse_obj(nice_data)


def get_nice_command_code(region: Region, cc_id: int) -> NiceCommandCode:
    raw_data = get_command_code_entity(region, cc_id, expand=True)

    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}
    nice_data: Dict[str, Any] = {
        "id": raw_data.mstCommandCode.id,
        "name": raw_data.mstCommandCode.name,
        "collectionNo": raw_data.mstCommandCode.collectionNo,
        "rarity": raw_data.mstCommandCode.rarity,
        "comment": raw_data.mstCommandCodeComment.comment,
        "extraAssets": {
            "charaGraph": {
                "cc": {cc_id: AssetURL.commandGraph.format(**base_settings)}
            },
            "faces": {"cc": {cc_id: AssetURL.commandCode.format(**base_settings)}},
        },
    }

    nice_data["skills"] = [
        get_nice_skill(skill, cc_id, region) for skill in raw_data.mstSkill
    ]
    return NiceCommandCode.parse_obj(nice_data)


def get_nice_quest_phase(region: Region, quest_id: int, phase: int) -> Dict[str, Any]:
    raw_data = get_quest_phase_entity(region, quest_id, phase)
    nice_data: Dict[str, Any] = {
        "id": raw_data.mstQuest.id,
        "phase": raw_data.mstQuestPhase.phase,
        "name": raw_data.mstQuest.name,
        "type": get_safe(QUEST_TYPE_NAME, raw_data.mstQuest.type),
        "consumeType": get_safe(QUEST_CONSUME_TYPE_NAME, raw_data.mstQuest.consumeType),
        "consume": raw_data.mstQuest.actConsume,
        "spotId": raw_data.mstQuest.spotId,
        "className": [CLASS_NAME[item] for item in raw_data.mstQuestPhase.classIds],
        "individuality": get_traits_list(raw_data.mstQuestPhase.individuality),
        "qp": raw_data.mstQuestPhase.qp,
        "exp": raw_data.mstQuestPhase.playerExp,
        "bond": raw_data.mstQuestPhase.friendshipExp,
        "noticeAt": raw_data.mstQuest.noticeAt,
        "openedAt": raw_data.mstQuest.openedAt,
        "closedAt": raw_data.mstQuest.closedAt,
    }
    return nice_data
