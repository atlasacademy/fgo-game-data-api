from typing import Any, Optional

import orjson
from sqlalchemy.engine import Connection

from ....config import Settings
from ....data.gamedata import masters
from ....schemas.common import Language, Region
from ....schemas.enums import ATTRIBUTE_NAME, CLASS_NAME
from ....schemas.gameenums import (
    CARD_TYPE_NAME,
    COND_TYPE_NAME,
    GENDER_TYPE_NAME,
    STATUS_RANK_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    NiceStatusRank,
    SvtType,
)
from ....schemas.nice import NiceCostume, NiceLoreComment, NiceServantChange
from ....schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    MstSvt,
    MstSvtChange,
    MstSvtComment,
    MstSvtCostume,
)
from ... import raw
from ...utils import get_traits_list, get_translation
from ..item import get_nice_item_amount
from ..skill import get_nice_skill_with_svt
from ..td import get_nice_td
from .ascensionAdd import get_nice_ascensionAdd
from .asset import get_svt_extraAssets
from .card import get_nice_card
from .voice import get_nice_voice


settings = Settings()


def get_nice_status_rank(rank_number: int) -> NiceStatusRank:
    return STATUS_RANK_NAME.get(rank_number, NiceStatusRank.unknown)


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


def get_nice_costume(costume: MstSvtCostume) -> NiceCostume:
    return NiceCostume(**costume.dict())


