from typing import Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, select

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


async def insert_rayshift_quest_db(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    quest_details: dict[int, QuestDetail],
) -> None:
    insert_stmt = insert(rayshiftQuest)
    do_update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[rayshiftQuest.c.queryId],
        set_={rayshiftQuest.c.questDetail: insert_stmt.excluded.questDetail},
    )
    data = []
    for query_id, quest_detail in quest_details.items():
        quest_detail_dict = quest_detail.dict()
        quest_detail_dict["addedTime"] = quest_detail.addedTime.isoformat()
        data.append(
            {
                "queryId": query_id,
                "questId": quest_id,
                "phase": phase,
                "questDetail": quest_detail_dict,
            }
        )
    await conn.execute(do_update_stmt, data)


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
