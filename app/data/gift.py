from pydantic import DirectoryPath

from ..schemas.raw import MstGift
from .utils import load_master_data


def get_gift_with_index(gamedata_path: DirectoryPath) -> list[MstGift]:
    mstGift = load_master_data(gamedata_path, MstGift)
    gift_index: dict[int, int] = {}

    for gift in mstGift:
        if gift.id not in gift_index:
            sort_id = 0
        else:
            sort_id = gift_index[gift.id] + 1
        gift_index[gift.id] = sort_id
        gift.sort_id = sort_id

    return mstGift
