from typing import Any, Dict, Union, List

from fastapi import APIRouter, HTTPException

from ..data import gamedata
from ..data.models.common import Region
from ..data.models.raw import SkillEntityNoReverse, FuncType
from ..data.models.nice import (
    Attribute,
    CardType,
    Gender,
    NiceServant,
    SvtClass,
    Trait,
)


CARD_TYPE_NAME: Dict[int, CardType] = {
    1: CardType.arts,
    2: CardType.buster,
    3: CardType.quick,
    4: CardType.extra,
}


GENDER_NAME: Dict[int, Gender] = {1: Gender.male, 2: Gender.female, 3: Gender.unknown}


ATTRIBUTE_NAME: Dict[int, Attribute] = {
    1: Attribute.human,
    2: Attribute.sky,
    3: Attribute.earth,
    4: Attribute.star,
    5: Attribute.beast,
}


CLASS_NAME: Dict[int, SvtClass] = {
    1: SvtClass.saber,
    2: SvtClass.archer,
    3: SvtClass.lancer,
    4: SvtClass.rider,
    5: SvtClass.caster,
    6: SvtClass.assassin,
    7: SvtClass.berserker,
    8: SvtClass.shielder,
    9: SvtClass.ruler,
    10: SvtClass.alterEgo,
    11: SvtClass.avenger,
    23: SvtClass.moonCancer,
    25: SvtClass.foreigner,
}


TRAIT_NAME: Dict[int, Trait] = {
    1: Trait.genderMale,
    2: Trait.genderFemale,
    3: Trait.genderUnknown,
    100: Trait.classSaber,
    101: Trait.classLancer,
    102: Trait.classArcher,
    103: Trait.classrider,
    104: Trait.classCaster,
    105: Trait.classAssassin,
    106: Trait.classBerserker,
    107: Trait.classShielder,
    108: Trait.classRuler,
    109: Trait.classAlterEgo,
    110: Trait.classAvenger,
    111: Trait.classDemonGodPillar,
    112: Trait.classGrandCaster,
    113: Trait.classBeastI,
    114: Trait.classBeastII,
    115: Trait.classMoonCancer,
    116: Trait.classBeastIIIR,
    117: Trait.classForeigner,
    118: Trait.classBeastIIIL,
    119: Trait.classBeastMaybe,
    200: Trait.attributeSky,
    201: Trait.attributeEarth,
    202: Trait.attributeHuman,
    203: Trait.attributeStar,
    204: Trait.attributeBeast,
    300: Trait.alignmentLawful,
    301: Trait.alignmentChaotic,
    302: Trait.alignmentNeutral,
    303: Trait.alignmentGood,
    304: Trait.alignmentEvil,
    305: Trait.alignmentBalanced,
    306: Trait.alignmentMadness,
    308: Trait.alignmentSummer,
    1000: Trait.basedOnServant,  # can be NPC or enemy but use a servant's data
    1001: Trait.human,  # Sanson's 3rd skill
    1002: Trait.undead,  # Scathach's 3rd skill
    1003: Trait.artificialDemon,
    1004: Trait.demonBeast,
    1005: Trait.daemon,
    1100: Trait.soldier,
    1101: Trait.amazoness,
    1102: Trait.skeleton,
    1103: Trait.zombie,
    1104: Trait.ghost,
    1105: Trait.automata,
    1106: Trait.golem,
    1107: Trait.spellBook,
    1108: Trait.homunculus,
    1110: Trait.lamia,
    1111: Trait.centaur,
    1112: Trait.werebeast,
    1113: Trait.chimera,
    1117: Trait.wyvern,
    1118: Trait.dragonType,
    1119: Trait.gazer,
    1120: Trait.handOrDoor,
    1121: Trait.demonGodPillar,
    1132: Trait.oni,
    1133: Trait.hand,
    1134: Trait.door,
    1172: Trait.threatToHumanity,
    2000: Trait.divine,
    2001: Trait.humanoid,
    2002: Trait.dragon,
    2003: Trait.dragonSlayer,
    2004: Trait.roman,
    2005: Trait.wildbeast,
    2006: Trait.atalante,
    2007: Trait.saberface,
    2008: Trait.weakToEnumaElish,
    2009: Trait.riding,
    2010: Trait.arthur,
    2011: Trait.skyOrEarth,  # Tesla's NP
    2012: Trait.brynhildsBeloved,
    2018: Trait.undeadOrDaemon,  # Amakusa bond Ce
    2019: Trait.demonic,
    2037: Trait.skyOrEarthExceptPseudoAndDemi,  # Raikou's 3rd skill
    2040: Trait.divineOrDaemonOrUndead,  # Ruler Martha's 3rd skill
    2075: Trait.saberClassServant,  # MHXA NP
    2076: Trait.superGiant,
    2113: Trait.king,
    2114: Trait.greekMythologyMales,
    2355: Trait.illya,
    2356: Trait.genderUnknownServant,  # Teach's 3rd skill
    2466: Trait.argonaut,
    2615: Trait.genderCaenisServant,  # Phantom's 2nd skill
    2631: Trait.humanoidServant,  # used in TamaVitch's fight
    2632: Trait.beastServant,  # used in TamaVitch's fight
    5000: Trait.canBeInBattle,  # can be NPC, enemy or playable servant i.e. not CE
    5010: Trait.notBasedOnServant,
}


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


