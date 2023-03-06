import functools
from typing import Any, Iterable, Optional, Union

from sqlalchemy import Integer, Table
from sqlalchemy.dialects.postgresql import array_agg
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import (
    ColumnElement,
    Join,
    and_,
    case,
    cast,
    func,
    literal_column,
    or_,
    select,
)
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import (
    ScriptFileList,
    mstBgm,
    mstClosedMessage,
    mstGift,
    mstGiftAdd,
    mstMap,
    mstQuest,
    mstQuestConsumeItem,
    mstQuestHint,
    mstQuestMessage,
    mstQuestPhase,
    mstQuestPhaseDetail,
    mstQuestRelease,
    mstQuestRestriction,
    mstQuestRestrictionInfo,
    mstRestriction,
    mstSpot,
    mstStage,
    mstStageRemap,
    mstSvt,
    mstWar,
    npcFollower,
    npcFollowerRelease,
    npcSvtEquip,
    npcSvtFollower,
)
from ...models.rayshift import rayshiftQuest, rayshiftQuestHash
from ...schemas.common import StageLink
from ...schemas.gameenums import QuestFlag
from ...schemas.raw import (
    MstBgm,
    MstQuestPhase,
    MstQuestWithPhase,
    MstQuestWithWar,
    MstStage,
    MstStageRemap,
    QuestEntity,
    QuestPhaseEntity,
)
from .utils import fetch_one, sql_jsonb_agg


QUEST_WITH_WAR_SELECT = select(
    mstQuest,
    mstWar.c.id.label("warId"),
    mstWar.c.longName.label("warLongName"),
    mstSpot.c.name.label("spotName"),
).select_from(
    mstQuest.join(mstSpot, mstSpot.c.id == mstQuest.c.spotId)
    .join(mstMap, mstMap.c.id == mstSpot.c.mapId)
    .join(mstWar, mstWar.c.id == mstMap.c.warId)
)


async def get_one_quest_with_war(
    conn: AsyncConnection, quest_id: int
) -> Optional[MstQuestWithWar]:
    stmt = QUEST_WITH_WAR_SELECT.where(mstQuest.c.id == quest_id)

    try:
        mstQuestWar = await fetch_one(conn, stmt)
    except DBAPIError:
        return None

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


MSTQUEST_WITH_PHASE_SELECT = select(
    mstQuest,
    mstWar.c.id.label("warId"),
    mstWar.c.longName.label("warLongName"),
    mstSpot.c.name.label("spotName"),
    mstQuestPhase.c.classIds,
    mstQuestPhase.c.individuality,
    mstQuestPhase.c.script,
    mstQuestPhase.c.questId,
    mstQuestPhase.c.phase,
    mstQuestPhase.c.isNpcOnly,
    mstQuestPhase.c.battleBgId,
    mstQuestPhase.c.battleBgType,
    mstQuestPhase.c.qp,
    mstQuestPhase.c.playerExp,
    mstQuestPhase.c.friendshipExp,
    mstQuestPhase.c.giftId.label("phaseGiftId"),
)
MSTQUEST_WITH_PHASE_FROM = (
    mstQuest.join(mstSpot, mstSpot.c.id == mstQuest.c.spotId)
    .join(mstMap, mstMap.c.id == mstSpot.c.mapId)
    .join(mstWar, mstWar.c.id == mstMap.c.warId)
    .join(mstQuestPhase, mstQuestPhase.c.questId == mstQuest.c.id)
)


async def get_one_quest_with_phase(
    conn: AsyncConnection, quest_id: int, phase_id: int
) -> Optional[MstQuestWithPhase]:
    stmt = MSTQUEST_WITH_PHASE_SELECT.select_from(MSTQUEST_WITH_PHASE_FROM).where(
        and_(mstQuest.c.id == quest_id, mstQuestPhase.c.phase == phase_id)
    )

    try:
        mstQuestWithPhase = await fetch_one(conn, stmt)
    except DBAPIError:
        return None

    if mstQuestWithPhase:
        return MstQuestWithPhase.from_orm(mstQuestWithPhase)

    return None


