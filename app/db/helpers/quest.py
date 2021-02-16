from typing import Iterable, List, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, func, select

from ...models.raw import (
    mstQuest,
    mstQuestConsumeItem,
    mstQuestPhase,
    mstQuestRelease,
    mstStage,
)
from ...schemas.raw import QuestEntity, QuestPhaseEntity
from .utils import sql_jsonb_agg


JOINED_QUEST_TABLES = (
    mstQuest.outerjoin(
        mstQuestConsumeItem, mstQuestConsumeItem.c.questId == mstQuest.c.id
    )
    .outerjoin(mstQuestRelease, mstQuestRelease.c.questId == mstQuest.c.id)
    .outerjoin(mstQuestPhase, mstQuestPhase.c.questId == mstQuest.c.id)
)


SELECT_QUEST_ENTITY = [
    func.to_jsonb(mstQuest.table_valued()).label(mstQuest.name),
    sql_jsonb_agg(mstQuestConsumeItem),
    sql_jsonb_agg(mstQuestRelease),
    func.jsonb_agg(mstQuestPhase.c.phase.distinct()).label("phases"),
]


def get_quest_entity(conn: Connection, quest_ids: Iterable[int]) -> List[QuestEntity]:
    stmt = (
        select(*SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_TABLES)
        .where(mstQuest.c.id.in_(quest_ids))
        .group_by(mstQuest.c.id)
    )
    return [QuestEntity.from_orm(quest) for quest in conn.execute(stmt).fetchall()]


def get_quest_by_spot(conn: Connection, spot_ids: Iterable[int]) -> List[QuestEntity]:
    stmt = (
        select(*SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_TABLES)
        .where(mstQuest.c.spotId.in_(tuple(spot_ids)))
        .group_by(mstQuest.c.id)
    )
    return [QuestEntity.from_orm(quest) for quest in conn.execute(stmt).fetchall()]


def get_quest_phase_entity(
    conn: Connection, quest_id: int, phase_id: int
) -> Optional[QuestPhaseEntity]:
    all_phases_cte = (
        select(
            mstQuestPhase.c.questId,
            func.jsonb_agg(mstQuestPhase.c.phase).label("phases"),
        )
        .where(mstQuestPhase.c.questId == quest_id)
        .group_by(mstQuestPhase.c.questId)
        .cte()
    )

    joined_quest_phase_tables = JOINED_QUEST_TABLES.outerjoin(
        all_phases_cte, mstQuest.c.id == all_phases_cte.c.questId
    ).outerjoin(
        mstStage,
        and_(
            mstQuest.c.id == mstStage.c.questId,
            mstQuestPhase.c.phase == mstStage.c.questPhase,
        ),
    )

    select_quest_phase = [
        func.to_jsonb(mstQuest.table_valued()).label(mstQuest.name),
        sql_jsonb_agg(mstQuestConsumeItem),
        sql_jsonb_agg(mstQuestRelease),
        all_phases_cte.c.phases,
        func.to_jsonb(mstQuestPhase.table_valued()).label(mstQuestPhase.name),
        sql_jsonb_agg(mstStage),
    ]

    sql_stmt = (
        select(*select_quest_phase)
        .select_from(joined_quest_phase_tables)
        .where(and_(mstQuest.c.id == quest_id, mstQuestPhase.c.phase == phase_id))
        .group_by(
            mstQuest.table_valued(),
            mstQuestPhase.table_valued(),
            all_phases_cte.c.phases,
        )
    )

    quest_phase = conn.execute(sql_stmt).fetchone()
    if quest_phase:
        return QuestPhaseEntity.from_orm(quest_phase)

    return None
