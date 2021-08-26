from typing import Any, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, case, func, select

from ...models.rayshift import rayshiftQuest
from ...schemas.rayshift import QuestDetail, QuestList


async def get_rayshift_quest_db(
    conn: AsyncConnection, quest_id: int, phase: int
) -> Optional[QuestDetail]:
    stmt = select(rayshiftQuest.c.questDetail).where(
        and_(
            rayshiftQuest.c.questId == quest_id,
            rayshiftQuest.c.phase == phase,
            rayshiftQuest.c.questDetail.isnot(None),
        )
    )
    rayshift_quest = (await conn.execute(stmt)).fetchone()
    if rayshift_quest and rayshift_quest.questDetail:
        return QuestDetail.parse_obj(rayshift_quest.questDetail)

    return None


insert_quest_stmt = insert(rayshiftQuest)
do_update_quest_stmt = insert_quest_stmt.on_conflict_do_update(
    index_elements=[rayshiftQuest.c.queryId],
    set_={rayshiftQuest.c.questDetail: insert_quest_stmt.excluded.questDetail},
)


def get_insert_rayshift_quest_data(
    quest_details: dict[int, QuestDetail]
) -> list[dict[str, Any]]:
    data = []
    for query_id, quest_detail in quest_details.items():
        quest_detail_dict = quest_detail.dict()
        quest_detail_dict["addedTime"] = quest_detail.addedTime.isoformat()
        data.append(
            {
                "queryId": query_id,
                "questId": quest_detail.questId,
                "phase": quest_detail.questPhase,
                "questDetail": quest_detail_dict,
            }
        )
    return data


async def insert_rayshift_quest_db(
    conn: AsyncConnection, quest_details: dict[int, QuestDetail]
) -> None:
    data = get_insert_rayshift_quest_data(quest_details)
    await conn.execute(do_update_quest_stmt, data)  # type: ignore


def insert_rayshift_quest_db_sync(
    conn: Connection, quest_details: dict[int, QuestDetail]
) -> None:
    data = get_insert_rayshift_quest_data(quest_details)
    conn.execute(do_update_quest_stmt, data)


def insert_rayshift_quest_list(conn: Connection, quest_list: list[QuestList]) -> None:
    insert_stmt = insert(rayshiftQuest)
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(
        index_elements=[rayshiftQuest.c.queryId]
    )
    data = []
    for quest in quest_list:
        for query_id in quest.queryIds:
            data.append(
                {
                    "queryId": query_id,
                    "questId": quest.questId,
                    "phase": quest.questPhase,
                }
            )
    conn.execute(do_nothing_stmt, data)


def fetch_missing_quest_ids(conn: Connection) -> list[int]:
    count_values = (
        select(
            rayshiftQuest.c.questId,
            rayshiftQuest.c.phase,
            func.sum(case((rayshiftQuest.c.questDetail.is_(None), 0), else_=1)).label(
                "data_count"
            ),
            func.max(rayshiftQuest.c.queryId).label("queryId"),
        )
        .group_by(rayshiftQuest.c.questId, rayshiftQuest.c.phase)
        .cte()
    )
    stmt = select(count_values.c.queryId).where(count_values.c.data_count == 0)
    return [row.queryId for row in conn.execute(stmt).fetchall()]
