from typing import Any, Iterable, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, func, literal_column, select

from ...models.raw import mstSkill, mstSkillDetail, mstSkillLv, mstSvtSkill
from ...schemas.raw import MstSkill, SkillEntityNoReverse
from .utils import sql_jsonb_agg


def get_skillEntity(
    conn: Connection, skill_ids: Iterable[int]
) -> List[SkillEntityNoReverse]:
    mstSkillLvJson = (
        select(
            [
                mstSkillLv.c.skillId,
                func.jsonb_agg(
                    literal_column(f'"{mstSkillLv.name}" ORDER BY "lv"')
                ).label(mstSkillLv.name),
            ]
        )
        .where(mstSkillLv.c.skillId.in_(skill_ids))
        .group_by(mstSkillLv.c.skillId)
        .cte()
    )

    JOINED_SKILL_TABLES = (
        mstSkill.join(
            mstSkillDetail,
            mstSkillDetail.c.id == mstSkill.c.id,
            isouter=True,
        )
        .join(
            mstSvtSkill,
            mstSvtSkill.c.skillId == mstSkill.c.id,
            isouter=True,
        )
        .join(
            mstSkillLvJson,
            mstSkillLvJson.c.skillId == mstSkill.c.id,
            isouter=True,
        )
    )

    SELECT_SKILL_ENTITY = [
        func.to_jsonb(literal_column(f'"{mstSkill.name}"')).label(mstSkill.name),
        sql_jsonb_agg(mstSkillDetail),
        sql_jsonb_agg(mstSvtSkill),
        mstSkillLvJson.c.mstSkillLv,
    ]

    stmt = (
        select(SELECT_SKILL_ENTITY)
        .select_from(JOINED_SKILL_TABLES)
        .where(mstSkill.c.id.in_(skill_ids))
        .group_by(mstSkill.c.id, mstSkillLvJson.c.mstSkillLv)
    )

    skill_entities = (
        SkillEntityNoReverse.parse_obj(skill) for skill in conn.execute(stmt).fetchall()
    )
    order = {skill_id: i for i, skill_id in enumerate(skill_ids)}

    return sorted(skill_entities, key=lambda skill: order[skill.mstSkill.id])


def get_mstSvtSkill(conn: Connection, svt_id: int) -> List[Any]:
    mstSvtSkill_stmt = select([mstSvtSkill]).where(mstSvtSkill.c.svtId == svt_id)
    fetched: list[Any] = conn.execute(mstSvtSkill_stmt).fetchall()
    return fetched


def get_skill_search(
    conn: Connection,
    skillType: Optional[Iterable[int]],
    num: Optional[Iterable[int]],
    priority: Optional[Iterable[int]],
    strengthStatus: Optional[Iterable[int]],
    lvl1coolDown: Optional[Iterable[int]],
    numFunctions: Optional[Iterable[int]],
) -> List[MstSkill]:
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

    skill_search_stmt = (
        select([mstSkill])
        .select_from(
            mstSkill.join(
                mstSvtSkill, mstSvtSkill.c.skillId == mstSkill.c.id, isouter=True
            ).join(mstSkillLv, mstSkillLv.c.skillId == mstSkill.c.id, isouter=True)
        )
        .where(and_(*where_clause))
    )

    return [
        MstSkill.parse_obj(skill)
        for skill in conn.execute(skill_search_stmt).fetchall()
    ]
