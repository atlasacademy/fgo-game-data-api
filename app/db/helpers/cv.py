from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstCv
from ...schemas.raw import MstCv


def get_all_cvs(conn: Connection) -> list[MstCv]:  # pragma: no cover
    all_cv_stmt = select(mstCv).order_by(mstCv.c.id)
    return [MstCv.from_orm(item) for item in conn.execute(all_cv_stmt).fetchall()]
