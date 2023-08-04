from dataclasses import dataclass
from typing import Any, Iterable, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import SKILL_TYPE_NAME, SkillScriptCond
from ...schemas.gameenums import COND_TYPE_NAME
from ...schemas.nice import (
    AssetURL,
    ExtraPassive,
    NiceSelectAddInfoBtnCond,
    NiceSkill,
    NiceSkillAdd,
    NiceSkillReverse,
    NiceSkillSvt,
    NiceSvtSkillRelease,
)
from ...schemas.raw import (
    MstCommonRelease,
    MstSkillAdd,
    MstSvtPassiveSkill,
    MstSvtSkill,
    MstSvtSkillRelease,
    SkillEntityNoReverse,
)
from ..raw import get_skill_entity_no_reverse, get_skill_entity_no_reverse_many
from ..utils import get_traits_list, get_translation, strip_formatting_brackets
from .common_release import get_nice_common_release
from .func import get_nice_function


settings = Settings()


def get_nice_skill_svt(
    skill_svt: MstSvtSkill, skill_releases: list[MstSvtSkillRelease]
) -> NiceSkillSvt:
    return NiceSkillSvt(
        svtId=skill_svt.svtId,
        num=skill_svt.num,
        priority=skill_svt.priority,
        script=skill_svt.script,
        strengthStatus=skill_svt.strengthStatus,
        condQuestId=skill_svt.condQuestId,
        condQuestPhase=skill_svt.condQuestPhase,
        condLv=skill_svt.condLv,
        condLimitCount=skill_svt.condLimitCount,
        eventId=skill_svt.eventId,
        flag=skill_svt.flag,
        releaseConditions=[
            get_nice_skill_release(release)
            for release in skill_releases
            if (release.svtId, release.num, release.priority)
            == (skill_svt.svtId, skill_svt.num, skill_svt.priority)
        ],
    )


def get_extra_passive(svt_passive: MstSvtPassiveSkill) -> ExtraPassive:
    return ExtraPassive(
        num=svt_passive.num,
        priority=svt_passive.priority,
        condQuestId=svt_passive.condQuestId,
        condQuestPhase=svt_passive.condQuestPhase,
        condLv=svt_passive.condLv,
        condLimitCount=svt_passive.condLimitCount,
        condFriendshipRank=svt_passive.condFriendshipRank,
        eventId=svt_passive.eventId,
        flag=svt_passive.flag,
        startedAt=svt_passive.startedAt,
        endedAt=svt_passive.endedAt,
    )


def get_nice_skill_add(
    skill_adds: list[MstSkillAdd], releases: list[MstCommonRelease], lang: Language
) -> list[NiceSkillAdd]:
    return [
        NiceSkillAdd(
            priority=skill_add.priority,
            releaseConditions=[
                get_nice_common_release(release)
                for release in releases
                if release.id == skill_add.commonReleaseId
            ],
            name=get_translation(lang, skill_add.name),
            originalName=skill_add.name,
            ruby=skill_add.ruby,
        )
        for skill_add in skill_adds
    ]


def parse_skill_script_cond(cond: str) -> NiceSelectAddInfoBtnCond:
    if ":" in cond:
        cond_type, value = cond.split(":", maxsplit=2)
        if cond_type in SkillScriptCond.__members__:
            return NiceSelectAddInfoBtnCond(
                cond=SkillScriptCond(cond_type), value=int(value)
            )

    return NiceSelectAddInfoBtnCond(cond=SkillScriptCond.NONE)


def get_nice_skill_script(skill_script: dict[str, Any]) -> dict[str, Any]:
    if SelectAddInfo := skill_script.get("SelectAddInfo"):
        for button in SelectAddInfo["btn"]:
            button["conds"] = [
                parse_skill_script_cond(cond) for cond in button["conds"]
            ]

    return skill_script


