from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import and_, case, func, or_, select

from ...models.raw import (
    ScriptFileList,
    mstBgm,
    mstClosedMessage,
    mstGift,
    mstMap,
    mstQuest,
    mstQuestConsumeItem,
    mstQuestMessage,
    mstQuestPhase,
    mstQuestPhaseDetail,
    mstQuestRelease,
    mstSpot,
    mstStage,
    mstStageRemap,
    mstWar,
    npcFollower,
    npcFollowerRelease,
    npcSvtEquip,
    npcSvtFollower,
)
from ...models.rayshift import rayshiftQuest
from ...schemas.common import StageLink
from ...schemas.gameenums import QuestFlag
from ...schemas.raw import (
    MstBgm,
    MstQuestWithWar,
    MstStage,
    MstStageRemap,
    QuestEntity,
    QuestPhaseEntity,
)
from .utils import sql_jsonb_agg


QUEST_WITH_WAR_SELECT = select(mstQuest, mstWar.c.id.label("warId")).select_from(
    mstQuest.join(mstSpot, mstSpot.c.id == mstQuest.c.spotId)
    .join(mstMap, mstMap.c.id == mstSpot.c.mapId)
    .join(mstWar, mstWar.c.id == mstMap.c.warId)
)


async def get_one_quest_with_war(
    conn: AsyncConnection, quest_id: int
) -> Optional[MstQuestWithWar]:
    stmt = QUEST_WITH_WAR_SELECT.where(mstQuest.c.id == quest_id)

    mstQuestWar = (await conn.execute(stmt)).fetchone()
    if mstQuestWar:
        return MstQuestWithWar.from_orm(mstQuestWar)

    return None


async def get_many_quests_with_war(
    conn: AsyncConnection, quest_ids: Iterable[int]
) -> list[MstQuestWithWar]:
    stmt = QUEST_WITH_WAR_SELECT.where(mstQuest.c.id.in_(quest_ids))

    return [
        MstQuestWithWar.from_orm(quest)
        for quest in (await conn.execute(stmt)).fetchall()
    ]


JOINED_QUEST_TABLES = (
    mstQuest.outerjoin(
        mstQuestConsumeItem, mstQuestConsumeItem.c.questId == mstQuest.c.id
    )
    .outerjoin(mstQuestRelease, mstQuestRelease.c.questId == mstQuest.c.id)
    .outerjoin(mstQuestPhase, mstQuestPhase.c.questId == mstQuest.c.id)
    .outerjoin(
        mstClosedMessage, mstClosedMessage.c.id == mstQuestRelease.c.closedMessageId
    )
    .outerjoin(rayshiftQuest, rayshiftQuest.c.questId == mstQuest.c.id)
    .outerjoin(mstGift, mstGift.c.id == mstQuest.c.giftId)
)


JOINED_QUEST_ENTITY_TABLES = JOINED_QUEST_TABLES.outerjoin(
    mstQuestPhaseDetail,
    and_(
        mstQuest.c.id == mstQuestPhaseDetail.c.questId,
        mstQuestPhase.c.phase == mstQuestPhaseDetail.c.phase,
    ),
)


phasesWithEnemies = func.to_jsonb(
    func.array_remove(func.array_agg(rayshiftQuest.c.phase.distinct()), None)
).label("phasesWithEnemies")


phasesNoBattle = func.array_remove(
    func.array_agg(
        case(
            (
                mstQuestPhaseDetail.c.flag.op("&")(QuestFlag.NO_BATTLE.value) != 0,  # type: ignore
                mstQuestPhaseDetail.c.phase,
            ),
            (
                and_(
                    mstQuestPhaseDetail.c.flag.is_(None),
                    mstQuest.c.flag.op("&")(QuestFlag.NO_BATTLE.value) != 0,
                ),
                mstQuestPhase.c.phase,
            ),
        ).distinct()
    ),
    None,
).label("phasesNoBattle")


SELECT_QUEST_ENTITY = [
    func.to_jsonb(mstQuest.table_valued()).label(mstQuest.name),
    sql_jsonb_agg(mstQuestConsumeItem),
    sql_jsonb_agg(mstQuestRelease),
    sql_jsonb_agg(mstClosedMessage),
    sql_jsonb_agg(mstGift),
    func.to_jsonb(
        func.array_remove(func.array_agg(mstQuestPhase.c.phase.distinct()), None)
    ).label("phases"),
    phasesWithEnemies,
    phasesNoBattle,
]


async def get_quest_entity(
    conn: AsyncConnection, quest_ids: Iterable[int]
) -> list[QuestEntity]:
    stmt = (
        select(*SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_ENTITY_TABLES)
        .where(mstQuest.c.id.in_(quest_ids))
        .group_by(mstQuest.c.id)
    )
    return [
        QuestEntity.from_orm(quest) for quest in (await conn.execute(stmt)).fetchall()
    ]


async def get_quest_by_spot(
    conn: AsyncConnection, spot_ids: Iterable[int]
) -> list[QuestEntity]:
    stmt = (
        select(*SELECT_QUEST_ENTITY)
        .select_from(JOINED_QUEST_ENTITY_TABLES)
        .where(mstQuest.c.spotId.in_(spot_ids))
        .group_by(mstQuest.c.id)
    )
    return [
        QuestEntity.from_orm(quest) for quest in (await conn.execute(stmt)).fetchall()
    ]


