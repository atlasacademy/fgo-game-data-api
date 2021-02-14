from typing import Any, List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstSpot


def get_mstSpot(conn: Connection, war_id: int) -> List[Any]:
    mstSpot_stmt = (
        select([mstSpot]).where(mstSpot.c.warId == war_id).order_by(mstSpot.c.id)
    )
    fetched: list[Any] = conn.execute(mstSpot_stmt).fetchall()
    return fetched