def get_nice_skill_release(release: MstSvtSkillRelease) -> NiceSvtSkillRelease:
    return NiceSvtSkillRelease(
        idx=release.idx,
        condType=COND_TYPE_NAME[release.condType],
        condTargetId=release.condTargetId,
        condNum=release.condNum,
        condGroup=release.condGroup,
    )


async def get_nice_skill_with_svt(
    conn: AsyncConnection,
    skillEntity: SkillEntityNoReverse,
    svtId: int,
    region: Region,
    lang: Language,
    mstSvtPassiveSkills: Optional[list[MstSvtPassiveSkill]] = None,
) -> list[dict[str, Any]]:
    sorted_svtSkill = sorted(
        skillEntity.mstSvtSkill, key=lambda x: (x.svtId, x.num, -x.priority)
    )

    nice_skill: dict[str, Any] = {
        "id": skillEntity.mstSkill.id,
        "name": get_translation(lang, skillEntity.mstSkill.name),
        "originalName": skillEntity.mstSkill.name,
        "ruby": skillEntity.mstSkill.ruby,
        "type": SKILL_TYPE_NAME[skillEntity.mstSkill.type],
        "actIndividuality": get_traits_list(skillEntity.mstSkill.actIndividuality),
        "skillAdd": get_nice_skill_add(
            skillEntity.mstSkillAdd, skillEntity.mstCommonRelease, lang
        ),
        "skillSvts": [
            get_nice_skill_svt(td_svt, skillEntity.mstSvtSkillRelease)
            for td_svt in sorted_svtSkill
        ],
    }

    if mstSvtPassiveSkills:
        nice_skill["extraPassive"] = [
            get_extra_passive(svt_skill)
            for svt_skill in mstSvtPassiveSkills
            if svt_skill.skillId == skillEntity.mstSkill.id
        ]
    else:
        nice_skill["extraPassive"] = []

    iconId = skillEntity.mstSkill.iconId
    if iconId != 0:
        nice_skill["icon"] = AssetURL.skillIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    for detail in skillEntity.mstSkillDetail:
        if detail.id == skillEntity.mstSkill.id:
            nice_skill["detail"] = strip_formatting_brackets(detail.detail)
            nice_skill["unmodifiedDetail"] = detail.detail
            break

    nice_skill["aiIds"] = skillEntity.aiIds

    nice_skill["coolDown"] = [
        skill_lv.chargeTurn for skill_lv in skillEntity.mstSkillLv
    ]

    nice_skill["script"] = {
        scriptKey: [
            get_nice_skill_script(skillLv.script)[scriptKey]
            for skillLv in skillEntity.mstSkillLv
        ]
        for scriptKey in skillEntity.mstSkillLv[0].script
    }

    nice_skill["functions"] = []
    if skillEntity.mstSkillLv[0].expandedFuncId:
        for funci, _ in enumerate(skillEntity.mstSkillLv[0].funcId):
            if funci >= len(skillEntity.mstSkillLv[0].expandedFuncId):
                break
            function = skillEntity.mstSkillLv[0].expandedFuncId[funci]
            followerVals = (
                [
                    skill_lv.script["followerVals"][funci]
                    for skill_lv in skillEntity.mstSkillLv
                ]
                if "followerVals" in skillEntity.mstSkillLv[0].script
                else None
            )

            nice_func = await get_nice_function(
                conn,
                region,
                function,
                svals=[skill_lv.svals[funci] for skill_lv in skillEntity.mstSkillLv],
                followerVals=followerVals,
            )

            nice_skill["functions"].append(nice_func)

    if skillEntity.mstSkillGroup and skillEntity.mstSkillGroupOverwrite:
        skill_groups: list[dict[str, Any]] = []
        for group in skillEntity.mstSkillGroup:
            overwrite = next(
                overwrite
                for overwrite in skillEntity.mstSkillGroupOverwrite
                if overwrite.skillGroupId == group.id
            )
            overwrite_detail = next(
                detail
                for detail in skillEntity.mstSkillDetail
                if detail.id == overwrite.skillDetailId
            )
            skill_groups.append(
                {
                    "level": group.lv,
                    "skillGroupId": group.id,
                    "startedAt": overwrite.startedAt,
                    "endedAt": overwrite.endedAt,
                    "icon": AssetURL.skillIcon.format(
                        base_url=settings.asset_url,
                        region=region,
                        item_id=overwrite.iconId,
                    )
                    if overwrite.iconId != 0
                    else None,
                    "detail": strip_formatting_brackets(overwrite_detail.detail),
                    "unmodifiedDetail": overwrite_detail.detail,
                    "functions": [
                        await get_nice_function(conn, region, function, [svals])
                        for function, svals in zip(
                            overwrite.expandedFuncId
                            if overwrite.expandedFuncId
                            else [],
                            overwrite.svals,
                            strict=False,
                        )
                    ],
                }
            )

        nice_skill["groupOverwrites"] = skill_groups

    chosen_svts = [
        svt_skill for svt_skill in skillEntity.mstSvtSkill if svt_skill.svtId == svtId
    ]

    if not chosen_svts and not sorted_svtSkill:  # pragma: no cover
        nice_skill |= {
            "svtId": 0,
            "strengthStatus": 0,
            "num": 0,
            "priority": 0,
            "condQuestId": 0,
            "condQuestPhase": 0,
            "condLv": 0,
            "condLimitCount": 0,
            "releaseConditions": [],
        }
    else:
        if chosen_svts:
            chosen_svt = chosen_svts[0]
        else:
            chosen_svt = sorted_svtSkill[0]

        nice_skill |= {
            "svtId": chosen_svt.svtId,
            "strengthStatus": chosen_svt.strengthStatus,
            "num": chosen_svt.num,
            "priority": chosen_svt.priority,
            "condQuestId": chosen_svt.condQuestId,
            "condQuestPhase": chosen_svt.condQuestPhase,
            "condLv": chosen_svt.condLv,
            "condLimitCount": chosen_svt.condLimitCount,
            "releaseConditions": [
                get_nice_skill_release(release)
                for release in skillEntity.mstSvtSkillRelease
                if (release.svtId, release.num, release.priority)
                == (chosen_svt.svtId, chosen_svt.num, chosen_svt.priority)
            ],
        }

    return [nice_skill]


