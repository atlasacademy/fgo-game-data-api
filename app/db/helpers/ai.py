from sqlalchemy import Integer, Table
from sqlalchemy.dialects.postgresql import ARRAY, array, array_agg
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import cast, func, select

from ...models.raw import mstAi, mstAiAct, mstAiField
from ...schemas.raw import AiEntity


async def get_ai_entity(
    conn: AsyncConnection, ai_table: Table, ai_id: int
) -> list[AiEntity]:
    parent_ai = (
        select(
            func.jsonb_build_object(
                "svt" if ai_table is mstAi else "field",
                func.coalesce(
                    func.array_remove(array_agg(ai_table.c.id.distinct()), None),  # type: ignore[no-untyped-call]
                    [],
                ),
                "field" if ai_table is mstAi else "svt",
                cast(array([]), ARRAY(Integer)),  # type: ignore[no-untyped-call]
            )
        )
        .select_from(ai_table)
        .where(ai_table.c.avals[1] == ai_id)
        .scalar_subquery()
    )

    JOINED_AI_TABLES = ai_table.outerjoin(mstAiAct, ai_table.c.aiActId == mstAiAct.c.id)

    SELECT_AI_ENTITY = [
        ai_table.c.id,
        ai_table.c.idx,
        func.to_jsonb(ai_table.table_valued()).label("mstAi"),
        func.to_jsonb(mstAiAct.table_valued()).label(mstAiAct.name),
        parent_ai.label("parentAis"),
    ]

    stmt = (
        select(*SELECT_AI_ENTITY)
        .select_from(JOINED_AI_TABLES)
        .where(ai_table.c.id == ai_id)
        .order_by(ai_table.c.id, ai_table.c.idx)
    )
    try:
        return [
            AiEntity.from_orm(ai_entity)
            for ai_entity in (await conn.execute(stmt)).fetchall()
        ]
    except DBAPIError:
        return []


async def get_svt_ai_entity(conn: AsyncConnection, ai_id: int) -> list[AiEntity]:
    return await get_ai_entity(conn, mstAi, ai_id)


async def get_field_ai_entity(conn: AsyncConnection, ai_id: int) -> list[AiEntity]:
    return await get_ai_entity(conn, mstAiField, ai_id)
