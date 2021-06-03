from collections import defaultdict
from typing import Any, Optional

from aioredis import Redis
from fastapi import HTTPException
from sqlalchemy.engine import Connection

from ..config import Settings
from ..data.custom_mappings import TRANSLATIONS
from ..data.gamedata import masters
from ..db.helpers import fetch, func, war
from ..redis.helpers import pydantic_object
from ..schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicEvent,
    BasicFunctionReverse,
    BasicMysticCode,
    BasicQuest,
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
from ..schemas.common import Language, NiceBuffScript, Region, ReverseDepth
from ..schemas.enums import (
    ATTRIBUTE_NAME,
    CLASS_NAME,
    FUNC_APPLYTARGET_NAME,
    FUNC_VALS_NOT_BUFF,
    SvtClass,
)
from ..schemas.gameenums import (
    BUFF_TYPE_NAME,
    CLASS_OVERWRITE_NAME,
    EVENT_TYPE_NAME,
    FUNC_TARGETTYPE_NAME,
    FUNC_TYPE_NAME,
    QUEST_CONSUME_TYPE_NAME,
    QUEST_TYPE_NAME,
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    SvtType,
)
from ..schemas.nice import AssetURL
from ..schemas.raw import (
    MstBuff,
    MstClassRelationOverwrite,
    MstEvent,
    MstFunc,
    MstQuest,
    MstSkill,
    MstSvt,
    MstTreasureDevice,
    MstWar,
)
from . import reverse as reverse_ids
from .utils import (
    get_nice_trait,
    get_np_name,
    get_safe,
    get_traits_list,
    get_translation,
)


settings = Settings()


def get_nice_buff_script(region: Region, mstBuff: MstBuff) -> NiceBuffScript:
    script: dict[str, Any] = {}
    if "relationId" in mstBuff.script:
        relationOverwrite: list[MstClassRelationOverwrite] = masters[
            region
        ].mstClassRelationOverwriteId.get(mstBuff.script["relationId"], [])
        relationId: dict[str, dict[SvtClass, dict[SvtClass, Any]]] = {
            "atkSide": defaultdict(dict),
            "defSide": defaultdict(dict),
        }
        for relation in relationOverwrite:
            side = "atkSide" if relation.atkSide == 1 else "defSide"
            atkClass = CLASS_NAME[relation.atkClass]
            defClass = CLASS_NAME[relation.defClass]
            relationDetail = {
                "damageRate": relation.damageRate,
                "type": CLASS_OVERWRITE_NAME[relation.type],
            }
            relationId[side][atkClass][defClass] = relationDetail
        script["relationId"] = relationId

    for script_item in ("ReleaseText", "DamageRelease", "checkIndvType"):
        if script_item in mstBuff.script:
            script[script_item] = mstBuff.script[script_item]

    if "INDIVIDUALITIE" in mstBuff.script:
        script["INDIVIDUALITIE"] = get_nice_trait(mstBuff.script["INDIVIDUALITIE"])

    if "CheckOpponentBuffTypes" in mstBuff.script:
        script["CheckOpponentBuffTypes"] = [
            BUFF_TYPE_NAME[int(buffType)]
            for buffType in mstBuff.script["CheckOpponentBuffTypes"].split(",")
        ]

    return NiceBuffScript.parse_obj(script)


async def get_basic_buff_from_raw(
    conn: Connection,
    redis: Redis,
    region: Region,
    mstBuff: MstBuff,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BasicBuffReverse:
    basic_buff = BasicBuffReverse(
        id=mstBuff.id,
        name=mstBuff.name,
        icon=AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=mstBuff.iconId
        ),
        type=BUFF_TYPE_NAME[mstBuff.type],
        script=get_nice_buff_script(region, mstBuff),
        vals=get_traits_list(mstBuff.vals),
        tvals=get_traits_list(mstBuff.tvals),
        ckSelfIndv=get_traits_list(mstBuff.ckSelfIndv),
        ckOpIndv=get_traits_list(mstBuff.ckOpIndv),
    )
    if reverse and reverseDepth >= ReverseDepth.function:
        buff_reverse = BasicReversedBuff(
            function=[
                await get_basic_function_from_raw(
                    conn,
                    redis,
                    region,
                    func_entity.mstFunc,
                    lang,
                    reverse,
                    reverseDepth,
                )
                for func_entity in func.get_func_from_buff(conn, mstBuff.id)
            ]
        )
        basic_buff.reverse = BasicReversedBuffType(basic=buff_reverse)
    return basic_buff


