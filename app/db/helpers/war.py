from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstMap, mstSpot, mstWar
from ...schemas.raw import MstWar


def get_war_from_spot(conn: Connection, spot_id: int) -> int:
    stmt = (
        select(mstWar)
        .select_from(
            mstWar.outerjoin(mstMap, mstMap.c.warId == mstWar.c.id).outerjoin(
                mstSpot, mstSpot.c.mapId == mstMap.c.id
            )
        )
        .where(mstSpot.c.id == spot_id)
    )

    return MstWar.from_orm(conn.execute(stmt).fetchone()).id
