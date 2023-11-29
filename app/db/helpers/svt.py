from dataclasses import dataclass
from typing import Iterable, Optional, Union

from sqlalchemy import Table
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import Join, and_, not_, or_, select, true
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from ...models.raw import (
    mstCv,
    mstIllustrator,
    mstSubtitle,
    mstSvt,
    mstSvtComment,
    mstSvtGroup,
    mstSvtIndividuality,
    mstSvtLimit,
    mstSvtLimitAdd,
    mstSvtScript,
    mstSvtVoice,
    mstVoicePlayCond,
)
from ...schemas.gameenums import CondType, SvtType, VoiceCondType
from ...schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvt,
    MstSvtLimitAdd,
    MstSvtScript,
    MstSvtVoice,
    MstVoicePlayCond,
)


async def get_svt_id(conn: AsyncConnection, col_no: int) -> int:
    if col_no == 0:
        return 0
    stmt = (
        select(mstSvt.c.id)
        .where(
            and_(
                mstSvt.c.collectionNo == col_no,
                or_(
                    mstSvt.c.type == SvtType.HEROINE,
                    mstSvt.c.type == SvtType.NORMAL,
                    mstSvt.c.type == SvtType.ENEMY_COLLECTION_DETAIL,
                ),
            )
        )
        .limit(1)
    )

    try:
        mstSvt_db = (await conn.execute(stmt)).scalar()
    except DBAPIError:
        return col_no

    if mstSvt_db:
        return int(mstSvt_db)
    return col_no


async def get_ce_id(conn: AsyncConnection, col_no: int) -> int:
    if col_no == 0:
        return 0
    stmt = (
        select(mstSvt.c.id)
        .where(
            and_(
                mstSvt.c.collectionNo == col_no, mstSvt.c.type == SvtType.SERVANT_EQUIP
            )
        )
        .limit(1)
    )

    try:
        mstSvt_db = (await conn.execute(stmt)).scalar()
    except DBAPIError:
        return col_no

    if mstSvt_db:
        return int(mstSvt_db)
    return col_no


@dataclass
class SvtLimit:
    svt_id: int
    limit: int


async def get_svt_limit_add(
    conn: AsyncConnection, svt_limits: Iterable[SvtLimit]
) -> list[MstSvtLimitAdd]:
    if not svt_limits:
        return []

    stmt = select(mstSvtLimitAdd).where(
        or_(
            *[
                and_(
                    mstSvtLimitAdd.c.svtId == svt_limit.svt_id,
                    mstSvtLimitAdd.c.limitCount == svt_limit.limit,
                )
                for svt_limit in svt_limits
            ]
        )
    )

    return [
        MstSvtLimitAdd.from_orm(db_row)
        for db_row in (await conn.execute(stmt)).fetchall()
    ]


