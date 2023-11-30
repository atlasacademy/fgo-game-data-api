from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.common import Language, Region
from ...schemas.nice import NiceStageCutIn, NiceStageCutInSkill
from ...schemas.rayshift import CutInSkill, QuestDrop
from .enemy import get_nice_drop
from .skill import MultipleNiceSkills, SkillSvt, get_multiple_nice_skills


def get_nice_stage_cut_in(
    runs: int,
    stage: int,
    cutin_drops: list[QuestDrop],
    cutin_skills: list[CutInSkill],
    all_skills: MultipleNiceSkills,
) -> NiceStageCutIn:
    skills = [
        NiceStageCutInSkill(
            skill=all_skills[SkillSvt(skill.skill_id, 0)],
            appearCount=skill.appear_count,
        )
        for skill in cutin_skills
        if skill.stage == stage
    ]

    drops = [get_nice_drop(drop) for drop in cutin_drops if drop.stage == stage]

    return NiceStageCutIn(runs=runs, skills=skills, drops=drops)


async def get_quest_stage_cutins(
    conn: AsyncConnection,
    region: Region,
    runs: int,
    cutin_drops: list[QuestDrop],
    cutin_skills: list[CutInSkill],
    lang: Language = Language.jp,
) -> dict[int, NiceStageCutIn]:
    all_skill_ids = [SkillSvt(skill.skill_id, 0) for skill in cutin_skills]
    all_skills = await get_multiple_nice_skills(conn, region, all_skill_ids, lang)

    return {
        stage: get_nice_stage_cut_in(runs, stage, cutin_drops, cutin_skills, all_skills)
        for stage in {drop.stage for drop in cutin_drops}
        | {skill.stage for skill in cutin_skills}
    }