def get_nice_skill(skillEntity: SkillEntityNoReverse, svtId: int) -> Dict[str, Any]:
    nice_skill: Dict[str, Any] = {}
    nice_skill["id"] = skillEntity.mstSkill.id
    nice_skill["name"] = skillEntity.mstSkill.name
    nice_skill["iconId"] = skillEntity.mstSkill.iconId
    nice_skill["detail"] = skillEntity.mstSkillDetail[0].detail.replace(" [{0}] ", " ")

    chosenSvt = [item for item in skillEntity.mstSvtSkill if item.svtId == svtId]
    if len(chosenSvt) > 0:
        nice_skill["strengthStatus"] = chosenSvt[0].strengthStatus
        nice_skill["num"] = chosenSvt[0].num
        nice_skill["priority"] = chosenSvt[0].priority
        nice_skill["condQuestId"] = chosenSvt[0].condQuestId
        nice_skill["condQuestPhase"] = chosenSvt[0].condQuestPhase

    nice_skill["coolDown"] = [skillEntity.mstSkillLv[0].chargeTurn]
    nice_skill["functions"] = []

    for i in range(len(skillEntity.mstSkillLv[0].funcId)):
        function = skillEntity.mstSkillLv[0].expandedFuncId[i]
        functionInfo: Dict[str, Any] = {}
        functionInfo["funcId"] = function.mstFunc.id
        functionInfo["funcPopupText"] = function.mstFunc.popupText
        functionInfo["funcPopupIconId"] = function.mstFunc.popupIconId
        functionInfo["functvals"] = get_traits_list(function.mstFunc.tvals)

        buffs = []
        if len(function.mstFunc.expandedVals) > 0:
            for buff in function.mstFunc.expandedVals:
                buffInfo: Dict[str, Any] = {}
                buffInfo["id"] = buff.mstBuff.id
                buffInfo["name"] = buff.mstBuff.name
                buffInfo["detail"] = buff.mstBuff.detail
                buffInfo["iconId"] = buff.mstBuff.iconId
                buffInfo["type"] = buff.mstBuff.type
                buffInfo["vals"] = get_traits_list(buff.mstBuff.vals)
                buffInfo["tvals"] = get_traits_list(buff.mstBuff.tvals)
                buffInfo["ckOpIndv"] = get_traits_list(buff.mstBuff.ckOpIndv)
                buffInfo["ckSelfIndv"] = get_traits_list(buff.mstBuff.ckSelfIndv)
                buffs.append(buffInfo)
        functionInfo["buffs"] = buffs

        dataVals = parseDataVals(
            skillEntity.mstSkillLv[0].svals[i], function.mstFunc.funcType
        )
        svals: Dict[str, Any] = {}
        for key, value in dataVals.items():
            svals[key] = [value]
        functionInfo["svals"] = svals
        nice_skill["functions"].append(functionInfo)

    for skillLv in skillEntity.mstSkillLv[1:]:
        nice_skill["coolDown"].append(skillLv.chargeTurn)
        for i in range(len(skillLv.funcId)):
            dataVals = parseDataVals(
                skillLv.svals[i], skillLv.expandedFuncId[i].mstFunc.funcType
            )
            for key, value in dataVals.items():
                nice_skill["functions"][i]["svals"][key].append(value)

    return nice_skill


def get_nice_servant(region: Region, item_id: int) -> Dict[str, Any]:
    raw_data = gamedata.get_servant_entity(region, item_id, True)
    nice_data: Dict[str, Any] = {}

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
        TRAIT_NAME.get(item, Trait.unknown)
        for item in sorted(raw_data.mstSvt.individuality)
        if item != item_id
    ]

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

    actualTDs = [
        item for item in raw_data.mstTreasureDevice if item.mstTreasureDevice.id != 100
    ]
    nice_data["busterNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointB / 10000
    nice_data["artsNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointA / 10000
    nice_data["quickNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointQ / 10000
    nice_data["extraNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPointEx / 10000
    nice_data["npNpGain"] = actualTDs[0].mstTreasureDeviceLv[0].tdPoint / 10000
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