async def get_latest_quest_with_enemies(
    conn: AsyncConnection, limit_result: int = 50
) -> list[MstQuestWithPhase]:
    min_query_id = func.min(rayshiftQuest.c.queryId).label("min_queryId")
    latest_rayshifts = (
        select(rayshiftQuest.c.questId, rayshiftQuest.c.phase, min_query_id)
        .group_by(rayshiftQuest.c.questId, rayshiftQuest.c.phase)
        .order_by(min_query_id.desc())
        .limit(limit_result)
        .cte()
    )
    stmt = MSTQUEST_WITH_PHASE_SELECT.select_from(
        MSTQUEST_WITH_PHASE_FROM.join(
            latest_rayshifts,
            and_(
                mstQuestPhase.c.questId == latest_rayshifts.c.questId,
                mstQuestPhase.c.phase == latest_rayshifts.c.phase,
            ),
        )
    ).order_by(latest_rayshifts.c.min_queryId.desc())

    rows = (await conn.execute(stmt)).fetchall()

    return [MstQuestWithPhase.from_orm(row) for row in rows]


async def get_quest_phase_search(
    conn: AsyncConnection,
    name: Optional[str] = None,
    spot_name: Optional[str] = None,
    war_ids: Optional[Iterable[int]] = None,
    quest_type: Optional[Iterable[int]] = None,
    flag: Optional[Iterable[int]] = None,
    field_individuality: Optional[Iterable[int]] = None,
    battle_bg_id: Optional[int] = None,
    bgm_id: Optional[int] = None,
    field_ai_id: Optional[int] = None,
    enemy_svt_id: Optional[int] = None,
    enemy_svt_ai_id: Optional[int] = None,
    enemy_trait: Optional[Iterable[int]] = None,
    enemy_class: Optional[Iterable[int]] = None,
    enemy_skill: Optional[Iterable[int]] = None,
    enemy_np: Optional[Iterable[int]] = None,
) -> list[MstQuestWithPhase]:
    from_clause: Union[Join, Table] = MSTQUEST_WITH_PHASE_FROM
    if bgm_id or field_ai_id:
        from_clause = from_clause.join(
            mstStage,
            and_(
                mstQuest.c.id == mstStage.c.questId,
                mstQuestPhase.c.phase == mstStage.c.questPhase,
            ),
        )
    if (
        enemy_svt_id
        or enemy_svt_ai_id
        or enemy_trait
        or enemy_class
        or enemy_skill
        or enemy_np
    ):
        from_clause = from_clause.outerjoin(
            rayshiftQuest,
            and_(
                mstQuest.c.id == rayshiftQuest.c.questId,
                mstQuestPhase.c.phase == rayshiftQuest.c.phase,
            ),
        )

    def questDetail_contains(userSvt_shape: dict[str, Any]) -> ColumnElement[bool]:
        return rayshiftQuest.c.questDetail.contains({"userSvt": [userSvt_shape]})

    where_clause: list[_ColumnExpressionArgument[bool]] = []
    if name:
        where_clause.append(mstQuest.c.name.ilike(f"%{name}%"))
    if spot_name:
        overwrite_spot_names = (
            select(
                mstQuestPhaseDetail.c.questId,
                mstQuestPhaseDetail.c.phase,
                mstQuestPhaseDetail.c.spotId.label("overwriteSpotId"),
                mstSpot.c.name.label("overwriteSpotName"),
            )
            .select_from(
                mstQuestPhaseDetail.join(
                    mstSpot, mstQuestPhaseDetail.c.spotId == mstSpot.c.id
                )
            )
            .cte()
        )
        from_clause = from_clause.outerjoin(
            overwrite_spot_names,
            and_(
                mstQuest.c.id == overwrite_spot_names.c.questId,
                mstQuestPhase.c.phase == overwrite_spot_names.c.phase,
            ),
        )
        where_clause.append(
            or_(
                and_(
                    overwrite_spot_names.c.overwriteSpotName.is_(None),
                    mstSpot.c.name.ilike(f"%{spot_name}%"),
                ),
                and_(
                    overwrite_spot_names.c.overwriteSpotName.is_not(None),
                    overwrite_spot_names.c.overwriteSpotName.ilike(f"%{spot_name}%"),
                ),
            )
        )
    if war_ids:
        where_clause.append(mstWar.c.id.in_(war_ids))
    if quest_type:
        where_clause.append(mstQuest.c.type.in_(quest_type))
    if flag:
        flag_bit = functools.reduce(lambda x, y: x | y, flag)
        where_clause.append(mstQuest.c.flag.op("&")(flag_bit) == flag_bit)
    if field_individuality:
        where_clause.append(mstQuestPhase.c.individuality.contains(field_individuality))
    if battle_bg_id:
        where_clause.append(mstQuestPhase.c.battleBgId == battle_bg_id)
    if bgm_id:
        where_clause.append(mstStage.c.bgmId == bgm_id)
    if field_ai_id:
        where_clause.append(
            mstStage.c.script.contains({"aiFieldIds": [{"id": field_ai_id}]})
        )
    if enemy_svt_ai_id:
        where_clause.append(questDetail_contains({"aiId": enemy_svt_ai_id}))
    if enemy_trait:
        where_clause.append(questDetail_contains({"individuality": list(enemy_trait)}))
    if enemy_svt_id:
        where_clause.append(questDetail_contains({"svtId": enemy_svt_id}))
    if enemy_class:
        rayshift_svt_ids = select(
            rayshiftQuest.c.questId,
            rayshiftQuest.c.phase,
            literal_column(
                "(jsonb_path_query(\"questDetail\", '$.userSvt[*] ? (@.npcSvtClassId == 0).svtId')->0)::int",
                type_=Integer,
            ).label("rayshift_svt_id"),
        ).cte()
        deduped_svt_ids = (
            select(
                rayshift_svt_ids.c.questId,
                rayshift_svt_ids.c.phase,
                rayshift_svt_ids.c.rayshift_svt_id,
            )
            .group_by(
                rayshift_svt_ids.c.questId,
                rayshift_svt_ids.c.phase,
                rayshift_svt_ids.c.rayshift_svt_id,
            )
            .cte()
        )
        merged_class_ids = (
            select(deduped_svt_ids.c.questId, deduped_svt_ids.c.phase, mstSvt.c.classId)
            .join(mstSvt, mstSvt.c.id == deduped_svt_ids.c.rayshift_svt_id)
            .cte()
        )
        from_clause = from_clause.outerjoin(
            merged_class_ids,
            and_(
                mstQuest.c.id == merged_class_ids.c.questId,
                mstQuestPhase.c.phase == merged_class_ids.c.phase,
            ),
        )
        for class_id in enemy_class:
            where_clause.append(
                or_(
                    questDetail_contains({"npcSvtClassId": class_id}),
                    merged_class_ids.c.classId == class_id,
                )
            )
    if enemy_skill:
        for skill_id in enemy_skill:
            where_clause.append(
                or_(
                    questDetail_contains({"skillId1": skill_id}),
                    questDetail_contains({"skillId2": skill_id}),
                    questDetail_contains({"skillId3": skill_id}),
                    questDetail_contains({"classPassive": [skill_id]}),
                    questDetail_contains({"addPassive": [skill_id]}),
                )
            )
    if enemy_np:
        for np_id in enemy_np:
            where_clause.append(questDetail_contains({"treasureDeviceId": np_id}))

    quest_search_stmt = (
        MSTQUEST_WITH_PHASE_SELECT.distinct()
        .select_from(from_clause)
        .where(and_(*where_clause))
    )

    return [
        MstQuestWithPhase.from_orm(quest)
        for quest in (await conn.execute(quest_search_stmt)).fetchall()
    ]


