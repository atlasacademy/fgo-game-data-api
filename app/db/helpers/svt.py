from typing import List, Set

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select, text

from ...models.raw import mstSvtComment, mstSvtVoice
from ...schemas.raw import MstSvtComment, MstSvtVoice


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


def get_mstSvtVoice(conn: Connection, svt_id: int) -> List[MstSvtVoice]:
    mstSvtVoice_stmt = (
        select([mstSvtVoice])
        .where(mstSvtVoice.c.id == svt_id)
        .order_by(mstSvtVoice.c.id, mstSvtVoice.c.voicePrefix, mstSvtVoice.c.type)
    )
    return [
        MstSvtVoice.parse_obj(svt_voice)
        for svt_voice in conn.execute(mstSvtVoice_stmt).fetchall()
    ]


def get_related_voice_id(
    conn: Connection, cond_svt_value: Set[int], cond_group_value: Set[int]
) -> Set[int]:
    cond_svt_value_str = [str(i) for i in cond_svt_value]
    cond_group_value_str = [str(i) for i in cond_group_value]
    stmt = text(
        """
        SELECT
        DISTINCT "mstSvtVoice".id
        FROM "mstSvtVoice",
        jsonb_array_elements("mstSvtVoice"."scriptJson") scriptJsonExpanded,
        jsonb_array_elements(scriptJsonExpanded->'conds') condsExpanded
        WHERE
        (condsExpanded->>'condType' = '4' AND condsExpanded->>'value' = ANY(:svtvalue))
        OR
        (condsExpanded->>'condType' = '5' AND condsExpanded->>'value' = ANY(:groupvalue))
        """
    )
    fetched: Set[int] = set(
        svt_id[0]
        for svt_id in conn.execute(
            stmt,
            svtvalue=cond_svt_value_str,
            groupvalue=cond_group_value_str,
        ).fetchall()
    )
    return fetched