async def get_quest_phase_entity(
    conn: AsyncConnection, quest_id: int, phase_id: int
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

    joined_quest_phase_tables = (
        JOINED_QUEST_TABLES.outerjoin(
            all_phases_cte, mstQuest.c.id == all_phases_cte.c.questId
        )
        .outerjoin(
            mstQuestPhaseDetail,
            and_(
                mstQuest.c.id == mstQuestPhaseDetail.c.questId,
                mstQuestPhase.c.phase == mstQuestPhaseDetail.c.phase,
            ),
        )
        .outerjoin(
            mstQuestMessage,
            and_(
                mstQuest.c.id == mstQuestMessage.c.questId,
                mstQuestPhase.c.phase == mstQuestMessage.c.phase,
            ),
        )
        .outerjoin(
            mstStage,
            and_(
                mstQuest.c.id == mstStage.c.questId,
                mstQuestPhase.c.phase == mstStage.c.questPhase,
            ),
        )
        .outerjoin(
            npcFollower,
            and_(
                mstQuest.c.id == npcFollower.c.questId,
                mstQuestPhase.c.phase == npcFollower.c.questPhase,
            ),
        )
        .outerjoin(
            npcFollowerRelease,
            and_(
                mstQuest.c.id == npcFollowerRelease.c.questId,
                mstQuestPhase.c.phase == npcFollowerRelease.c.questPhase,
            ),
        )
        .outerjoin(npcSvtFollower, npcFollower.c.leaderSvtId == npcSvtFollower.c.id)
        .outerjoin(npcSvtEquip, npcFollower.c.svtEquipIds[1] == npcSvtEquip.c.id)
        .outerjoin(mstBgm, mstBgm.c.id == mstStage.c.bgmId)
        .outerjoin(
            ScriptFileList,
            and_(
                mstQuest.c.id == ScriptFileList.c.questId,
                mstQuestPhase.c.phase == ScriptFileList.c.phase,
            ),
        )
    )

    select_quest_phase = [
        func.to_jsonb(mstQuest.table_valued()).label(mstQuest.name),
        sql_jsonb_agg(mstQuestConsumeItem),
        sql_jsonb_agg(mstQuestRelease),
        sql_jsonb_agg(mstClosedMessage),
        sql_jsonb_agg(mstGift),
        all_phases_cte.c.phases,
        phasesWithEnemies,
        func.to_jsonb(mstQuestPhase.table_valued()).label(mstQuestPhase.name),
        func.to_jsonb(mstQuestPhaseDetail.table_valued()).label(
            mstQuestPhaseDetail.name
        ),
        sql_jsonb_agg(mstQuestMessage),
        func.array_remove(
            func.array_agg(ScriptFileList.c.scriptFileName.distinct()), None
        ).label("scripts"),
        sql_jsonb_agg(mstStage),
        sql_jsonb_agg(npcFollower),
        sql_jsonb_agg(npcFollowerRelease),
        sql_jsonb_agg(npcSvtFollower),
        sql_jsonb_agg(npcSvtEquip),
        sql_jsonb_agg(mstBgm),
    ]

    sql_stmt = (
        select(*select_quest_phase)
        .select_from(joined_quest_phase_tables)
        .where(and_(mstQuest.c.id == quest_id, mstQuestPhase.c.phase == phase_id))
        .group_by(
            mstQuest.table_valued(),
            mstQuestPhase.table_valued(),
            mstQuestPhaseDetail.table_valued(),
            all_phases_cte.c.phases,
        )
    )

    quest_phase = (await conn.execute(sql_stmt)).fetchone()
    if quest_phase:
        return QuestPhaseEntity.from_orm(quest_phase)

    return None


async def get_stage_remap(
    conn: AsyncConnection, quest_id: int, phase_id: int
) -> list[MstStageRemap]:
    stmt = select(mstStageRemap).where(
        and_(
            mstStageRemap.c.questId == quest_id, mstStageRemap.c.questPhase == phase_id
        )
    )
    stage_remaps = (await conn.execute(stmt)).fetchall()
    return [MstStageRemap.from_orm(stage_remap) for stage_remap in stage_remaps]


async def get_remapped_stages(
    conn: AsyncConnection, stage_remaps: Iterable[MstStageRemap]
) -> list[MstStage]:
    remapped_conditions = [
        and_(
            mstStage.c.questId == stage_remap.remapQuestId,
            mstStage.c.questPhase == stage_remap.remapPhase,
            mstStage.c.wave == stage_remap.remapWave,
        )
        for stage_remap in stage_remaps
    ]
    stmt = select(mstStage).where(or_(*remapped_conditions))
    return [MstStage.from_orm(stage) for stage in (await conn.execute(stmt)).fetchall()]


async def get_bgm_from_stage(
    conn: AsyncConnection, stages: Iterable[MstStage]
) -> list[MstBgm]:
    bgm_ids = [stage.bgmId for stage in stages]
    stmt = select(mstBgm).where(mstBgm.c.id.in_(bgm_ids))
    return [MstBgm.from_orm(bgm) for bgm in (await conn.execute(stmt)).fetchall()]


async def get_quest_from_ai(conn: AsyncConnection, ai_id: int) -> list[StageLink]:
    ai_script_pattern = {"aiFieldIds": [{"id": ai_id}]}
    stmt = select(mstStage.c.questId, mstStage.c.questPhase, mstStage.c.wave).where(
        mstStage.c.script.contains(ai_script_pattern)
    )

    stages = (await conn.execute(stmt)).fetchall()
    return [
        StageLink(questId=stage.questId, phase=stage.questPhase, stage=stage.wave)
        for stage in stages
    ]
