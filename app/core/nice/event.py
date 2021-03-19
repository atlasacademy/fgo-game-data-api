from collections import defaultdict

from sqlalchemy.engine import Connection

from ...config import Settings
from ...schemas.common import Region
from ...schemas.enums import ITEM_BG_TYPE_NAME
from ...schemas.gameenums import (
    COND_TYPE_NAME,
    DETAIL_MISSION_LINK_TYPE,
    EVENT_TYPE_NAME,
    MISSION_PROGRESS_TYPE_NAME,
    MISSION_REWARD_TYPE_NAME,
    MISSION_TYPE_NAME,
    PAY_TYPE_NAME,
    PURCHASE_TYPE_NAME,
    SHOP_TYPE_NAME,
    BoxGachaFlag,
    CondType,
    PayType,
    PurchaseType,
)
from ...schemas.nice import (
    AssetURL,
    NiceEvent,
    NiceEventLottery,
    NiceEventLotteryBox,
    NiceEventMission,
    NiceEventMissionCondition,
    NiceEventMissionConditionDetail,
    NiceEventPointBuff,
    NiceEventReward,
    NiceEventTower,
    NiceEventTowerReward,
    NiceGift,
    NiceItemAmount,
    NiceItemSet,
    NiceShop,
)
from ...schemas.raw import (
    MstBoxGacha,
    MstBoxGachaBase,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventPointBuff,
    MstEventReward,
    MstEventTower,
    MstEventTowerReward,
    MstGift,
    MstSetItem,
    MstShop,
)
from .. import raw
from ..utils import get_traits_list
from .gift import get_nice_gift
from .item import get_nice_item


settings = Settings()


def get_nice_gifts(gift_id: int, gift_maps: dict[int, list[MstGift]]) -> list[NiceGift]:
    return [get_nice_gift(gift) for gift in gift_maps[gift_id]]


def get_nice_set_item(set_item: MstSetItem) -> NiceItemSet:
    return NiceItemSet(
        id=set_item.id,
        purchaseType=PURCHASE_TYPE_NAME[set_item.purchaseType],
        targetId=set_item.targetId,
        setNum=set_item.setNum,
    )


def get_nice_shop(
    region: Region, shop: MstShop, set_items: list[MstSetItem]
) -> NiceShop:
    if shop.payType == PayType.FRIEND_POINT:
        shop_item_id = 4
    elif shop.payType == PayType.MANA:
        shop_item_id = 3
    else:
        shop_item_id = shop.itemIds[0]

    if shop.purchaseType == PurchaseType.SET_ITEM:
        shop_set_items = [
            get_nice_set_item(set_item)
            for set_item in set_items
            if set_item.id in shop.targetIds
        ]
    else:
        shop_set_items = []

    return NiceShop(
        id=shop.id,
        baseShopId=shop.baseShopId,
        shopType=SHOP_TYPE_NAME[shop.shopType],
        eventId=shop.eventId,
        slot=shop.slot,
        priority=shop.priority,
        name=shop.name,
        detail=shop.detail,
        infoMessage=shop.infoMessage,
        warningMessage=shop.warningMessage,
        payType=PAY_TYPE_NAME[shop.payType],
        cost=NiceItemAmount(
            item=get_nice_item(region, shop_item_id), amount=shop.prices[0]
        ),
        purchaseType=PURCHASE_TYPE_NAME[shop.purchaseType],
        targetIds=shop.targetIds,
        itemSet=shop_set_items,
        setNum=shop.setNum,
        limitNum=shop.limitNum,
        defaultLv=shop.defaultLv,
        defaultLimitCount=shop.defaultLimitCount,
        openedAt=shop.openedAt,
        closedAt=shop.closedAt,
    )


def get_bgImage_url(region: Region, bgImageId: int, event_id: int, prefix: str) -> str:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return (
        AssetURL.eventReward.format(**base_settings, fname=f"{prefix}{bgImageId}")
        if bgImageId > 0
        else AssetURL.eventReward.format(**base_settings, fname=f"{prefix}{event_id}00")
    )


