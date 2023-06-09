from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import or_, select

from ...models.raw import mstBlankEarthSpot, mstMap, mstSpot, mstWar
from ...schemas.raw import MstBlankEarthSpot, MstSpot, MstWar
from .utils import fetch_one


async def get_war_from_spot(conn: AsyncConnection, spot_id: int) -> MstWar | None:
    stmt = (
        select(mstWar)
        .select_from(
            mstWar.outerjoin(mstMap, mstMap.c.warId == mstWar.c.id)
            .outerjoin(mstSpot, mstSpot.c.mapId == mstMap.c.id)
            .outerjoin(mstBlankEarthSpot, mstBlankEarthSpot.c.mapId == mstMap.c.id)
        )
        .where(or_(mstSpot.c.id == spot_id, mstBlankEarthSpot.c.id == spot_id))
    )

    war = await fetch_one(conn, stmt)
    if war:
        return MstWar.from_orm(war)

    return None  # pragma: no cover


async def get_spot_from_id(
    conn: AsyncConnection, spot_id: int
) -> MstSpot | MstBlankEarthSpot | None:
    stmt = select(mstSpot).where(mstSpot.c.id == spot_id)
    spot = await fetch_one(conn, stmt)
    if spot:
        return MstSpot.from_orm(spot)

    stmt = select(mstBlankEarthSpot).where(mstBlankEarthSpot.c.id == spot_id)
    spot = await fetch_one(conn, stmt)
    if spot:
        return MstBlankEarthSpot.from_orm(spot)

    return None  # pragma: no cover


async def get_spot_from_ids(
    conn: AsyncConnection, spot_ids: Iterable[int]
) -> list[MstSpot]:
    stmt = select(mstSpot).where(mstSpot.c.id.in_(spot_ids))
    return [MstSpot.from_orm(spot) for spot in (await conn.execute(stmt)).fetchall()]
