from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import (
    EVENT_TYPE_NAME,
    ITEM_BG_TYPE_NAME,
    PAY_TYPE_NAME,
    PURCHASE_TYPE_NAME,
    SHOP_TYPE_NAME,
    PayType,
)
from ...schemas.nice import (
    AssetURL,
    NiceEvent,
    NiceEventPointBuff,
    NiceEventReward,
    NiceItemAmount,
    NiceShop,
)
from ...schemas.raw import MstEventPointBuff, MstEventReward, MstShop
from .. import raw
from .gift import get_nice_gift
from .item import get_nice_item


settings = Settings()


def get_nice_shop(region: Region, shop: MstShop) -> NiceShop:
    if shop.payType == PayType.FRIEND_POINT:
        shop_item_id = 4
    elif shop.payType == PayType.MANA:
        shop_item_id = 3
    else:
        shop_item_id = shop.itemIds[0]

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
    region: Region, reward: MstEventReward, event_id: int
) -> NiceEventReward:
    return NiceEventReward(
        groupId=reward.groupId,
        point=reward.point,
        gifts=get_nice_gift(region, reward.giftId),
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


def get_nice_event(conn: Connection, region: Region, event_id: int) -> NiceEvent:
    raw_event = raw.get_event_entity(conn, region, event_id)

    base_settings = {"base_url": settings.asset_url, "region": region}
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
        warIds=(war.id for war in masters[region].mstWarEventId.get(event_id, [])),
        shop=(get_nice_shop(region, shop) for shop in raw_event.mstShop),
        rewards=(
            get_nice_reward(region, reward, event_id)
            for reward in raw_event.mstEventReward
        ),
        pointBuffs=(
            get_nice_pointBuff(region, pointBuff)
            for pointBuff in raw_event.mstEventPointBuff
        ),
    )

    return nice_event
