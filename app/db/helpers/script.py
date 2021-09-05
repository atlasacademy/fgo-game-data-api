from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import func, literal_column, select

from ...models.raw import ScriptFileList
from ...schemas.raw import ScriptEntity, ScriptSearchResult
from .quest import get_quest_entity


async def get_script(conn: AsyncConnection, script_id: str) -> Optional[ScriptEntity]:
    stmt = select(
        ScriptFileList.c.scriptFileName,
        func.octet_length(ScriptFileList.c.rawScript).label("scriptSizeBytes"),
        ScriptFileList.c.questId,
    ).where(ScriptFileList.c.scriptFileName == script_id)

    rows = (await conn.execute(stmt)).fetchall()

    if len(rows) == 0:
        return None

    quest_ids: list[int] = [row.questId for row in rows]
    quests = await get_quest_entity(conn, quest_ids)

    return ScriptEntity(
        scriptId=script_id, scriptSizeBytes=rows[0].scriptSizeBytes, quests=quests
    )


async def get_script_search(
    conn: AsyncConnection, search_query: str, limit_result: int = 50
) -> list[ScriptSearchResult]:
    score = func.pgroonga_score(literal_column("tableoid"), literal_column("ctid"))
    snippets = func.pgroonga_snippet_html(
        ScriptFileList.c.textScript, func.pgroonga_query_extract_keywords(search_query)
    )
    stmt = (
        select(
            ScriptFileList.c.scriptFileName.distinct().label("scriptId"),
            score.label("score"),
            snippets.label("snippets"),
        )
        .where(ScriptFileList.c.textScript.op("&@~")(search_query))
        .order_by(score.desc())
        .limit(limit_result)
    )
    return [
        ScriptSearchResult.from_orm(result)
        for result in (await conn.execute(stmt)).fetchall()
    ]
