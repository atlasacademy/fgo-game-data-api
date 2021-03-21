from typing import Any, Iterable, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, select

from ...models.raw import mstBuff
from ...schemas.raw import MstBuff


def get_buff_search(
    conn: Connection,
    buff_types: Optional[Iterable[int]],
    buffGroup: Optional[Iterable[int]],
    vals: Optional[Iterable[int]],
    tvals: Optional[Iterable[int]],
    ckSelfIndv: Optional[Iterable[int]],
    ckOpIndv: Optional[Iterable[int]],
) -> list[MstBuff]:
    where_clause: list[Any] = [True]
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
        MstBuff.from_orm(buff) for buff in conn.execute(func_search_stmt).fetchall()
    ]
