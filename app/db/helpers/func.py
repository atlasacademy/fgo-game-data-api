from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, or_, select, true
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import mstFunc
from ...schemas.raw import MstFunc


async def get_func_search(
    conn: AsyncConnection,
    func_types: Optional[Iterable[int]],
    target_types: Optional[Iterable[int]],
    apply_targets: Optional[Iterable[int]],
    vals: Optional[Iterable[int]],
    tvals: Optional[Iterable[int]],
    questTvals: Optional[Iterable[int]],
) -> list[MstFunc]:
    where_clause: list[_ColumnExpressionArgument[bool]] = [true()]
    if func_types:
        where_clause.append(mstFunc.c.funcType.in_(func_types))
    if target_types:
        where_clause.append(mstFunc.c.targetType.in_(target_types))
    if apply_targets:
        where_clause.append(mstFunc.c.applyTarget.in_(apply_targets))
    if vals:
        where_clause.append(mstFunc.c.vals.contains(vals))
    if tvals:
        where_clause.append(
            or_(
                mstFunc.c.tvals.contains(tvals),
                mstFunc.c.overWriteTvalsList.contains([list(tvals)]),
            )
        )
    if questTvals:
        where_clause.append(mstFunc.c.questTvals.contains(questTvals))

    func_search_stmt = select(mstFunc).distinct().where(and_(*where_clause))

    return [
        MstFunc.from_orm(func)
        for func in (await conn.execute(func_search_stmt)).fetchall()
    ]
