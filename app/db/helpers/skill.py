from typing import Iterable, Optional

from sqlalchemy.dialects.postgresql import aggregate_order_by, array_agg
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, func, or_, select

from ...models.raw import (
    mstAi,
    mstAiAct,
    mstAiField,
    mstCommonRelease,
    mstSkill,
    mstSkillAdd,
    mstSkillDetail,
    mstSkillGroup,
    mstSkillGroupOverwrite,
    mstSkillLv,
    mstSvtSkill,
    mstSvtSkillRelease,
)
from ...schemas.raw import MstSkill, MstSvtSkill, SkillEntityNoReverse
from .utils import sql_jsonb_agg


async def get_skillEntity(
    conn: AsyncConnection, skill_ids: Iterable[int]
) -> list[SkillEntityNoReverse]:
    mstSkillLvJson = (
        select(
            mstSkillLv.c.skillId,
            func.jsonb_agg(
                aggregate_order_by(mstSkillLv.table_valued(), mstSkillLv.c.lv)  # type: ignore[no-untyped-call]
            ).label(mstSkillLv.name),
        )
        .where(mstSkillLv.c.skillId.in_(skill_ids))
        .group_by(mstSkillLv.c.skillId)
        .cte()
    )

    aiIds = (
        select(
            mstAiAct.c.skillVals[1].label("skillId"),
            func.jsonb_build_object(
                "svt",
                func.coalesce(
                    func.array_remove(array_agg(mstAi.c.id.distinct()), None),  # type: ignore[no-untyped-call]
                    [],
                ),
                "field",
                func.coalesce(
                    func.array_remove(array_agg(mstAiField.c.id.distinct()), None),  # type: ignore[no-untyped-call]
                    [],
                ),
            ).label("aiIds"),
        )
        .select_from(
            mstAiAct.outerjoin(mstAi, mstAi.c.aiActId == mstAiAct.c.id).outerjoin(
                mstAiField, mstAiField.c.aiActId == mstAiAct.c.id
            )
        )
        .where(mstAiAct.c.skillVals[1].in_(skill_ids))
        .group_by(mstAiAct.c.skillVals)
        .cte()
    )

    JOINED_SKILL_TABLES = (
        mstSkill.outerjoin(mstSvtSkill, mstSvtSkill.c.skillId == mstSkill.c.id)
        .outerjoin(mstSkillAdd, mstSkillAdd.c.skillId == mstSkill.c.id)
        .outerjoin(
            mstCommonRelease, mstSkillAdd.c.commonReleaseId == mstCommonRelease.c.id
        )
        .outerjoin(mstSkillLvJson, mstSkillLvJson.c.skillId == mstSkill.c.id)
        .outerjoin(aiIds, aiIds.c.skillId == mstSkill.c.id)
        .outerjoin(mstSkillGroup, mstSkillGroup.c.skillId == mstSkill.c.id)
        .outerjoin(
            mstSkillGroupOverwrite,
            mstSkillGroupOverwrite.c.skillGroupId == mstSkillGroup.c.id,
        )
        .outerjoin(
            mstSvtSkillRelease,
            and_(
                mstSvtSkillRelease.c.svtId == mstSvtSkill.c.svtId,
                mstSvtSkillRelease.c.num == mstSvtSkill.c.num,
                mstSvtSkillRelease.c.priority == mstSvtSkill.c.priority,
            ),
        )
        .outerjoin(
            mstSkillDetail,
            or_(
                mstSkillDetail.c.id == mstSkill.c.id,
                mstSkillDetail.c.id == mstSkillGroupOverwrite.c.skillDetailId,
            ),
        )
    )

    SELECT_SKILL_ENTITY = [
        func.to_jsonb(mstSkill.table_valued()).label(mstSkill.name),
        sql_jsonb_agg(mstSkillDetail),
        sql_jsonb_agg(mstSvtSkill),
        sql_jsonb_agg(mstSkillAdd),
        sql_jsonb_agg(mstCommonRelease),
        sql_jsonb_agg(mstSkillGroup),
        sql_jsonb_agg(mstSkillGroupOverwrite),
        sql_jsonb_agg(mstSvtSkillRelease),
        mstSkillLvJson.c.mstSkillLv,
        aiIds.c.aiIds,
    ]

    stmt = (
        select(*SELECT_SKILL_ENTITY)
        .select_from(JOINED_SKILL_TABLES)
        .where(mstSkill.c.id.in_(skill_ids))
        .group_by(mstSkill.c.id, mstSkillLvJson.c.mstSkillLv, aiIds.c.aiIds)
    )

    try:
        skill_entities = [
            SkillEntityNoReverse.from_orm(skill)
            for skill in (await conn.execute(stmt)).fetchall()
        ]
        order = {skill_id: i for i, skill_id in enumerate(skill_ids)}
    except DBAPIError:
        return []

    return sorted(skill_entities, key=lambda skill: order[skill.mstSkill.id])


async def get_mstSvtSkill(conn: AsyncConnection, svt_id: int) -> list[MstSvtSkill]:
    mstSvtSkill_stmt = select(mstSvtSkill).where(mstSvtSkill.c.svtId == svt_id)
    fetched = (await conn.execute(mstSvtSkill_stmt)).fetchall()
    return [MstSvtSkill.from_orm(svt_skill) for svt_skill in fetched]


async def get_skill_search(
    conn: AsyncConnection,
    skillType: Optional[Iterable[int]],
    num: Optional[Iterable[int]],
    priority: Optional[Iterable[int]],
    strengthStatus: Optional[Iterable[int]],
    lvl1coolDown: Optional[Iterable[int]],
    numFunctions: Optional[Iterable[int]],
    svalsContain: str | None,
    triggerSkillId: Iterable[int] | None,
) -> list[MstSkill]:
    where_clause = [mstSkillLv.c.lv == 1]
    if skillType:
        where_clause.append(mstSkill.c.type.in_(skillType))
    if num:
        where_clause.append(mstSvtSkill.c.num.in_(num))
    if priority:
        where_clause.append(mstSvtSkill.c.priority.in_(priority))
    if strengthStatus:
        where_clause.append(mstSvtSkill.c.strengthStatus.in_(strengthStatus))
    if lvl1coolDown:
        where_clause.append(mstSkillLv.c.chargeTurn.in_(lvl1coolDown))
    if numFunctions:
        where_clause.append(func.array_length(mstSkillLv.c.funcId, 1).in_(numFunctions))
    if svalsContain:
        where_clause.append(
            func.array_to_string(mstSkillLv.c.svals, "|").like(f"%{svalsContain}%")
        )
    if triggerSkillId:
        for skill_id in triggerSkillId:
            where_clause.append(mstSkillLv.c.relatedSkillIds.contains([skill_id]))

    skill_search_stmt = (
        select(mstSkill)
        .distinct()
        .select_from(
            mstSkill.outerjoin(
                mstSvtSkill, mstSvtSkill.c.skillId == mstSkill.c.id
            ).outerjoin(mstSkillLv, mstSkillLv.c.skillId == mstSkill.c.id)
        )
        .where(and_(*where_clause))
    )

    return [
        MstSkill.from_orm(skill)
        for skill in (await conn.execute(skill_search_stmt)).fetchall()
    ]
