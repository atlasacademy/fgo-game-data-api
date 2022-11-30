from ..schemas.gameenums import PayType
from ..schemas.raw import MstShop


def get_shop_cost_item_id(shop: MstShop) -> int:
    if shop.payType == PayType.FRIEND_POINT:
        return 4
    elif shop.payType == PayType.MANA:
        return 3
    elif shop.payType == PayType.COMMON_CONSUME:
        return 0
    else:
        return shop.itemIds[0]
