import re
from typing import Any, Optional

from fastapi import HTTPException
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings, logger
from ...schemas.common import Language, Region
from ...schemas.enums import FUNC_APPLYTARGET_NAME, FUNC_VALS_NOT_BUFF
from ...schemas.gameenums import FUNC_TARGETTYPE_NAME, FUNC_TYPE_NAME, FuncType
from ...schemas.nice import (
    AssetURL,
    FunctionScript,
    NiceFuncGroup,
    ValCheckBattlePointPhaseRange,
    ValDamageRateBattlePointPhase,
)
from ...schemas.raw import FunctionEntityNoReverse, MstFunc, MstFuncGroup
from ..raw import get_func_entity_no_reverse
from ..utils import fmt_url, get_traits_list, get_traits_list_list
from .buff import get_nice_buff


settings = Settings()


def remove_brackets(val_string: str) -> str:
    return val_string.removeprefix("[").removesuffix("]")


EVENT_DROP_FUNCTIONS = {
    FuncType.EVENT_POINT_UP,
    FuncType.EVENT_POINT_RATE_UP,
    FuncType.EVENT_DROP_UP,
    FuncType.EVENT_DROP_RATE_UP,
    FuncType.EVENT_FORTIFICATION_POINT_UP,
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
LIST_DATAVALS = {
    "TargetList",
    "TargetRarityList",
    "AndCheckIndividualityList",
    "ParamAddSelfIndividuality",
    "ParamAddOpIndividuality",
    "ParamAddFieldIndividuality",
    "DamageRates",
    "OnPositions",
    "OffPositions",
    "NotTargetSkillIdArray",
    "CopyTargetFunctionType",
    "CopyTargetBuffType",
    "NotSkillCopyTargetFuncIds",
    "NotSkillCopyTargetIndividualities",
    "TargetEnemyRange",
    "FieldIndividuality",
    "SnapShotParamAddSelfIndv",
    "SnapShotParamAddOpIndv",
    "SnapShotParamAddFieldIndv",
    "StartingPosition",
    "ShortenMaxCountEachSkill",
    "TargetFunctionIndividuality",
    "TargetBuffIndividuality",
    "TriggeredFuncIndexAndCheckList",
}
LIST_2D_DATAVALS = {
    "ParamAddSelfIndividualityAndCheck",
    "ParamAddOpIndividualityAndCheck",
    "ParamAddFieldIndividualityAndCheck",
    "SnapShotParamAddSelfIndividualityAndCheck",
    "SnapShotParamAddOpIndividualityAndCheck",
    "SnapShotParamAddFieldIndividualityAndCheck",
    "AndOrCheckIndividualityList",
}
STRING_DATAVALS = {
    "PopValueText",
    "TriggeredFieldCountRange",
    "TriggeredTargetHpRange",
    "TriggeredTargetHpRateRange",
    "DisplayNoEffectCauses",
}
STRING_LIST_DATAVALS = {"ApplyValueUp", "CheckOverChargeStageRange"}


DataValType = dict[
    str,
    int
    | str
    | list[int]
    | list[list[int]]
    | list[str]
    | dict[str, Any]
    | list[ValDamageRateBattlePointPhase]
    | list[ValCheckBattlePointPhaseRange],
]


async def parse_dataVals(
    conn: AsyncConnection, region: Region, datavals: str, functype: int, lang: Language
) -> DataValType:
    error_message = f"Can't parse datavals: {datavals}"
    exception = HTTPException(status_code=500, detail=error_message)
    INITIAL_VALUE = -98765
    # Prefix to be used for temporary keys that need further parsing.
    # Some functions' datavals can't be parsed by themselves and need the first
    # or second datavals to determine whether it's a rate % or an absolute value.
    # See the "Further parsing" section.
    # The prefix should be something unlikely to be a dataval key.
    prefix = "aa"
    DamageRateBattlePointPhase: list[ValDamageRateBattlePointPhase] = []
    CheckBattlePointPhaseRange: list[ValCheckBattlePointPhaseRange] = []
    AddIndividualtyList: list[int] = []

    output: DataValType = {}
    if datavals != "[]":
        datavals = remove_brackets(datavals)
        array = re.split(r",\s*(?![^\[\]]*])", datavals)
        for i, arrayi in enumerate(array):
            if arrayi == "":
                continue
            text = ""
            value = INITIAL_VALUE
            try:
                value = int(arrayi)
                if functype in {
                    FuncType.DAMAGE_NP_INDIVIDUAL,
                    FuncType.DAMAGE_NP_STATE_INDIVIDUAL,
                    FuncType.DAMAGE_NP_STATE_INDIVIDUAL_FIX,
                    FuncType.DAMAGE_NP_INDIVIDUAL_SUM,
                    FuncType.DAMAGE_NP_RARE,
                    FuncType.DAMAGE_NP_AND_OR_CHECK_INDIVIDUALITY,
                    FuncType.DAMAGE_NP_BATTLE_POINT_PHASE,
                }:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Target"
                    elif i == 3:
                        text = "Correction"
                elif functype in {
                    FuncType.ADD_STATE,
                    FuncType.ADD_STATE_SHORT,
                    FuncType.ADD_FIELD_CHANGE_TO_FIELD,
                }:
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
                elif functype in {
                    FuncType.SUB_STATE,
                    FuncType.GAIN_NP_INDIVIDUAL_SUM,
                    FuncType.GAIN_NP_TARGET_SUM,
                    FuncType.SUB_FIELD_BUFF,
                    FuncType.SHORTEN_SKILL,
                    FuncType.EXTEND_SKILL,
                    FuncType.SHORTEN_USER_EQUIP_SKILL,
                    FuncType.EXTEND_USER_EQUIP_SKILL,
                }:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Value2"
                elif functype == FuncType.TRANSFORM_SERVANT:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "Value"
                    elif i == 2:
                        text = "Target"
                    elif i == 3:
                        text = "SetLimitCount"
                elif functype in EVENT_FUNCTIONS:
                    if i == 0:
                        text = "Individuality"
                    elif i == 3:
                        text = "EventId"
                    else:
                        text = prefix + str(i)
                elif functype == FuncType.CLASS_DROP_UP:
                    if i == 2:
                        text = "EventId"
                    else:
                        text = prefix + str(i)
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
                        text = prefix + str(i)
                elif functype in {
                    FuncType.FRIEND_POINT_UP,
                    FuncType.FRIEND_POINT_UP_DUPLICATE,
                }:
                    if i == 0:
                        text = "AddCount"
                elif functype == FuncType.ADD_BATTLE_POINT:
                    if i == 0:
                        text = "Rate"
                    elif i == 1:
                        text = "BattlePointId"
                    elif i == 2:
                        text = "BattlePointValue"
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
                        # using DUMMY_PREFIX + ... and parse it later
                        if "DependFuncId" not in output:
                            logger.error(
                                f"Failed to find DependFuncId dataval for {arrayi}"
                            )
                            raise exception from None

                        depend_func_entity = await get_func_entity_no_reverse(
                            conn,
                            int(output["DependFuncId"]),  # type: ignore[arg-type]
                        )

                        output["DependFunc"] = await get_nice_function(
                            conn, region, depend_func_entity, lang
                        )
                        output["DependFuncVals"] = await parse_dataVals(
                            conn,
                            region,
                            array2[1],
                            depend_func_entity.mstFunc.funcType,
                            lang,
                        )
                    elif array2[0] in LIST_DATAVALS:
                        try:
                            output[array2[0]] = [
                                int(i)
                                for i in array2[1].split(
                                    "/" if "/" in array2[1] else "&"
                                )
                            ]
                        except ValueError:
                            logger.error(
                                f"Failed to parse list datavals: {array2[1]} of {arrayi}"
                            )
                    elif array2[0] in LIST_2D_DATAVALS:
                        try:
                            output[array2[0]] = [
                                [
                                    int(i)
                                    for i in arrayi.split("/" if "/" in arrayi else "&")
                                ]
                                for arrayi in array2[1].split("|")
                            ]
                        except ValueError:
                            logger.error(
                                f"Failed to parse list datavals: {array2[1]} of {arrayi}"
                            )
                    elif array2[0] in STRING_LIST_DATAVALS:
                        output[array2[0]] = array2[1].split("/")
                    elif array2[0] in STRING_DATAVALS:
                        output[array2[0]] = array2[1]
                    elif array2[0].startswith("DamageRateBattlePointPhase"):
                        DamageRateBattlePointPhase.append(
                            ValDamageRateBattlePointPhase(
                                battlePointPhase=int(array2[0].split("_")[1]),
                                value=int(array2[1]),
                            )
                        )
                    elif array2[0].startswith("CheckBattlePointPhaseRange"):
                        CheckBattlePointPhaseRange.append(
                            ValCheckBattlePointPhaseRange(
                                battlePointId=int(array2[0].split("_")[1]),
                                range=array2[1].split("/"),
                            )
                        )
                    else:
                        try:
                            text = array2[0]
                            value = int(array2[1])
                            if text == "AddIndividualty":
                                AddIndividualtyList.append(value)
                        except ValueError:
                            logger.error(
                                f"Failed to parse string dataval to int: {array2[1]} of {arrayi}"
                            )
                else:
                    logger.error(f"Failed to parse keyword dataval: {arrayi}")

            if text:
                output[text] = value

        if DamageRateBattlePointPhase:
            output["DamageRateBattlePointPhase"] = DamageRateBattlePointPhase
        if CheckBattlePointPhaseRange:
            output["CheckBattlePointPhaseRange"] = CheckBattlePointPhaseRange
        if AddIndividualtyList:
            output["AddIndividualtyList"] = AddIndividualtyList

        if not any(key.startswith(prefix) for key in output):
            if (
                len([val for val in array if val])
                != (
                    len([k for k in output if k != "DependFunc"])
                    + (
                        max(len(AddIndividualtyList) - 2, -1)
                        if AddIndividualtyList
                        else 0
                    )
                )
                and functype != FuncType.NONE
            ):
                logger.warning(
                    f"Some datavals weren't parsed for func type {functype}: [{datavals}] => {output}"
                )

    # Further parsing
    prefix_0 = prefix + "0"
    prefix_1 = prefix + "1"
    prefix_2 = prefix + "2"
    if functype in EVENT_FUNCTIONS and prefix_1 in output:
        if output[prefix_1] == 1:
            output["AddCount"] = output[prefix_2]
        elif output[prefix_1] == 2:
            output["RateCount"] = output[prefix_2]
        elif output[prefix_1] == 3:
            output["DropRateCount"] = output[prefix_2]
    elif (
        functype in {FuncType.CLASS_DROP_UP} | FRIEND_SUPPORT_FUNCTIONS
        and prefix_0 in output
    ):
        if output[prefix_0] == 1:
            output["AddCount"] = output[prefix_1]
        elif output[prefix_0] == 2:
            output["RateCount"] = output[prefix_1]

    return output


def get_func_group_icon(region: Region, funcType: int, iconId: int) -> HttpUrl | None:
    if iconId == 0:
        return None

    base_settings = {"base_url": settings.asset_url, "region": region}
    if funcType in EVENT_DROP_FUNCTIONS:
        return fmt_url(AssetURL.items, **base_settings, item_id=iconId)
    else:
        return fmt_url(
            AssetURL.eventUi, **base_settings, event=f"func_group_icon_{iconId}"
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


def get_nice_func_script(mstFunc: MstFunc) -> FunctionScript:
    if not mstFunc.script:
        return FunctionScript()

    script: dict[str, Any] = {}
    if "overwriteTvals" in mstFunc.script:
        script["overwriteTvals"] = get_traits_list_list(
            mstFunc.script["overwriteTvals"]
        )
    if "funcIndividuality" in mstFunc.script:
        script["funcIndividuality"] = get_traits_list(
            mstFunc.script["funcIndividuality"]
        )

    return FunctionScript.model_validate(script)


async def get_nice_function(
    conn: AsyncConnection,
    region: Region,
    function: FunctionEntityNoReverse,
    lang: Language,
    svals: Optional[list[str]] = None,
    svals2: Optional[list[str]] = None,
    svals3: Optional[list[str]] = None,
    svals4: Optional[list[str]] = None,
    svals5: Optional[list[str]] = None,
    followerVals: Optional[list[str]] = None,
) -> dict[str, Any]:
    nice_func: dict[str, Any] = {
        "funcId": function.mstFunc.id,
        "funcPopupText": function.mstFunc.popupText,
        "funcquestTvals": get_traits_list(function.mstFunc.questTvals),
        "functvals": get_traits_list(function.mstFunc.tvals),
        "overWriteTvalsList": get_traits_list_list(
            function.mstFunc.overWriteTvalsList or []
        ),
        "funcType": FUNC_TYPE_NAME[function.mstFunc.funcType],
        "funcTargetTeam": FUNC_APPLYTARGET_NAME[function.mstFunc.applyTarget],
        "funcTargetType": FUNC_TARGETTYPE_NAME[function.mstFunc.targetType],
        "funcGroup": [
            get_nice_func_group(region, func_group, function.mstFunc.funcType)
            for func_group in function.mstFuncGroup
        ],
        "buffs": [
            get_nice_buff(buff, region, lang) for buff in function.mstFunc.expandedVals
        ],
        "script": get_nice_func_script(function.mstFunc),
    }

    if function.mstFunc.funcType in FUNC_VALS_NOT_BUFF:
        nice_func["traitVals"] = get_traits_list(function.mstFunc.vals)

    funcPopupIconId = function.mstFunc.popupIconId
    if funcPopupIconId != 0:
        nice_func["funcPopupIcon"] = AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=funcPopupIconId
        )

    for field, argument in [
        ("svals", svals),
        ("svals2", svals2),
        ("svals3", svals3),
        ("svals4", svals4),
        ("svals5", svals5),
        ("followerVals", followerVals),
    ]:
        if argument:
            nice_func[field] = [
                await parse_dataVals(
                    conn, region, sval, function.mstFunc.funcType, lang
                )
                for sval in argument
            ]

    return nice_func
