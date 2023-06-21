from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, func, literal_column, select
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import ScriptFileList, mstMap, mstQuest, mstSpot, mstWar
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

    quest_ids: list[int] = [row.questId for row in rows if row.questId != -1]
    if quest_ids:
        quests = await get_quest_entity(conn, quest_ids)
    else:
        quests = []

    return ScriptEntity(
        scriptId=script_id, scriptSizeBytes=rows[0].scriptSizeBytes, quests=quests
    )


async def get_script_search(
    conn: AsyncConnection,
    search_query: str,
    script_file_name: str | None = None,
    raw_script: bool | None = None,
    war_ids: Iterable[int] | None = None,
    limit_result: int = 50,
) -> list[ScriptSearchResult]:
    if raw_script:
        search_field = ScriptFileList.c.rawScript
    else:
        search_field = ScriptFileList.c.textScript

    where_conds: list[_ColumnExpressionArgument[bool]] = [
        search_field.op("&@~")(search_query)
    ]

    score = func.pgroonga_score(literal_column("tableoid"), literal_column("ctid"))
    snippets = func.pgroonga_snippet_html(
        search_field, func.pgroonga_query_extract_keywords(search_query)
    )

    if script_file_name:
        where_conds.append(
            ScriptFileList.c.scriptFileName.like(f"%{script_file_name}%")
        )

    if war_ids:
        quest_ids = (
            select(mstQuest.c.id)
            .select_from(
                mstQuest.join(mstSpot, mstSpot.c.id == mstQuest.c.spotId)
                .join(mstMap, mstMap.c.id == mstSpot.c.mapId)
                .join(mstWar, mstWar.c.id == mstMap.c.warId)
            )
            .where(mstWar.c.id.in_(war_ids))
        )
        where_conds.append(ScriptFileList.c.questId.in_(quest_ids))

    stmt = (
        select(
            ScriptFileList.c.scriptFileName.distinct().label("scriptId"),
            score.label("score"),
            snippets.label("snippets"),
        )
        .where(and_(*where_conds))
        .order_by(score.desc())
        .limit(limit_result)
    )
    return [
        ScriptSearchResult.from_orm(result)
        for result in (await conn.execute(stmt)).fetchall()
    ]
