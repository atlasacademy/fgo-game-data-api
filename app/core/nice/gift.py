from typing import List

from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import GIFT_TYPE_NAME
from ...schemas.nice import NiceGift


def get_nice_gift(region: Region, gift_id: int) -> List[NiceGift]:
    raw_gifts = masters[region].mstGiftId.get(gift_id, [])
    return [
        NiceGift(
            id=raw_gift.id,
            type=GIFT_TYPE_NAME[raw_gift.type],
            objectId=raw_gift.objectId,
            priority=raw_gift.priority,
            num=raw_gift.num,
        )
        for raw_gift in raw_gifts
    ]
