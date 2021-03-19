from ...schemas.gameenums import GIFT_TYPE_NAME
from ...schemas.nice import NiceGift
from ...schemas.raw import MstGift


def get_nice_gift(raw_gift: MstGift) -> NiceGift:
    return NiceGift(
        id=raw_gift.id,
        type=GIFT_TYPE_NAME[raw_gift.type],
        objectId=raw_gift.objectId,
        priority=raw_gift.priority,
        num=raw_gift.num,
    )
