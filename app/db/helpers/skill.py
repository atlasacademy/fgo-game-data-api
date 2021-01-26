from typing import Any, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstSkill, mstSkillDetail, mstSkillLv, mstSvtSkill


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
