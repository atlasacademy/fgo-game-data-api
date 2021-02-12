from typing import List

from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.sql import func, select

from ...models.raw import mstAi, mstAiAct, mstAiField
from ...schemas.raw import AiEntity


def get_ai_entity(conn: Connection, ai_table: Table, ai_id: int) -> List[AiEntity]:
    JOINED_AI_TABLES = ai_table.outerjoin(mstAiAct, ai_table.c.aiActId == mstAiAct.c.id)

    SELECT_AI_ENTITY = [
        ai_table.c.id,
        ai_table.c.idx,
        func.to_jsonb(ai_table.table_valued()).label("mstAi"),
        func.to_jsonb(mstAiAct.table_valued()).label(mstAiAct.name),
    ]

    stmt = (
        select(SELECT_AI_ENTITY)
        .select_from(JOINED_AI_TABLES)
        .where(ai_table.c.id == ai_id)
        .order_by(ai_table.c.id, ai_table.c.idx)
    )

    return [
        AiEntity.parse_obj(ai_entity) for ai_entity in conn.execute(stmt).fetchall()
    ]


def get_svt_ai_entity(conn: Connection, ai_id: int) -> List[AiEntity]:
    return get_ai_entity(conn, mstAi, ai_id)


def get_field_ai_entity(conn: Connection, ai_id: int) -> List[AiEntity]:
    return get_ai_entity(conn, mstAiField, ai_id)
