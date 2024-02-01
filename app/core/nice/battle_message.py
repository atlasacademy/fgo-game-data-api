from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.nice import NiceBattleMessage, NiceBattleMessageGroup
from ...schemas.raw import (
    BattleMessageEntity,
    BattleMessageGroupEntity,
    MstBattleMessage,
    MstCommonRelease,
)
from .. import raw
from .common_release import get_nice_common_releases


def get_nice_battle_message(
    message: MstBattleMessage, raw_releases: list[MstCommonRelease]
) -> NiceBattleMessage:
    return NiceBattleMessage(
        id=message.id,
        idx=message.idx,
        priority=message.priority,
        releaseConditions=get_nice_common_releases(
            raw_releases, message.commonReleaseId
        ),
        motionId=message.motionId,
        message=message.message,
        script=message.script,
    )


async def get_nice_battle_messages(
    conn: AsyncConnection,
    message_id: int,
    mstBattleMessage: BattleMessageEntity | None = None,
) -> list[NiceBattleMessage]:
    if not mstBattleMessage:
        mstBattleMessage = await raw.get_battle_message_entity(conn, message_id)
    return [
        get_nice_battle_message(message, mstBattleMessage.mstCommonRelease)
        for message in mstBattleMessage.mstBattleMessage
    ]


async def get_nice_battle_message_groups(
    conn: AsyncConnection,
    group_id: int,
    mstBattleMessageGroup: BattleMessageGroupEntity | None = None,
) -> list[NiceBattleMessageGroup]:
    if not mstBattleMessageGroup:
        mstBattleMessageGroup = await raw.get_battle_message_group_entity(
            conn, group_id
        )
    return [
        NiceBattleMessageGroup(
            groupId=group.groupId,
            probability=group.probability,
            messages=[
                get_nice_battle_message(message, mstBattleMessageGroup.mstCommonRelease)
                for message in mstBattleMessageGroup.mstBattleMessage
                if message.id == group.messageId
            ],
        )
        for group in mstBattleMessageGroup.mstBattleMessageGroup
    ]
