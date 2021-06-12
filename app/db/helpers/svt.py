from typing import Iterable, Optional, Union

from sqlalchemy import Table
from sqlalchemy.engine import Connection
from sqlalchemy.sql import Join, and_, or_, select
from sqlalchemy.sql.elements import ClauseElement

from ...models.raw import (
    mstCv,
    mstIllustrator,
    mstSubtitle,
    mstSvt,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtScript,
    mstSvtVoice,
    mstVoicePlayCond,
)
from ...schemas.enums import SERVANT_TYPES
from ...schemas.gameenums import CondType, SvtType, VoiceCondType
from ...schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvt,
    MstSvtScript,
    MstSvtVoice,
    MstVoicePlayCond,
)


def get_all_servants(conn: Connection) -> list[MstSvt]:  # pragma: no cover
    stmt = select(mstSvt).where(
        and_(mstSvt.c.collectionNo != 0, mstSvt.c.type.in_(SERVANT_TYPES))
    )
    return [MstSvt.from_orm(svt) for svt in conn.execute(stmt).fetchall()]


def get_all_equips(conn: Connection) -> list[MstSvt]:  # pragma: no cover
    stmt = select(mstSvt).where(
        and_(mstSvt.c.collectionNo != 0, mstSvt.c.type == SvtType.SERVANT_EQUIP)
    )
    return [MstSvt.from_orm(svt) for svt in conn.execute(stmt).fetchall()]


def get_svt_script(conn: Connection, svt_ids: list[int]) -> list[MstSvtScript]:
    stmt = (
        select(mstSvtScript)
        .where((mstSvtScript.c.id / 10).in_(svt_ids))
        .order_by(mstSvtScript.c.id, mstSvtScript.c.form)
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
    illustrator: Optional[str] = None,
    cv: Optional[str] = None,
) -> list[MstSvt]:
    from_clause: Union[Join, Table] = mstSvt
    where_clause: list[Union[ClauseElement, bool]] = [True]

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
        from_clause = from_clause.outerjoin(
            mstSvtLimitAdd, mstSvtLimitAdd.c.svtId == mstSvt.c.id
        )
        where_clause.append(
            or_(
                mstSvt.c.individuality.contains(trait_ints),
                mstSvtLimitAdd.c.individuality.contains(trait_ints),
            )
        )
    if rarity_ints:
        from_clause = from_clause.outerjoin(
            mstSvtLimit, mstSvtLimit.c.svtId == mstSvt.c.id
        )
        where_clause.append(mstSvtLimit.c.rarity.in_(rarity_ints))
    if illustrator:
        from_clause = from_clause.outerjoin(
            mstIllustrator, mstIllustrator.c.id == mstSvt.c.illustratorId
        )
        where_clause.append(mstIllustrator.c.name == illustrator)
    if cv:
        from_clause = from_clause.outerjoin(mstCv, mstCv.c.id == mstSvt.c.cvId)
        where_clause.append(mstCv.c.name == cv)

    if cond_svt_value or cond_group_value:
        from_clause = from_clause.outerjoin(
            mstSvtVoice, mstSvtVoice.c.id == mstSvt.c.id
        )

    or_voice_clause: list[ClauseElement] = []
    if cond_svt_value:
        or_voice_clause += [
            mstSvtVoice.c.scriptJson.contains(
                voice_cond_pattern(VoiceCondType.SVT_GET.value, svt_value)
            )
            for svt_value in cond_svt_value
        ]
        from_clause = from_clause.outerjoin(
            mstVoicePlayCond, mstVoicePlayCond.c.svtId == mstSvt.c.id
        )
        or_voice_clause += [
            and_(
                mstVoicePlayCond.c.svtId != mstVoicePlayCond.c.targetId,
                mstVoicePlayCond.c.targetId == svt_value,
                mstVoicePlayCond.c.condType == CondType.SVT_HAVING,
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

    svt_search_stmt = (
        select(mstSvt).distinct().select_from(from_clause).where(and_(*where_clause))
    )

    return [MstSvt.from_orm(svt) for svt in conn.execute(svt_search_stmt).fetchall()]
