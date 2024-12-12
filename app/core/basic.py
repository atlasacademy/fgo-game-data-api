import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Generator, Iterable, Optional, Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection

from ..config import Settings, logger
from ..db.helpers import fetch, quest
from ..redis import Redis
from ..redis.helpers import pydantic_object
from ..redis.helpers.reverse import RedisReverse, get_reverse_ids
from ..schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicEvent,
    BasicFunctionReverse,
    BasicMysticCode,
    BasicQuest,
    BasicQuestPhase,
    BasicReversedBuff,
    BasicReversedBuffType,
    BasicReversedFunction,
    BasicReversedFunctionType,
    BasicReversedSkillTd,
    BasicReversedSkillTdType,
    BasicServant,
    BasicSkillReverse,
    BasicTdReverse,
    BasicWar,
)
from ..schemas.common import (
    BuffScript,
    Language,
    MCAssets,
    NiceTrait,
    Region,
    ReverseDepth,
)
from ..schemas.enums import (
    FUNC_APPLYTARGET_NAME,
    FUNC_VALS_NOT_BUFF,
    SvtClass,
    get_class_name,
)
from ..schemas.gameenums import (
    ATTRIBUTE_NAME,
    BUFF_CONVERT_LIMIT_TYPE_NAME,
    BUFF_CONVERT_TYPE_NAME,
    BUFF_TYPE_NAME,
    CLASS_OVERWRITE_NAME,
    EVENT_TYPE_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    QUEST_AFTER_CLEAR_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SVT_FLAG_NAME,
    SVT_FLAG_ORIGINAL_NAME,
    SVT_TYPE_NAME,
    WAR_FLAG_NAME,
    BuffConvertType,
    NiceSvtFlag,
    Quest_FLAG_NAME,
    SvtAttribute,
    SvtType,
)
from ..schemas.nice import LIMIT_TO_FACE_ID, AssetURL
from ..schemas.raw import (
    MstBuff,
    MstClassRelationOverwrite,
    MstCommandCode,
    MstEquip,
    MstEvent,
    MstFunc,
    MstQuestWithPhase,
    MstQuestWithWar,
    MstSkill,
    MstSvt,
    MstSvtExtra,
    MstSvtLimit,
    MstTreasureDevice,
    MstWar,
)
from .utils import (
    fmt_url,
    get_flags,
    get_nice_trait,
    get_np_name,
    get_traits_list,
    get_traits_list_list,
    get_translation,
)


settings = Settings()


