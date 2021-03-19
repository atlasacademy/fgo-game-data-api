from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstMap, mstSpot, mstWar


def get_war_from_spot(conn: Connection, spot_id: int) -> int:
    stmt = (
        select(mstWar.c.id)
        .select_from(
            mstWar.outerjoin(mstMap, mstMap.c.warId == mstWar.c.id).outerjoin(
                mstSpot, mstSpot.c.mapId == mstMap.c.id
            )
        )
        .where(mstSpot.c.id == spot_id)
    )

    war = conn.execute(stmt).fetchone()
    if war:
        return int(war.id)
    else:
        return -1
