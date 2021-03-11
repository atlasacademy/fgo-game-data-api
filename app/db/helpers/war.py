from typing import Iterable

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstSpot, mstWarAdd
from ...schemas.raw import MstSpot, MstWarAdd


def get_mstSpot(conn: Connection, map_ids: Iterable[int]) -> list[MstSpot]:
    mstSpot_stmt = (
        select(mstSpot).where(mstSpot.c.mapId.in_(map_ids)).order_by(mstSpot.c.id)
    )
    return [MstSpot.from_orm(spot) for spot in conn.execute(mstSpot_stmt).fetchall()]


def get_mstWarAdd(conn: Connection, war_ids: Iterable[int]) -> list[MstWarAdd]:
    mstWarAdd_stmt = (
        select(mstWarAdd)
        .where(mstWarAdd.c.warId.in_(war_ids))
        .order_by(mstWarAdd.c.warId, mstWarAdd.c.type)
    )
    return [
        MstWarAdd.from_orm(war_add)
        for war_add in conn.execute(mstWarAdd_stmt).fetchall()
    ]