T = TypeVar("T", NiceSkill, NiceSkillReverse)


async def get_nice_skill_from_raw(
    conn: AsyncConnection,
    region: Region,
    raw_skill: SkillEntityNoReverse,
    nice_skill_type: Type[T],
    lang: Language,
) -> T:
    svt_list = [svt_skill.svtId for svt_skill in raw_skill.mstSvtSkill]
    if svt_list:
        svt_id = svt_list[0]
    else:
        svt_id = 0

    nice_skill = nice_skill_type.parse_obj(
        (await get_nice_skill_with_svt(conn, raw_skill, svt_id, region, lang))[0]
    )

    return nice_skill


async def get_nice_skill_from_id(
    conn: AsyncConnection,
    region: Region,
    skill_id: int,
    nice_skill_type: Type[T],
    lang: Language,
) -> T:
    raw_skill = await get_skill_entity_no_reverse(conn, skill_id, expand=True)
    return await get_nice_skill_from_raw(conn, region, raw_skill, nice_skill_type, lang)


@dataclass(eq=True, frozen=True)
class SkillSvt:
    """Required parameters to get a specific nice skill"""

    skill_id: int
    svt_id: int


MultipleNiceSkills = dict[SkillSvt, NiceSkill]


async def get_multiple_nice_skills(
    conn: AsyncConnection,
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
        for skill in await get_skill_entity_no_reverse_many(
            conn, [skill.skill_id for skill in skill_svts], expand=True
        )
    }
    return {
        skill_svt: NiceSkill.parse_obj(
            (
                await get_nice_skill_with_svt(
                    conn, raw_skills[skill_svt.skill_id], skill_svt.svt_id, region, lang
                )
            )[0]
        )
        for skill_svt in skill_svts
        if skill_svt.skill_id in raw_skills
    }
