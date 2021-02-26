from typing import Any, Iterable, Optional

from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, func, select

from ...models.raw import (
    mstSvtTreasureDevice,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstTreasureDeviceLv,
)
from ...schemas.raw import MstTreasureDevice, TdEntityNoReverse
from .utils import sql_jsonb_agg


def get_tdEntity(conn: Connection, td_ids: Iterable[int]) -> list[TdEntityNoReverse]:
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
    )

    SELECT_TD_ENTITY = [
        mstTreasureDevice.c.id,
        func.to_jsonb(mstTreasureDevice.table_valued()).label(mstTreasureDevice.name),
        sql_jsonb_agg(mstTreasureDeviceDetail),
        sql_jsonb_agg(mstSvtTreasureDevice),
        mstTreasureDeviceLvJson.c.mstTreasureDeviceLv,
    ]

    stmt = (
        select(*SELECT_TD_ENTITY)
        .select_from(JOINED_TD_TABLES)
        .where(mstTreasureDevice.c.id.in_(td_ids))
        .group_by(mstTreasureDevice.c.id, mstTreasureDeviceLvJson.c.mstTreasureDeviceLv)
    )

    skill_entities = [
        TdEntityNoReverse.from_orm(skill) for skill in conn.execute(stmt).fetchall()
    ]
    order = {skill_id: i for i, skill_id in enumerate(td_ids)}

    return sorted(skill_entities, key=lambda td: order[td.mstTreasureDevice.id])


def get_mstSvtTreasureDevice(conn: Connection, svt_id: int) -> list[Any]:
    mstSvtTreasureDevice_stmt = select(mstSvtTreasureDevice).where(
        mstSvtTreasureDevice.c.svtId == svt_id
    )
    fetched: list[Any] = conn.execute(mstSvtTreasureDevice_stmt).fetchall()
    return fetched


def get_td_search(
    conn: Connection,
    individuality: Optional[Iterable[int]],
    card: Optional[Iterable[int]],
    hits: Optional[Iterable[int]],
    strengthStatus: Optional[Iterable[int]],
    numFunctions: Optional[Iterable[int]],
    minNpNpGain: Optional[int],
    maxNpNpGain: Optional[int],
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

    td_search_stmt = (
        select(mstTreasureDevice)
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
        MstTreasureDevice.from_orm(td) for td in conn.execute(td_search_stmt).fetchall()
    ]
