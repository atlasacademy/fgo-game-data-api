from typing import Any, Dict, Union, List

from fastapi import APIRouter, HTTPException

from ..data import gamedata
from ..data.models.common import Region, Settings
from ..data.models.raw import (
    BuffEntityNoReverse,
    SkillEntityNoReverse,
    TdEntityNoReverse,
    FuncType,
)
from ..data.models.nice import (
    NiceServant,
    Trait,
    CARD_TYPE_NAME,
    GENDER_NAME,
    ATTRIBUTE_NAME,
    CLASS_NAME,
    TRAIT_NAME,
    FUNC_TYPE_NAME,
    BUFF_TYPE_NAME,
)


FORMATTING_BRACKETS = {"[g][o]": "", "[/o][/g]": "", " [{0}] ": " "}


settings = Settings()


def strip_formatting_brackets(detail_string: str) -> str:
    for k, v in FORMATTING_BRACKETS.items():
        detail_string = detail_string.replace(k, v)
    return detail_string


def get_traits_list(input_idv: List[int]) -> List[Union[Trait, int]]:
    return [TRAIT_NAME.get(item, item) for item in input_idv]


def parseDataVals(datavals: str, functype: int) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    array = datavals.replace("[", "").replace("]", "").split(",")
    for i, arrayi in enumerate(array):
        text = ""
        value = 0
        try:
            value = int(arrayi)
            if functype in [
                FuncType.DAMAGE_NP_INDIVIDUAL,
                FuncType.DAMAGE_NP_STATE_INDIVIDUAL,
                FuncType.DAMAGE_NP_STATE_INDIVIDUAL_FIX,
            ]:
                if i == 0:
                    text = "Rate"
                elif i == 1:
                    text = "Value"
                elif i == 2:
                    text = "Target"
                elif i == 3:
                    text = "Correction"
            elif functype in [FuncType.ADD_STATE, FuncType.ADD_STATE_SHORT]:
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
            elif functype != FuncType.SUB_STATE:
                if i == 0:
                    text = "Rate"
                elif i == 1:
                    text = "Value"
                elif i == 2:
                    text = "Target"
            else:
                if i == 0:
                    text = "Rate"
                elif i == 1:
                    text = "Value"
                elif i == 2:
                    text = "Value2"
        except ValueError:
            array2 = arrayi.split(":")
            if len(array2) > 1:
                text = array2[0]
                try:
                    value = int(array2[1])
                except ValueError:
                    if "strVals" in output:
                        output["strVals"][text] = array2[1]
                    else:
                        output["strVals"] = {text: array2[1]}
        if text != "":
            output[text] = value
    return output


def is_level_dependent(function: Dict[str, Any]) -> Any:
    # not the best response type because of the Any in Dict
    return (
        function["svals"]
        == function.get("svals2", [])
        == function.get("svals3", [])
        == function.get("svals4", [])
        == function.get("svals5", [])
    )


def is_overcharge_dependent(function: Dict[str, Any]) -> bool:
    isOvercharge = True
    svalsCount = len([key for key in function.keys() if key.startswith("svals")])
    for vali in range(1, svalsCount + 1):
        valName = f"svals{vali}" if vali >= 2 else "svals"
        if valName in function:
            for valValues in function[valName].values():
                isOvercharge &= len(set(valValues)) == 1
    return isOvercharge


def is_constant(function: Dict[str, Any]) -> bool:
    return is_overcharge_dependent(function) and is_level_dependent(function)


def combine_svals_overcharge(function: Dict[str, Any]) -> Dict[str, Any]:
    svals: Dict[str, List[Any]] = {}
    for valType in function["svals"]:
        svals[valType] = []
        for vali in range(1, 6):
            valName = f"svals{vali}" if vali >= 2 else "svals"
            svals[valType].append(function[valName][valType][0])
    return svals


