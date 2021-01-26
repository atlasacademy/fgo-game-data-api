from typing import Any, List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstAi, mstAiAct, mstAiField


def get_mstAi(conn: Connection, ai_id: int) -> List[Any]:
    mstAi_stmt = select([mstAi]).where(mstAi.c.id == ai_id)
    fetched: list[Any] = conn.execute(mstAi_stmt).fetchall()
    return fetched


def get_mstAiField(conn: Connection, ai_id: int) -> List[Any]:
    mstAiField_stmt = select([mstAiField]).where(mstAiField.c.id == ai_id)
    fetched: list[Any] = conn.execute(mstAiField_stmt).fetchall()
    return fetched


def get_mstAiAct(conn: Connection, ai_act_id: int) -> Any:
    mstAiAct_stmt = select([mstAiAct]).where(mstAiAct.c.id == ai_act_id)
    return conn.execute(mstAiAct_stmt).fetchone()
