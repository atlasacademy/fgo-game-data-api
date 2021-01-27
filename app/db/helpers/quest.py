from inspect import cleandoc
from typing import Any, List

from sqlalchemy.engine import Connection
from sqlalchemy.sql import text

from ...schemas.raw import QuestEntity


def get_quest_entity(conn: Connection, quest_ids: List[int]) -> List[QuestEntity]:
    stmt = text(
        cleandoc(
            """
            SELECT
            TO_JSONB("mstQuest") as "mstQuest",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestConsumeItem"), NULL)) AS "mstQuestConsumeItem",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestRelease"), NULL)) AS "mstQuestRelease",
            JSONB_AGG(DISTINCT "mstQuestPhase"."phase") AS "phases"
            FROM "mstQuest"
            LEFT JOIN "mstQuestConsumeItem" ON "mstQuestConsumeItem"."questId"="mstQuest"."id"
            LEFT JOIN "mstQuestRelease" ON "mstQuestRelease"."questId"="mstQuest"."id"
            LEFT JOIN "mstQuestPhase" ON "mstQuestPhase"."questId"="mstQuest"."id"
            WHERE "mstQuest"."id"=ANY(:questIds)
            GROUP BY "mstQuest"."id"
            """
        )
    )
    return [
        QuestEntity.parse_obj(quest)
        for quest in conn.execute(stmt, questIds=quest_ids).fetchall()
    ]


def get_quest_by_spot(conn: Connection, spot_ids: List[int]) -> List[QuestEntity]:
    stmt = text(
        cleandoc(
            """
            SELECT
            TO_JSONB("mstQuest") as "mstQuest",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestConsumeItem"), NULL)) AS "mstQuestConsumeItem",
            TO_JSONB(ARRAY_REMOVE(ARRAY_AGG(DISTINCT "mstQuestRelease"), NULL)) AS "mstQuestRelease",
            JSONB_AGG(DISTINCT "mstQuestPhase"."phase") AS "phases"
            FROM "mstQuest"
            LEFT JOIN "mstQuestConsumeItem" ON "mstQuestConsumeItem"."questId"="mstQuest"."id"
            LEFT JOIN "mstQuestRelease" ON "mstQuestRelease"."questId"="mstQuest"."id"
            LEFT JOIN "mstQuestPhase" ON "mstQuestPhase"."questId"="mstQuest"."id"
            WHERE "mstQuest"."spotId"=ANY(:spotIds)
            GROUP BY "mstQuest"."id"
            """
        )
    )
    return [
        QuestEntity.parse_obj(quest)
        for quest in conn.execute(stmt, spotIds=spot_ids).fetchall()
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
