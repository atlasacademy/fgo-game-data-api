from typing import Iterable

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstSetItem
from ...schemas.raw import MstSetItem


def get_mstSetItem(conn: Connection, set_item_ids: Iterable[int]) -> list[MstSetItem]:
    mstSetItem_stmt = (
        select(mstSetItem)
        .where(mstSetItem.c.id.in_(set_item_ids))
        .order_by(mstSetItem.c.id)
    )
    return [
        MstSetItem.from_orm(set_item)
        for set_item in conn.execute(mstSetItem_stmt).fetchall()
    ]
