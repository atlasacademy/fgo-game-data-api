from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import select

from ...models.raw import mstBgm


async def search_bgm(conn: AsyncConnection, file_name: str) -> int | None:
    search_stmt = select(mstBgm.c.id).where(mstBgm.c.fileName == file_name)

    res = (await conn.execute(search_stmt)).fetchone()
    if res:
        return res.id  # type: ignore
    else:
        return None
