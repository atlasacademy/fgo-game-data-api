from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncConnection

from ....config import Settings
from ....core.nice.gift import GiftData, get_nice_common_consume, get_nice_gifts
from ....core.nice.item import get_nice_item_from_raw
from ....core.raw import get_raw_mstShop, get_shop_entities
from ....data.shop import get_shop_cost_item_id
from ....schemas.common import Language, Region
from ....schemas.enums import NiceItemBGType
from ....schemas.gameenums import (
    COND_TYPE_NAME,
    PAY_TYPE_NAME,
    PURCHASE_TYPE_NAME,
    SHOP_TYPE_NAME,
    NiceItemType,
    PayType,
    PurchaseType,
)
from ....schemas.nice import (
    AssetURL,
    NiceGift,
    NiceItem,
    NiceItemAmount,
    NiceItemSet,
    NiceShop,
    NiceShopRelease,
)
from ....schemas.raw import (
    MstCommonConsume,
    MstGift,
    MstSetItem,
    MstShop,
    MstShopRelease,
    MstShopScript,
)
from ...utils import fmt_url
from ..base_script import get_script_url


settings = Settings()


def get_nice_set_item(
    region: Region, set_item: MstSetItem, gift_data: GiftData
) -> NiceItemSet:
    return NiceItemSet(
        id=set_item.id,
        purchaseType=PURCHASE_TYPE_NAME[set_item.purchaseType],
        targetId=set_item.targetId,
        setNum=set_item.setNum,
        gifts=get_nice_gifts(region, set_item.targetId, gift_data)
        if set_item.purchaseType == PurchaseType.GIFT
        else [],
    )


def get_nice_shop_release(shop_release: MstShopRelease) -> NiceShopRelease:
    return NiceShopRelease(
        condValues=shop_release.condValues,
        shopId=shop_release.shopId,
        condType=COND_TYPE_NAME[shop_release.condType],
        condNum=shop_release.condNum,
        priority=shop_release.priority,
        isClosedDisp=shop_release.isClosedDisp,
        closedMessage=shop_release.closedMessage,
        closedItemName=shop_release.closedItemName,
    )


def get_nice_shop(
    region: Region,
    shop: MstShop,
    set_items: list[MstSetItem],
    shop_scripts: dict[int, MstShopScript],
    item_map: dict[int, NiceItem],
    gift_data: GiftData,
    raw_consumes: list[MstCommonConsume],
    shop_releases: list[MstShopRelease],
) -> NiceShop:
    shop_item_id = get_shop_cost_item_id(shop)

    if shop.purchaseType == PurchaseType.SET_ITEM:
        shop_set_items = [
            get_nice_set_item(region, set_item, gift_data)
            for set_item in set_items
            if set_item.id in shop.targetIds
        ]
    else:
        shop_set_items = []

    if shop.payType in (PayType.FREE, PayType.COMMON_CONSUME):
        cost = NiceItemAmount(
            item=NiceItem(
                id=0,
                name="",
                originalName="",
                type=NiceItemType.stone,
                uses=[],
                detail="",
                individuality=[],
                icon=fmt_url(
                    AssetURL.items,
                    base_url=settings.asset_url,
                    region=region,
                    item_id=0,
                ),
                background=NiceItemBGType.zero,
                value=0,
                priority=0,
                dropPriority=0,
                startedAt=0,
                endedAt=0,
                itemSelects=[],
            ),
            amount=0,
        )
    else:
        cost = NiceItemAmount(item=item_map[shop_item_id], amount=shop.prices[0])

    if shop.payType == PayType.COMMON_CONSUME:
        common_consumes = [
            get_nice_common_consume(consume)
            for consume in raw_consumes
            if consume.id in shop.itemIds
        ]
    else:
        common_consumes = []

    gifts: list[NiceGift] = []
    if shop.purchaseType == PurchaseType.GIFT:  # pragma: no cover
        for gift_id in shop.targetIds:
            gifts += get_nice_gifts(region, gift_id, gift_data)

    nice_shop = NiceShop(
        id=shop.id,
        baseShopId=shop.baseShopId,
        shopType=SHOP_TYPE_NAME[shop.shopType],
        releaseConditions=[
            get_nice_shop_release(release)
            for release in shop_releases
            if release.shopId == shop.id
        ],
        eventId=shop.eventId,
        slot=shop.slot,
        priority=shop.priority,
        name=shop.name,
        detail=shop.detail,
        infoMessage=shop.infoMessage,
        warningMessage=shop.warningMessage,
        payType=PAY_TYPE_NAME[shop.payType],
        cost=cost,
        consumes=common_consumes,
        purchaseType=PURCHASE_TYPE_NAME[shop.purchaseType],
        targetIds=shop.targetIds,
        itemSet=shop_set_items,
        gifts=gifts,
        setNum=shop.setNum,
        limitNum=shop.limitNum,
        defaultLv=shop.defaultLv,
        defaultLimitCount=shop.defaultLimitCount,
        image=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=shop.imageId,
        )
        if shop.imageId != 0
        else None,
        openedAt=shop.openedAt,
        closedAt=shop.closedAt,
    )

    if shop.id in shop_scripts:
        shop_script = shop_scripts[shop.id]
        nice_shop.scriptName = shop_script.name
        nice_shop.scriptId = shop_script.scriptId
        nice_shop.script = get_script_url(region, shop_script.scriptId)

    return nice_shop


async def get_nice_shops_from_raw(
    conn: AsyncConnection,
    region: Region,
    shops: list[MstShop],
    lang: Language,
) -> list[NiceShop]:
    raw_shops = await get_shop_entities(conn, shops)
    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for shop in raw_shops:
        for gift in shop.mstGift:
            gift_maps[gift.id].append(gift)
    gift_data = GiftData(
        [gift_add for shop in raw_shops for gift_add in shop.mstGiftAdd], gift_maps
    )
    script_map = {
        shop.mstShopScript.shopId: shop.mstShopScript
        for shop in raw_shops
        if shop.mstShopScript
    }
    item_map = {
        item.id: get_nice_item_from_raw(region, item, lang)
        for shop in raw_shops
        for item in shop.mstItem
    }
    return [
        get_nice_shop(
            region=region,
            shop=shop.mstShop,
            set_items=shop.mstSetItem,
            shop_scripts=script_map,
            item_map=item_map,
            raw_consumes=shop.mstCommonConsume,
            gift_data=gift_data,
            shop_releases=shop.mstShopRelease,
        )
        for shop in raw_shops
    ]


async def get_nice_shop_from_raw(
    conn: AsyncConnection,
    region: Region,
    shop_id: int,
    lang: Language,
) -> NiceShop:
    raw_shop = await get_raw_mstShop(conn, shop_id)
    return (await get_nice_shops_from_raw(conn, region, [raw_shop], lang))[0]
