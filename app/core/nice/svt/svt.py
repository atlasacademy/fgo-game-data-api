from typing import Any, Optional

import orjson
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from ....config import Settings
from ....data.custom_mappings import TRIAL_QUESTS
from ....schemas.common import Language, NiceCostume, Region
from ....schemas.enums import (
    SERVANT_PERSONALITY_NAME,
    SERVANT_POLICY_NAME,
    ServantPersonality,
    ServantPolicy,
    get_class_name,
)
from ....schemas.gameenums import (
    ATTRIBUTE_NAME,
    CARD_TYPE_NAME,
    COND_TYPE_NAME,
    GENDER_TYPE_NAME,
    SVT_FLAG_NAME,
    SVT_FLAG_ORIGINAL_NAME,
    SVT_TYPE_NAME,
    NiceSvtFlag,
    SvtType,
)
from ....schemas.nice import (
    NiceLoreComment,
    NiceLoreCommentAdd,
    NiceServantChange,
    NiceServantLimitImage,
)
from ....schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    MstSvt,
    MstSvtChange,
    MstSvtComment,
    MstSvtCommentAdd,
    MstSvtCostume,
    MstSvtLimitImage,
    ServantEntity,
)
from ... import raw
from ...utils import get_flags, get_traits_list, get_translation
from ..item import get_nice_item_amount_qp, get_nice_item_from_raw
from ..skill import get_nice_skill_with_svt
from ..td import get_nice_td
from .append_passive import get_nice_svt_append_passives
from .ascensionAdd import get_nice_ascensionAdd
from .asset import (
    get_male_image_extraAssets,
    get_nice_image_parts_group,
    get_svt_extraAssets,
)
from .battle_point import get_svt_bp
from .card import get_nice_card
from .chara_script import get_nice_chara_script
from .individuality import get_nice_svt_trait
from .limit import get_nice_status_rank, get_nice_svt_limit
from .overwrite import get_nice_svt_overwrite
from .voice import get_nice_voice


settings = Settings()


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
        ruby=change.ruby,
        battleName=change.battleName,
        svtVoiceId=change.svtVoiceId,
        limitCount=change.limitCount,
        flag=change.flag,
        battleSvtId=change.battleSvtId,
    )


def get_nice_comment_adds(comment_add: MstSvtCommentAdd) -> NiceLoreCommentAdd:
    return NiceLoreCommentAdd(
        idx=comment_add.idx,
        condType=COND_TYPE_NAME[comment_add.condType],
        condValues=comment_add.condValues,
        condValue2=comment_add.condValue2,
    )


def get_nice_comment(
    comment: MstSvtComment, comment_adds: list[MstSvtCommentAdd]
) -> NiceLoreComment:
    return NiceLoreComment(
        id=comment.id,
        priority=comment.priority,
        condMessage=comment.condMessage,
        comment=comment.comment,
        condType=COND_TYPE_NAME[comment.condType],
        condValues=comment.condValues,
        condValue2=comment.condValue2,
        additionalConds=[
            get_nice_comment_adds(add)
            for add in comment_adds
            if add.id == comment.id and add.priority == comment.priority
        ],
    )


def get_nice_costume(
    costume: MstSvtCostume, battleCharaId: int, lang: Language
) -> NiceCostume:
    return NiceCostume(
        id=costume.id,
        costumeCollectionNo=costume.costumeCollectionNo,
        battleCharaId=battleCharaId,
        name=costume.name,
        shortName=get_translation(lang, costume.shortName),
        detail=costume.detail,
        priority=costume.priority,
    )


def get_nice_svt_limit_image(limit_image: MstSvtLimitImage) -> NiceServantLimitImage:
    return NiceServantLimitImage(
        limitCount=limit_image.limitCount,
        priority=limit_image.priority,
        defaultLimitCount=limit_image.defaultLimitCount,
        condType=COND_TYPE_NAME[limit_image.condType],
        condTargetId=limit_image.condTargetId,
        condNum=limit_image.condNum,
    )


