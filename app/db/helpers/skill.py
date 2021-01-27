from typing import Any, Iterable, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, func, select

from ...models.raw import mstSkill, mstSkillDetail, mstSkillLv, mstSvtSkill
from ...schemas.raw import MstSkill


def get_mstSkill(conn: Connection, skill_id: int) -> Any:
    mstSkill_stmt = select([mstSkill]).where(mstSkill.c.id == skill_id)
    return conn.execute(mstSkill_stmt).fetchone()


def get_mstSkillDetail(conn: Connection, skill_id: int) -> List[Any]:
    mstSkillDetail_stmt = select([mstSkillDetail]).where(
        mstSkillDetail.c.id == skill_id
    )
    fetched: list[Any] = conn.execute(mstSkillDetail_stmt).fetchall()
    return fetched


def get_mstSkillLv(conn: Connection, skill_id: int) -> List[Any]:
    mstSkillLv_stmt = (
        select([mstSkillLv])
        .where(mstSkillLv.c.skillId == skill_id)
        .order_by(mstSkillLv.c.lv)
    )
    fetched: list[Any] = conn.execute(mstSkillLv_stmt).fetchall()
    return fetched


def get_mstSvtSkill(
    conn: Connection, skill_id: Optional[int] = None, svt_id: Optional[int] = None
) -> List[Any]:
    if skill_id:
        mstSvtSkill_stmt = select([mstSvtSkill]).where(
            mstSvtSkill.c.skillId == skill_id
        )
    elif svt_id:
        mstSvtSkill_stmt = select([mstSvtSkill]).where(mstSvtSkill.c.svtId == svt_id)
    else:
        raise ValueError("Must give at least one input for get_mstSvtSkill.")
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
