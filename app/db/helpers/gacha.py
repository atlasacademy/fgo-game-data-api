from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import func, select

from ...models.raw import (
    mstCommonRelease,
    mstGacha,
    mstGachaStoryAdjust,
    mstGachaSub,
    viewGachaFeaturedSvt,
)
from ...schemas.raw import GachaEntity
from .utils import sql_jsonb_agg


SELECT_GACHA_ENTITY = select(
    func.to_jsonb(mstGacha.table_valued()).label(mstGacha.name),
    sql_jsonb_agg(mstGachaStoryAdjust),
    sql_jsonb_agg(mstGachaSub),
    sql_jsonb_agg(mstCommonRelease),
    sql_jsonb_agg(viewGachaFeaturedSvt),
).select_from(
    mstGacha.outerjoin(
        mstGachaStoryAdjust, mstGacha.c.id == mstGachaStoryAdjust.c.gachaId
    )
    .outerjoin(mstGachaSub, mstGacha.c.id == mstGachaSub.c.gachaId)
    .outerjoin(mstCommonRelease, mstGachaSub.c.commonReleaseId == mstCommonRelease.c.id)
    .outerjoin(viewGachaFeaturedSvt, mstGacha.c.id == viewGachaFeaturedSvt.c.gachaId)
)


async def get_gacha_entity(conn: AsyncConnection, gacha_id: int) -> GachaEntity | None:
    stmt = SELECT_GACHA_ENTITY.where(mstGacha.c.id == gacha_id).group_by(
        mstGacha.table_valued()
    )
    res = (await conn.execute(stmt)).fetchone()

    if res is not None:
        return GachaEntity.from_orm(res)
    else:
        return None


async def get_all_gacha_entities(conn: AsyncConnection) -> list[GachaEntity]:
    stmt = SELECT_GACHA_ENTITY.group_by(mstGacha.table_valued())

    return [
        GachaEntity.from_orm(gacha) for gacha in ((await conn.execute(stmt)).fetchall())
    ]
