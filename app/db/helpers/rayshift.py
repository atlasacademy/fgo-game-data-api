from dataclasses import dataclass
from typing import Any, Optional
from typing import cast as typing_cast

from sqlalchemy import BIGINT, ColumnElement, Integer, Table
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import Join, and_, case, cast, false, func, or_, select
from sqlalchemy.sql._typing import _ColumnExpressionArgument
from sqlalchemy.sql.elements import literal_column
from sqlalchemy.sql.expression import text

from ...core.rayshift import get_quest_enemy_hash
from ...models.rayshift import rayshiftQuest, rayshiftQuestHash
from ...schemas.rayshift import CutInSkill, QuestDetail, QuestDrop, QuestList
from .utils import fetch_one


def quest_select_or(questSelect: list[int]) -> ColumnElement[bool]:
    return or_(
        false(),
        *[
            rayshiftQuest.c.questDetail.contains({"questSelect": questSelectId})
            for questSelectId in questSelect
        ],
    )


async def get_rayshift_quest_db(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
) -> list[QuestDetail]:
    where_conds = [
        rayshiftQuest.c.questId == quest_id,
        rayshiftQuest.c.phase == phase,
        rayshiftQuest.c.questDetail.isnot(None),
    ]

    order_by = [rayshiftQuest.c.queryId.desc()]

    if questHash:
        where_conds.append(rayshiftQuestHash.c.questHash == questHash)
    else:
        order_by = [rayshiftQuestHash.c.questHash.desc(), *order_by]

    if questSelect:
        where_conds.append(quest_select_or(questSelect))

    stmt = (
        select(rayshiftQuest.c.questDetail)
        .select_from(
            rayshiftQuest.join(
                rayshiftQuestHash,
                rayshiftQuest.c.queryId == rayshiftQuestHash.c.queryId,
            )
        )
        .where(and_(*where_conds))
    )

    stmt = stmt.order_by(*order_by)

    rayshift_quest = await fetch_one(conn, stmt)
    if rayshift_quest and rayshift_quest.questDetail:
        return [QuestDetail.parse_obj(rayshift_quest.questDetail)]

    return []


async def get_war_board_quest_details(
    conn: AsyncConnection, quest_id: int, phase: int
) -> list[QuestDetail]:
    stmt = (
        select(rayshiftQuest.c.questDetail)
        .distinct(rayshiftQuestHash.c.questHash)
        .select_from(
            rayshiftQuest.join(
                rayshiftQuestHash,
                rayshiftQuest.c.queryId == rayshiftQuestHash.c.queryId,
            )
        )
        .where(
            and_(
                rayshiftQuest.c.questId == quest_id,
                rayshiftQuest.c.phase == phase,
                rayshiftQuestHash.c.questHash.like("1_01%"),
            )
        )
    )

    res = await conn.execute(stmt)
    return [QuestDetail.parse_obj(row.questDetail) for row in res.fetchall()]


async def get_all_quest_hashes(
    conn: AsyncConnection, quest_id: int, phase: int, questSelect: list[int]
) -> list[str]:
    where_conds = [
        rayshiftQuest.c.questId == quest_id,
        rayshiftQuest.c.phase == phase,
    ]

    if questSelect:
        where_conds.append(quest_select_or(questSelect))

    stmt = (
        select(rayshiftQuestHash.c.questHash.distinct())
        .select_from(
            rayshiftQuestHash.join(
                rayshiftQuest,
                rayshiftQuestHash.c.queryId == rayshiftQuest.c.queryId,
            )
        )
        .where(and_(*where_conds))
        .order_by(rayshiftQuestHash.c.questHash)
    )

    res = await conn.execute(stmt)
    rows = res.fetchall()
    return [str(row.questHash) for row in rows]


@dataclass
class RayshiftSelect:
    select_from: Table | Join
    where_conds: list[_ColumnExpressionArgument[bool]]


def get_rayshift_select(
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
    min_query_id: int | None = None,
) -> RayshiftSelect:
    select_from: Table | Join = rayshiftQuest
    where_conds: list[_ColumnExpressionArgument[bool]] = [
        rayshiftQuest.c.questId == quest_id,
        rayshiftQuest.c.phase == phase,
        rayshiftQuest.c.questDetail.isnot(None),
    ]

    if min_query_id is not None:
        where_conds.append(rayshiftQuest.c.queryId >= min_query_id)
    if questHash:
        select_from = select_from.join(
            rayshiftQuestHash, rayshiftQuest.c.queryId == rayshiftQuestHash.c.queryId
        )
        where_conds.append(rayshiftQuestHash.c.questHash == questHash)
    if questSelect:
        where_conds.append(quest_select_or(questSelect))

    return RayshiftSelect(select_from=select_from, where_conds=where_conds)


