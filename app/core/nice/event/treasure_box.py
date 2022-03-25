from ....schemas.nice import NiceEventTreasureBox, NiceEventTreasureBoxGift
from ....schemas.raw import (
    MstCommonConsume,
    MstGift,
    MstTreasureBox,
    MstTreasureBoxGift,
)
from .utils import get_nice_common_consume, get_nice_gifts


def get_nice_treasure_box_gift(
    box_gift: MstTreasureBoxGift, gift_maps: dict[int, list[MstGift]]
) -> NiceEventTreasureBoxGift:
    return NiceEventTreasureBoxGift(
        id=box_gift.id,
        idx=box_gift.idx,
        gifts=get_nice_gifts(box_gift.giftId, gift_maps),
        collateralUpperLimit=box_gift.collateralUpperLimit,
    )


def get_nice_treasure_box(
    treasure_box: MstTreasureBox,
    box_gifts: list[MstTreasureBoxGift],
    gift_maps: dict[int, list[MstGift]],
    common_consumes: dict[int, MstCommonConsume],
) -> NiceEventTreasureBox:
    return NiceEventTreasureBox(
        slot=treasure_box.slot,
        id=treasure_box.id,
        idx=treasure_box.idx,
        treasureBoxGifts=[
            get_nice_treasure_box_gift(box_gift, gift_maps)
            for box_gift in box_gifts
            if box_gift.id == treasure_box.treasureBoxGiftId
        ],
        maxDrawNumOnce=treasure_box.maxDrawNumOnce,
        extraGifts=get_nice_gifts(treasure_box.extraGiftId, gift_maps),
        commonConsume=get_nice_common_consume(
            common_consumes[treasure_box.commonConsumeId]
        ),
    )
