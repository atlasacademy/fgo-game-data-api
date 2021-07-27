from sqlalchemy import Table
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import func, select

from ...models.raw import mstAi, mstAiAct, mstAiField
from ...schemas.raw import AiEntity


async def get_ai_entity(
    conn: AsyncConnection, ai_table: Table, ai_id: int
) -> list[AiEntity]:
    JOINED_AI_TABLES = ai_table.outerjoin(mstAiAct, ai_table.c.aiActId == mstAiAct.c.id)

    SELECT_AI_ENTITY = [
        ai_table.c.id,
        ai_table.c.idx,
        func.to_jsonb(ai_table.table_valued()).label("mstAi"),
        func.to_jsonb(mstAiAct.table_valued()).label(mstAiAct.name),
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
