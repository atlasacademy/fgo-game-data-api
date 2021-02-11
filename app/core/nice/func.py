import re
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import (
    FUNC_APPLYTARGET_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    FUNC_VALS_NOT_BUFF,
    FuncType,
)
from ...schemas.nice import AssetURL, NiceFuncGroup
from ...schemas.raw import FunctionEntityNoReverse, MstFuncGroup
from ..utils import get_traits_list
from .buff import get_nice_buff


settings = Settings()


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
