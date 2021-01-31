from inspect import cleandoc
from typing import Any, Iterable, List, Set

from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.sql import func, literal_column, select, text
from sqlalchemy.sql.selectable import CTE

from ...models.raw import (
    mstCombineCostume,
    mstCombineLimit,
    mstCombineSkill,
    mstSubtitle,
    mstSvt,
    mstSvtCard,
    mstSvtChange,
    mstSvtComment,
    mstSvtCostume,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtVoice,
)
from ...schemas.enums import VoiceCondType
from ...schemas.raw import GlobalNewMstSubtitle, MstSvtComment, MstSvtVoice
from .utils import sql_jsonb_agg


def sql_sorted_cte(table: Table, svt_id: int, svt_id_col: str, order_col: str) -> CTE:
    return (
        select(
            [
                table.c[svt_id_col],
                func.jsonb_agg(
                    literal_column(f'"{table.name}" ORDER BY "{order_col}"')
                ).label(table.name),
            ]
        )
        .where(table.c[svt_id_col] == svt_id)
        .group_by(table.c[svt_id_col])
        .cte()
    )


def coalesce_select(cte_table: CTE, orig_table: Table) -> Any:
    return func.coalesce(
        cte_table.c[orig_table.name], literal_column("'[]'::jsonb")
    ).label(orig_table.name)


def get_servantEntity(conn: Connection, svt_id: int) -> Any:
    mstSvtCardJson = sql_sorted_cte(mstSvtCard, svt_id, "svtId", "cardId")
    mstCombineSkillJson = sql_sorted_cte(mstCombineSkill, svt_id, "id", "skillLv")
    mstCombineLimitJson = sql_sorted_cte(mstCombineLimit, svt_id, "id", "svtLimit")
    mstSvtLimitAddJson = sql_sorted_cte(mstSvtLimitAdd, svt_id, "svtId", "limitCount")

    JOINED_SVT_TABLES = (
        mstSvt.join(
            mstSvtCardJson,
            mstSvtCardJson.c.svtId == mstSvt.c.id,
            isouter=True,
        )
        .join(
            mstSvtLimit,
            mstSvtLimit.c.svtId == mstSvt.c.id,
            isouter=True,
        )
        .join(
            mstCombineSkillJson,
            mstCombineSkillJson.c.id == mstSvt.c.combineSkillId,
            isouter=True,
        )
        .join(
            mstCombineLimitJson,
            mstCombineLimitJson.c.id == mstSvt.c.combineLimitId,
            isouter=True,
        )
        .join(
            mstCombineCostume,
            mstCombineCostume.c.svtId == mstSvt.c.id,
            isouter=True,
        )
        .join(
            mstSvtLimitAddJson,
            mstSvtLimitAddJson.c.svtId == mstSvt.c.id,
            isouter=True,
        )
        .join(
            mstSvtChange,
            mstSvtChange.c.svtId == mstSvt.c.id,
            isouter=True,
        )
        .join(
            mstSvtCostume,
            mstSvtCostume.c.svtId == mstSvt.c.id,
            isouter=True,
        )
    )

    SELECT_SVT_ENTITY = [
        func.to_jsonb(literal_column(f'"{mstSvt.name}"')).label(mstSvt.name),
        coalesce_select(mstSvtCardJson, mstSvtCard),
        sql_jsonb_agg(mstSvtLimit),
        coalesce_select(mstCombineSkillJson, mstCombineSkill),
        coalesce_select(mstCombineLimitJson, mstCombineLimit),
        sql_jsonb_agg(mstCombineCostume),
        coalesce_select(mstSvtLimitAddJson, mstSvtLimitAdd),
        sql_jsonb_agg(mstSvtChange),
        sql_jsonb_agg(mstSvtCostume),
    ]

    stmt = (
        select(SELECT_SVT_ENTITY)
        .select_from(JOINED_SVT_TABLES)
        .where(mstSvt.c.id == svt_id)
        .group_by(
            mstSvt.c.id,
            mstSvtCardJson.c.mstSvtCard,
            mstCombineSkillJson.c.mstCombineSkill,
            mstCombineLimitJson.c.mstCombineLimit,
            mstSvtLimitAddJson.c.mstSvtLimitAdd,
        )
    )

    return conn.execute(stmt).fetchone()


def get_mstSvtComment(conn: Connection, svt_id: int) -> List[MstSvtComment]:
    mstSvtComment_stmt = (
        select([mstSvtComment])
        .where(mstSvtComment.c.svtId == svt_id)
        .order_by(mstSvtComment.c.id)
    )
    return [
        MstSvtComment.parse_obj(svt_comment)
        for svt_comment in conn.execute(mstSvtComment_stmt).fetchall()
    ]


def get_mstSvtVoice(conn: Connection, svt_ids: Iterable[int]) -> List[MstSvtVoice]:
    mstSvtVoice_stmt = (
        select([mstSvtVoice])
        .where(mstSvtVoice.c.id.in_(svt_ids))
        .order_by(mstSvtVoice.c.id, mstSvtVoice.c.voicePrefix, mstSvtVoice.c.type)
    )
    return [
        MstSvtVoice.parse_obj(svt_voice)
        for svt_voice in conn.execute(mstSvtVoice_stmt).fetchall()
    ]


def get_mstSubtitle(
    conn: Connection, svt_ids: Iterable[int]
) -> List[GlobalNewMstSubtitle]:
    mstSubtitle_stmt = (
        select([mstSubtitle])
        .where(mstSubtitle.c.svtId.in_(svt_ids))
        .order_by(mstSubtitle.c.id)
    )
    return [
        GlobalNewMstSubtitle.parse_obj(subtitle)
        for subtitle in conn.execute(mstSubtitle_stmt).fetchall()
    ]


def get_related_voice_id(
    conn: Connection, cond_svt_value: Set[int], cond_group_value: Set[int]
) -> Set[int]:
    text_stmt = cleandoc(
        """
        SELECT
        DISTINCT "mstSvtVoice".id
        FROM "mstSvtVoice",
        jsonb_array_elements("mstSvtVoice"."scriptJson") scriptJsonExpanded,
        jsonb_array_elements(scriptJsonExpanded->'conds') condsExpanded
        WHERE
        (condsExpanded->>'condType' = :svtCond AND condsExpanded->>'value' IN :svtValue)
        """
    )
    if cond_group_value:
        text_stmt += "OR (condsExpanded->>'condType' = :groupCond AND condsExpanded->>'value' IN :groupValue)"
    stmt = text(text_stmt)
    fetched: Set[int] = {
        svt_id[0]
        for svt_id in conn.execute(
            stmt,
            svtCond=str(VoiceCondType.SVT_GET.value),
            groupCond=str(VoiceCondType.SVT_GROUP.value),
            svtValue=tuple(str(i) for i in cond_svt_value),
            groupValue=tuple(str(i) for i in cond_group_value),
        ).fetchall()
    }
    return fetched