def get_nice_reward(
    region: Region,
    reward: MstEventReward,
    event_id: int,
    gift_maps: dict[int, list[MstGift]],
) -> NiceEventReward:
    return NiceEventReward(
        groupId=reward.groupId,
        point=reward.point,
        gifts=get_nice_gifts(reward.giftId, gift_maps),
        bgImagePoint=get_bgImage_url(
            region, reward.bgImageId, event_id, "event_rewardpoint_"
        ),
        bgImageGet=get_bgImage_url(
            region, reward.bgImageId, event_id, "event_rewardget_"
        ),
    )


def get_nice_pointBuff(
    region: Region, pointBuff: MstEventPointBuff
) -> NiceEventPointBuff:
    return NiceEventPointBuff.parse_obj(
        {
            "id": pointBuff.id,
            "funcIds": pointBuff.funcIds,
            "groupId": pointBuff.groupId,
            "eventPoint": pointBuff.eventPoint,
            "name": pointBuff.name,
            "detail": pointBuff.detail,
            "icon": AssetURL.items.format(
                base_url=settings.asset_url, region=region, item_id=pointBuff.imageId
            ),
            "background": ITEM_BG_TYPE_NAME[pointBuff.bgImageId],
            "value": pointBuff.value,
        }
    )


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
    if (
        cond.condType == CondType.MISSION_CONDITION_DETAIL
        and cond.targetIds[0] in details
    ):
        nice_mission_cond.detail = get_nice_mission_cond_detail(
            details[cond.targetIds[0]]
        )
    return nice_mission_cond


def get_nice_mission(
    mission: MstEventMission,
    conds: list[MstEventMissionCondition],
    details: dict[int, MstEventMissionConditionDetail],
    gift_maps: dict[int, list[MstGift]],
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
        gifts=get_nice_gifts(mission.giftId, gift_maps),
        bannerGroup=mission.bannerGroup,
        priority=mission.priority,
        rewardRarity=mission.rewardRarity,
        notfyPriority=mission.notfyPriority,
        presentMessageId=mission.presentMessageId,
        conds=(get_nice_mission_cond(cond, details) for cond in conds),
    )


def get_nice_tower_rewards(
    region: Region, reward: MstEventTowerReward, gift_maps: dict[int, list[MstGift]]
) -> NiceEventTowerReward:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceEventTowerReward(
        floor=reward.floor,
        gifts=get_nice_gifts(reward.giftId, gift_maps),
        boardMessage=reward.boardMessage,
        rewardGet=AssetURL.eventReward.format(
            **base_settings,
            fname=f"event_tower_rewardget_{reward.boardImageId}",
        ),
        banner=AssetURL.eventReward.format(
            **base_settings,
            fname=f"event_towerbanner_{reward.boardImageId}",
        ),
    )


def get_nice_event_tower(
    region: Region,
    tower: MstEventTower,
    rewards: list[MstEventTowerReward],
    gift_maps: dict[int, list[MstGift]],
) -> NiceEventTower:
    return NiceEventTower(
        towerId=tower.towerId,
        name=tower.name,
        rewards=[
            get_nice_tower_rewards(region, reward, gift_maps)
            for reward in rewards
            if reward.towerId == tower.towerId
        ],
    )


def get_nice_lottery_box(
    region: Region,
    box: MstBoxGachaBase,
    box_index: int,
    gift_maps: dict[int, list[MstGift]],
) -> NiceEventLotteryBox:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceEventLotteryBox(
        id=box.id,
        boxIndex=box_index,
        no=box.no,
        type=box.type,
        gifts=get_nice_gifts(box.targetId, gift_maps),
        maxNum=box.maxNum,
        isRare=box.isRare,
        priority=box.priority,
        detail=box.detail,
        icon=AssetURL.eventReward.format(
            **base_settings,
            fname=f"icon_event_{box.iconId}",
        ),
        banner=AssetURL.eventReward.format(
            **base_settings,
            fname=f"event_gachabanner_{box.bannerId}",
        ),
    )


