from typing import Any, Optional

from sqlalchemy import BIGINT, Integer
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, case, cast, func, select
from sqlalchemy.sql.elements import literal_column
from sqlalchemy.sql.expression import text

from ...models.rayshift import rayshiftQuest
from ...schemas.rayshift import QuestDetail, QuestDrop, QuestList
from .utils import fetch_one


async def get_rayshift_quest_db(
    conn: AsyncConnection, quest_id: int, phase: int, questSelect: int | None = None
) -> Optional[QuestDetail]:
    where_conds = [
        rayshiftQuest.c.questId == quest_id,
        rayshiftQuest.c.phase == phase,
        rayshiftQuest.c.questDetail.isnot(None),
    ]
    if questSelect is not None:
        where_conds.append(
            rayshiftQuest.c.questDetail.contains({"questSelect": questSelect})
        )
    stmt = (
        select(rayshiftQuest.c.questDetail)
        .where(and_(*where_conds))
        .order_by(rayshiftQuest.c.queryId.desc())
        .limit(1)
    )
    rayshift_quest = await fetch_one(conn, stmt)
    if rayshift_quest and rayshift_quest.questDetail:
        return QuestDetail.parse_obj(rayshift_quest.questDetail)

    return None


async def get_rayshift_drops(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    min_query_id: int | None = None,
) -> list[QuestDrop]:
    where_conds = [
        rayshiftQuest.c.questId == quest_id,
        rayshiftQuest.c.phase == phase,
        rayshiftQuest.c.questDetail.isnot(None),
    ]
    if questSelect is not None:
        where_conds.append(
            rayshiftQuest.c.questDetail.contains({"questSelect": questSelect})
        )
    if min_query_id is not None:
        where_conds.append(rayshiftQuest.c.queryId >= min_query_id)

    enemy_deck_svt = (
        select(
            rayshiftQuest.c.queryId,
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
        .where(and_(*where_conds))
    )

    shift_deck_svt = (
        select(
            rayshiftQuest.c.queryId,
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
        .where(and_(*where_conds))
    )

    deck_svt = enemy_deck_svt.union_all(shift_deck_svt).cte(name="deck_svt")

    drops = (
        select(
            deck_svt.c.queryId,
            deck_svt.c.deckType,
            deck_svt.c.stage,
            literal_column("deck_svt.deck_svt->>'id'").label("deckId"),
            literal_column("deck_svt.deck_svt->>'npcId'").label("npcId"),
            func.jsonb_array_elements(
                literal_column("deck_svt.deck_svt->'dropInfos'"), type_=JSONB
            ).label("drops"),
        )
        .where(literal_column("deck_svt.deck_svt->'dropInfos' != 'null'::JSONB"))
        .cte(name="drops")
    )

    all_drops = select(
        drops.c.queryId,
        drops.c.stage,
        drops.c.deckType,
        cast(drops.c.deckId, Integer).label("deckId"),
        cast(drops.c.npcId, Integer).label("npcId"),
        drops.c.drops["type"].label("type"),
        drops.c.drops["objectId"].label("objectId"),
        drops.c.drops["originalNum"].label("originalNum"),
    ).cte(name="all_drops")

    run_enemy_drop_items = (
        select(
            all_drops.c.queryId,
            all_drops.c.stage,
            all_drops.c.deckType,
            all_drops.c.deckId,
            all_drops.c.npcId,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
            func.count(all_drops.c.objectId).label("dropCount"),
        )
        .group_by(
            all_drops.c.queryId,
            all_drops.c.stage,
            all_drops.c.deckType,
            all_drops.c.deckId,
            all_drops.c.npcId,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
        )
        .cte(name="run_enemy_drop_items")
    )

    run_drop_items = (
        select(
            all_drops.c.queryId,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
            func.count(all_drops.c.objectId).label("dropCount"),
        )
        .group_by(
            all_drops.c.queryId,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
        )
        .cte(name="run_drop_items")
    )

    runs = (
        select(func.count(rayshiftQuest.c.queryId))
        .where(and_(*where_conds))
        .subquery()
        .select()
    )

    individual_enemy_drops = (
        select(
            run_enemy_drop_items.c.stage,
            run_enemy_drop_items.c.deckType,
            run_enemy_drop_items.c.deckId,
            run_enemy_drop_items.c.npcId,
            run_enemy_drop_items.c.type,
            run_enemy_drop_items.c.objectId,
            run_enemy_drop_items.c.originalNum,
            runs.label("runs"),
            func.sum(run_enemy_drop_items.c.dropCount).label("dropCount"),
            cast(
                func.sum(func.power(run_enemy_drop_items.c.dropCount, 2)), BIGINT
            ).label("sumDropCountSquared"),
        )
        .group_by(
            run_enemy_drop_items.c.stage,
            run_enemy_drop_items.c.deckType,
            run_enemy_drop_items.c.deckId,
            run_enemy_drop_items.c.npcId,
            run_enemy_drop_items.c.type,
            run_enemy_drop_items.c.objectId,
            run_enemy_drop_items.c.originalNum,
        )
        .order_by(
            run_enemy_drop_items.c.stage,
            run_enemy_drop_items.c.deckType,
            run_enemy_drop_items.c.deckId,
            run_enemy_drop_items.c.npcId,
            run_enemy_drop_items.c.type,
            run_enemy_drop_items.c.objectId,
            run_enemy_drop_items.c.originalNum,
        )
    )

    run_drops = (
        select(
            literal_column("-1").label("stage"),
            literal_column("'enemy'").label("deckType"),
            literal_column("-1").label("deckId"),
            literal_column("-1").label("npcId"),
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
            runs.label("runs"),
            func.sum(run_drop_items.c.dropCount).label("dropCount"),
            cast(func.sum(func.power(run_drop_items.c.dropCount, 2)), BIGINT).label(
                "sumDropCountSquared"
            ),
        )
        .group_by(
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
        )
        .order_by(
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
        )
    )

    stmt = individual_enemy_drops.union_all(run_drops)

    results = await conn.execute(stmt)
    return [QuestDrop.from_orm(row) for row in results.fetchall()]


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


def fetch_missing_quest_ids(
    conn: Connection, quest_ids: Optional[list[int]] = None
) -> list[int]:
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
    if quest_ids:
        stmt = select(count_values.c.queryId).where(
            and_(count_values.c.data_count == 0, count_values.c.questId.in_(quest_ids))
        )
    else:
        stmt = select(count_values.c.queryId).where(count_values.c.data_count == 0)
    return [row.queryId for row in conn.execute(stmt).fetchall()]


def fetch_all_missing_quest_ids(
    conn: Connection, quest_ids: Optional[list[int]] = None
) -> list[int]:
    if quest_ids:
        stmt = select(rayshiftQuest.c.queryId).where(
            and_(
                rayshiftQuest.c.questDetail.is_(None),
                rayshiftQuest.c.questId.in_(quest_ids),
            )
        )
    else:
        stmt = select(rayshiftQuest.c.queryId).where(
            rayshiftQuest.c.questDetail.is_(None)
        )
    return [row.queryId for row in conn.execute(stmt).fetchall()]
