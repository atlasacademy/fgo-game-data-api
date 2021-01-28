from inspect import cleandoc
from typing import Iterable, List, Set

from sqlalchemy.engine import Connection
from sqlalchemy.sql import select, text

from ...models.raw import mstSubtitle, mstSvtComment, mstSvtVoice
from ...schemas.enums import VoiceCondType
from ...schemas.raw import GlobalNewMstSubtitle, MstSvtComment, MstSvtVoice


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
