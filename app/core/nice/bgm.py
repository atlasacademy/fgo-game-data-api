from ...config import Settings
from ...schemas.common import Region
from ...schemas.nice import AssetURL, NiceBgm
from ...schemas.raw import MstBgm


settings = Settings()


def get_nice_bgm(region: Region, raw_bgm: MstBgm) -> NiceBgm:
    return NiceBgm(
        id=raw_bgm.id,
        name=raw_bgm.name,
        audioAsset=AssetURL.audio.format(
            base_url=settings.asset_url,
            region=region,
            folder=raw_bgm.fileName,
            id=raw_bgm.fileName,
        )
        if raw_bgm.id != 0
        else None,
    )
