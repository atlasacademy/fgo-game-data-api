from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import ITEM_BG_TYPE_NAME, NiceItemUse
from ...schemas.gameenums import ITEM_TYPE_NAME
from ...schemas.nice import AssetURL, NiceItem, NiceItemAmount
from ...schemas.raw import MstItem
from ..raw import get_item_entity, get_multiple_items
from ..utils import get_traits_list, get_translation


settings = Settings()


def get_item_use(item: MstItem) -> list[NiceItemUse]:
    item_uses: list[NiceItemUse] = []

    for use_type, use_variable in (
        (NiceItemUse.skill, item.useSkill),
        (NiceItemUse.ascension, item.useAscension),
        (NiceItemUse.costume, item.useCostume),
    ):
        if use_variable:
            item_uses.append(use_type)

    return item_uses


async def get_nice_item(
    conn: AsyncConnection, region: Region, item_id: int, lang: Language
) -> NiceItem:
    raw_item = (await get_item_entity(conn, item_id)).mstItem
    return get_nice_item_from_raw(region, raw_item, lang)


def get_nice_item_from_raw(
    region: Region, raw_item: MstItem, lang: Language
) -> NiceItem:
    return NiceItem(
        id=raw_item.id,
        name=get_translation(lang, raw_item.name),
        type=ITEM_TYPE_NAME[raw_item.type],
        uses=get_item_use(raw_item),
        detail=raw_item.detail,
        individuality=get_traits_list(raw_item.individuality),
        icon=AssetURL.items.format(
            base_url=settings.asset_url, region=region, item_id=raw_item.imageId
        ),
        background=ITEM_BG_TYPE_NAME[raw_item.bgImageId],
        priority=raw_item.priority,
        dropPriority=raw_item.dropPriority,
    )


async def get_nice_item_amount(
    conn: AsyncConnection,
    region: Region,
    item_list: list[int],
    amount_list: list[int],
    lang: Language,
) -> list[NiceItemAmount]:
    return [
        NiceItemAmount(item=get_nice_item_from_raw(region, item, lang), amount=amount)
        for item, amount in zip(await get_multiple_items(conn, item_list), amount_list)
    ]


def get_all_nice_items(
    region: Region, lang: Language, mstItems: Iterable[MstItem]
) -> list[NiceItem]:  # pragma: no cover
    return [get_nice_item_from_raw(region, raw_item, lang) for raw_item in mstItems]
