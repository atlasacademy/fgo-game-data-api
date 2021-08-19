from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import func, literal_column, select

from ...models.raw import ScriptFileList
from ...schemas.raw import ScriptSearchResult


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
