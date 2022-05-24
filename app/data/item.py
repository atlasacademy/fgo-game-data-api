from pydantic import DirectoryPath

from ..schemas.raw import (
    BAD_COMBINE_SVT_LIMIT,
    MstCombineAppendPassiveSkill,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineSkill,
    MstItem,
)
from .utils import load_master_data


def get_item_with_use(gamedata_path: DirectoryPath) -> list[MstItem]:
    mstItem = load_master_data(gamedata_path, MstItem)
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

    for item in mstItem:
        item.useSkill = item.id in skill_items
        item.useAppendSkill = item.id in append_skill_items
        item.useAscension = item.id in limit_items
        item.useCostume = item.id in costume_items

    return mstItem
