from sqlalchemy.engine import Connection
from sqlalchemy.sql import select

from ...models.raw import mstIllustrator
from ...schemas.raw import MstIllustrator


def get_all_illustrators(conn: Connection) -> list[MstIllustrator]:  # pragma: no cover
    all_illustrator_stmt = select(mstIllustrator).order_by(mstIllustrator.c.id)
    return [
        MstIllustrator.from_orm(item)
        for item in conn.execute(all_illustrator_stmt).fetchall()
    ]
