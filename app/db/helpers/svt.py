from typing import Any, Iterable, Optional

from sqlalchemy.engine import Connection
from sqlalchemy.sql import and_, or_, select

from ...models.raw import (
    mstSubtitle,
    mstSvt,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtScript,
    mstSvtVoice,
    mstVoicePlayCond,
)
from ...schemas.gameenums import VoiceCondType
from ...schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvt,
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


def get_svt_search(
    conn: Connection,
    svt_type_ints: Optional[Iterable[int]] = None,
    svt_flag_ints: Optional[Iterable[int]] = None,
    excludeCollectionNo: Optional[Iterable[int]] = None,
    class_ints: Optional[Iterable[int]] = None,
    gender_ints: Optional[Iterable[int]] = None,
    attribute_ints: Optional[Iterable[int]] = None,
    trait_ints: Optional[Iterable[int]] = None,
    rarity_ints: Optional[Iterable[int]] = None,
    cond_svt_value: Optional[set[int]] = None,
    cond_group_value: Optional[set[int]] = None,
) -> list[MstSvt]:
    where_clause: list[Any] = [True]
    if svt_type_ints:
        where_clause.append(mstSvt.c.type.in_(svt_type_ints))
    if svt_flag_ints:
        where_clause.append(mstSvt.c.flag.in_(svt_flag_ints))
    if excludeCollectionNo:
        where_clause.append(mstSvt.c.collectionNo.notin_(excludeCollectionNo))
    if class_ints:
        where_clause.append(mstSvt.c.classId.in_(class_ints))
    if gender_ints:
        where_clause.append(mstSvt.c.genderType.in_(gender_ints))
    if attribute_ints:
        where_clause.append(mstSvt.c.attri.in_(attribute_ints))
    if trait_ints:
        where_clause.append(
            or_(
                mstSvt.c.individuality.contains(trait_ints),
                mstSvtLimitAdd.c.individuality.contains(trait_ints),
            )
        )
    if rarity_ints:
        where_clause.append(mstSvtLimit.c.rarity.in_(rarity_ints))

    or_voice_clause = []
    if cond_svt_value:
        or_voice_clause += [
            mstSvtVoice.c.scriptJson.contains(
                voice_cond_pattern(VoiceCondType.SVT_GET.value, svt_value)
            )
            for svt_value in cond_svt_value
        ]
    if cond_group_value:
        or_voice_clause += [
            mstSvtVoice.c.scriptJson.contains(
                voice_cond_pattern(VoiceCondType.SVT_GROUP.value, group_value)
            )
            for group_value in cond_group_value
        ]

    if or_voice_clause:
        where_clause.append(or_(*or_voice_clause))

    joined_svt = (
        mstSvt.outerjoin(mstSvtLimit, mstSvtLimit.c.svtId == mstSvt.c.id)
        .outerjoin(mstSvtLimitAdd, mstSvtLimitAdd.c.svtId == mstSvt.c.id)
        .outerjoin(mstSvtVoice, mstSvtVoice.c.id == mstSvt.c.id)
    )

    svt_search_stmt = (
        select(mstSvt).distinct().select_from(joined_svt).where(and_(*where_clause))
    )

    return [MstSvt.from_orm(svt) for svt in conn.execute(svt_search_stmt).fetchall()]