def get_nice_buff_script(
    mstBuff: MstBuff, raw_to_out: Callable[[MstBuff], Any]
) -> dict[str, Any]:
    script: dict[str, Any] = {}
    if "relationOverwrite" in mstBuff.script:
        relationOverwrite = [
            MstClassRelationOverwrite.parse_obj(overwrite)
            for overwrite in mstBuff.script["relationOverwrite"]
        ]
        relationId: dict[str, dict[SvtClass | str, dict[SvtClass | str, Any]]] = {
            "atkSide": defaultdict(dict),
            "defSide": defaultdict(dict),
        }
        for relation in relationOverwrite:
            side = "atkSide" if relation.atkSide == 1 else "defSide"
            atkClass = get_class_name(relation.atkClass)
            defClass = get_class_name(relation.defClass)
            relationDetail = {
                "damageRate": relation.damageRate,
                "type": CLASS_OVERWRITE_NAME[relation.type],
            }
            relationId[side][atkClass][defClass] = relationDetail
        script["relationId"] = relationId

    for script_item in (
        "ReleaseText",
        "DamageRelease",
        "checkIndvType",
        "HP_LOWER",
        "INDIVIDUALITIE_COUNT_ABOVE",
        "INDIVIDUALITIE_COUNT_BELOW",
        "HP_HIGHER",
        "CounterMessage",
        "avoidanceText",
        "gutsText",
        "missText",
        "AppId",
        "IncludeIgnoreIndividuality",
        "ProgressSelfTurn",
        "extendLowerLimit",
        "useFirstTimeInTurn",
        "fromCommandSpell",
        "fromMasterEquip",
    ):
        if script_item in mstBuff.script:
            script[script_item] = mstBuff.script[script_item]

    for script_item in ("INDIVIDUALITIE", "TargetIndiv"):
        if script_item in mstBuff.script:
            script[script_item] = get_nice_trait(mstBuff.script[script_item])

    for script_item in (
        "INDIVIDUALITIE_AND",
        "INDIVIDUALITIE_OR",
        "UpBuffRateBuffIndiv",
    ):
        if script_item in mstBuff.script:
            script[script_item] = get_traits_list(
                int(trait_id) for trait_id in mstBuff.script[script_item].split(",")
            )

    if "CheckOpponentBuffTypes" in mstBuff.script:
        script["CheckOpponentBuffTypes"] = [
            BUFF_TYPE_NAME[int(buffType)]
            for buffType in mstBuff.script["CheckOpponentBuffTypes"].split(",")
        ]

    if "NotPierceIndividuality" in mstBuff.script:
        script["NotPierceIndividuality"] = get_traits_list_list(
            mstBuff.script["NotPierceIndividuality"]
        )

    if "convert" in mstBuff.script:
        convert = mstBuff.script["convert"]

        targetBuffs: list[Any] = []
        targetIndividualities: list[NiceTrait] = []

        if convert["convertType"] == BuffConvertType.BUFF:
            targets = [raw_to_out(buff) for buff in convert["targetBuffs"]]
            targetBuffs = targets
        elif convert["convertType"] == BuffConvertType.INDIVIDUALITY:
            targets = get_traits_list(convert["targetIds"])
            targetIndividualities = targets
        else:
            targets = []

        script["convert"] = {
            "targetLimit": BUFF_CONVERT_LIMIT_TYPE_NAME[convert["targetLimit"]],
            "convertType": BUFF_CONVERT_TYPE_NAME[convert["convertType"]],
            "targets": targets,
            "targetBuffs": targetBuffs,
            "targetIndividualities": targetIndividualities,
            "convertBuffs": [raw_to_out(buff) for buff in convert["convertBuffs"]],
            "script": convert["script"],
            "effectId": convert["effectId"],
        }

    return script


def get_basic_buff_no_reverse(
    mstBuff: MstBuff, region: Region, lang: Language
) -> BasicBuffReverse:
    return BasicBuffReverse(
        id=mstBuff.id,
        name=get_translation(lang, mstBuff.name),
        originalName=mstBuff.name,
        detail=mstBuff.detail,
        icon=fmt_url(
            AssetURL.buffIcon,
            base_url=settings.asset_url,
            region=region,
            item_id=mstBuff.iconId,
        ),
        type=BUFF_TYPE_NAME[mstBuff.type],
        buffGroup=mstBuff.buffGroup,
        script=BuffScript.model_validate(
            get_nice_buff_script(
                mstBuff,
                lambda buff: get_basic_buff_no_reverse(
                    MstBuff.model_validate(buff), region, lang
                ).model_dump(mode="json", exclude_unset=True, exclude_none=True),
            )
        ),
        originalScript=mstBuff.script,
        vals=get_traits_list(mstBuff.vals),
        tvals=get_traits_list(mstBuff.tvals),
        ckSelfIndv=get_traits_list(mstBuff.ckSelfIndv),
        ckOpIndv=get_traits_list(mstBuff.ckOpIndv),
        maxRate=mstBuff.maxRate,
    )


