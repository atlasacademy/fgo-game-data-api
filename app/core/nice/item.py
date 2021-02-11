from typing import List

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import ITEM_BG_TYPE_NAME, ITEM_TYPE_NAME, NiceItemUse
from ...schemas.nice import AssetURL, NiceItem, NiceItemAmount
from ...schemas.raw import MstItem
from ..utils import get_traits_list


settings = Settings()


def get_item_use(region: Region, item_id: int) -> List[NiceItemUse]:
    item_uses: List[NiceItemUse] = []

    for use_type, use_table in (
        (NiceItemUse.skill, masters[region].mstCombineSkillItem),
        (NiceItemUse.ascension, masters[region].mstCombineLimitItem),
        (NiceItemUse.costume, masters[region].mstCombineCostumeItem),
    ):
        if item_id in use_table:
            item_uses.append(use_type)

    return item_uses


def get_nice_item(region: Region, item_id: int) -> NiceItem:
    raw_item = masters[region].mstItemId[item_id]
    return get_nice_item_from_raw(region, raw_item)


def get_nice_item_from_raw(region: Region, raw_item: MstItem) -> NiceItem:
    return NiceItem(
        id=raw_item.id,
        name=raw_item.name,
        type=ITEM_TYPE_NAME[raw_item.type],
        uses=get_item_use(region, raw_item.id),
        detail=raw_item.detail,
        individuality=get_traits_list(raw_item.individuality),
        icon=AssetURL.items.format(
            base_url=settings.asset_url, region=region, item_id=raw_item.imageId
        ),
        background=ITEM_BG_TYPE_NAME[raw_item.bgImageId],
        priority=raw_item.priority,
        dropPriority=raw_item.dropPriority,
    )


def get_nice_item_amount(
    region: Region, item_list: List[int], amount_list: List[int]
) -> List[NiceItemAmount]:
    return [
        NiceItemAmount(item=get_nice_item(region, item_id), amount=amount)
        for item_id, amount in zip(item_list, amount_list)
    ]
