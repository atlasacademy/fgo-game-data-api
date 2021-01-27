from typing import List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstShop
from ...schemas.raw import MstShop


def get_mstShop(conn: Connection, event_id: int) -> List[MstShop]:
    mstSkill_stmt = select([mstShop]).where(mstShop.c.eventId == event_id)
    return [MstShop.parse_obj(shop) for shop in conn.execute(mstSkill_stmt).fetchall()]


def get_mstShop_by_id(conn: Connection, shop_id: int) -> MstShop:
    mstSkill_stmt = select([mstShop]).where(mstShop.c.id == shop_id)
    return MstShop.parse_obj(conn.execute(mstSkill_stmt).fetchone())