scripts_cte = select(
    ScriptFileList.c.scriptFileName,
    ScriptFileList.c.questId,
    ScriptFileList.c.phase,
    ScriptFileList.c.sceneType,
).cte()


JOINED_QUEST_TABLES = (
    mstQuest.outerjoin(
        mstQuestConsumeItem, mstQuestConsumeItem.c.questId == mstQuest.c.id
    )
    .outerjoin(mstQuestRelease, mstQuestRelease.c.questId == mstQuest.c.id)
    .outerjoin(mstQuestPhase, mstQuestPhase.c.questId == mstQuest.c.id)
    .outerjoin(
        mstClosedMessage, mstClosedMessage.c.id == mstQuestRelease.c.closedMessageId
    )
    .outerjoin(mstGiftAdd, mstGiftAdd.c.giftId == mstQuest.c.giftId)
    .outerjoin(
        mstGift,
        or_(
            mstGift.c.id == mstQuest.c.giftId, mstGift.c.id == mstGiftAdd.c.priorGiftId
        ),
    )
)


JOINED_QUEST_ENTITY_TABLES = (
    JOINED_QUEST_TABLES.outerjoin(
        rayshiftQuest, rayshiftQuest.c.questId == mstQuest.c.id
    )
    .outerjoin(
        mstQuestPhaseDetail,
        and_(
            mstQuest.c.id == mstQuestPhaseDetail.c.questId,
            mstQuestPhase.c.phase == mstQuestPhaseDetail.c.phase,
        ),
    )
    .outerjoin(scripts_cte, mstQuest.c.id == scripts_cte.c.questId)
)


