from ...config import Settings
from ...schemas.common import Region
from ...schemas.gameenums import COND_TYPE_NAME, GIFT_TYPE_NAME
from ...schemas.nice import AssetURL, NiceBaseGift, NiceGift, NiceGiftAdd
from ...schemas.raw import MstGift, MstGiftAdd
from ..utils import fmt_url


settings = Settings()


def get_nice_base_gift(raw_gift: MstGift) -> NiceBaseGift:
    return NiceBaseGift(
        id=raw_gift.id,
        type=GIFT_TYPE_NAME[raw_gift.type],
        objectId=raw_gift.objectId,
        priority=raw_gift.priority,
        num=raw_gift.num,
    )


def get_nice_gift_add(
    region: Region, gift_add: MstGiftAdd, prior_gifts: list[MstGift], icon_idx: int
) -> NiceGiftAdd:
    return NiceGiftAdd(
        priority=1 if gift_add.priority is None else gift_add.priority,
        replacementGiftIcon=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=gift_add.priorGiftIconIds[icon_idx],
        ),
        condType=COND_TYPE_NAME[gift_add.condType],
        targetId=gift_add.targetId,
        targetNum=gift_add.targetNum,
        replacementGifts=[get_nice_base_gift(gift) for gift in prior_gifts],
    )


def get_nice_gift_adds(
    region: Region,
    gift: MstGift,
    gift_adds: list[MstGiftAdd],
    gift_maps: dict[int, list[MstGift]],
) -> list[NiceGiftAdd]:
    nice_gift_adds: list[NiceGiftAdd] = []

    for gift_add in gift_adds:
        if gift_add.giftId == gift.id and len(gift_add.priorGiftIconIds) > gift.num:
            nice_gift_adds.append(
                get_nice_gift_add(
                    region, gift_add, gift_maps[gift_add.priorGiftId], gift.num - 1
                )
            )

    return nice_gift_adds


def get_nice_gift(
    region: Region,
    raw_gift: MstGift,
    gift_adds: list[MstGiftAdd],
    gift_maps: dict[int, list[MstGift]],
) -> NiceGift:
    return NiceGift(
        id=raw_gift.id,
        type=GIFT_TYPE_NAME[raw_gift.type],
        objectId=raw_gift.objectId,
        priority=raw_gift.priority,
        num=raw_gift.num,
        giftAdds=get_nice_gift_adds(region, raw_gift, gift_adds, gift_maps),
    )