def categorize_functions(
    combinedFunctionList: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    functions: Dict[str, List[Dict[str, Any]]] = {
        "level": [],
        "overcharge": [],
        "constant": [],
        "other": [],
    }
    svalsCount = len(
        [key for key in combinedFunctionList[0].keys() if key.startswith("svals")]
    )
    if svalsCount > 1:
        # TD combinedFunc
        for combinedFunc in combinedFunctionList:
            if is_constant(combinedFunc):
                for vali in range(2, 6):
                    combinedFunc.pop(f"svals{vali}")
                functions["constant"].append(combinedFunc)
            elif is_level_dependent(combinedFunc):
                for vali in range(2, 6):
                    combinedFunc.pop(f"svals{vali}")
                functions["level"].append(combinedFunc)
            elif is_overcharge_dependent(combinedFunc):
                svals = combine_svals_overcharge(combinedFunc)
                for vali in range(2, 6):
                    combinedFunc.pop(f"svals{vali}")
                combinedFunc["svals"] = svals
                functions["overcharge"].append(combinedFunc)
            else:
                functions["other"].append(combinedFunc)
    else:
        # Skill combinedFunc
        for combinedFunc in combinedFunctionList:
            if is_overcharge_dependent(combinedFunc):
                # check for constant value in the datavals arrays
                functions["constant"].append(combinedFunc)
            else:
                functions["level"].append(combinedFunc)

    functions = {k: v for k, v in functions.items() if len(v) > 0}
    return functions


def get_nice_buff(buffEntity: BuffEntityNoReverse) -> Dict[str, Any]:
    buffInfo: Dict[str, Any] = {}
    buffInfo["id"] = buffEntity.mstBuff.id
    buffInfo["name"] = buffEntity.mstBuff.name
    buffInfo["detail"] = buffEntity.mstBuff.detail
    iconId = buffEntity.mstBuff.iconId
    if iconId != 0:
        iconUrl = f"{settings.asset_url}/BuffIcons/DownloadBuffIcon/DownloadBuffIconAtlas1/bufficon_{iconId}.png"
        buffInfo["icon"] = iconUrl
    buffInfo["type"] = BUFF_TYPE_NAME.get(
        buffEntity.mstBuff.type, buffEntity.mstBuff.type
    )
    buffInfo["vals"] = get_traits_list(buffEntity.mstBuff.vals)
    buffInfo["tvals"] = get_traits_list(buffEntity.mstBuff.tvals)
    buffInfo["ckOpIndv"] = get_traits_list(buffEntity.mstBuff.ckOpIndv)
    buffInfo["ckSelfIndv"] = get_traits_list(buffEntity.mstBuff.ckSelfIndv)
    return buffInfo


def get_nice_skill(skillEntity: SkillEntityNoReverse, svtId: int) -> Dict[str, Any]:
    nice_skill: Dict[str, Any] = {}
    nice_skill["id"] = skillEntity.mstSkill.id
    nice_skill["name"] = skillEntity.mstSkill.name
    iconId = skillEntity.mstSkill.iconId
    if iconId != 0:
        if iconId < 520:
            iconAtlas = 1
        else:
            iconAtlas = 2
        iconUrl = f"{settings.asset_url}/SkillIcons/DownloadSkillIcon/DownloadSkillIconAtlas{iconAtlas}/skill_{iconId:05}.png"
        nice_skill["icon"] = iconUrl
    print(nice_skill["icon"])
    nice_skill["detail"] = strip_formatting_brackets(
        skillEntity.mstSkillDetail[0].detail
    )

    chosenSvt = [item for item in skillEntity.mstSvtSkill if item.svtId == svtId]
    if len(chosenSvt) > 0:
        nice_skill["strengthStatus"] = chosenSvt[0].strengthStatus
        nice_skill["num"] = chosenSvt[0].num
        nice_skill["priority"] = chosenSvt[0].priority
        nice_skill["condQuestId"] = chosenSvt[0].condQuestId
        nice_skill["condQuestPhase"] = chosenSvt[0].condQuestPhase

    nice_skill["coolDown"] = [skillEntity.mstSkillLv[0].chargeTurn]

    combinedFunctionList: List[Dict[str, Any]] = []

    # Build the first function item and add the first svals value
    for funci in range(len(skillEntity.mstSkillLv[0].funcId)):
        function = skillEntity.mstSkillLv[0].expandedFuncId[funci]
        functionInfo: Dict[str, Any] = {}
        functionInfo["funcId"] = function.mstFunc.id
        functionInfo["funcPopupText"] = function.mstFunc.popupText
        funcPopupIconId = function.mstFunc.popupIconId
        if funcPopupIconId != 0:
            iconUrl = f"{settings.asset_url}/BuffIcons/DownloadBuffIcon/DownloadBuffIconAtlas1/bufficon_{funcPopupIconId}.png"
            functionInfo["funcPopupIcon"] = iconUrl
        functionInfo["functvals"] = get_traits_list(function.mstFunc.tvals)
        functionInfo["funcType"] = FUNC_TYPE_NAME.get(
            function.mstFunc.funcType, function.mstFunc.funcType
        )

        buffs = []
        if len(function.mstFunc.expandedVals) > 0:
            for buff in function.mstFunc.expandedVals:
                buffs.append(get_nice_buff(buff))
        functionInfo["buffs"] = buffs

        dataVals = parseDataVals(
            skillEntity.mstSkillLv[0].svals[funci], function.mstFunc.funcType
        )
        svals: Dict[str, Any] = {}
        for key, value in dataVals.items():
            svals[key] = [value]
        functionInfo["svals"] = svals
        combinedFunctionList.append(functionInfo)

    # Add the remaining cooldown and svals values
    for skillLv in skillEntity.mstSkillLv[1:]:
        nice_skill["coolDown"].append(skillLv.chargeTurn)
        for funci in range(len(skillLv.funcId)):
            dataVals = parseDataVals(
                skillLv.svals[funci], skillLv.expandedFuncId[funci].mstFunc.funcType
            )
            for key, value in dataVals.items():
                combinedFunctionList[funci]["svals"][key].append(value)

    nice_skill["functions"] = categorize_functions(combinedFunctionList)

    return nice_skill


def get_nice_td(tdEntity: TdEntityNoReverse, svtId: int) -> Dict[str, Any]:
    nice_td: Dict[str, Any] = {}
    nice_td["id"] = tdEntity.mstTreasureDevice.id
    nice_td["name"] = tdEntity.mstTreasureDevice.name
    nice_td["rank"] = tdEntity.mstTreasureDevice.rank
    nice_td["typeText"] = tdEntity.mstTreasureDevice.typeText
    nice_td["npNpGain"] = tdEntity.mstTreasureDeviceLv[0].tdPoint / 10000
    nice_td["detail"] = strip_formatting_brackets(
        tdEntity.mstTreasureDeviceDetail[0].detail
    )

    chosenSvt = [item for item in tdEntity.mstSvtTreasureDevice if item.svtId == svtId]
    nice_td["strengthStatus"] = chosenSvt[0].strengthStatus
    nice_td["num"] = chosenSvt[0].num
    nice_td["priority"] = chosenSvt[0].priority
    nice_td["condQuestId"] = chosenSvt[0].condQuestId
    nice_td["condQuestPhase"] = chosenSvt[0].condQuestPhase
    nice_td["card"] = CARD_TYPE_NAME[chosenSvt[0].cardId]
    nice_td["npDistribution"] = chosenSvt[0].damage

    combinedFunctionList: List[Dict[str, Any]] = []

    # Build the first function item and add the first svals value
    for funci in range(len(tdEntity.mstTreasureDeviceLv[0].funcId)):
        function = tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci]
        functionInfo: Dict[str, Any] = {}
        functionInfo["funcId"] = function.mstFunc.id
        functionInfo["funcPopupText"] = function.mstFunc.popupText
        functionInfo["funcPopupIconId"] = function.mstFunc.popupIconId
        functionInfo["functvals"] = get_traits_list(function.mstFunc.tvals)
        functionInfo["funcType"] = FUNC_TYPE_NAME.get(
            function.mstFunc.funcType, function.mstFunc.funcType
        )

        buffs = []
        if len(function.mstFunc.expandedVals) > 0:
            for buff in function.mstFunc.expandedVals:
                buffs.append(get_nice_buff(buff))
        functionInfo["buffs"] = buffs

        for vali in range(1, 6):
            valName = f"svals{vali}" if vali >= 2 else "svals"
            dataVals = parseDataVals(
                getattr(tdEntity.mstTreasureDeviceLv[0], valName)[funci],
                function.mstFunc.funcType,
            )
            svals: Dict[str, Any] = {}
            for key, value in dataVals.items():
                svals[key] = [value]
            functionInfo[valName] = svals
        combinedFunctionList.append(functionInfo)

    # Add the remaining svals values
    for tdLv in tdEntity.mstTreasureDeviceLv[1:]:
        for funci in range(len(tdLv.funcId)):
            for vali in range(1, 6):
                valName = f"svals{vali}" if vali >= 2 else "svals"
                dataVals = parseDataVals(
                    getattr(tdLv, valName)[funci],
                    tdLv.expandedFuncId[funci].mstFunc.funcType,
                )
                for key, value in dataVals.items():
                    combinedFunctionList[funci][valName][key].append(value)

    nice_td["functions"] = categorize_functions(combinedFunctionList)

    return nice_td


