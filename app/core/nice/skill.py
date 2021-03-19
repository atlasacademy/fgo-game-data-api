from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable

from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.custom_mappings import TRANSLATIONS
from ...schemas.common import Language, Region
from ...schemas.enums import SKILL_TYPE_NAME, AiType
from ...schemas.nice import AssetURL, NiceSkill, NiceSkillReverse
from ...schemas.raw import SkillEntityNoReverse
from ..raw import get_skill_entity_no_reverse, get_skill_entity_no_reverse_many
from ..reverse import get_ai_id_from_skill
from ..utils import get_safe, get_traits_list, strip_formatting_brackets
from .func import get_nice_function


settings = Settings()


def get_nice_skill_with_svt(
    skillEntity: SkillEntityNoReverse, svtId: int, region: Region, lang: Language
) -> list[dict[str, Any]]:
    nice_skill: dict[str, Any] = {
        "id": skillEntity.mstSkill.id,
        "name": get_safe(TRANSLATIONS, skillEntity.mstSkill.name)
        if lang == Language.en
        else skillEntity.mstSkill.name,
        "ruby": skillEntity.mstSkill.ruby,
        "type": SKILL_TYPE_NAME[skillEntity.mstSkill.type],
        "actIndividuality": get_traits_list(skillEntity.mstSkill.actIndividuality),
    }

    iconId = skillEntity.mstSkill.iconId
    if iconId != 0:
        nice_skill["icon"] = AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    if skillEntity.mstSkillDetail:
        nice_skill["detail"] = strip_formatting_brackets(
            skillEntity.mstSkillDetail[0].detail
        )

    aiIds = get_ai_id_from_skill(region, skillEntity.mstSkill.id)
    if aiIds[AiType.svt] or aiIds[AiType.field]:
        nice_skill["aiIds"] = aiIds

    nice_skill["coolDown"] = [
        skill_lv.chargeTurn for skill_lv in skillEntity.mstSkillLv
    ]

    nice_skill["script"] = {
        scriptKey: [skillLv.script[scriptKey] for skillLv in skillEntity.mstSkillLv]
        for scriptKey in skillEntity.mstSkillLv[0].script
    }

    nice_skill["functions"] = []
    for funci, _ in enumerate(skillEntity.mstSkillLv[0].funcId):
        function = skillEntity.mstSkillLv[0].expandedFuncId[funci]
        followerVals = (
            [
                skill_lv.script["followerVals"][funci]
                for skill_lv in skillEntity.mstSkillLv
            ]
            if "followerVals" in skillEntity.mstSkillLv[0].script
            else None
        )

        nice_func = get_nice_function(
            region,
            function,
            svals=[skill_lv.svals[funci] for skill_lv in skillEntity.mstSkillLv],
            followerVals=followerVals,
        )

        nice_skill["functions"].append(nice_func)

    # .mstSvtSkill returns the list of SvtSkill with the same skill_id
    chosen_svts = [
        svt_skill for svt_skill in skillEntity.mstSvtSkill if svt_skill.svtId == svtId
    ]
    if chosen_svts:
        out_skills = []
        for chosenSvt in chosen_svts:
            out_skill = deepcopy(nice_skill)
            out_skill |= {
                "strengthStatus": chosenSvt.strengthStatus,
                "num": chosenSvt.num,
                "priority": chosenSvt.priority,
                "condQuestId": chosenSvt.condQuestId,
                "condQuestPhase": chosenSvt.condQuestPhase,
                "condLv": chosenSvt.condLv,
                "condLimitCount": chosenSvt.condLimitCount,
            }
            out_skills.append(out_skill)
        return out_skills

    return [nice_skill]


def get_nice_skill_from_raw(
    region: Region, raw_skill: SkillEntityNoReverse, lang: Language
) -> NiceSkillReverse:
    svt_list = [svt_skill.svtId for svt_skill in raw_skill.mstSvtSkill]
    if svt_list:
        svt_id = svt_list[0]
    else:
        svt_id = 0

    nice_skill = NiceSkillReverse.parse_obj(
        get_nice_skill_with_svt(raw_skill, svt_id, region, lang)[0]
    )

    return nice_skill


def get_nice_skill_from_id(
    conn: Connection,
    region: Region,
    skill_id: int,
    lang: Language,
) -> NiceSkillReverse:
    raw_skill = get_skill_entity_no_reverse(conn, region, skill_id, expand=True)
    return get_nice_skill_from_raw(region, raw_skill, lang)


@dataclass(eq=True, frozen=True)
class SkillSvt:
    """Required parameters to get a specific nice skill"""

    skill_id: int
    svt_id: int


MultipleNiceSkills = dict[SkillSvt, NiceSkill]


def get_multiple_nice_skills(
    conn: Connection,
    region: Region,
    skill_svts: Iterable[SkillSvt],
    lang: Language,
) -> MultipleNiceSkills:
    """Get multiple nice skills at once

    Args:
        `conn`: DB Connection
        `region`: Region
        `skill_svts`: List of skill id - svt id tuple pairs
        `lang`: Language

    Returns:
        Mapping of skill id - svt id tuple to nice skill
    """
    raw_skills = {
        skill.mstSkill.id: skill
        for skill in get_skill_entity_no_reverse_many(
            conn, region, [skill.skill_id for skill in skill_svts], expand=True
        )
    }
    return {
        skill_svt: NiceSkill.parse_obj(
            get_nice_skill_with_svt(
                raw_skills[skill_svt.skill_id], skill_svt.svt_id, region, lang
            )[0]
        )
        for skill_svt in skill_svts
        if skill_svt.skill_id in raw_skills
    }
