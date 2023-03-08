from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, select, true
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import mstBuff
from ...schemas.raw import MstBuff


async def get_buff_search(
    conn: AsyncConnection,
    buff_types: Optional[Iterable[int]],
    buffGroup: Optional[Iterable[int]],
    vals: Optional[Iterable[int]],
    tvals: Optional[Iterable[int]],
    ckSelfIndv: Optional[Iterable[int]],
    ckOpIndv: Optional[Iterable[int]],
) -> list[MstBuff]:
    where_clause: list[_ColumnExpressionArgument[bool]] = [true()]
    if buff_types:
        where_clause.append(mstBuff.c.type.in_(buff_types))
    if buffGroup:
        where_clause.append(mstBuff.c.buffGroup.in_(buffGroup))
    if vals:
        where_clause.append(mstBuff.c.vals.contains(vals))
    if tvals:
        where_clause.append(mstBuff.c.tvals.contains(tvals))
    if ckSelfIndv:
        where_clause.append(mstBuff.c.ckSelfIndv.contains(ckSelfIndv))
    if ckOpIndv:
        where_clause.append(mstBuff.c.ckOpIndv.contains(ckOpIndv))

    func_search_stmt = select(mstBuff).distinct().where(and_(*where_clause))

    return [
        MstBuff.from_orm(buff)
        for buff in (await conn.execute(func_search_stmt)).fetchall()
    ]