async def get_svt_script(
    conn: AsyncConnection, svt_ids: list[int]
) -> list[MstSvtScript]:
    stmt = (
        select(mstSvtScript)
        .where((mstSvtScript.c.id // 10).in_(set(svt_ids)))
        .order_by(mstSvtScript.c.id, mstSvtScript.c.form)
    )
    return [
        MstSvtScript.from_orm(db_row)
        for db_row in (await conn.execute(stmt)).fetchall()
    ]


async def get_mstSvtVoice(
    conn: AsyncConnection, svt_ids: Iterable[int]
) -> list[MstSvtVoice]:
    mstSvtVoice_stmt = (
        select(mstSvtVoice)
        .where(mstSvtVoice.c.id.in_(svt_ids))
        .order_by(mstSvtVoice.c.id, mstSvtVoice.c.voicePrefix, mstSvtVoice.c.type)
    )
    return [
        MstSvtVoice.from_orm(svt_voice)
        for svt_voice in (await conn.execute(mstSvtVoice_stmt)).fetchall()
    ]


async def get_mstVoicePlayCond(
    conn: AsyncConnection, svt_ids: Iterable[int]
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
        for play_cond in (await conn.execute(mstVoicePlayCond_stmt)).fetchall()
    ]


async def get_mstSubtitle(
    conn: AsyncConnection, svt_ids: Iterable[int]
) -> list[GlobalNewMstSubtitle]:
    mstSubtitle_stmt = (
        select(mstSubtitle)
        .where(mstSubtitle.c.svtId.in_(svt_ids))
        .order_by(mstSubtitle.c.id)
    )
    return [
        GlobalNewMstSubtitle.from_orm(subtitle)
        for subtitle in (await conn.execute(mstSubtitle_stmt)).fetchall()
    ]


async def get_svt_ids(conn: AsyncConnection, svt_colNos: Iterable[int]) -> set[int]:
    stmt = select(mstSvt.c.id).where(
        or_(mstSvt.c.collectionNo.in_(svt_colNos), mstSvt.c.id.in_(svt_colNos))
    )
    return {int(mstSvt.id) for mstSvt in (await conn.execute(stmt)).fetchall()}


async def get_svt_groups(conn: AsyncConnection, svt_ids: Iterable[int]) -> set[int]:
    stmt = select(mstSvtGroup.c.id).where(mstSvtGroup.c.svtId.in_(svt_ids))
    return {int(group_id.id) for group_id in (await conn.execute(stmt)).fetchall()}


def voice_cond_pattern(
    condType: int, value: int
) -> list[dict[str, list[dict[str, int]]]]:
    return [{"conds": [{"condType": condType, "value": value}]}]


async def get_svt_search(
    conn: AsyncConnection,
    svt_type_ints: Optional[Iterable[int]] = None,
    svt_flag_ints: Optional[Iterable[int]] = None,
    excludeCollectionNo: Optional[Iterable[int]] = None,
    class_ints: Optional[Iterable[int]] = None,
    gender_ints: Optional[Iterable[int]] = None,
    attribute_ints: Optional[Iterable[int]] = None,
    trait_ints: Optional[Iterable[int]] = None,
    not_trait_ints: Optional[Iterable[int]] = None,
    rarity_ints: Optional[Iterable[int]] = None,
    cond_svt_value: Optional[set[int]] = None,
    cond_group_value: Optional[set[int]] = None,
    illustrator: Optional[str] = None,
    cv: Optional[str] = None,
    profile_contains: Optional[str] = None,
) -> list[MstSvt]:
    from_clause: Union[Join, Table] = mstSvt
    where_clause: list[_ColumnExpressionArgument[bool]] = [true()]

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
    if trait_ints or not_trait_ints:
        from_clause = from_clause.outerjoin(
            mstSvtLimitAdd, mstSvtLimitAdd.c.svtId == mstSvt.c.id
        ).outerjoin(mstSvtIndividuality, mstSvtIndividuality.c.svtId == mstSvt.c.id)
    if trait_ints:
        where_clause.append(
            mstSvt.c.individuality.op("||")(mstSvtLimitAdd.c.individuality)
            .op("||")(mstSvtIndividuality.c.individuality)
            .contains(trait_ints)
        )
    if not_trait_ints:
        where_clause.append(
            not_(
                mstSvt.c.individuality.op("||")(mstSvtLimitAdd.c.individuality)
                .op("||")(mstSvtIndividuality.c.individuality)
                .overlap(not_trait_ints)
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

    or_voice_clause: list[_ColumnExpressionArgument[bool]] = []
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
    if profile_contains:
        from_clause = from_clause.outerjoin(
            mstSvtComment, mstSvtComment.c.svtId == mstSvt.c.id
        )
        where_clause.append(mstSvtComment.c.comment.op("&@~")(profile_contains))

    svt_search_stmt = (
        select(mstSvt).distinct().select_from(from_clause).where(and_(*where_clause))
    )

    return [
        MstSvt.from_orm(svt) for svt in (await conn.execute(svt_search_stmt)).fetchall()
    ]
