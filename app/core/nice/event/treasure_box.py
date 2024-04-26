from ....schemas.common import Region
from ....schemas.nice import NiceEventTreasureBox, NiceEventTreasureBoxGift
from ....schemas.raw import MstCommonConsume, MstTreasureBox, MstTreasureBoxGift
from ..gift import GiftData, get_nice_common_consume, get_nice_gifts


def get_nice_treasure_box_gift(
    region: Region, box_gift: MstTreasureBoxGift, gift_data: GiftData
) -> NiceEventTreasureBoxGift:
    return NiceEventTreasureBoxGift(
        id=box_gift.id,
        idx=box_gift.idx,
        gifts=get_nice_gifts(region, box_gift.giftId, gift_data),
        collateralUpperLimit=box_gift.collateralUpperLimit,
    )


def get_nice_treasure_box(
    region: Region,
    treasure_box: MstTreasureBox,
    box_gifts: list[MstTreasureBoxGift],
    gift_data: GiftData,
    raw_consumes: list[MstCommonConsume],
) -> NiceEventTreasureBox:
    return NiceEventTreasureBox(
        slot=treasure_box.slot,
        id=treasure_box.id,
        idx=treasure_box.idx,
        treasureBoxGifts=[
            get_nice_treasure_box_gift(region, box_gift, gift_data)
            for box_gift in box_gifts
            if box_gift.id == treasure_box.treasureBoxGiftId
        ],
        maxDrawNumOnce=treasure_box.maxDrawNumOnce,
        extraGifts=get_nice_gifts(region, treasure_box.extraGiftId, gift_data),
        consumes=[
            get_nice_common_consume(consume)
            for consume in raw_consumes
            if consume.id == treasure_box.commonConsumeId
        ],
    )
