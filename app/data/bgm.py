from pydantic import DirectoryPath

from ..schemas.raw import AssetStorageLine, MstBgm
from .utils import load_master_data


def get_bgms(
    gamedata_path: DirectoryPath, asset_lines: list[AssetStorageLine]
) -> list[MstBgm]:
    mstBgms = load_master_data(gamedata_path, MstBgm)

    audio_locations = {
        asset_detail.fileName: asset_detail.path for asset_detail in asset_lines
    }

    for bgm in mstBgms:
        bgm.fileLocation = audio_locations.get(f"{bgm.fileName}.cpk.bytes", None)

    return mstBgms