async def get_rayshift_drops(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
    min_query_id: int | None = None,
) -> list[QuestDrop]:
    select_detail = get_rayshift_select(
        quest_id=quest_id,
        phase=phase,
        questSelect=questSelect,
        questHash=questHash,
        min_query_id=min_query_id,
    )
    select_from = select_detail.select_from
    where_conds = select_detail.where_conds

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
            select_from,
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
            select_from,
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
            func.jsonb_array_elements(
                literal_column("deck_svt.deck_svt->'dropInfos'"), type_=JSONB
            ).label("drops"),
        )
        .where(literal_column("deck_svt.deck_svt->'dropInfos' != 'null'::JSONB"))
        .cte(name="drops")
    )

    all_drops = (
        select(
            drops.c.queryId,
            drops.c.stage,
            drops.c.deckType,
            cast(drops.c.deckId, Integer).label("deckId"),
            drops.c.drops["type"].label("type"),
            drops.c.drops["objectId"].label("objectId"),
            drops.c.drops["originalNum"].label("originalNum"),
        )
        .where(drops.c.drops["isRateUp"] != literal_column("'true'::JSONB"))
        .cte(name="all_drops")
    )

    run_enemy_drop_items = (
        select(
            all_drops.c.queryId,
            all_drops.c.stage,
            all_drops.c.deckType,
            all_drops.c.deckId,
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
        .select_from(select_from)
        .where(and_(*where_conds))
        .subquery()
        .select()
    )

    individual_enemy_drops = (
        select(
            run_enemy_drop_items.c.stage,
            run_enemy_drop_items.c.deckType,
            run_enemy_drop_items.c.deckId,
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
            run_enemy_drop_items.c.type,
            run_enemy_drop_items.c.objectId,
            run_enemy_drop_items.c.originalNum,
        )
        .order_by(
            run_enemy_drop_items.c.stage,
            run_enemy_drop_items.c.deckType,
            run_enemy_drop_items.c.deckId,
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


async def quest_has_cutins(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
    min_query_id: int | None = None,
) -> int | None:
    select_detail = get_rayshift_select(
        quest_id=quest_id,
        phase=phase,
        questSelect=questSelect,
        questHash=questHash,
        min_query_id=min_query_id,
    )

    stmt = (
        select(func.count(rayshiftQuest.c.queryId).label("query_count"))
        .select_from(select_detail.select_from)
        .where(
            and_(
                *select_detail.where_conds,
                rayshiftQuest.c.questDetail["stageCutins"].is_not(None),
                rayshiftQuest.c.questDetail["stageCutins"]
                != literal_column("'null'::jsonb"),
                func.jsonb_array_length(rayshiftQuest.c.questDetail["stageCutins"]) > 0,
            )
        )
    )

    row = (await conn.execute(stmt)).fetchone()
    if row:
        return int(row.query_count)
    else:
        return False


async def get_cutin_skills(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
    min_query_id: int | None = None,
) -> list[CutInSkill]:
    select_detail = get_rayshift_select(
        quest_id=quest_id,
        phase=phase,
        questSelect=questSelect,
        questHash=questHash,
        min_query_id=min_query_id,
    )

    cutins = (
        select(
            cast(
                func.jsonb_array_elements(rayshiftQuest.c.questDetail["stageCutins"]),
                JSONB,
            ).label("stage_cutin")
        )
        .select_from(select_detail.select_from)
        .where(and_(*select_detail.where_conds))
        .cte(name="cutins")
    )

    skill_list = (
        select(
            cast(cutins.c.stage_cutin["wave"], Integer).label("stage"),
            cast(cutins.c.stage_cutin["skillId"], Integer).label("skill_id"),
        )
        .select_from(cutins)
        .cte(name="skill_list")
    )

    stmt = (
        select(
            skill_list.c.stage,
            skill_list.c.skill_id,
            func.count(skill_list.c.stage).label("appear_count"),
        )
        .select_from(skill_list)
        .group_by(skill_list.c.stage, skill_list.c.skill_id)
        .order_by(skill_list.c.stage, skill_list.c.skill_id)
    )

    rows = (await conn.execute(stmt)).fetchall()
    return [CutInSkill.from_orm(row) for row in rows]


async def get_cutin_drops(
    conn: AsyncConnection,
    quest_id: int,
    phase: int,
    questSelect: list[int],
    questHash: str | None = None,
    min_query_id: int | None = None,
    runs: int | None = None,
) -> list[QuestDrop]:
    select_detail = get_rayshift_select(
        quest_id=quest_id,
        phase=phase,
        questSelect=questSelect,
        questHash=questHash,
        min_query_id=min_query_id,
    )

    cutins = (
        select(
            rayshiftQuest.c.queryId,
            cast(
                func.jsonb_array_elements(rayshiftQuest.c.questDetail["stageCutins"]),
                JSONB,
            ).label("stage_cutin"),
        )
        .select_from(select_detail.select_from)
        .where(and_(*select_detail.where_conds))
        .cte(name="cutins")
    )

    drops = (
        select(
            cutins.c.queryId,
            cast(cutins.c.stage_cutin["wave"], Integer).label("stage"),
            cast(
                func.jsonb_array_elements(cutins.c.stage_cutin["dropInfos"]), JSONB
            ).label("drops"),
        )
        .select_from(cutins)
        .cte(name="drop_infos")
    )

    all_drops = select(
        drops.c.queryId,
        drops.c.stage,
        drops.c.drops["type"].label("type"),
        drops.c.drops["objectId"].label("objectId"),
        drops.c.drops["originalNum"].label("originalNum"),
    ).cte(name="all_drops")

    run_drop_items = (
        select(
            all_drops.c.queryId,
            all_drops.c.stage,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
            func.count(all_drops.c.objectId).label("dropCount"),
        )
        .group_by(
            all_drops.c.queryId,
            all_drops.c.stage,
            all_drops.c.type,
            all_drops.c.objectId,
            all_drops.c.originalNum,
        )
        .cte(name="run_drop_items")
    )

    run_drops = (
        select(
            run_drop_items.c.stage,
            literal_column("'enemy'").label("deckType"),
            literal_column("-2").label("deckId"),
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
            literal_column(f"{runs if runs else -2}").label("runs"),
            func.sum(run_drop_items.c.dropCount).label("dropCount"),
            cast(func.sum(func.power(run_drop_items.c.dropCount, 2)), BIGINT).label(
                "sumDropCountSquared"
            ),
        )
        .group_by(
            run_drop_items.c.stage,
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
        )
        .order_by(
            run_drop_items.c.stage,
            run_drop_items.c.type,
            run_drop_items.c.objectId,
            run_drop_items.c.originalNum,
        )
    )

    rows = (await conn.execute(run_drops)).fetchall()
    return [QuestDrop.from_orm(row) for row in rows]


insert_quest_stmt = insert(rayshiftQuest)
do_update_quest_stmt = insert_quest_stmt.on_conflict_do_update(
    index_elements=[rayshiftQuest.c.queryId],
    set_={rayshiftQuest.c.questDetail: insert_quest_stmt.excluded.questDetail},
)


def get_insert_rayshift_quest_data(
    quest_details: dict[int, QuestDetail],
) -> list[dict[str, Any]]:
    data = []
    for query_id, quest_detail in quest_details.items():
        quest_detail_dict = quest_detail.model_dump(mode="json")
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


def get_insert_rayshift_quest_hash_data(
    quest_details: dict[int, QuestDetail],
) -> list[dict[str, Any]]:
    return [
        {
            "queryId": queryId,
            "questHash": get_quest_enemy_hash(1, quest_detail),
        }
        for queryId, quest_detail in quest_details.items()
    ]


insert_quest_hash_stmt = insert(rayshiftQuestHash)
do_update_quest_hash_stmt = insert_quest_hash_stmt.on_conflict_do_update(
    index_elements=[rayshiftQuestHash.c.queryId],
    set_={rayshiftQuestHash.c.questHash: insert_quest_hash_stmt.excluded.questHash},
)


async def insert_rayshift_quest_hash_db(
    conn: AsyncConnection, quest_details: dict[int, QuestDetail]
) -> None:
    data = get_insert_rayshift_quest_hash_data(quest_details)
    await conn.execute(do_update_quest_hash_stmt, data)


def insert_rayshift_quest_hash_db_sync(
    conn: Connection, quest_details: dict[int, QuestDetail]
) -> None:
    data = get_insert_rayshift_quest_hash_data(quest_details)
    conn.execute(do_update_quest_hash_stmt, data)


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


def fetch_missing_enemy_hash(
    conn: Connection, limit: int = 100
) -> dict[int, QuestDetail]:
    stmt = (
        select(rayshiftQuest.c.queryId, rayshiftQuest.c.questDetail)
        .select_from(
            rayshiftQuest.join(
                rayshiftQuestHash,
                rayshiftQuest.c.queryId == rayshiftQuestHash.c.queryId,
                isouter=True,
            )
        )
        .where(
            and_(
                rayshiftQuestHash.c.questHash.is_(None),
                rayshiftQuest.c.questDetail.is_not(None),
            )
        )
        .limit(limit)
    )

    return typing_cast(
        dict[int, QuestDetail],
        {
            row.queryId: QuestDetail.parse_obj(row.questDetail)
            for row in conn.execute(stmt).fetchall()
        },
    )
