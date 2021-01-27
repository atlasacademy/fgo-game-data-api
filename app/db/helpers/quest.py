from inspect import cleandoc
from typing import Any, Iterable, List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import func, literal_column, select, text

from ...models.raw import mstQuest, mstQuestConsumeItem, mstQuestPhase, mstQuestRelease
from ...schemas.raw import QuestEntity
from .utils import sql_jsonb_agg


JOINED_QUEST_TABLES = (
    mstQuest.join(
        mstQuestConsumeItem,
        mstQuestConsumeItem.c.questId == mstQuest.c.id,
        isouter=True,
    )
    .join(
        mstQuestRelease,
        mstQuestRelease.c.questId == mstQuest.c.id,
        isouter=True,
    )
    .join(
        mstQuestPhase,
        mstQuestPhase.c.questId == mstQuest.c.id,
        isouter=True,
    )
)


SELECT_QUEST_ENTITY = [
    func.to_jsonb(literal_column('"mstQuest"')).label("mstQuest"),
    sql_jsonb_agg(mstQuestConsumeItem),
    sql_jsonb_agg(mstQuestRelease),
    func.jsonb_agg(mstQuestPhase.c.phase.distinct()).label("phases"),
]


def get_quest_entity(conn: Connection, quest_ids: Iterable[int]) -> List[QuestEntity]:
    stmt = (
        select(SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_TABLES)
        .where(mstQuest.c.id.in_(quest_ids))
        .group_by(mstQuest.c.id)
    )
    return [QuestEntity.parse_obj(quest) for quest in conn.execute(stmt).fetchall()]


def get_quest_by_spot(conn: Connection, spot_ids: Iterable[int]) -> List[QuestEntity]:
    stmt = (
        select(SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_TABLES)
        .where(mstQuest.c.spotId.in_(spot_ids))
        .group_by(mstQuest.c.id)
    )
    return [
        QuestEntity.parse_obj(quest)
        for quest in conn.execute(stmt, spotIds=tuple(spot_ids)).fetchall()
    ]


def get_quest_phase_entity(conn: Connection, quest_id: int, phase_id: int) -> Any:
    stmt = text(
        cleandoc(
            """
            SELECT
            TO_JSONB("mstQuest") as "mstQuest",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestConsumeItem"), NULL)) AS "mstQuestConsumeItem",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestRelease"), NULL)) AS "mstQuestRelease",
            JSONB_AGG(DISTINCT "allPhases"."phase") AS "phases",
            TO_JSONB("mstQuestPhase") AS "mstQuestPhase",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstStage"), NULL)) AS "mstStage"
            FROM "mstQuestPhase" AS "allPhases",
            "mstQuest"
            LEFT JOIN "mstQuestConsumeItem" ON "mstQuestConsumeItem"."questId"="mstQuest"."id"
            LEFT JOIN "mstQuestRelease" ON "mstQuestRelease"."questId"="mstQuest"."id"
            JOIN "mstQuestPhase" ON "mstQuestPhase"."questId"="mstQuest"."id"
            LEFT JOIN "mstStage"
            ON "mstStage"."questId"="mstQuest"."id"
            AND  "mstStage"."questPhase"="mstQuestPhase"."phase"
            WHERE "allPhases"."questId"=:questId
            AND "mstQuest"."id"=:questId
            AND "mstQuestPhase"."phase"=:phaseId
            GROUP BY "mstQuest".*, "mstQuestPhase".*
            """
        )
    )
    return conn.execute(stmt, questId=quest_id, phaseId=phase_id).fetchone()