async def get_basic_buff_from_raw(
    redis: Redis,
    region: Region,
    mstBuff: MstBuff,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BasicBuffReverse:
    basic_buff = get_basic_buff_no_reverse(mstBuff, region, lang)
    if reverse and reverseDepth >= ReverseDepth.function:
        func_ids = await get_reverse_ids(
            redis, region, RedisReverse.BUFF_TO_FUNC, mstBuff.id
        )
        buff_reverse = BasicReversedBuff(
            function=[
                await get_basic_function(
                    redis, region, func_id, lang, reverse, reverseDepth
                )
                for func_id in func_ids
            ]
        )
        basic_buff.reverse = BasicReversedBuffType(basic=buff_reverse)
    return basic_buff


async def get_basic_buff(
    redis: Redis,
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BasicBuffReverse:
    mstBuff = await pydantic_object.fetch_id(redis, region, MstBuff, buff_id)
    if not mstBuff:
        raise HTTPException(status_code=404, detail="Buff not found")
    return await get_basic_buff_from_raw(
        redis, region, mstBuff, lang, reverse, reverseDepth
    )


async def get_basic_function_from_raw(
    redis: Redis,
    region: Region,
    mstFunc: MstFunc,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
) -> BasicFunctionReverse:
    traitVals = []
    buffs: list[BasicBuffReverse] = []
    if mstFunc.funcType in FUNC_VALS_NOT_BUFF:
        traitVals = get_traits_list(mstFunc.vals)
    else:
        for buff_id in mstFunc.vals:
            mstBuff = await pydantic_object.fetch_id(redis, region, MstBuff, buff_id)
            if mstBuff:
                buffs.append(
                    await get_basic_buff_from_raw(redis, region, mstBuff, lang)
                )

    basic_func = BasicFunctionReverse(
        funcId=mstFunc.id,
        funcType=FUNC_TYPE_NAME[mstFunc.funcType],
        funcTargetTeam=FUNC_APPLYTARGET_NAME[mstFunc.applyTarget],
        funcTargetType=FUNC_TARGETTYPE_NAME[mstFunc.targetType],
        funcquestTvals=get_traits_list(mstFunc.questTvals),
        functvals=get_traits_list(mstFunc.tvals),
        funcPopupText=mstFunc.popupText,
        overWriteTvalsList=get_traits_list_list(mstFunc.overWriteTvalsList or []),
        traitVals=traitVals,
        buffs=buffs,
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        skill_ids = await get_reverse_ids(
            redis, region, RedisReverse.FUNC_TO_SKILL, mstFunc.id
        )
        td_ids = await get_reverse_ids(
            redis, region, RedisReverse.FUNC_TO_TD, mstFunc.id
        )
        func_reverse = BasicReversedFunction(
            skill=[
                await get_basic_skill(
                    redis, region, skill_id, lang, reverse, reverseDepth
                )
                for skill_id in skill_ids
            ],
            NP=[
                await get_basic_td(redis, region, td_id, lang, reverse, reverseDepth)
                for td_id in td_ids
            ],
        )
        basic_func.reverse = BasicReversedFunctionType(basic=func_reverse)

    return basic_func


async def get_basic_function(
    redis: Redis,
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
) -> BasicFunctionReverse:
    mstFunc = await pydantic_object.fetch_id(redis, region, MstFunc, func_id)
    if not mstFunc:
        raise HTTPException(status_code=404, detail="Function not found")
    return await get_basic_function_from_raw(
        redis, region, mstFunc, lang, reverse, reverseDepth
    )


async def get_basic_skill(
    redis: Redis,
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    mstSkill: Optional[MstSkill] = None,
) -> BasicSkillReverse:
    if not mstSkill:
        mstSkill = await pydantic_object.fetch_id(redis, region, MstSkill, skill_id)
    if not mstSkill:
        raise HTTPException(status_code=404, detail="Skill not found")
    basic_skill = BasicSkillReverse(
        id=mstSkill.id,
        name=get_translation(lang, mstSkill.name),
        ruby=mstSkill.ruby,
        icon=fmt_url(
            AssetURL.skillIcon,
            base_url=settings.asset_url,
            region=region,
            item_id=mstSkill.iconId,
        ),
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = set(
            await get_reverse_ids(
                redis, region, RedisReverse.ACTIVE_SKILL_TO_SVT, skill_id
            )
        )
        passiveSkills = set(
            await get_reverse_ids(
                redis, region, RedisReverse.PASSIVE_SKILL_TO_SVT, skill_id
            )
        )
        mc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_MC, skill_id
        )
        cc_ids = await get_reverse_ids(
            redis, region, RedisReverse.SKILL_TO_CC, skill_id
        )

        skill_reverse = BasicReversedSkillTd(
            servant=[
                await get_basic_servant(redis, region, svt_id, lang=lang)
                for svt_id in sorted(activeSkills | passiveSkills)
            ],
            MC=[await get_basic_mc(redis, region, mc_id, lang) for mc_id in mc_ids],
            CC=[await get_basic_cc(redis, region, cc_id, lang) for cc_id in cc_ids],
        )
        basic_skill.reverse = BasicReversedSkillTdType(basic=skill_reverse)
    return basic_skill


async def get_basic_td(
    redis: Redis,
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    mstTreasureDevice: Optional[MstTreasureDevice] = None,
) -> BasicTdReverse:
    if not mstTreasureDevice:
        mstTreasureDevice = await pydantic_object.fetch_id(
            redis, region, MstTreasureDevice, td_id
        )
    if not mstTreasureDevice:
        raise HTTPException(status_code=404, detail="NP not found")
    basic_td = BasicTdReverse(
        id=mstTreasureDevice.id,
        name=get_np_name(mstTreasureDevice.name, mstTreasureDevice.ruby, lang),
        ruby=mstTreasureDevice.ruby,
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        svt_ids = await get_reverse_ids(redis, region, RedisReverse.TD_TO_SVT, td_id)
        td_reverse = BasicReversedSkillTd(
            servant=[
                await get_basic_servant(redis, region, svt_id, lang=lang)
                for svt_id in svt_ids
            ]
        )
        basic_td.reverse = BasicReversedSkillTdType(basic=td_reverse)
    return basic_td


def select_mstSvtLimit(
    limits: list[MstSvtLimit],
    svt_limit: Optional[int] = None,
    prefer_lower: bool = False,
) -> MstSvtLimit | None:
    limit_map = {limit.limitCount: limit for limit in limits}
    if svt_limit is not None and svt_limit in limit_map:
        return limit_map[svt_limit]

    low_limit_counts = {0, 1, 2, 3} & limit_map.keys()

    if low_limit_counts:
        chosen_limit = min(low_limit_counts) if prefer_lower else max(low_limit_counts)
        return limit_map[chosen_limit]

    if limit_map:
        return limit_map[min(limit_map.keys())]

    return None


async def get_basic_svt(
    redis: Redis,
    region: Region,
    svt_id: int,
    svt_limit: Optional[int] = None,
    disp_limit: int | None = None,
    image_svt_id: int | None = None,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> dict[str, Any]:
    svtExtra = await pydantic_object.fetch_id(redis, region, MstSvtExtra, svt_id)

    if not svtExtra:  # pragma: no cover
        raise HTTPException(
            status_code=404, detail=f"Svt extra {region} {svt_id} not found"
        )

    if not mstSvt:
        mstSvt = svtExtra.mstSvt

    mstSvtLimit = select_mstSvtLimit(svtExtra.limits, svt_limit, mstSvt.isServant())

    if not mstSvtLimit:  # pragma: no cover
        raise HTTPException(
            status_code=404, detail=f"Svt limit {region} {svt_id} not found"
        )

    basic_servant = {
        "id": svt_id,
        "collectionNo": mstSvt.collectionNo,
        "type": SVT_TYPE_NAME[mstSvt.type],
        "flag": SVT_FLAG_NAME.get(mstSvt.flag, NiceSvtFlag.unknown),
        "flags": get_flags(mstSvt.flag, SVT_FLAG_ORIGINAL_NAME),
        "name": mstSvt.name,
        "originalName": mstSvt.name,
        "classId": mstSvt.classId,
        "className": get_class_name(mstSvt.classId),
        "attribute": ATTRIBUTE_NAME[mstSvt.attri],
        "traits": get_traits_list(sorted(mstSvt.individuality)),
        "rarity": mstSvtLimit.rarity,
        "atkMax": mstSvtLimit.atkMax,
        "hpMax": mstSvtLimit.hpMax,
        "costume": {},
    }

    basic_servant["bondEquipOwner"] = svtExtra.bondEquipOwner
    basic_servant["valentineEquipOwner"] = svtExtra.valentineEquipOwner
    basic_servant["costume"] = {}
    for costume in svtExtra.costumeLimitSvtIdMap.values():
        if costume.battleCharaId not in basic_servant["costume"]:  # type: ignore
            basic_servant["costume"][costume.battleCharaId] = {  # type: ignore
                "id": costume.id,
                "costumeCollectionNo": costume.costumeCollectionNo,
                "battleCharaId": costume.battleCharaId,
                "shortName": (
                    get_translation(lang, costume.shortName)
                    if region == Region.JP and lang is not None
                    else costume.shortName
                ),
            }
    if svtExtra.zeroLimitOverwriteName is not None:
        basic_servant["name"] = svtExtra.zeroLimitOverwriteName
        basic_servant["originalName"] = svtExtra.zeroLimitOverwriteName
        basic_servant["overwriteName"] = mstSvt.name
        basic_servant["originalOverwriteName"] = mstSvt.name

    for limit_add in svtExtra.limitAdds:
        if (
            svt_limit
            and limit_add.attri
            and limit_add.limitCount == svt_limit
            and limit_add.attri != SvtAttribute.DEFAULT
        ):
            basic_servant["attribute"] = ATTRIBUTE_NAME[limit_add.attri]

    base_settings = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": svt_id,
    }
    if mstSvt.type == SvtType.SVT_MATERIAL_TD:
        base_settings["item_id"] = mstSvt.baseSvtId

    face_limit = disp_limit or mstSvtLimit.limitCount

    if image_svt_id:
        base_settings["item_id"] = image_svt_id
        basic_servant["face"] = AssetURL.face.format(**base_settings, i="")
    elif mstSvt.type == SvtType.SERVANT_EQUIP:
        basic_servant["face"] = AssetURL.face.format(**base_settings, i=0)
    elif mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        if svtExtra and face_limit in svtExtra.costumeLimitSvtIdMap:
            basic_servant["face"] = AssetURL.enemy.format(
                base_url=settings.asset_url,
                region=region,
                item_id=svtExtra.costumeLimitSvtIdMap[face_limit].battleCharaId,
                i=face_limit,
            )
        else:
            basic_servant["face"] = AssetURL.enemy.format(**base_settings, i=face_limit)
    elif (
        svtExtra
        and face_limit is not None
        and face_limit > 10
        and face_limit in svtExtra.costumeLimitSvtIdMap
    ):
        basic_servant["face"] = AssetURL.face.format(
            base_url=settings.asset_url,
            region=region,
            item_id=svtExtra.costumeLimitSvtIdMap[face_limit].battleCharaId,
            i=0,
        )
    else:
        basic_servant["face"] = AssetURL.face.format(
            **base_settings,
            i=LIMIT_TO_FACE_ID.get(face_limit, face_limit),
        )

    if region == Region.JP and lang is not None:
        basic_servant["name"] = get_translation(lang, str(basic_servant["name"]))
        if "overwriteName" in basic_servant:
            basic_servant["overwriteName"] = get_translation(
                lang, str(basic_servant["overwriteName"])
            )

    return basic_servant


async def get_basic_servant(
    redis: Redis,
    region: Region,
    item_id: int,
    svt_limit: Optional[int] = None,
    disp_limit: int | None = None,
    image_svt_id: int | None = None,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> BasicServant:
    return BasicServant.parse_obj(
        await get_basic_svt(
            redis, region, item_id, svt_limit, disp_limit, image_svt_id, lang, mstSvt
        )
    )


@dataclass
class BasicServantGet:
    svt_id: int
    svt_limit: int
    disp_limit: int
    image_svt_id: int | None


async def get_multiple_basic_servants(
    redis: Redis,
    region: Region,
    svt_details: Sequence[BasicServantGet],
    lang: Language | None = None,
) -> list[BasicServant]:
    return await asyncio.gather(
        *[
            get_basic_servant(
                redis,
                region,
                detail.svt_id,
                detail.svt_limit,
                detail.disp_limit,
                detail.image_svt_id,
                lang,
            )
            for detail in svt_details
        ]
    )


async def get_all_basic_servants(
    redis: Redis, region: Region, lang: Language, all_servants: list[MstSvt]
) -> list[BasicServant]:  # pragma: no cover
    out: list[BasicServant] = []
    for svt in all_servants:
        try:
            svt_out = await get_basic_servant(
                redis, region, svt.id, svt_limit=0, lang=lang, mstSvt=svt
            )
            out.append(svt_out)
        except HTTPException:
            logger.warning(f"Failed to get basic servant of {svt}")

    return out


async def get_basic_equip(
    redis: Redis,
    region: Region,
    item_id: int,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> BasicEquip:
    return BasicEquip.parse_obj(
        await get_basic_svt(redis, region, item_id, lang=lang, mstSvt=mstSvt)
    )


async def get_all_basic_equips(
    redis: Redis, region: Region, lang: Language, all_equips: list[MstSvt]
) -> list[BasicEquip]:  # pragma: no cover
    return [
        await get_basic_equip(redis, region, svt.id, lang=lang) for svt in all_equips
    ]


def get_basic_mc_from_raw(
    region: Region, mstEquip: MstEquip, lang: Language
) -> BasicMysticCode:
    base_settings = {"base_url": settings.asset_url, "region": region}
    item_assets = MCAssets(
        male=fmt_url(
            AssetURL.mc["item"], **base_settings, item_id=mstEquip.maleImageId
        ),
        female=fmt_url(
            AssetURL.mc["item"], **base_settings, item_id=mstEquip.femaleImageId
        ),
    )

    basic_mc = BasicMysticCode(
        id=mstEquip.id,
        name=get_translation(lang, mstEquip.name),
        item=item_assets,
    )

    return basic_mc


async def get_basic_mc(
    redis: Redis, region: Region, mc_id: int, lang: Language
) -> BasicMysticCode:
    mstEquip = await pydantic_object.fetch_id(redis, region, MstEquip, mc_id)
    if not mstEquip:
        raise HTTPException(status_code=404, detail="Mystic Code not found")

    return get_basic_mc_from_raw(region, mstEquip, lang)


def get_all_basic_mcs(
    region: Region, lang: Language, mstEquips: Iterable[MstEquip]
) -> Generator[BasicMysticCode, None, None]:  # pragma: no cover
    return (get_basic_mc_from_raw(region, mstEquip, lang) for mstEquip in mstEquips)


def get_basic_cc_from_raw(
    region: Region, mstCommandCode: MstCommandCode, lang: Language
) -> BasicCommandCode:
    basic_cc = BasicCommandCode(
        id=mstCommandCode.id,
        collectionNo=mstCommandCode.collectionNo,
        name=get_translation(lang, mstCommandCode.name),
        rarity=mstCommandCode.rarity,
        face=fmt_url(
            AssetURL.commandCode,
            base_url=settings.asset_url,
            region=region,
            item_id=mstCommandCode.id,
        ),
    )

    return basic_cc


async def get_basic_cc(
    redis: Redis, region: Region, cc_id: int, lang: Language
) -> BasicCommandCode:
    mstCommandCode = await pydantic_object.fetch_id(
        redis, region, MstCommandCode, cc_id
    )
    if not mstCommandCode:
        raise HTTPException(status_code=404, detail="Command Code not found")

    return get_basic_cc_from_raw(region, mstCommandCode, lang)


def get_all_basic_ccs(
    region: Region,
    lang: Language,
    mstCommandCodes: Iterable[MstCommandCode],
) -> Generator[BasicCommandCode, None, None]:  # pragma: no cover
    return (get_basic_cc_from_raw(region, mstCcs, lang) for mstCcs in mstCommandCodes)


def get_basic_event_from_raw(mstEvent: MstEvent, lang: Language) -> BasicEvent:
    basic_event = BasicEvent(
        id=mstEvent.id,
        type=EVENT_TYPE_NAME[mstEvent.type],
        name=get_translation(lang, mstEvent.name),
        noticeAt=mstEvent.noticeAt,
        startedAt=mstEvent.startedAt,
        endedAt=mstEvent.endedAt,
        finishedAt=mstEvent.finishedAt,
        materialOpenedAt=mstEvent.materialOpenedAt,
        warIds=mstEvent.warIds,
    )

    return basic_event


async def get_basic_event(
    conn: AsyncConnection, event_id: int, lang: Language
) -> BasicEvent:
    mstEvent = await fetch.get_one(conn, MstEvent, event_id)
    if not mstEvent:
        raise HTTPException(status_code=404, detail="Event not found")

    return get_basic_event_from_raw(mstEvent, lang)


def get_all_basic_events(
    lang: Language, mstEvents: Iterable[MstEvent]
) -> Generator[BasicEvent, None, None]:  # pragma: no cover
    return (get_basic_event_from_raw(mstEvent, lang) for mstEvent in mstEvents)


def get_basic_war_from_raw(mstWar: MstWar, lang: Language) -> BasicWar:
    return BasicWar(
        id=mstWar.id,
        coordinates=mstWar.coordinates,
        age=mstWar.age,
        name=get_translation(lang, mstWar.name),
        longName=get_translation(lang, mstWar.longName),
        flags=get_flags(mstWar.flag, WAR_FLAG_NAME),
        eventId=mstWar.eventId,
        eventName=get_translation(lang, mstWar.eventName),
    )


async def get_basic_war(conn: AsyncConnection, war_id: int, lang: Language) -> BasicWar:
    mstWar = await fetch.get_one(conn, MstWar, war_id)
    if not mstWar:
        raise HTTPException(status_code=404, detail="War not found")
    return get_basic_war_from_raw(mstWar, lang)


def get_all_basic_wars(
    lang: Language, mstWars: Iterable[MstWar]
) -> Generator[BasicWar, None, None]:  # pragma: no cover
    return (get_basic_war_from_raw(mstWar, lang) for mstWar in mstWars)


def get_basic_quest_from_raw(mstQuest: MstQuestWithWar, lang: Language) -> BasicQuest:
    return BasicQuest(
        id=mstQuest.id,
        name=get_translation(lang, mstQuest.name),
        type=QUEST_TYPE_NAME[mstQuest.type],
        flags=get_flags(mstQuest.flag, Quest_FLAG_NAME),
        afterClear=QUEST_AFTER_CLEAR_NAME[mstQuest.afterClear],
        consumeType=QUEST_CONSUME_TYPE_NAME[mstQuest.consumeType],
        consume=mstQuest.actConsume,
        spotId=mstQuest.spotId,
        spotName=get_translation(lang, mstQuest.spotName),
        warId=mstQuest.warId,
        warLongName=get_translation(lang, mstQuest.warLongName),
        priority=mstQuest.priority,
        noticeAt=mstQuest.noticeAt,
        openedAt=mstQuest.openedAt,
        closedAt=mstQuest.closedAt,
    )


async def get_basic_quest(
    conn: AsyncConnection, quest_id: int, lang: Language
) -> BasicQuest:
    mstQuest = await quest.get_one_quest_with_war(conn, quest_id)
    if not mstQuest:
        raise HTTPException(status_code=404, detail="Quest not found")

    return get_basic_quest_from_raw(mstQuest, lang)


def get_basic_quest_phase_from_raw(
    mstQuestPhase: MstQuestWithPhase, lang: Language
) -> BasicQuestPhase:
    return BasicQuestPhase(
        id=mstQuestPhase.id,
        name=get_translation(lang, mstQuestPhase.name),
        type=QUEST_TYPE_NAME[mstQuestPhase.type],
        flags=get_flags(mstQuestPhase.flag, Quest_FLAG_NAME),
        afterClear=QUEST_AFTER_CLEAR_NAME[mstQuestPhase.afterClear],
        consumeType=QUEST_CONSUME_TYPE_NAME[mstQuestPhase.consumeType],
        consume=mstQuestPhase.actConsume,
        spotId=mstQuestPhase.spotId,
        spotName=get_translation(lang, mstQuestPhase.spotName),
        warId=mstQuestPhase.warId,
        warLongName=get_translation(lang, mstQuestPhase.warLongName),
        priority=mstQuestPhase.priority,
        noticeAt=mstQuestPhase.noticeAt,
        openedAt=mstQuestPhase.openedAt,
        closedAt=mstQuestPhase.closedAt,
        phase=mstQuestPhase.phase,
        individuality=get_traits_list(mstQuestPhase.individuality),
        qp=mstQuestPhase.qp if mstQuestPhase.qp else 0,
        exp=mstQuestPhase.playerExp,
        bond=mstQuestPhase.playerExp,
        battleBgId=mstQuestPhase.battleBgId,
    )


async def get_basic_quest_phase(
    conn: AsyncConnection, quest_id: int, phase: int, lang: Language
) -> BasicQuestPhase:
    mstQuestPhase = await quest.get_one_quest_with_phase(conn, quest_id, phase)
    if not mstQuestPhase:
        raise HTTPException(status_code=404, detail="Quest Phase not found")

    return get_basic_quest_phase_from_raw(mstQuestPhase, lang)


async def get_basic_quest_latest_with_enemies(
    conn: AsyncConnection, lang: Language
) -> list[BasicQuestPhase]:
    raw_phases = await quest.get_latest_quest_with_enemies(conn)
    return [
        get_basic_quest_phase_from_raw(quest_phase, lang) for quest_phase in raw_phases
    ]
