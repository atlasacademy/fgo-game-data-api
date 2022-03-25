from ....config import Settings
from ....data.shop import get_shop_cost_item_id
from ....schemas.common import Region
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
    NiceItem,
    NiceItemAmount,
    NiceItemSet,
    NiceShop,
    NiceShopRelease,
)
from ....schemas.raw import MstSetItem, MstShop, MstShopRelease, MstShopScript
from ...utils import fmt_url
from ..base_script import get_script_url


settings = Settings()


def get_nice_set_item(set_item: MstSetItem) -> NiceItemSet:
    return NiceItemSet(
        id=set_item.id,
        purchaseType=PURCHASE_TYPE_NAME[set_item.purchaseType],
        targetId=set_item.targetId,
        setNum=set_item.setNum,
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
    shop_releases: list[MstShopRelease],
) -> NiceShop:
    shop_item_id = get_shop_cost_item_id(shop)

    if shop.purchaseType == PurchaseType.SET_ITEM:
        shop_set_items = [
            get_nice_set_item(set_item)
            for set_item in set_items
            if set_item.id in shop.targetIds
        ]
    else:
        shop_set_items = []

    if shop.payType == PayType.FREE:
        cost = NiceItemAmount(
            item=NiceItem(
                id=0,
                name="",
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
                priority=0,
                dropPriority=0,
            ),
            amount=0,
        )
    else:
        cost = NiceItemAmount(item=item_map[shop_item_id], amount=shop.prices[0])

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

    if shop.id in shop_scripts:
        shop_script = shop_scripts[shop.id]
        nice_shop.scriptName = shop_script.name
        nice_shop.scriptId = shop_script.scriptId
        nice_shop.script = get_script_url(region, shop_script.scriptId)

    return nice_shop
