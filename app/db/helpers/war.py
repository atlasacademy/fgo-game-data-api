from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstSpot
from ...schemas.raw import MstSpot


def get_mstSpot(conn: Connection, war_id: int) -> list[MstSpot]:
    mstSpot_stmt = (
        select(mstSpot).where(mstSpot.c.warId == war_id).order_by(mstSpot.c.id)
    )
    return [MstSpot.from_orm(spot) for spot in conn.execute(mstSpot_stmt).fetchall()]
