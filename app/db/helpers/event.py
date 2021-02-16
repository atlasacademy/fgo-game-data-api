from typing import List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstEventReward, mstShop
from ...schemas.raw import MstEventReward, MstShop


def get_mstShop(conn: Connection, event_id: int) -> List[MstShop]:
    mstShop_stmt = (
        select(mstShop).where(mstShop.c.eventId == event_id).order_by(mstShop.c.id)
    )
    return [MstShop.from_orm(shop) for shop in conn.execute(mstShop_stmt).fetchall()]


def get_mstShop_by_id(conn: Connection, shop_id: int) -> MstShop:
    mstShop_stmt = select(mstShop).where(mstShop.c.id == shop_id)
    return MstShop.from_orm(conn.execute(mstShop_stmt).fetchone())


def get_mstEventReward(conn: Connection, event_id: int) -> List[MstEventReward]:
    mstEventReward_stmt = select(mstEventReward).where(
        mstEventReward.c.eventId == event_id
    )
    return [
        MstEventReward.from_orm(reward)
        for reward in conn.execute(mstEventReward_stmt).fetchall()
    ]
