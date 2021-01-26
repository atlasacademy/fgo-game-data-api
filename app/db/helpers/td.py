from typing import Any, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import (
    mstSvtTreasureDevice,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstTreasureDeviceLv,
)


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
