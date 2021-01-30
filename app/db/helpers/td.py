from typing import Any, Iterable, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import func, literal_column, select

from ...models.raw import (
    mstSvtTreasureDevice,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstTreasureDeviceLv,
)
from ...schemas.raw import TdEntityNoReverse
from .utils import sql_jsonb_agg


def get_tdEntity(conn: Connection, td_ids: Iterable[int]) -> List[TdEntityNoReverse]:
    mstTreasureDeviceLvJson = (
        select(
            [
                mstTreasureDeviceLv.c.treaureDeviceId,
                func.jsonb_agg(
                    literal_column(f'"{mstTreasureDeviceLv.name}" ORDER BY "lv"')
                ).label(mstTreasureDeviceLv.name),
            ]
        )
        .where(mstTreasureDeviceLv.c.treaureDeviceId.in_(td_ids))
        .group_by(mstTreasureDeviceLv.c.treaureDeviceId)
        .cte()
    )

    JOINED_TD_TABLES = (
        mstTreasureDevice.join(
            mstTreasureDeviceDetail,
            mstTreasureDeviceDetail.c.id == mstTreasureDevice.c.id,
            isouter=True,
        )
        .join(
            mstSvtTreasureDevice,
            mstSvtTreasureDevice.c.treasureDeviceId == mstTreasureDevice.c.id,
            isouter=True,
        )
        .join(
            mstTreasureDeviceLvJson,
            mstTreasureDeviceLvJson.c.treaureDeviceId == mstTreasureDevice.c.id,
            isouter=True,
        )
    )

    SELECT_TD_ENTITY = [
        mstTreasureDevice.c.id.label("sqlalchemy"),
        func.to_jsonb(literal_column(f'"{mstTreasureDevice.name}"')).label(
            mstTreasureDevice.name
        ),
        sql_jsonb_agg(mstTreasureDeviceDetail),
        sql_jsonb_agg(mstSvtTreasureDevice),
        mstTreasureDeviceLvJson.c.mstTreasureDeviceLv,
    ]

    stmt = (
        select(SELECT_TD_ENTITY)
        .select_from(JOINED_TD_TABLES)
        .where(mstTreasureDevice.c.id.in_(td_ids))
        .group_by(mstTreasureDevice.c.id, mstTreasureDeviceLvJson.c.mstTreasureDeviceLv)
    )

    skill_entities = [
        TdEntityNoReverse.parse_obj(skill) for skill in conn.execute(stmt).fetchall()
    ]
    order = {skill_id: i for i, skill_id in enumerate(td_ids)}

    return sorted(skill_entities, key=lambda td: order[td.mstTreasureDevice.id])


def get_mstTreasureDevice(conn: Connection, td_id: int) -> Any:
    mstSkill_stmt = select([mstTreasureDevice]).where(mstTreasureDevice.c.id == td_id)
    return conn.execute(mstSkill_stmt).fetchone()


def get_mstTreasureDeviceDetail(conn: Connection, td_id: int) -> List[Any]:
    mstTreasureDeviceDetail_stmt = select([mstTreasureDeviceDetail]).where(
        mstTreasureDeviceDetail.c.id == td_id
    )
    fetched: list[Any] = conn.execute(mstTreasureDeviceDetail_stmt).fetchall()
    return fetched


def get_mstTreasureDeviceLv(conn: Connection, td_id: int) -> List[Any]:
    mstTreasureDeviceLv_stmt = (
        select([mstTreasureDeviceLv])
        .where(mstTreasureDeviceLv.c.treaureDeviceId == td_id)
        .order_by(mstTreasureDeviceLv.c.lv)
    )
    fetched: list[Any] = conn.execute(mstTreasureDeviceLv_stmt).fetchall()
    return fetched


def get_mstSvtTreasureDevice(
    conn: Connection, td_id: Optional[int] = None, svt_id: Optional[int] = None
) -> List[Any]:
    if td_id:
        mstSvtTreasureDevice_stmt = select([mstSvtTreasureDevice]).where(
            mstSvtTreasureDevice.c.treasureDeviceId == td_id
        )
    elif svt_id:
        mstSvtTreasureDevice_stmt = select([mstSvtTreasureDevice]).where(
            mstSvtTreasureDevice.c.svtId == svt_id
        )
    else:
        raise ValueError("Must give at least one input for get_mstSvtTreasureDevice.")
    fetched: list[Any] = conn.execute(mstSvtTreasureDevice_stmt).fetchall()
    return fetched
