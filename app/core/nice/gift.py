from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...db.helpers import fetch
from ...schemas.common import Region
from ...schemas.gameenums import (
    COMMON_CONSUME_TYPE_NAME,
    COND_TYPE_NAME,
    GIFT_TYPE_NAME,
)
from ...schemas.nice import (
    AssetURL,
    NiceBaseGift,
    NiceCommonConsume,
    NiceGift,
    NiceGiftAdd,
)
from ...schemas.raw import MstCommonConsume, MstGift, MstGiftAdd
from ..utils import fmt_url


settings = Settings()


@dataclass
class GiftData:
    gift_adds: list[MstGiftAdd]
    gift_map: dict[int, list[MstGift]]


def get_gift_map(gifts: list[MstGift]) -> dict[int, list[MstGift]]:
    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in gifts:
        gift_maps[gift.id].append(gift)

    return gift_maps


def gift_sort(gift: MstGift) -> tuple[int, int, int, int, int]:
    return (gift.id, -gift.priority, gift.type, gift.objectId, gift.sort_id)


def get_nice_gifts(region: Region, gift_id: int, gift_data: GiftData) -> list[NiceGift]:
    return [
        get_nice_gift(region, gift, gift_data.gift_adds, gift_data.gift_map)
        for gift in sorted(gift_data.gift_map[gift_id], key=gift_sort)
    ]


def get_nice_common_consume(common_consume: MstCommonConsume) -> NiceCommonConsume:
    return NiceCommonConsume(
        id=common_consume.id,
        priority=common_consume.priority,
        type=COMMON_CONSUME_TYPE_NAME[common_consume.type],
        objectId=common_consume.objectId,
        num=common_consume.num,
    )


def get_nice_common_consumes(
    raw_releases: list[MstCommonConsume], consume_id: int | None = None
) -> list[NiceCommonConsume]:
    return [
        get_nice_common_consume(consume)
        for consume in raw_releases
        if consume_id is None or consume.id == consume_id
    ]


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

    gift_index = sorted(gift.sort_id for gift in gift_maps[gift.id]).index(gift.sort_id)

    for gift_add in gift_adds:
        if gift_add.giftId == gift.id and len(gift_add.priorGiftIconIds) > gift_index:
            nice_gift_adds.append(
                get_nice_gift_add(
                    region, gift_add, gift_maps[gift_add.priorGiftId], gift_index
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


async def get_nice_gifts_from_id(
    conn: AsyncConnection,
    region: Region,
    gift_ids: list[int],
) -> list[NiceGift]:
    gift_adds = await fetch.get_all_multiple(conn, MstGiftAdd, gift_ids)
    replacement_gift_ids = {gift.priorGiftId for gift in gift_adds}

    all_gifts = await fetch.get_all_multiple(
        conn, MstGift, set(gift_ids) | replacement_gift_ids
    )
    gift_maps = get_gift_map(all_gifts)

    gifts = [gift for gift_id in gift_ids for gift in gift_maps[gift_id]]

    return [
        get_nice_gift(region, gift, gift_adds, gift_maps)
        for gift in sorted(gifts, key=gift_sort)
    ]
