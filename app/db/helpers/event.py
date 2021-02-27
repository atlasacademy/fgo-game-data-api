from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstEventPointBuff, mstEventReward, mstShop
from ...schemas.raw import MstEventPointBuff, MstEventReward, MstShop


def get_mstShop(conn: Connection, event_id: int) -> list[MstShop]:
    mstShop_stmt = (
        select(mstShop).where(mstShop.c.eventId == event_id).order_by(mstShop.c.id)
    )
    return [MstShop.from_orm(shop) for shop in conn.execute(mstShop_stmt).fetchall()]


def get_mstShop_by_id(conn: Connection, shop_id: int) -> MstShop:
    mstShop_stmt = select(mstShop).where(mstShop.c.id == shop_id)
    return MstShop.from_orm(conn.execute(mstShop_stmt).fetchone())


def get_mstEventReward(conn: Connection, event_id: int) -> list[MstEventReward]:
    mstEventReward_stmt = select(mstEventReward).where(
        mstEventReward.c.eventId == event_id
    )
    return [
        MstEventReward.from_orm(reward)
        for reward in conn.execute(mstEventReward_stmt).fetchall()
    ]


def get_mstEventPointBuff(conn: Connection, event_id: int) -> list[MstEventPointBuff]:
    mstEventPointBuff_stmt = (
        select(mstEventPointBuff)
        .where(mstEventPointBuff.c.eventId == event_id)
        .order_by(mstEventPointBuff.c.id)
    )
    return [
        MstEventPointBuff.from_orm(pointBuff)
        for pointBuff in conn.execute(mstEventPointBuff_stmt).fetchall()
    ]
