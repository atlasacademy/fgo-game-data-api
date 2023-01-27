from typing import Iterable

from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import Join, and_, select, true
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import mstBoxGachaBase, mstEventTowerReward, mstShop, mstWar
from ...schemas.raw import MstBoxGachaBase, MstEventTowerReward, MstShop, MstWar
from .utils import fetch_one


async def get_event_wars(conn: AsyncConnection, event_id: int) -> list[MstWar]:
    mstWar_stmt = (
        select(mstWar).where(mstWar.c.eventId == event_id).order_by(mstWar.c.id)
    )
    return [
        MstWar.from_orm(war) for war in (await conn.execute(mstWar_stmt)).fetchall()
    ]


async def get_mstShop_by_id(conn: AsyncConnection, shop_id: int) -> MstShop:
    mstShop_stmt = select(mstShop).where(mstShop.c.id == shop_id)
    return MstShop.from_orm(await fetch_one(conn, mstShop_stmt))


async def get_mstEventTowerReward(
    conn: AsyncConnection, event_id: int
) -> list[MstEventTowerReward]:
    mstEventTowerReward_stmt = (
        select(mstEventTowerReward)
        .where(mstEventTowerReward.c.eventId == event_id)
        .order_by(mstEventTowerReward.c.towerId, mstEventTowerReward.c.floor)
    )
    return [
        MstEventTowerReward.from_orm(tower_reward)
        for tower_reward in (await conn.execute(mstEventTowerReward_stmt)).fetchall()
    ]


async def get_mstBoxGachaBase(
    conn: AsyncConnection, box_gacha_base_ids: Iterable[int]
) -> list[MstBoxGachaBase]:
    mstBoxGachaBase_stmt = (
        select(mstBoxGachaBase)
        .where(mstBoxGachaBase.c.id.in_(box_gacha_base_ids))
        .order_by(mstBoxGachaBase.c.id, mstBoxGachaBase.c.no)
    )
    return [
        MstBoxGachaBase.from_orm(box_gacha_base)
        for box_gacha_base in (await conn.execute(mstBoxGachaBase_stmt)).fetchall()
    ]


async def get_shop_search(
    conn: AsyncConnection,
    event_ids: Iterable[int] | None = None,
    shop_type_ints: Iterable[int] | None = None,
    pay_type_ints: Iterable[int] | None = None,
) -> list[MstShop]:
    from_clause: Join | Table = mstShop
    where_clause: list[_ColumnExpressionArgument[bool]] = [true()]

    if event_ids:
        where_clause.append(mstShop.c.eventId.in_(event_ids))
    if shop_type_ints:
        where_clause.append(mstShop.c.shopType.in_(shop_type_ints))
    if pay_type_ints:
        where_clause.append(mstShop.c.payType.in_(pay_type_ints))

    shop_search_stmt = (
        select(mstShop).distinct().select_from(from_clause).where(and_(*where_clause))
    )

    return [
        MstShop.from_orm(shop)
        for shop in (await conn.execute(shop_search_stmt)).fetchall()
    ]
