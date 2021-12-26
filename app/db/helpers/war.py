from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import select

from ...models.raw import mstMap, mstSpot, mstWar
from ...schemas.raw import MstSpot, MstWar


async def get_war_from_spot(conn: AsyncConnection, spot_id: int) -> MstWar:
    stmt = (
        select(mstWar)
        .select_from(
            mstWar.outerjoin(mstMap, mstMap.c.warId == mstWar.c.id).outerjoin(
                mstSpot, mstSpot.c.mapId == mstMap.c.id
            )
        )
        .where(mstSpot.c.id == spot_id)
    )

    return MstWar.from_orm((await conn.execute(stmt)).fetchone())


async def get_spot_from_id(conn: AsyncConnection, spot_id: int) -> MstSpot:
    stmt = select(mstSpot).where(mstSpot.c.id == spot_id)
    return MstSpot.from_orm((await conn.execute(stmt)).fetchone())
