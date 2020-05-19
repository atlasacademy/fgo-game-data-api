from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..data import gamedata
from ..data.models.common import Region
from ..data.models.nice import Attribute, CardType, Gender, NiceServantEntity


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
    3: Attribute.ground,
    4: Attribute.star,
    5: Attribute.beast,
}


def get_nice_servant(region: Region, item_id: int) -> Dict[str, Any]:
    raw_data = gamedata.get_servant_entity(region, item_id)
    nice_data: Dict[str, Any] = {}

    nice_data["collectionNo"] = raw_data.mstSvt.collectionNo
    nice_data["name"] = raw_data.mstSvt.name
    nice_data["gender"] = GENDER_NAME[raw_data.mstSvt.genderType]
    nice_data["attribute"] = ATTRIBUTE_NAME[raw_data.mstSvt.attri]
    nice_data["cost"] = raw_data.mstSvt.cost
    nice_data["instantDeathChance"] = raw_data.mstSvt.deathRate / 1000
    nice_data["starAbsorb"] = raw_data.mstSvtLimit[0].criticalWeight
    nice_data["starGen"] = raw_data.mstSvt.starRate / 1000

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
    return nice_data


router = APIRouter()


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=NiceServantEntity,
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
