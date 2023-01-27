from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, select, true
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import mstItem, mstSetItem
from ...schemas.enums import NiceItemUse
from ...schemas.raw import MstItem, MstSetItem


async def get_mstSetItem(
    conn: AsyncConnection, set_item_ids: Iterable[int]
) -> list[MstSetItem]:
    mstSetItem_stmt = (
        select(mstSetItem)
        .where(mstSetItem.c.id.in_(set_item_ids))
        .order_by(mstSetItem.c.id)
    )
    return [
        MstSetItem.from_orm(set_item)
        for set_item in (await conn.execute(mstSetItem_stmt)).fetchall()
    ]


async def get_item_search(
    conn: AsyncConnection,
    individuality: Optional[Iterable[int]],
    item_type: Optional[Iterable[int]],
    bg_type: Optional[Iterable[int]],
    uses: Optional[list[NiceItemUse]],
) -> list[MstItem]:
    where_clause: list[_ColumnExpressionArgument[bool]] = [true()]
    if individuality:
        where_clause.append(mstItem.c.individuality.contains(individuality))
    if item_type:
        where_clause.append(mstItem.c.type.in_(item_type))
    if bg_type:
        where_clause.append(mstItem.c.bgImageId.in_(bg_type))
    if uses:
        if NiceItemUse.skill in uses:
            where_clause.append(mstItem.c.useSkill.is_(True))
        if NiceItemUse.appendSkill in uses:
            where_clause.append(mstItem.c.useAppendSkill.is_(True))
        if NiceItemUse.ascension in uses:
            where_clause.append(mstItem.c.useAscension.is_(True))
        if NiceItemUse.costume in uses:
            where_clause.append(mstItem.c.useCostume.is_(True))

    item_search_stmt = select(mstItem).distinct().where(and_(*where_clause))

    return [
        MstItem.from_orm(item)
        for item in (await conn.execute(item_search_stmt)).fetchall()
    ]
