from collections import defaultdict

from pydantic import DirectoryPath

from ..schemas.gameenums import ItemType
from ..schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    MstCombineAppendPassiveSkill,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineSkill,
    MstGift,
    MstGiftAdd,
    MstItem,
    MstItemSelect,
)
from .utils import load_master_data


def get_item_with_use(gamedata_path: DirectoryPath) -> list[MstItem]:
    mstItem = load_master_data(gamedata_path, MstItem)
    mstItemSelect = load_master_data(gamedata_path, MstItemSelect)
    mstGift = load_master_data(gamedata_path, MstGift)
    mstGiftAdd = load_master_data(gamedata_path, MstGiftAdd)
    mstCombineSkill = load_master_data(gamedata_path, MstCombineSkill)
    mstCombineAppendPassiveSkill = load_master_data(
        gamedata_path, MstCombineAppendPassiveSkill
    )
    mstCombineLimit = load_master_data(gamedata_path, MstCombineLimit)
    mstCombineCostume = load_master_data(gamedata_path, MstCombineCostume)

    skill_items = {
        item_id for combine in mstCombineSkill for item_id in combine.itemIds
    }
    append_skill_items = {
        item_id
        for combine in mstCombineAppendPassiveSkill
        for item_id in combine.itemIds
    }
    limit_items = {
        item_id
        for combine in mstCombineLimit
        for item_id in combine.itemIds
        if combine.svtLimit != BAD_COMBINE_SVT_LIMIT
    }
    costume_items = {
        item_id for combine in mstCombineCostume for item_id in combine.itemIds
    }

    item_select_maps: dict[int, list[MstItemSelect]] = defaultdict(list)
    for item_select in mstItemSelect:
        item_select_maps[item_select.itemId].append(item_select)
    gift_maps: dict[int, list[MstGift]] = defaultdict(list)
    for gift in mstGift:
        gift_maps[gift.id].append(gift)
    gift_add_maps: dict[int, list[MstGiftAdd]] = defaultdict(list)
    for gift_add in mstGiftAdd:
        gift_add_maps[gift_add.giftId].append(gift_add)

    for item in mstItem:
        item.useSkill = item.id in skill_items
        item.useAppendSkill = item.id in append_skill_items
        item.useAscension = item.id in limit_items
        item.useCostume = item.id in costume_items
        if item.type == ItemType.ITEM_SELECT:
            item.mstItemSelect = item_select_maps[item.id]
            for item_select in item.mstItemSelect:
                item.mstGift += gift_maps[item_select.candidateGiftId]
                item.mstGiftAdd += gift_add_maps[item_select.candidateGiftId]

    return mstItem