def get_nice_servant(
    conn: Connection,
    region: Region,
    svt_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
) -> dict[str, Any]:
    # Get expanded servant entity to get function and buff details
    raw_svt = raw.get_servant_entity(
        conn, svt_id, expand=True, lore=lore, mstSvt=mstSvt
    )
    first_svt_limit = raw_svt.mstSvtLimit[0]

    nice_data: dict[str, Any] = {
        "id": raw_svt.mstSvt.id,
        "collectionNo": raw_svt.mstSvt.collectionNo,
        "name": get_translation(lang, raw_svt.mstSvt.name),
        "ruby": raw_svt.mstSvt.ruby,
        "gender": GENDER_TYPE_NAME[raw_svt.mstSvt.genderType],
        "attribute": ATTRIBUTE_NAME[raw_svt.mstSvt.attri],
        "className": CLASS_NAME[raw_svt.mstSvt.classId],
        "type": SVT_TYPE_NAME[raw_svt.mstSvt.type],
        "flag": SVT_FLAG_NAME[raw_svt.mstSvt.flag],
        "cost": raw_svt.mstSvt.cost,
        "instantDeathChance": raw_svt.mstSvt.deathRate,
        "starGen": raw_svt.mstSvt.starRate,
        "traits": get_traits_list(sorted(raw_svt.mstSvt.individuality)),
        "starAbsorb": first_svt_limit.criticalWeight,
        "rarity": first_svt_limit.rarity,
        "cards": [CARD_TYPE_NAME[card_id] for card_id in raw_svt.mstSvt.cardIds],
        "bondGrowth": [
            friendship.friendship
            for friendship in sorted(
                raw_svt.mstFriendship, key=lambda friendship: friendship.rank
            )
            if friendship.friendship != -1
        ],
        "bondEquip": masters[region].bondEquip.get(svt_id, 0),
        "valentineEquip": masters[region].valentineEquip.get(svt_id, []),
        "bondEquipOwner": masters[region].bondEquipOwner.get(svt_id),
        "valentineEquipOwner": masters[region].valentineEquipOwner.get(svt_id),
        "relateQuestIds": raw_svt.mstSvt.relateQuestIds,
    }

    costume_limits = {svt_costume.id for svt_costume in raw_svt.mstSvtCostume}
    costume_ids = {
        svt_limit_add.limitCount: svt_limit_add.battleCharaId
        for svt_limit_add in raw_svt.mstSvtLimitAdd
        if svt_limit_add.limitCount in costume_limits
    }

    nice_data["extraAssets"] = get_svt_extraAssets(region, svt_id, raw_svt, costume_ids)

    lvMax = max(svt_limit.lvMax for svt_limit in raw_svt.mstSvtLimit)
    atkMax = first_svt_limit.atkMax
    atkBase = first_svt_limit.atkBase
    hpMax = first_svt_limit.hpMax
    hpBase = first_svt_limit.hpBase
    growthCurveMax = 101 if raw_svt.mstSvt.type == SvtType.NORMAL else (lvMax + 1)
    growthCurveValues = sorted(raw_svt.mstSvtExp, key=lambda svtExp: svtExp.lv)
    atkGrowth = [
        atkBase + (atkMax - atkBase) * exp.curve // 1000
        for exp in growthCurveValues[1:growthCurveMax]
    ]
    hpGrowth = [
        hpBase + (hpMax - hpBase) * exp.curve // 1000
        for exp in growthCurveValues[1:growthCurveMax]
    ]
    expGrowth = [exp.exp for exp in growthCurveValues[: growthCurveMax - 1]]
    nice_data |= {
        "lvMax": lvMax,
        "growthCurve": raw_svt.mstSvt.expType,
        "atkMax": atkMax,
        "atkBase": atkBase,
        "hpMax": hpMax,
        "hpBase": hpBase,
        "atkGrowth": atkGrowth,
        "hpGrowth": hpGrowth,
        "expGrowth": expGrowth,
    }

    nice_data["expFeed"] = [
        combine.value for combine in raw_svt.mstCombineMaterial[: growthCurveMax - 1]
    ]

    nice_data["hitsDistribution"] = {
        CARD_TYPE_NAME[svt_card.cardId]: svt_card.normalDamage
        for svt_card in raw_svt.mstSvtCard
    }

    nice_data["cardDetails"] = {
        CARD_TYPE_NAME[svt_card.cardId]: get_nice_card(svt_card)
        for svt_card in raw_svt.mstSvtCard
    }

    nice_data["ascensionAdd"] = get_nice_ascensionAdd(
        region, raw_svt, costume_ids, lang
    )

    nice_data["svtChange"] = [
        get_nice_servant_change(change) for change in raw_svt.mstSvtChange
    ]

    nice_data["ascensionMaterials"] = {
        combineLimit.svtLimit: {
            "items": get_nice_item_amount(
                region, combineLimit.itemIds, combineLimit.itemNums, lang
            ),
            "qp": combineLimit.qp,
        }
        for combineLimit in raw_svt.mstCombineLimit
        if combineLimit.svtLimit != BAD_COMBINE_SVT_LIMIT
    }

    nice_data["skillMaterials"] = {
        combineSkill.skillLv: {
            "items": get_nice_item_amount(
                region, combineSkill.itemIds, combineSkill.itemNums, lang
            ),
            "qp": combineSkill.qp,
        }
        for combineSkill in raw_svt.mstCombineSkill
    }

    nice_data["costumeMaterials"] = {
        costume_ids[combineCostume.costumeId]: {
            "items": get_nice_item_amount(
                region, combineCostume.itemIds, combineCostume.itemNums, lang
            ),
            "qp": combineCostume.qp,
        }
        for combineCostume in raw_svt.mstCombineCostume
    }

    nice_data["script"] = {}
    if "SkillRankUp" in raw_svt.mstSvt.script:
        nice_data["script"]["SkillRankUp"] = {
            rank_up_script[0]: rank_up_script[1:]
            for rank_up_script in orjson.loads(raw_svt.mstSvt.script["SkillRankUp"])
        }

    nice_data["skills"] = [
        skill
        for skillEntity in raw_svt.mstSkill
        for skill in get_nice_skill_with_svt(skillEntity, svt_id, region, lang)
    ]

    nice_data["classPassive"] = [
        skill
        for skillEntity in raw_svt.mstSvt.expandedClassPassive
        for skill in get_nice_skill_with_svt(skillEntity, svt_id, region, lang)
    ]

    nice_data["extraPassive"] = [
        skill
        for skillEntity in raw_svt.expandedExtraPassive
        for skill in get_nice_skill_with_svt(skillEntity, svt_id, region, lang)
    ]

    # Filter out dummy TDs that are used by enemy servants
    if raw_svt.mstSvt.isServant():
        playable_tds = [
            td
            for td in raw_svt.mstTreasureDevice
            if td.mstSvtTreasureDevice[0].num == 1
        ]
        for playable_td in playable_tds:
            if "tdTypeChangeIDs" in playable_td.mstTreasureDevice.script:
                # Space Ishtar different NPs
                tdTypeChangeIDs: list[int] = playable_td.mstTreasureDevice.script[
                    "tdTypeChangeIDs"
                ]
                for td in raw_svt.mstTreasureDevice:
                    if (
                        td.mstTreasureDevice.id in tdTypeChangeIDs
                        and td not in playable_tds
                    ):
                        playable_tds.append(td)
    else:
        playable_tds = raw_svt.mstTreasureDevice

    nice_data["noblePhantasms"] = [
        td
        for tdEntity in sorted(playable_tds, key=lambda x: x.mstTreasureDevice.id)
        for td in get_nice_td(tdEntity, svt_id, region, lang)
    ]

    if lore:
        nice_data["profile"] = {
            "cv": raw_svt.mstCv.name if raw_svt.mstCv else "",
            "illustrator": raw_svt.mstIllustrator.name
            if raw_svt.mstIllustrator
            else "",
            "costume": {
                costume_ids[costume.id]: get_nice_costume(costume)
                for costume in raw_svt.mstSvtCostume
            },
            "comments": [
                get_nice_comment(svt_comment) for svt_comment in raw_svt.mstSvtComment
            ],
            "voices": get_nice_voice(region, raw_svt, costume_ids),
            "stats": {
                "strength": get_nice_status_rank(first_svt_limit.power),
                "endurance": get_nice_status_rank(first_svt_limit.defense),
                "agility": get_nice_status_rank(first_svt_limit.agility),
                "magic": get_nice_status_rank(first_svt_limit.magic),
                "luck": get_nice_status_rank(first_svt_limit.luck),
                "np": get_nice_status_rank(first_svt_limit.treasureDevice),
            },
        }

    return nice_data
