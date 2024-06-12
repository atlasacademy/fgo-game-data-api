from sqlalchemy.ext.asyncio import AsyncConnection

from ....schemas.common import Region
from ....schemas.enums import DETAIL_MISSION_LINK_TYPE
from ....schemas.gameenums import (
    COND_TYPE_NAME,
    MISSION_PROGRESS_TYPE_NAME,
    MISSION_REWARD_TYPE_NAME,
    MISSION_TYPE_NAME,
    CondType,
)
from ....schemas.nice import (
    NiceEventMission,
    NiceEventMissionCondition,
    NiceEventMissionConditionDetail,
    NiceEventMissionGroup,
    NiceEventRandomMission,
)
from ....schemas.raw import (
    EventMissionEntity,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventMissionGroup,
    MstEventRandomMission,
)
from ... import raw
from ...utils import get_traits_list
from ..gift import GiftData, get_gift_map, get_nice_gifts


def get_nice_mission_cond_detail(
    cond_detail: MstEventMissionConditionDetail,
) -> NiceEventMissionConditionDetail:
    return NiceEventMissionConditionDetail(
        id=cond_detail.id,
        missionTargetId=cond_detail.missionTargetId,
        missionCondType=cond_detail.missionCondType,
        logicType=cond_detail.logicType,
        targetIds=cond_detail.targetIds,
        addTargetIds=cond_detail.addTargetIds,
        targetQuestIndividualities=get_traits_list(
            cond_detail.targetQuestIndividualities
        ),
        conditionLinkType=DETAIL_MISSION_LINK_TYPE[cond_detail.conditionLinkType],
        targetEventIds=cond_detail.targetEventIds,
    )


def get_nice_mission_cond(
    cond: MstEventMissionCondition, details: dict[int, MstEventMissionConditionDetail]
) -> NiceEventMissionCondition:
    nice_mission_cond = NiceEventMissionCondition(
        id=cond.id,
        missionProgressType=MISSION_PROGRESS_TYPE_NAME[cond.missionProgressType],
        priority=cond.priority,
        missionTargetId=cond.missionTargetId,
        condGroup=cond.condGroup,
        condType=COND_TYPE_NAME[cond.condType],
        targetIds=cond.targetIds,
        targetNum=cond.targetNum,
        conditionMessage=cond.conditionMessage,
        closedMessage=cond.closedMessage,
        flag=cond.flag,
    )

    if cond.condType == CondType.MISSION_CONDITION_DETAIL and cond.targetIds:
        nice_mission_cond.details = [
            get_nice_mission_cond_detail(details[detail_id])
            for detail_id in cond.targetIds
            if detail_id in details
        ]

    return nice_mission_cond


def get_nice_mission(
    region: Region,
    mission: MstEventMission,
    conds: list[MstEventMissionCondition],
    details: dict[int, MstEventMissionConditionDetail],
    gift_data: GiftData,
) -> NiceEventMission:
    return NiceEventMission(
        id=mission.id,
        flag=mission.flag,
        type=MISSION_TYPE_NAME[mission.type],
        missionTargetId=mission.missionTargetId,
        dispNo=mission.dispNo,
        name=mission.name,
        detail=mission.detail,
        startedAt=mission.startedAt,
        endedAt=mission.endedAt,
        closedAt=mission.closedAt,
        rewardType=MISSION_REWARD_TYPE_NAME[mission.rewardType],
        gifts=get_nice_gifts(region, mission.giftId, gift_data),
        bannerGroup=mission.bannerGroup,
        priority=mission.priority,
        rewardRarity=mission.rewardRarity,
        notfyPriority=mission.notfyPriority,
        presentMessageId=mission.presentMessageId,
        conds=[get_nice_mission_cond(cond, details) for cond in conds],
    )


def get_nice_missions(
    region: Region,
    mstEventMission: list[MstEventMission],
    mstEventMissionCondition: list[MstEventMissionCondition],
    mstEventMissionConditionDetail: list[MstEventMissionConditionDetail],
    gift_data: GiftData,
) -> list[NiceEventMission]:
    mission_cond_details = {
        detail.id: detail for detail in mstEventMissionConditionDetail
    }
    missions = [
        get_nice_mission(
            region,
            mission,
            [cond for cond in mstEventMissionCondition if cond.missionId == mission.id],
            mission_cond_details,
            gift_data,
        )
        for mission in mstEventMission
    ]
    return missions


def get_nice_random_mission(
    random_mission: MstEventRandomMission,
) -> NiceEventRandomMission:
    return NiceEventRandomMission(
        missionId=random_mission.missionId,
        missionRank=random_mission.missionRank,
        condType=COND_TYPE_NAME[random_mission.condType],
        condId=random_mission.condId,
        condNum=random_mission.condNum,
    )


def get_nice_mission_groups(
    mission_groups: list[MstEventMissionGroup],
) -> list[NiceEventMissionGroup]:
    group_ids = {group.id for group in mission_groups}
    return [
        NiceEventMissionGroup(
            id=group_id,
            missionIds=[
                group.missionId for group in mission_groups if group.id == group_id
            ],
        )
        for group_id in group_ids
    ]


def get_nice_event_mission_from_raw(
    region: Region, raw_mission: EventMissionEntity
) -> NiceEventMission:
    gift_map = get_gift_map(raw_mission.mstGift)

    return get_nice_mission(
        region,
        raw_mission.mstEventMission,
        raw_mission.mstEventMissionCondition,
        {detail.id: detail for detail in raw_mission.mstEventMissionConditionDetail},
        GiftData(raw_mission.mstGiftAdd, gift_map),
    )


async def get_nice_event_mission(
    conn: AsyncConnection,
    region: Region,
    mission_id: int,
    mstEventMission: MstEventMission | None = None,
) -> NiceEventMission:
    raw_mm = await raw.get_event_mission_entity(conn, mission_id, mstEventMission)
    return get_nice_event_mission_from_raw(region, raw_mm)
