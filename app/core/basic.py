from collections import defaultdict
from typing import Any, Optional

from ..config import Settings
from ..data.custom_mappings import TRANSLATIONS
from ..data.gamedata import masters
from ..schemas.basic import (
    BasicBuffReverse,
    BasicCommandCode,
    BasicEquip,
    BasicEvent,
    BasicFunctionReverse,
    BasicMysticCode,
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
    SVT_FLAG_NAME,
    SVT_TYPE_NAME,
    SvtType,
)
from ..schemas.nice import AssetURL
from ..schemas.raw import MstBuff, MstClassRelationOverwrite
from .raw import (
    active_to_svtId,
    buff_to_func,
    func_to_skillId,
    func_to_tdId,
    passive_to_svtId,
    skill_to_CCId,
    skill_to_MCId,
)
from .utils import get_nice_trait, get_safe, get_traits_list


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

    for script_item in ("ReleaseText", "DamageRelease"):
        if script_item in mstBuff.script:
            script[script_item] = mstBuff.script[script_item]

    if "INDIVIDUALITIE" in mstBuff.script:
        script["INDIVIDUALITIE"] = get_nice_trait(mstBuff.script["INDIVIDUALITIE"])

    return NiceBuffScript.parse_obj(script)


def get_basic_buff(
    region: Region,
    buff_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BasicBuffReverse:
    mstBuff = masters[region].mstBuffId[buff_id]
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
            function=(
                get_basic_function(region, func_id, lang, reverse, reverseDepth)
                for func_id in buff_to_func(region, buff_id)
            )
        )
        basic_buff.reverse = BasicReversedBuffType(basic=buff_reverse)
    return basic_buff


def get_basic_function(
    region: Region,
    func_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
) -> BasicFunctionReverse:
    mstFunc = masters[region].mstFuncId[func_id]

    traitVals = []
    buffs = []
    if mstFunc.funcType in FUNC_VALS_NOT_BUFF:
        traitVals = get_traits_list(mstFunc.vals)
    else:
        buffs = [
            get_basic_buff(region, buff_id, lang)
            for buff_id in mstFunc.vals
            if buff_id in masters[region].mstBuffId
        ]

    basic_func = BasicFunctionReverse(
        funcId=mstFunc.id,
        funcType=FUNC_TYPE_NAME[mstFunc.funcType],
        funcTargetTeam=FUNC_APPLYTARGET_NAME[mstFunc.applyTarget],
        funcTargetType=FUNC_TARGETTYPE_NAME[mstFunc.targetType],
        funcquestTvals=get_traits_list(mstFunc.questTvals),
        functvals=get_traits_list(mstFunc.tvals),
        traitVals=traitVals,
        buffs=buffs,
    )

    if reverse and reverseDepth >= ReverseDepth.skillNp:
        func_reverse = BasicReversedFunction(
            skill=(
                get_basic_skill(region, skill_id, lang, reverse, reverseDepth)
                for skill_id in func_to_skillId(region, func_id)
            ),
            NP=(
                get_basic_td(region, td_id, lang, reverse, reverseDepth)
                for td_id in func_to_tdId(region, func_id)
            ),
        )
        basic_func.reverse = BasicReversedFunctionType(basic=func_reverse)

    return basic_func


def get_basic_skill(
    region: Region,
    skill_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
) -> BasicSkillReverse:
    mstSkill = masters[region].mstSkillId[skill_id]
    basic_skill = BasicSkillReverse(
        id=mstSkill.id,
        name=get_safe(TRANSLATIONS, mstSkill.name)
        if lang == Language.en
        else mstSkill.name,
        ruby=mstSkill.ruby,
        icon=AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=mstSkill.iconId
        ),
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = active_to_svtId(region, skill_id)
        passiveSkills = passive_to_svtId(region, skill_id)
        skill_reverse = BasicReversedSkillTd(
            servant=(
                get_basic_servant(region, svt_id, lang=lang)
                for svt_id in activeSkills | passiveSkills
            ),
            MC=(
                get_basic_mc(region, mc_id, lang)
                for mc_id in skill_to_MCId(region, skill_id)
            ),
            CC=(
                get_basic_cc(region, cc_id, lang)
                for cc_id in skill_to_CCId(region, skill_id)
            ),
        )
        basic_skill.reverse = BasicReversedSkillTdType(basic=skill_reverse)
    return basic_skill


def get_basic_td(
    region: Region,
    td_id: int,
    lang: Language,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
) -> BasicTdReverse:
    mstTreasureDevice = masters[region].mstTreasureDeviceId[td_id]
    basic_td = BasicTdReverse(
        id=mstTreasureDevice.id,
        name=mstTreasureDevice.name,
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
    region: Region, svt_id: int, lang: Optional[Language] = None
) -> dict[str, Any]:
    mstSvt = masters[region].mstSvtId[svt_id]
    mstSvtLimit = masters[region].mstSvtLimitFirst[svt_id]

    basic_servant = {
        "id": svt_id,
        "collectionNo": mstSvt.collectionNo,
        "type": SVT_TYPE_NAME[mstSvt.type],
        "flag": SVT_FLAG_NAME[mstSvt.flag],
        "name": mstSvt.name,
        "className": CLASS_NAME[mstSvt.classId],
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
    region: Region, item_id: int, lang: Optional[Language] = None
) -> BasicServant:
    return BasicServant.parse_obj(get_basic_svt(region, item_id, lang))


def get_basic_equip(
    region: Region, item_id: int, lang: Optional[Language] = None
) -> BasicEquip:
    return BasicEquip.parse_obj(get_basic_svt(region, item_id, lang))


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
        name=get_safe(TRANSLATIONS, mstEquip.name)
        if lang == Language.en
        else mstEquip.name,
        item=item_assets,
    )

    return basic_mc


def get_basic_cc(region: Region, cc_id: int, lang: Language) -> BasicCommandCode:
    mstCommandCode = masters[region].mstCommandCodeId[cc_id]
    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}

    basic_cc = BasicCommandCode(
        id=mstCommandCode.id,
        collectionNo=mstCommandCode.collectionNo,
        name=get_safe(TRANSLATIONS, mstCommandCode.name)
        if lang == Language.en
        else mstCommandCode.name,
        rarity=mstCommandCode.rarity,
        face=AssetURL.commandCode.format(**base_settings),
    )

    return basic_cc


def get_basic_event(region: Region, event_id: int) -> BasicEvent:
    mstEvent = masters[region].mstEventId[event_id]

    basic_event = BasicEvent(
        id=mstEvent.id,
        type=EVENT_TYPE_NAME[mstEvent.type],
        name=mstEvent.name,
        noticeAt=mstEvent.noticeAt,
        startedAt=mstEvent.startedAt,
        endedAt=mstEvent.endedAt,
        finishedAt=mstEvent.finishedAt,
        materialOpenedAt=mstEvent.materialOpenedAt,
        warIds=(war.id for war in masters[region].mstWarEventId.get(event_id, [])),
    )

    return basic_event


def get_basic_war(region: Region, war_id: int) -> BasicWar:
    mstWar = masters[region].mstWarId[war_id]

    return BasicWar(
        id=mstWar.id,
        coordinates=mstWar.coordinates,
        age=mstWar.age,
        name=mstWar.name,
        longName=mstWar.longName,
        eventId=mstWar.eventId,
    )
