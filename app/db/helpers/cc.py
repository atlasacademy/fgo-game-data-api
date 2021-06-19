from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstCommandCode


def get_cc_id(conn: Connection, col_no: int) -> int:
    stmt = select(mstCommandCode.c.id).where(mstCommandCode.c.collectionNo == col_no)
    mstCc_db = conn.execute(stmt).fetchone()
    if mstCc_db:
        return int(mstCc_db.id)
    return col_no
