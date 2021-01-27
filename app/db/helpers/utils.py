from typing import Any

from sqlalchemy import Table
from sqlalchemy.sql import func, literal_column


def sql_jsonb_agg(table: Table) -> Any:
    t_name = table.name
    return func.to_jsonb(
        func.array_remove(
            func.array_agg(literal_column(f'"{t_name}"').distinct()),
            None,
        )
    ).label(t_name)
