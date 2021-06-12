from typing import Optional

from sqlalchemy.engine.base import Connection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.gameenums import COND_TYPE_NAME, BgmFlag
from ...schemas.nice import AssetURL, NiceBgm, NiceBgmEntity, NiceBgmRelease
from ...schemas.raw import BgmEntity, MstBgm, MstBgmRelease, MstClosedMessage
from ..raw import get_bgm_entity
from ..utils import get_translation
from .event import get_nice_shop


settings = Settings()


def get_bgm_url(region: Region, raw_bgm: MstBgm) -> Optional[str]:
    return (
        AssetURL.audio.format(
            base_url=settings.asset_url,
            region=region,
            folder=raw_bgm.fileName,
            id=raw_bgm.fileName,
        )
        if raw_bgm.fileName != ""
        else None
    )


def get_nice_bgm(region: Region, raw_bgm: MstBgm) -> NiceBgm:
    return NiceBgm(
        id=raw_bgm.id,
        name=raw_bgm.name,
        fileName=raw_bgm.fileName,
        notReleased=raw_bgm.flag == BgmFlag.IS_NOT_RELEASE,
        audioAsset=get_bgm_url(region, raw_bgm),
    )


def get_nice_bgm_release(
    raw_release: MstBgmRelease, closed_messages: list[MstClosedMessage]
) -> NiceBgmRelease:
    closed_message = next(
        message
        for message in closed_messages
        if message.id == raw_release.closedMessageId
    )
    return NiceBgmRelease(
        id=raw_release.id,
        type=COND_TYPE_NAME[raw_release.type],
        condGroup=raw_release.condGroup,
        targetIds=raw_release.targetIds,
        vals=raw_release.vals,
        priority=raw_release.priority,
        closedMessage=closed_message.message,
    )


def get_nice_bgm_entity_from_raw(
    conn: Connection, region: Region, bgm_entity: BgmEntity, lang: Language
) -> NiceBgmEntity:
    nice_bgm = NiceBgmEntity(
        id=bgm_entity.mstBgm.id,
        name=get_translation(lang, bgm_entity.mstBgm.name),
        fileName=bgm_entity.mstBgm.fileName,
        audioAsset=get_bgm_url(region, bgm_entity.mstBgm),
        priority=bgm_entity.mstBgm.priority,
        detail=bgm_entity.mstBgm.detail,
        notReleased=bgm_entity.mstBgm.flag == BgmFlag.IS_NOT_RELEASE,
        logo=AssetURL.bgmLogo.format(
            base_url=settings.asset_url,
            region=region,
            logo_id=bgm_entity.mstBgm.logoId,
        ),
        releaseConditions=(
            get_nice_bgm_release(release, bgm_entity.mstClosedMessage)
            for release in bgm_entity.mstBgmRelease
        ),
    )

    if (
        bgm_entity.mstBgm.flag != BgmFlag.IS_NOT_RELEASE
        and bgm_entity.mstShop is not None
    ):
        nice_bgm.shop = get_nice_shop(conn, region, bgm_entity.mstShop, [], {}, lang)

    return nice_bgm


def get_nice_bgm_entity(
    conn: Connection, region: Region, bgm_id: int, lang: Language
) -> NiceBgmEntity:
    bgm_entity = get_bgm_entity(conn, bgm_id)
    return get_nice_bgm_entity_from_raw(conn, region, bgm_entity, lang)


def get_all_nice_bgms(
    conn: Connection, region: Region, lang: Language, bgms: list[BgmEntity]
) -> list[NiceBgmEntity]:  # pragma: no cover
    return [
        get_nice_bgm_entity_from_raw(conn, region, bgm_entity, lang)
        for bgm_entity in bgms
    ]