async def get_basic_buff(
    conn: Connection,
    redis: Redis,
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BasicBuffReverse:
    mstBuff = fetch.get_one(conn, MstBuff, buff_id)
    if not mstBuff:
        raise HTTPException(status_code=404, detail="Buff not found")
    return await get_basic_buff_from_raw(
        conn, redis, region, mstBuff, lang, reverse, reverseDepth
    )


async def get_basic_function_from_raw(
    conn: Connection,
    redis: Redis,
    region: Region,
    mstFunc: MstFunc,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
) -> BasicFunctionReverse:
    traitVals = []
    if mstFunc.funcType in FUNC_VALS_NOT_BUFF:
        traitVals = get_traits_list(mstFunc.vals)

    basic_func = BasicFunctionReverse(
        funcId=mstFunc.id,
        funcType=FUNC_TYPE_NAME[mstFunc.funcType],
        funcTargetTeam=FUNC_APPLYTARGET_NAME[mstFunc.applyTarget],
        funcTargetType=FUNC_TARGETTYPE_NAME[mstFunc.targetType],
        funcquestTvals=get_traits_list(mstFunc.questTvals),
        functvals=get_traits_list(mstFunc.tvals),
        traitVals=traitVals,
        buffs=[
            await get_basic_buff_from_raw(conn, redis, region, buff.mstBuff, lang)
            for buff in mstFunc.expandedVals
        ],
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        func_reverse = BasicReversedFunction(
            skill=[
                await get_basic_skill(
                    redis, region, skill_id, lang, reverse, reverseDepth
                )
                for skill_id in reverse_ids.func_to_skillId(region, mstFunc.id)
            ],
            NP=[
                await get_basic_td(redis, region, td_id, lang, reverse, reverseDepth)
                for td_id in reverse_ids.func_to_tdId(region, mstFunc.id)
            ],
        )
        basic_func.reverse = BasicReversedFunctionType(basic=func_reverse)

    return basic_func


async def get_basic_function(
    conn: Connection,
    redis: Redis,
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
) -> BasicFunctionReverse:
    func_entity = func.get_func_id(conn, func_id)
    if not func_entity:
        raise HTTPException(status_code=404, detail="Function not found")
    return await get_basic_function_from_raw(
        conn, redis, region, func_entity.mstFunc, lang, reverse, reverseDepth
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
        icon=AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=mstSkill.iconId
        ),
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = reverse_ids.active_to_svtId(region, skill_id)
        passiveSkills = reverse_ids.passive_to_svtId(region, skill_id)
        skill_reverse = BasicReversedSkillTd(
            servant=(
                get_basic_servant(region, svt_id, lang=lang)
                for svt_id in activeSkills | passiveSkills
            ),
            MC=(
                get_basic_mc(region, mc_id, lang)
                for mc_id in reverse_ids.skill_to_MCId(region, skill_id)
            ),
            CC=(
                get_basic_cc(region, cc_id, lang)
                for cc_id in reverse_ids.skill_to_CCId(region, skill_id)
            ),
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
        name=get_np_name(mstTreasureDevice, lang),
        ruby=mstTreasureDevice.ruby,
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        mstSvtTreasureDevice = masters[region].tdToSvt.get(td_id, set())
        td_reverse = BasicReversedSkillTd(
            servant=(
                get_basic_servant(region, svt_id, lang=lang)
                for svt_id in mstSvtTreasureDevice
            )
        )
        basic_td.reverse = BasicReversedSkillTdType(basic=td_reverse)
    return basic_td


def get_basic_svt(
    region: Region,
    svt_id: int,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> dict[str, Any]:
    if not mstSvt:
        mstSvt = masters[region].mstSvtId[svt_id]
    mstSvtLimit = masters[region].mstSvtLimitFirst[svt_id]

    basic_servant = {
        "id": svt_id,
        "collectionNo": mstSvt.collectionNo,
        "type": SVT_TYPE_NAME[mstSvt.type],
        "flag": SVT_FLAG_NAME[mstSvt.flag],
        "name": masters[region].mstSvtLimitOverwriteName.get(svt_id, mstSvt.name),
        "className": CLASS_NAME[mstSvt.classId],
        "attribute": ATTRIBUTE_NAME[mstSvt.attri],
        "rarity": mstSvtLimit.rarity,
        "atkMax": mstSvtLimit.atkMax,
        "hpMax": mstSvtLimit.hpMax,
        "bondEquipOwner": masters[region].bondEquipOwner.get(svt_id),
        "valentineEquipOwner": masters[region].valentineEquipOwner.get(svt_id),
    }

    base_settings = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": svt_id,
    }
    if mstSvt.type in (SvtType.ENEMY, SvtType.ENEMY_COLLECTION):
        basic_servant["face"] = AssetURL.enemy.format(**base_settings, i=1)
    else:
        basic_servant["face"] = AssetURL.face.format(**base_settings, i=0)

    if region == Region.JP and lang == Language.en:
        basic_servant["name"] = get_safe(TRANSLATIONS, basic_servant["name"])

    return basic_servant


def get_basic_servant(
    region: Region,
    item_id: int,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> BasicServant:
    return BasicServant.parse_obj(get_basic_svt(region, item_id, lang, mstSvt))


def get_basic_equip(
    region: Region,
    item_id: int,
    lang: Optional[Language] = None,
    mstSvt: Optional[MstSvt] = None,
) -> BasicEquip:
    return BasicEquip.parse_obj(get_basic_svt(region, item_id, lang, mstSvt))


def get_basic_mc(region: Region, mc_id: int, lang: Language) -> BasicMysticCode:
    mstEquip = masters[region].mstEquipId[mc_id]
    base_settings = {"base_url": settings.asset_url, "region": region}
    item_assets = {
        "male": AssetURL.mc["item"].format(
            **base_settings, item_id=mstEquip.maleImageId
        ),
        "female": AssetURL.mc["item"].format(
            **base_settings, item_id=mstEquip.femaleImageId
        ),
    }

    basic_mc = BasicMysticCode(
        id=mstEquip.id,
        name=get_translation(lang, mstEquip.name),
        item=item_assets,
    )

    return basic_mc


def get_basic_cc(region: Region, cc_id: int, lang: Language) -> BasicCommandCode:
    mstCommandCode = masters[region].mstCommandCodeId[cc_id]
    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}

    basic_cc = BasicCommandCode(
        id=mstCommandCode.id,
        collectionNo=mstCommandCode.collectionNo,
        name=get_translation(lang, mstCommandCode.name),
        rarity=mstCommandCode.rarity,
        face=AssetURL.commandCode.format(**base_settings),
    )

    return basic_cc


def get_basic_event_from_raw(
    region: Region, mstEvent: MstEvent, lang: Language
) -> BasicEvent:
    basic_event = BasicEvent(
        id=mstEvent.id,
        type=EVENT_TYPE_NAME[mstEvent.type],
        name=get_translation(lang, mstEvent.name),
        noticeAt=mstEvent.noticeAt,
        startedAt=mstEvent.startedAt,
        endedAt=mstEvent.endedAt,
        finishedAt=mstEvent.finishedAt,
        materialOpenedAt=mstEvent.materialOpenedAt,
        warIds=(war.id for war in masters[region].mstWarEventId.get(mstEvent.id, [])),
    )

    return basic_event


def get_basic_event(
    conn: Connection, region: Region, event_id: int, lang: Language
) -> BasicEvent:
    mstEvent = fetch.get_one(conn, MstEvent, event_id)
    if not mstEvent:
        raise HTTPException(status_code=404, detail="Event not found")

    return get_basic_event_from_raw(region, mstEvent, lang)


def get_all_basic_events(
    conn: Connection, region: Region, lang: Language
) -> list[BasicEvent]:
    all_mstEvent = fetch.get_everything(conn, MstEvent)
    return [
        get_basic_event_from_raw(region, mstEvent, lang) for mstEvent in all_mstEvent
    ]


def get_basic_war_from_raw(mstWar: MstWar, lang: Language) -> BasicWar:
    return BasicWar(
        id=mstWar.id,
        coordinates=mstWar.coordinates,
        age=mstWar.age,
        name=mstWar.name,
        longName=get_translation(lang, mstWar.longName),
        eventId=mstWar.eventId,
    )


def get_basic_war(conn: Connection, war_id: int, lang: Language) -> BasicWar:
    mstWar = fetch.get_one(conn, MstWar, war_id)
    if not mstWar:
        raise HTTPException(status_code=404, detail="War not found")
    return get_basic_war_from_raw(mstWar, lang)


def get_all_basic_wars(conn: Connection, lang: Language) -> list[BasicWar]:
    all_mstWar = fetch.get_everything(conn, MstWar)
    return [get_basic_war_from_raw(mstWar, lang) for mstWar in all_mstWar]


def get_basic_quest(conn: Connection, quest_id: int) -> BasicQuest:
    mstQuest = fetch.get_one(conn, MstQuest, quest_id)
    if not mstQuest:
        raise HTTPException(status_code=404, detail="Quest not found")

    return BasicQuest(
        id=mstQuest.id,
        name=mstQuest.name,
        type=QUEST_TYPE_NAME[mstQuest.type],
        consumeType=QUEST_CONSUME_TYPE_NAME[mstQuest.consumeType],
        consume=mstQuest.actConsume,
        spotId=mstQuest.spotId,
        warId=war.get_war_from_spot(conn, mstQuest.spotId),
        noticeAt=mstQuest.noticeAt,
        openedAt=mstQuest.openedAt,
        closedAt=mstQuest.closedAt,
    )
