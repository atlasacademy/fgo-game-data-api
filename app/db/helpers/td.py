from typing import Any, Iterable, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, func, literal_column, select, text

from ...models.raw import (
    mstSvtTreasureDevice,
    mstTreasureDevice,
    mstTreasureDeviceDetail,
    mstTreasureDeviceLv,
)
from ...schemas.raw import MstTreasureDevice, TdEntityNoReverse
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


def get_mstSvtTreasureDevice(conn: Connection, svt_id: int) -> List[Any]:
    mstSvtTreasureDevice_stmt = select([mstSvtTreasureDevice]).where(
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
) -> List[MstTreasureDevice]:
    where_clause = [mstTreasureDeviceLv.c.lv == 1]
    if individuality:
        where_clause.append(mstTreasureDevice.c.individuality.contains(individuality))
    if card:
        where_clause.append(mstSvtTreasureDevice.c.cardId.in_(card))
    if hits:
        # where_clause.append(
        #     func.array_length(mstSvtTreasureDevice.c.damage, 1).in_(hits)
        # )
        # Workaround for https://github.com/sqlalchemy/sqlalchemy/issues/5934
        where_clause.append(
            text('array_length("mstSvtTreasureDevice"."damage", 1) IN :hits')
        )
    if strengthStatus:
        where_clause.append(mstSvtTreasureDevice.c.strengthStatus.in_(strengthStatus))
    if numFunctions:
        # where_clause.append(
        #     func.array_length(mstTreasureDeviceLv.c.funcId, 1).in_(numFunctions)
        # )
        where_clause.append(
            text('array_length("mstTreasureDeviceLv"."funcId", 1) IN :numFunctions')
        )
    if minNpNpGain:
        where_clause.append(mstTreasureDeviceLv.c.tdPoint >= minNpNpGain)
    if maxNpNpGain:
        where_clause.append(mstTreasureDeviceLv.c.tdPoint <= maxNpNpGain)

    td_search_stmt = (
        select([mstTreasureDevice])
        .select_from(
            mstTreasureDevice.join(
                mstSvtTreasureDevice,
                mstSvtTreasureDevice.c.treasureDeviceId == mstTreasureDevice.c.id,
                isouter=True,
            ).join(
                mstTreasureDeviceLv,
                mstTreasureDeviceLv.c.treaureDeviceId == mstTreasureDevice.c.id,
                isouter=True,
            )
        )
        .where(and_(*where_clause))
    )

    return [
        MstTreasureDevice.parse_obj(td)
        for td in conn.execute(
            td_search_stmt,
            hits=tuple(hits) if hits else (),
            numFunctions=tuple(numFunctions) if numFunctions else (),
        ).fetchall()
    ]
