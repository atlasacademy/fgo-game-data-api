from typing import Iterable

from sqlalchemy.engine import Connection
from sqlalchemy.sql import or_, select

from ...models.raw import mstSubtitle, mstSvtScript, mstSvtVoice, mstVoicePlayCond
from ...schemas.gameenums import VoiceCondType
from ...schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvtScript,
    MstSvtVoice,
    MstVoicePlayCond,
)


def get_svt_script(conn: Connection, svt_id: int) -> list[MstSvtScript]:
    stmt = (
        select(mstSvtScript)
        .where(mstSvtScript.c.id / 10 == svt_id)
        .order_by(mstSvtScript.c.form)
    )
    return [MstSvtScript.from_orm(db_row) for db_row in conn.execute(stmt).fetchall()]


def get_mstSvtVoice(conn: Connection, svt_ids: Iterable[int]) -> list[MstSvtVoice]:
    mstSvtVoice_stmt = (
        select(mstSvtVoice)
        .where(mstSvtVoice.c.id.in_(svt_ids))
        .order_by(mstSvtVoice.c.id, mstSvtVoice.c.voicePrefix, mstSvtVoice.c.type)
    )
    return [
        MstSvtVoice.from_orm(svt_voice)
        for svt_voice in conn.execute(mstSvtVoice_stmt).fetchall()
    ]


def get_mstVoicePlayCond(
    conn: Connection, svt_ids: Iterable[int]
) -> list[MstVoicePlayCond]:
    mstVoicePlayCond_stmt = (
        select(mstVoicePlayCond)
        .where(mstVoicePlayCond.c.svtId.in_(svt_ids))
        .order_by(
            mstVoicePlayCond.c.svtId, mstVoicePlayCond.c.voiceId, mstVoicePlayCond.c.idx
        )
    )
    return [
        MstVoicePlayCond.from_orm(play_cond)
        for play_cond in conn.execute(mstVoicePlayCond_stmt).fetchall()
    ]


def get_mstSubtitle(
    conn: Connection, svt_ids: Iterable[int]
) -> list[GlobalNewMstSubtitle]:
    mstSubtitle_stmt = (
        select(mstSubtitle)
        .where(mstSubtitle.c.svtId.in_(svt_ids))
        .order_by(mstSubtitle.c.id)
    )
    return [
        GlobalNewMstSubtitle.from_orm(subtitle)
        for subtitle in conn.execute(mstSubtitle_stmt).fetchall()
    ]


def voice_cond_pattern(
    condType: int, value: int
) -> list[dict[str, list[dict[str, int]]]]:
    return [{"conds": [{"condType": condType, "value": value}]}]


def get_related_voice_id(
    conn: Connection, cond_svt_value: set[int], cond_group_value: set[int]
) -> set[int]:
    where_clause = [
        mstSvtVoice.c.scriptJson.contains(
            voice_cond_pattern(VoiceCondType.SVT_GET.value, svt_value)
        )
        for svt_value in cond_svt_value
    ]

    if cond_group_value:
        where_clause += [
            mstSvtVoice.c.scriptJson.contains(
                voice_cond_pattern(VoiceCondType.SVT_GROUP.value, group_value)
            )
            for group_value in cond_group_value
        ]

    stmt = select(mstSvtVoice.c.id).where(or_(*where_clause))

    fetched: set[int] = {svt_voice.id for svt_voice in conn.execute(stmt).fetchall()}
    return fetched
