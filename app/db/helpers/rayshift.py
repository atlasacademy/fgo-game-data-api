from typing import Any, Optional

from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, case, func, select
from sqlalchemy.sql.elements import literal_column
from sqlalchemy.sql.expression import text

from ...models.rayshift import rayshiftQuest
from ...schemas.rayshift import QuestDetail, QuestDrop, QuestList


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


async def get_rayshift_drops(
    conn: AsyncConnection, quest_id: int, phase: int
) -> list[QuestDrop]:
    enemy_deck_svt = (
        select(
            literal_column("'enemy'").label("deckType"),
            func.jsonb_array_elements(literal_column("d.deck->'svts'")).label(
                "deck_svt"
            ),
            literal_column("d.stage").label("stage"),
        )
        .select_from(
            rayshiftQuest,
            text(
                'jsonb_array_elements("rayshiftQuest"."questDetail"->\'enemyDeck\') '
                "with ordinality as d(deck, stage)"
            ),
        )
        .where(
            and_(
                rayshiftQuest.c.questId == quest_id,
                rayshiftQuest.c.phase == phase,
                rayshiftQuest.c.questDetail.is_not(None),
            )
        )
    )

    shift_deck_svt = (
        select(
            literal_column("'shift'").label("deckType"),
            func.jsonb_array_elements(literal_column("d.deck->'svts'")).label(
                "deck_svt"
            ),
            literal_column("d.stage").label("stage"),
        )
        .select_from(
            rayshiftQuest,
            text(
                'jsonb_array_elements("rayshiftQuest"."questDetail"->\'shiftDeck\') '
                "with ordinality as d(deck, stage)"
            ),
        )
        .where(
            and_(
                rayshiftQuest.c.questId == quest_id,
                rayshiftQuest.c.phase == phase,
                rayshiftQuest.c.questDetail.is_not(None),
            )
        )
    )

    deck_svt = enemy_deck_svt.union_all(shift_deck_svt).cte(name="deck_svt")

    drops = select(
        deck_svt.c.deckType,
        deck_svt.c.stage,
        literal_column("deck_svt.deck_svt->>'id'").label("deckId"),
        func.jsonb_array_elements(
            literal_column("deck_svt.deck_svt->'dropInfos'"), type_=JSONB
        ).label("drops"),
    ).cte(name="drops")

    drop_items = select(
        drops.c.stage,
        drops.c.deckType,
        drops.c.deckId,
        drops.c.drops["type"].label("type"),
        drops.c.drops["objectId"].label("objectId"),
        drops.c.drops["originalNum"].label("originalNum"),
    ).cte(name="drop_items")

    runs = (
        select(func.count(rayshiftQuest.c.queryId))
        .where(
            and_(
                rayshiftQuest.c.questId == quest_id,
                rayshiftQuest.c.phase == phase,
                rayshiftQuest.c.questDetail.is_not(None),
            )
        )
        .subquery()
        .select()
    )

    stmt = select(
        drop_items.c.stage,
        drop_items.c.deckType,
        drop_items.c.deckId,
        drop_items.c.type,
        drop_items.c.objectId,
        drop_items.c.originalNum,
        func.count(drop_items.c.objectId).label("dropCount"),
        runs.label("runs"),
    ).group_by(
        drop_items.c.stage,
        drop_items.c.deckType,
        drop_items.c.deckId,
        drop_items.c.type,
        drop_items.c.objectId,
        drop_items.c.originalNum,
    )

    results = await conn.execute(stmt)
    return [QuestDrop.parse_obj(row) for row in results.fetchall()]


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
    await conn.execute(do_update_quest_stmt, data)


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


def fetch_all_missing_quest_ids(conn: Connection) -> list[int]:
    stmt = select(rayshiftQuest.c.queryId).where(rayshiftQuest.c.questDetail.is_(None))
    return [row.queryId for row in conn.execute(stmt).fetchall()]