phasesWithEnemies = func.to_jsonb(
    func.array_remove(array_agg(rayshiftQuest.c.phase.distinct()), None)
).label("phasesWithEnemies")


phasesNoBattle = func.array_remove(
    array_agg(
        case(
            (
                mstQuestPhaseDetail.c.flag.op("&")(QuestFlag.NO_BATTLE.value) != 0,
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
    sql_jsonb_agg(mstGiftAdd),
    func.to_jsonb(
        func.array_remove(array_agg(mstQuestPhase.c.phase.distinct()), None)
    ).label("phases"),
    phasesWithEnemies,
    phasesNoBattle,
    func.to_jsonb(
        func.array_remove(array_agg(scripts_cte.table_valued().distinct()), None)
    ).label("allScripts"),
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

    try:
        return [
            QuestEntity.from_orm(quest)
            for quest in (await conn.execute(stmt)).fetchall()
        ]
    except DBAPIError:
        return []


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

    all_scripts_cte = (
        select(
            ScriptFileList.c.scriptFileName,
            ScriptFileList.c.questId,
            ScriptFileList.c.phase,
            ScriptFileList.c.sceneType,
        )
        .where(ScriptFileList.c.questId == quest_id)
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
            mstQuestHint,
            and_(
                mstQuest.c.id == mstQuestHint.c.questId,
                mstQuestPhase.c.phase == mstQuestHint.c.questPhase,
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
        .outerjoin(
            mstQuestRestriction,
            and_(
                mstQuest.c.id == mstQuestRestriction.c.questId,
                or_(
                    mstQuestPhase.c.phase == mstQuestRestriction.c.phase,
                    mstQuestRestriction.c.phase == 0,
                ),
            ),
        )
        .outerjoin(
            mstQuestRestrictionInfo,
            and_(
                mstQuest.c.id == mstQuestRestrictionInfo.c.questId,
                mstQuestPhase.c.phase == mstQuestRestrictionInfo.c.phase,
            ),
        )
        .outerjoin(
            mstRestriction,
            mstRestriction.c.id == mstQuestRestriction.c.restrictionId,
        )
        .outerjoin(npcSvtEquip, npcFollower.c.svtEquipIds[1] == npcSvtEquip.c.id)
        .outerjoin(mstBgm, mstBgm.c.id == mstStage.c.bgmId)
        .outerjoin(
            ScriptFileList,
            and_(
                mstQuest.c.id == ScriptFileList.c.questId,
                mstQuestPhase.c.phase == ScriptFileList.c.phase,
            ),
        )
        .outerjoin(all_scripts_cte, mstQuest.c.id == all_scripts_cte.c.questId)
        .outerjoin(
            npcSvtFollower,
            or_(
                npcFollower.c.leaderSvtId == npcSvtFollower.c.id,
                cast(mstQuestPhase.c.script["aiNpc"]["npcId"], Integer)
                == npcSvtFollower.c.id,
                literal_column(
                    "any(array(select jsonb_path_query(\"mstQuestPhase\".script, '$.aiMultiNpc[*].npcId')::int))"
                )
                == npcSvtFollower.c.id,
            ),
        )
    )

    select_quest_phase = [
        func.to_jsonb(mstQuest.table_valued()).label(mstQuest.name),
        sql_jsonb_agg(mstQuestConsumeItem),
        sql_jsonb_agg(mstQuestRelease),
        sql_jsonb_agg(mstClosedMessage),
        sql_jsonb_agg(mstGift),
        sql_jsonb_agg(mstGiftAdd),
        all_phases_cte.c.phases,
        func.coalesce(
            select(func.array_remove(array_agg(rayshiftQuest.c.phase.distinct()), None))
            .where(rayshiftQuest.c.questId == quest_id)
            .scalar_subquery(),
            [],
        ).label("phasesWithEnemies"),
        func.coalesce(
            select(
                func.array_remove(
                    array_agg(rayshiftQuestHash.c.questHash.distinct()), None
                )
            )
            .select_from(
                rayshiftQuestHash.join(
                    rayshiftQuest,
                    rayshiftQuestHash.c.queryId == rayshiftQuest.c.queryId,
                )
            )
            .where(rayshiftQuest.c.questId == quest_id)
            .scalar_subquery(),
            [],
        ).label("availableEnemyHashes"),
        func.to_jsonb(mstQuestPhase.table_valued()).label(mstQuestPhase.name),
        func.to_jsonb(mstQuestPhaseDetail.table_valued()).label(
            mstQuestPhaseDetail.name
        ),
        sql_jsonb_agg(mstQuestMessage),
        sql_jsonb_agg(mstQuestHint),
        func.array_remove(
            array_agg(ScriptFileList.c.scriptFileName.distinct()), None
        ).label("scripts"),
        func.to_jsonb(
            func.array_remove(
                array_agg(all_scripts_cte.table_valued().distinct()), None
            )
        ).label("allScripts"),
        sql_jsonb_agg(mstStage),
        sql_jsonb_agg(npcFollower),
        sql_jsonb_agg(npcFollowerRelease),
        sql_jsonb_agg(npcSvtFollower),
        sql_jsonb_agg(npcSvtEquip),
        sql_jsonb_agg(mstBgm),
        sql_jsonb_agg(mstQuestRestriction),
        sql_jsonb_agg(mstQuestRestrictionInfo),
        sql_jsonb_agg(mstRestriction),
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

    try:
        quest_phase = await fetch_one(conn, sql_stmt)
        if quest_phase:
            return QuestPhaseEntity.from_orm(quest_phase)
    except DBAPIError:
        pass

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


async def get_questSelect_container(
    conn: AsyncConnection, quest_id: int, phase: int
) -> MstQuestPhase | None:
    stmt = select(mstQuestPhase).where(
        and_(
            mstQuestPhase.c.phase == phase,
            mstQuestPhase.c.script.contains({"questSelect": [quest_id]}),
        )
    )

    quest_phase = await fetch_one(conn, stmt)
    if quest_phase:
        return MstQuestPhase.from_orm(quest_phase)

    return None
