from typing import Iterable, Optional

from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, func, or_, select

from ...models.raw import (
    mstSvtTreasureDevice,
    mstSvtTreasureDeviceRelease,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstTreasureDeviceLv,
)
from ...schemas.raw import MstSvtTreasureDevice, MstTreasureDevice, TdEntityNoReverse
from .utils import sql_jsonb_agg


async def get_tdEntity(
    conn: AsyncConnection, td_ids: Iterable[int]
) -> list[TdEntityNoReverse]:
    mstTreasureDeviceLvJson = (
        select(
            mstTreasureDeviceLv.c.treaureDeviceId,
            func.jsonb_agg(
                aggregate_order_by(
                    mstTreasureDeviceLv.table_valued(), mstTreasureDeviceLv.c.lv
                )
            ).label(mstTreasureDeviceLv.name),
        )
        .where(mstTreasureDeviceLv.c.treaureDeviceId.in_(td_ids))
        .group_by(mstTreasureDeviceLv.c.treaureDeviceId)
        .cte()
    )

    JOINED_TD_TABLES = (
        mstTreasureDevice.outerjoin(
            mstTreasureDeviceDetail,
            mstTreasureDeviceDetail.c.id == mstTreasureDevice.c.id,
        )
        .outerjoin(
            mstSvtTreasureDevice,
            mstSvtTreasureDevice.c.treasureDeviceId == mstTreasureDevice.c.id,
        )
        .outerjoin(
            mstTreasureDeviceLvJson,
            mstTreasureDeviceLvJson.c.treaureDeviceId == mstTreasureDevice.c.id,
        )
        .outerjoin(
            mstSvtTreasureDeviceRelease,
            and_(
                mstSvtTreasureDeviceRelease.c.svtId == mstSvtTreasureDevice.c.svtId,
                mstSvtTreasureDeviceRelease.c.num == mstSvtTreasureDevice.c.num,
                mstSvtTreasureDeviceRelease.c.priority
                == mstSvtTreasureDevice.c.priority,
            ),
        )
    )

    SELECT_TD_ENTITY = [
        mstTreasureDevice.c.id,
        func.to_jsonb(mstTreasureDevice.table_valued()).label(mstTreasureDevice.name),
        sql_jsonb_agg(mstTreasureDeviceDetail),
        sql_jsonb_agg(mstSvtTreasureDevice),
        sql_jsonb_agg(mstSvtTreasureDeviceRelease),
        mstTreasureDeviceLvJson.c.mstTreasureDeviceLv,
    ]

    stmt = (
        select(*SELECT_TD_ENTITY)
        .select_from(JOINED_TD_TABLES)
        .where(mstTreasureDevice.c.id.in_(td_ids))
        .group_by(mstTreasureDevice.c.id, mstTreasureDeviceLvJson.c.mstTreasureDeviceLv)
    )

    try:
        td_entities = [
            TdEntityNoReverse.from_orm(td)
            for td in (await conn.execute(stmt)).fetchall()
        ]
    except DBAPIError:
        return []

    order = {td_id: i for i, td_id in enumerate(td_ids)}

    return sorted(td_entities, key=lambda td: order[td.mstTreasureDevice.id])


async def get_mstSvtTreasureDevice(
    conn: AsyncConnection, svt_id: int
) -> list[MstSvtTreasureDevice]:
    mstSvtTreasureDevice_stmt = select(mstSvtTreasureDevice).where(
        mstSvtTreasureDevice.c.svtId == svt_id
    )
    fetched = (await conn.execute(mstSvtTreasureDevice_stmt)).fetchall()
    return [MstSvtTreasureDevice.from_orm(svt_td) for svt_td in fetched]


async def get_td_search(
    conn: AsyncConnection,
    individuality: Optional[Iterable[int]],
    card: Optional[Iterable[int]],
    hits: Optional[Iterable[int]],
    strengthStatus: Optional[Iterable[int]],
    numFunctions: Optional[Iterable[int]],
    minNpNpGain: Optional[int],
    maxNpNpGain: Optional[int],
    svalsContain: str | None,
    triggerSkillId: Iterable[int] | None,
) -> list[MstTreasureDevice]:
    where_clause = [mstTreasureDeviceLv.c.lv == 1]
    if individuality:
        where_clause.append(mstTreasureDevice.c.individuality.contains(individuality))
    if card:
        where_clause.append(mstSvtTreasureDevice.c.cardId.in_(card))
    if hits:
        where_clause.append(
            func.array_length(mstSvtTreasureDevice.c.damage, 1).in_(hits)
        )
    if strengthStatus:
        where_clause.append(mstSvtTreasureDevice.c.strengthStatus.in_(strengthStatus))
    if numFunctions:
        where_clause.append(
            func.array_length(mstTreasureDeviceLv.c.funcId, 1).in_(numFunctions)
        )
    if minNpNpGain:
        where_clause.append(mstTreasureDeviceLv.c.tdPoint >= minNpNpGain)
    if maxNpNpGain:
        where_clause.append(mstTreasureDeviceLv.c.tdPoint <= maxNpNpGain)
    if svalsContain:
        where_clause.append(
            or_(
                func.array_to_string(mstTreasureDeviceLv.c.svals, "|").like(
                    f"%{svalsContain}%"
                ),
                func.array_to_string(mstTreasureDeviceLv.c.svals2, "|").like(
                    f"%{svalsContain}%"
                ),
                func.array_to_string(mstTreasureDeviceLv.c.svals3, "|").like(
                    f"%{svalsContain}%"
                ),
                func.array_to_string(mstTreasureDeviceLv.c.svals4, "|").like(
                    f"%{svalsContain}%"
                ),
                func.array_to_string(mstTreasureDeviceLv.c.svals5, "|").like(
                    f"%{svalsContain}%"
                ),
            )
        )
    if triggerSkillId:
        for skill_id in triggerSkillId:
            where_clause.append(
                mstTreasureDeviceLv.c.relatedSkillIds.contains([skill_id])
            )

    td_search_stmt = (
        select(mstTreasureDevice)
        .distinct()
        .select_from(
            mstTreasureDevice.outerjoin(
                mstSvtTreasureDevice,
                mstSvtTreasureDevice.c.treasureDeviceId == mstTreasureDevice.c.id,
            ).outerjoin(
                mstTreasureDeviceLv,
                mstTreasureDeviceLv.c.treaureDeviceId == mstTreasureDevice.c.id,
            )
        )
        .where(and_(*where_clause))
    )

    return [
        MstTreasureDevice.from_orm(td)
        for td in (await conn.execute(td_search_stmt)).fetchall()
    ]
