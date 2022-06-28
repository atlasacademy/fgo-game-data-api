from pydantic import DirectoryPath

from ..schemas.raw import MstGift
from .utils import load_master_data


def get_gift_with_index(gamedata_path: DirectoryPath) -> list[MstGift]:
    mstGift = load_master_data(gamedata_path, MstGift)

    for idx, gift in enumerate(mstGift):
        gift.sort_id = idx

    return mstGift
