from typing import Any, Iterable, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, select

from ...models.raw import mstFunc
from ...schemas.enums import FUNC_VALS_NOT_BUFF
from ...schemas.raw import FunctionEntityNoReverse


def get_func_id(conn: Connection, func_id: int) -> Optional[FunctionEntityNoReverse]:
    stmt = select(mstFunc).where(mstFunc.c.id == func_id)
    func_entity = conn.execute(stmt).fetchone()
    if func_entity:
        return FunctionEntityNoReverse.from_orm(func_entity)
    return None


def get_func_search(
    conn: Connection,
    func_types: Optional[Iterable[int]],
    target_types: Optional[Iterable[int]],
    apply_targets: Optional[Iterable[int]],
    vals: Optional[Iterable[int]],
    tvals: Optional[Iterable[int]],
    questTvals: Optional[Iterable[int]],
) -> list[FunctionEntityNoReverse]:
    where_clause: list[Any] = [True]
    if func_types:
        where_clause.append(mstFunc.c.funcType.in_(func_types))
    if target_types:
        where_clause.append(mstFunc.c.targetType.in_(target_types))
    if apply_targets:
        where_clause.append(mstFunc.c.applyTarget.in_(apply_targets))
    if vals:
        where_clause.append(mstFunc.c.vals.contains(vals))
    if tvals:
        where_clause.append(mstFunc.c.tvals.contains(tvals))
    if questTvals:
        where_clause.append(mstFunc.c.questTvals.contains(questTvals))

    func_search_stmt = select(mstFunc).distinct().where(and_(*where_clause))

    return [
        FunctionEntityNoReverse.from_orm(func)
        for func in conn.execute(func_search_stmt).fetchall()
    ]


def get_func_from_buff(conn: Connection, buff_id: int) -> list[FunctionEntityNoReverse]:
    func_search_stmt = (
        select(mstFunc)
        .where(
            and_(
                mstFunc.c.vals[1] == buff_id,
                mstFunc.c.funcType.notin_(FUNC_VALS_NOT_BUFF),
            )
        )
        .order_by(mstFunc.c.id)
    )

    return [
        FunctionEntityNoReverse.from_orm(func)
        for func in conn.execute(func_search_stmt).fetchall()
    ]
