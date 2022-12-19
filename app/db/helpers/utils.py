from typing import Any

from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import Select, func


def sql_jsonb_agg(table: Table) -> Any:
    """Equivalent to `func.JSONB_AGG` but removes empty elements from the output"""
    return func.to_jsonb(
        func.array_remove(array_agg(table.table_valued().distinct()), None)
    ).label(table.name)


async def fetch_one(conn: AsyncConnection, stmt: Select) -> Row | None:
    res = await conn.execute(stmt.limit(1))
    return res.first()
