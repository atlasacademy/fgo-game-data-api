from ....config import Settings
from ....schemas.common import Region
from ....schemas.enums import NiceItemBGType
from ....schemas.gameenums import NiceItemType
from ....schemas.nice import (
    AssetURL,
    NiceEventTradeGoods,
    NiceEventTradePickup,
    NiceItem,
)
from ....schemas.raw import (
    MstCommonConsume,
    MstCommonRelease,
    MstEventTradeGoods,
    MstEventTradePickup,
)
from ...utils import fmt_url
from ..common_release import get_nice_common_releases
from ..gift import GiftData, get_nice_common_consumes, get_nice_gifts

settings = Settings()


def get_nice_trade_pick(pickup: MstEventTradePickup) -> NiceEventTradePickup:
    return NiceEventTradePickup(
        startedAt=pickup.startedAt,
        endedAt=pickup.endedAt,
        tradeTimeRate=pickup.tradeTimeRate,
    )


def get_nice_trade_goods(
    region: Region,
    trade: MstEventTradeGoods,
    pickups: list[MstEventTradePickup],
    gift_data: GiftData,
    raw_consumes: list[MstCommonConsume],
    raw_releases: list[MstCommonRelease],
    item_map: dict[int, NiceItem],
) -> NiceEventTradeGoods:
    dummy_point_item = NiceItem(
        id=5,
        name="",
        originalName="",
        type=NiceItemType.questRewardQp,
        uses=[],
        detail="",
        individuality=[],
        icon=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=5,
        ),
        background=NiceItemBGType.questClearQPReward,
        value=0,
        eventId=0,
        eventGroupId=0,
        priority=0,
        dropPriority=0,
        startedAt=0,
        endedAt=0,
        itemSelects=[],
    )

    return NiceEventTradeGoods(
        id=trade.id,
        name=trade.name,
        goodsIcon=fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{trade.eventId}/icon_{trade.goodsIconId}",
        ),
        gifts=get_nice_gifts(region, trade.giftId, gift_data),
        consumes=get_nice_common_consumes(raw_consumes, trade.commonConsumeId),
        eventPointNum=trade.eventPointNum,
        eventPointItem=item_map.get(trade.eventPointItemId, dummy_point_item),
        tradeTime=trade.tradeTime,
        maxNum=trade.maxNum,
        maxTradeTime=trade.maxTradeTime,
        releaseConditions=get_nice_common_releases(raw_releases, trade.commonReleaseId),
        closedMessage=trade.closedMessage,
        pickups=[
            get_nice_trade_pick(pickup)
            for pickup in pickups
            if pickup.tradeGoodsId == trade.id
        ],
    )