async def get_nice_servant(
    conn: AsyncConnection,
    region: Region,
    svt_id: int,
    lang: Language,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
    raw_svt: Optional[ServantEntity] = None,
) -> dict[str, Any]:
    # Get expanded servant entity to get function and buff details
    if not raw_svt:
        raw_svt = await raw.get_servant_entity(
            conn, svt_id, expand=True, lore=lore, mstSvt=mstSvt
        )

    if not raw_svt.mstSvtLimit:
        raise HTTPException(status_code=404, detail="Svt not found")
    last_svt_limit = raw_svt.mstSvtLimit[-1]

    nice_data: dict[str, Any] = {
        "id": raw_svt.mstSvt.id,
        "collectionNo": raw_svt.mstSvt.collectionNo,
        "name": get_translation(lang, raw_svt.mstSvt.name),
        "originalName": raw_svt.mstSvt.name,
        "ruby": raw_svt.mstSvt.ruby,
        "battleName": get_translation(lang, raw_svt.mstSvt.battleName),
        "originalBattleName": raw_svt.mstSvt.battleName,
        "gender": GENDER_TYPE_NAME[raw_svt.mstSvt.genderType],
        "attribute": ATTRIBUTE_NAME[raw_svt.mstSvt.attri],
        "classId": raw_svt.mstSvt.classId,
        "className": get_class_name(raw_svt.mstSvt.classId),
        "type": SVT_TYPE_NAME[raw_svt.mstSvt.type],
        "flag": SVT_FLAG_NAME.get(raw_svt.mstSvt.flag, NiceSvtFlag.unknown),
        "flags": get_flags(raw_svt.mstSvt.flag, SVT_FLAG_ORIGINAL_NAME),
        "cost": raw_svt.mstSvt.cost,
        "instantDeathChance": raw_svt.mstSvt.deathRate,
        "starGen": raw_svt.mstSvt.starRate,
        "traits": get_traits_list(sorted(raw_svt.mstSvt.individuality)),
        "starAbsorb": last_svt_limit.criticalWeight,
        "rarity": last_svt_limit.rarity,
        "cards": [CARD_TYPE_NAME[card_id] for card_id in raw_svt.mstSvt.cardIds],
        "charaScripts": [get_nice_chara_script(s) for s in raw_svt.mstSvtScript],
        "battlePoints": get_svt_bp(raw_svt.mstBattlePoint, raw_svt.mstBattlePointPhase),
        "bondGrowth": [
            friendship.friendship
            for friendship in sorted(
                raw_svt.mstFriendship, key=lambda friendship: friendship.rank
            )
            if friendship.friendship != -1
        ],
        "traitAdd": [
            get_nice_svt_trait(svt_individuality)
            for svt_individuality in raw_svt.mstSvtIndividuality
        ],
        "limits": [get_nice_svt_limit(limit) for limit in raw_svt.mstSvtLimit],
        "overwrites": [
            await get_nice_svt_overwrite(
                conn, region, overwrite, svt_id, raw_svt.mstTreasureDevice, lang
            )
            for overwrite in raw_svt.mstSvtOverwrite
        ],
        # "bondEquip": masters[region].bondEquip.get(svt_id, 0),
        "relateQuestIds": raw_svt.mstSvt.relateQuestIds,
        "trialQuestIds": TRIAL_QUESTS.get(svt_id, []),
    }

    if raw_svt.mstSvtExtra:
        nice_data["bondEquip"] = raw_svt.mstSvtExtra.bondEquip
        nice_data["valentineEquip"] = raw_svt.mstSvtExtra.valentineEquip
        nice_data["valentineScript"] = raw_svt.mstSvtExtra.valentineScript
        nice_data["bondEquipOwner"] = raw_svt.mstSvtExtra.bondEquipOwner
        nice_data["valentineEquipOwner"] = raw_svt.mstSvtExtra.valentineEquipOwner
        costume_ids = {
            costumeMap.id: costumeMap.battleCharaId
            for limitCount, costumeMap in raw_svt.mstSvtExtra.costumeLimitSvtIdMap.items()
            if limitCount > 10
        }
    else:
        nice_data["bondEquip"] = 0
        nice_data["valentineEquip"] = []
        nice_data["valentineScript"] = []
        nice_data["bondEquipOwner"] = None
        nice_data["valentineEquipOwner"] = None
        costume_ids = {}

    nice_data["extraAssets"] = get_svt_extraAssets(region, svt_id, raw_svt, costume_ids)

    lvMax = max(svt_limit.lvMax for svt_limit in raw_svt.mstSvtLimit)
    atkMax = last_svt_limit.atkMax
    atkBase = last_svt_limit.atkBase
    hpMax = last_svt_limit.hpMax
    hpBase = last_svt_limit.hpBase
    growthCurveMax = 121 if raw_svt.mstSvt.type == SvtType.NORMAL else (lvMax + 1)
    if raw_svt.mstSvt.type == SvtType.HEROINE and region == Region.JP:
        growthCurveMax = 91
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

    card_add_map = {card_add.cardId: card_add for card_add in raw_svt.mstSvtCardAdd}
    nice_data["cardDetails"] = {
        CARD_TYPE_NAME[svt_card.cardId]: get_nice_card(
            svt_card, card_add_map.get(svt_card.cardId)
        )
        for svt_card in raw_svt.mstSvtCard
    }

    nice_data["ascensionAdd"] = get_nice_ascensionAdd(
        region, raw_svt, costume_ids, lang
    )

    nice_data["svtChange"] = [
        get_nice_servant_change(change) for change in raw_svt.mstSvtChange
    ]

    nice_data["ascensionImage"] = [
        get_nice_svt_limit_image(limitImage) for limitImage in raw_svt.mstSvtLimitImage
    ]

    item_map = {
        item.id: get_nice_item_from_raw(region, item, lang) for item in raw_svt.mstItem
    }

    nice_data["ascensionMaterials"] = {
        combine.svtLimit: get_nice_item_amount_qp(
            combine.itemIds, combine.itemNums, combine.qp, item_map
        )
        for combine in raw_svt.mstCombineLimit
        if combine.svtLimit != BAD_COMBINE_SVT_LIMIT
    }

    nice_data["skillMaterials"] = {
        combine.skillLv: get_nice_item_amount_qp(
            combine.itemIds, combine.itemNums, combine.qp, item_map
        )
        for combine in raw_svt.mstCombineSkill
    }

    nice_data["appendSkillMaterials"] = {
        combine.skillLv: get_nice_item_amount_qp(
            combine.itemIds, combine.itemNums, combine.qp, item_map
        )
        for combine in raw_svt.mstCombineAppendPassiveSkill
    }

    nice_data["costumeMaterials"] = {
        costume_ids[combine.costumeId]: get_nice_item_amount_qp(
            combine.itemIds, combine.itemNums, combine.qp, item_map
        )
        for combine in raw_svt.mstCombineCostume
        if combine.costumeId in costume_ids
    }

    if raw_svt.mstSvtCoin:
        nice_data["coin"] = {
            "summonNum": raw_svt.mstSvtCoin.summonNum,
            "item": item_map[raw_svt.mstSvtCoin.itemId],
        }

    nice_data["script"] = {}
    if "SkillRankUp" in raw_svt.mstSvt.script:
        nice_data["script"]["SkillRankUp"] = {
            rank_up_script[0]: rank_up_script[1:]
            for rank_up_script in orjson.loads(raw_svt.mstSvt.script["SkillRankUp"])
        }
    if "svtBuffTurnExtend" in raw_svt.mstSvt.script:
        nice_data["script"]["svtBuffTurnExtend"] = (
            raw_svt.mstSvt.script["svtBuffTurnExtend"] == 1
        )
    if "maleImageId" in raw_svt.mstSvt.script:
        nice_data["script"]["maleImage"] = get_male_image_extraAssets(
            region, raw_svt.mstSvt.script["maleImageId"]
        )
    if "imagePartsGroupId" in raw_svt.mstSvt.script:
        nice_data["script"]["imagePartsGroup"] = [
            get_nice_image_parts_group(imagePartsGroup)
            for imagePartsGroup in raw_svt.mstImagePartsGroup
            if imagePartsGroup.id == raw_svt.mstSvt.script["imagePartsGroupId"]
        ]

    nice_data["skills"] = [
        skill
        for skillEntity in raw_svt.mstSkill
        for skill in await get_nice_skill_with_svt(
            conn, skillEntity, svt_id, region, lang
        )
    ]

    nice_data["classPassive"] = [
        skill
        for skillEntity in raw_svt.mstSvt.expandedClassPassive
        for skill in await get_nice_skill_with_svt(
            conn, skillEntity, svt_id, region, lang
        )
    ]

    nice_data["extraPassive"] = [
        skill
        for skillEntity in raw_svt.expandedExtraPassive
        for skill in await get_nice_skill_with_svt(
            conn,
            skillEntity,
            svt_id,
            region,
            lang,
            raw_svt.mstSvtPassiveSkill,
            raw_svt.mstCommonRelease,
        )
    ]

    nice_data["appendPassive"] = await get_nice_svt_append_passives(
        conn, region, raw_svt, item_map, lang
    )

    # Filter out dummy TDs that are used by enemy servants
    if raw_svt.mstSvt.isServant():
        playable_tds = [
            td
            for td in raw_svt.mstTreasureDevice
            if next(
                svtTd for svtTd in td.mstSvtTreasureDevice if svtTd.svtId == svt_id
            ).num
            == 1
        ]

        to_append_td_ids: set[int] = set()

        for playable_td in playable_tds:
            for k, v in playable_td.mstTreasureDevice.script.items():
                if k == "tdTypeChangeIDs":
                    # Space Ishtar different NPs
                    tdTypeChangeIDs: list[int] = v
                    to_append_td_ids |= set(tdTypeChangeIDs)
                elif k.startswith("tdChangeByBattlePoint"):
                    to_append_td_ids.add(int(v))

        for td in raw_svt.mstTreasureDevice:
            if td.mstTreasureDevice.id in to_append_td_ids and td not in playable_tds:
                playable_tds.append(td)
    else:
        playable_tds = raw_svt.mstTreasureDevice

    nice_data["noblePhantasms"] = [
        td
        for tdEntity in sorted(playable_tds, key=lambda x: x.mstTreasureDevice.id)
        for td in await get_nice_td(conn, tdEntity, svt_id, region, lang)
    ]

    if lore:
        nice_data["profile"] = {
            "cv": get_translation(lang, raw_svt.mstCv.name if raw_svt.mstCv else ""),
            "illustrator": get_translation(
                lang, raw_svt.mstIllustrator.name if raw_svt.mstIllustrator else ""
            ),
            "costume": {
                costume_ids[costume.id]: get_nice_costume(
                    costume, costume_ids[costume.id], lang
                )
                for costume in raw_svt.mstSvtCostume
                if costume.id in costume_ids
            },
            "comments": [
                get_nice_comment(svt_comment, raw_svt.mstSvtCommentAdd)
                for svt_comment in raw_svt.mstSvtComment
            ],
            "voices": get_nice_voice(region, raw_svt, costume_ids, lang),
            "stats": {
                "strength": get_nice_status_rank(last_svt_limit.power),
                "endurance": get_nice_status_rank(last_svt_limit.defense),
                "agility": get_nice_status_rank(last_svt_limit.agility),
                "magic": get_nice_status_rank(last_svt_limit.magic),
                "luck": get_nice_status_rank(last_svt_limit.luck),
                "np": get_nice_status_rank(last_svt_limit.treasureDevice),
                "deity": get_nice_status_rank(last_svt_limit.deity),
                "policy": SERVANT_POLICY_NAME.get(
                    last_svt_limit.policy, ServantPolicy.unknown
                ),
                "personality": SERVANT_PERSONALITY_NAME.get(
                    last_svt_limit.personality, ServantPersonality.unknown
                ),
            },
        }

    return nice_data