def get_nice_lottery(
    region: Region,
    lottery: MstBoxGacha,
    boxes: list[MstBoxGachaBase],
    gift_maps: dict[int, list[MstGift]],
) -> NiceEventLottery:
    nice_boxes: list[NiceEventLotteryBox] = []
    for box_index, base_id in enumerate(lottery.baseIds):
        for box in boxes:
            if box.id == base_id:
                nice_boxes.append(
                    get_nice_lottery_box(region, box, box_index, gift_maps)
                )

    return NiceEventLottery(
        id=lottery.id,
        slot=lottery.slot,
        payType=PAY_TYPE_NAME[lottery.payType],
        cost=NiceItemAmount(
            item=get_nice_item(region, lottery.payTargetId), amount=lottery.payValue
        ),
        priority=lottery.priority,
        limited=lottery.flag == BoxGachaFlag.LIMIT_RESET,
        boxes=nice_boxes,
    )


def get_nice_event(conn: Connection, region: Region, event_id: int) -> NiceEvent:
    raw_event = raw.get_event_entity(conn, event_id)

    base_settings = {"base_url": settings.asset_url, "region": region}

    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in raw_event.mstGift:
        gift_maps[gift.id].append(gift)

    mission_cond_details = {
        detail.id: detail for detail in raw_event.mstEventMissionConditionDetail
    }
    missions = [
        get_nice_mission(
            mission,
            [
                cond
                for cond in raw_event.mstEventMissionCondition
                if cond.missionId == mission.id
            ],
            mission_cond_details,
            gift_maps,
        )
        for mission in raw_event.mstEventMission
    ]

    nice_event = NiceEvent(
        id=raw_event.mstEvent.id,
        type=EVENT_TYPE_NAME[raw_event.mstEvent.type],
        name=raw_event.mstEvent.name,
        shortName=raw_event.mstEvent.shortName,
        detail=raw_event.mstEvent.detail,
        noticeBanner=AssetURL.banner.format(
            **base_settings, banner=f"event_war_{raw_event.mstEvent.noticeBannerId}"
        )
        if raw_event.mstEvent.noticeBannerId != 0
        else None,
        banner=AssetURL.banner.format(
            **base_settings, banner=f"event_war_{raw_event.mstEvent.bannerId}"
        )
        if raw_event.mstEvent.bannerId != 0
        else None,
        icon=AssetURL.banner.format(
            **base_settings, banner=f"banner_icon_{raw_event.mstEvent.iconId}"
        )
        if raw_event.mstEvent.iconId != 0
        else None,
        bannerPriority=raw_event.mstEvent.bannerPriority,
        noticeAt=raw_event.mstEvent.noticeAt,
        startedAt=raw_event.mstEvent.startedAt,
        endedAt=raw_event.mstEvent.endedAt,
        finishedAt=raw_event.mstEvent.finishedAt,
        materialOpenedAt=raw_event.mstEvent.materialOpenedAt,
        warIds=(war.id for war in raw_event.mstWar),
        shop=(
            get_nice_shop(region, shop, raw_event.mstSetItem)
            for shop in raw_event.mstShop
        ),
        rewards=(
            get_nice_reward(region, reward, event_id, gift_maps)
            for reward in raw_event.mstEventReward
        ),
        pointBuffs=(
            get_nice_pointBuff(region, pointBuff)
            for pointBuff in raw_event.mstEventPointBuff
        ),
        missions=missions,
        towers=(
            get_nice_event_tower(
                region, tower, raw_event.mstEventTowerReward, gift_maps
            )
            for tower in raw_event.mstEventTower
        ),
        lotteries=(
            get_nice_lottery(region, lottery, raw_event.mstBoxGachaBase, gift_maps)
            for lottery in raw_event.mstBoxGacha
        ),
    )

    return nice_event