def get_nice_servant(region: Region, item_id: int) -> Dict[str, Any]:
    raw_data = gamedata.get_servant_entity(region, item_id, True)
    nice_data: Dict[str, Any] = {}

    nice_data["id"] = raw_data.mstSvt.id
    nice_data["collectionNo"] = raw_data.mstSvt.collectionNo
    nice_data["name"] = raw_data.mstSvt.name
    nice_data["gender"] = GENDER_NAME[raw_data.mstSvt.genderType]
    nice_data["attribute"] = ATTRIBUTE_NAME[raw_data.mstSvt.attri]
    nice_data["className"] = CLASS_NAME[raw_data.mstSvt.classId]
    nice_data["cost"] = raw_data.mstSvt.cost
    nice_data["instantDeathChance"] = raw_data.mstSvt.deathRate / 1000
    nice_data["starAbsorb"] = raw_data.mstSvtLimit[0].criticalWeight
    nice_data["starGen"] = raw_data.mstSvt.starRate / 1000
    nice_data["traits"] = [
        TRAIT_NAME.get(item, item)
        for item in sorted(raw_data.mstSvt.individuality)
        if item != item_id
    ]

    charaGraph: Dict[str, Dict[int, str]] = {}
    charaGraph["ascension"] = {
        1: f"{settings.asset_url}/CharaGraph/{item_id}/{item_id}a@1.png",
        2: f"{settings.asset_url}/CharaGraph/{item_id}/{item_id}a@2.png",
        3: f"{settings.asset_url}/CharaGraph/{item_id}/{item_id}b@1.png",
        4: f"{settings.asset_url}/CharaGraph/{item_id}/{item_id}b@2.png",
    }
    costume_ids = [
        item.battleCharaId for item in raw_data.mstSvtLimitAdd if item.limitCount == 11
    ]
    if len(costume_ids) > 0:
        for costume_id in costume_ids:
            charaGraph["costume"] = {
                costume_id: f"{settings.asset_url}/CharaGraph/{costume_id}/{costume_id}a.png"
            }
    nice_data["extraAssets"] = {"charaGraph": charaGraph}

    atkMax = raw_data.mstSvtLimit[0].atkMax
    atkBase = raw_data.mstSvtLimit[0].atkBase
    hpMax = raw_data.mstSvtLimit[0].hpMax
    hpBase = raw_data.mstSvtLimit[0].hpBase
    growthCurve = raw_data.mstSvt.expType
    growthCurveValues = [
        gamedata.masters[region].mstSvtExpId[growthCurve][lv].curve
        for lv in range(1, 101)
    ]
    atkGrowth = [
        atkBase + (atkMax - atkBase) * curve // 1000 for curve in growthCurveValues
    ]
    hpGrowth = [
        hpBase + (hpMax - hpBase) * curve // 1000 for curve in growthCurveValues
    ]

    nice_data["growthCurve"] = growthCurve
    nice_data["atkMax"] = atkMax
    nice_data["atkBase"] = atkBase
    nice_data["hpMax"] = hpMax
    nice_data["hpBase"] = hpBase
    nice_data["atkGrowth"] = atkGrowth
    nice_data["hpGrowth"] = hpGrowth

    nice_data["cards"] = [CARD_TYPE_NAME[item] for item in raw_data.mstSvt.cardIds]
    cardsDistribution = {item.cardId: item.normalDamage for item in raw_data.mstSvtCard}
    nice_data["artsDistribution"] = cardsDistribution[1]
    nice_data["busterDistribution"] = cardsDistribution[2]
    nice_data["quickDistribution"] = cardsDistribution[3]
    nice_data["extraDistribution"] = cardsDistribution[4]

    actualTDs: List[TdEntityNoReverse] = [
        item for item in raw_data.mstTreasureDevice if item.mstTreasureDevice.id != 100
    ]
    nice_data["busterNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointB / 10000
    nice_data["artsNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointA / 10000
    nice_data["quickNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointQ / 10000
    nice_data["extraNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointEx / 10000
    nice_data["defenceNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointDef / 10000

    ascenionMaterials = {}
    for combineLimit in raw_data.mstCombineLimit:
        itemLists = [
            {
                "id": item,
                "name": gamedata.masters[region].mstItemId[item].name,
                "amount": amount,
            }
            for item, amount in zip(combineLimit.itemIds, combineLimit.itemNums)
        ]
        ascenionMaterials[combineLimit.svtLimit + 1] = {
            "items": itemLists,
            "qp": combineLimit.qp,
        }
    nice_data["ascenionMaterials"] = ascenionMaterials

    skillMaterials = {}
    for combineSkill in raw_data.mstCombineSkill:
        itemLists = [
            {
                "id": item,
                "name": gamedata.masters[region].mstItemId[item].name,
                "amount": amount,
            }
            for item, amount in zip(combineSkill.itemIds, combineSkill.itemNums)
        ]
        skillMaterials[combineSkill.skillLv] = {
            "items": itemLists,
            "qp": combineSkill.qp,
        }
    nice_data["skillMaterials"] = skillMaterials

    nice_data["skills"] = [
        get_nice_skill(skill, item_id) for skill in raw_data.mstSkill
    ]
    nice_data["classPassive"] = [
        get_nice_skill(skill, item_id) for skill in raw_data.mstSvt.expandedClassPassive
    ]
    nice_data["NPs"] = [get_nice_td(td, item_id) for td in actualTDs]
    return nice_data


router = APIRouter()


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=NiceServant,
    response_model_exclude_unset=True,
)
async def get_servant(region: Region, item_id: int):
    """
    Get servant info from ID

    If the given ID is a servants's collectionNo, the corresponding servant data is returned.
    Otherwise, it will look up the actual ID field.
    """
    if item_id in gamedata.masters[region].mstSvtServantCollectionNo:
        item_id = gamedata.masters[region].mstSvtServantCollectionNo[item_id]
    if (
        item_id in gamedata.masters[region].mstSvtId
        and gamedata.masters[region].mstSvtId[item_id].collectionNo
        in gamedata.masters[region].mstSvtServantCollectionNo
    ):
        return get_nice_servant(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")
