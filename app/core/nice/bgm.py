from fastapi import HTTPException
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...core.nice.gift import GiftData
from ...db.helpers.bgm import search_bgm
from ...schemas.common import Language, Region
from ...schemas.gameenums import COND_TYPE_NAME, BgmFlag
from ...schemas.nice import AssetURL, NiceBgm, NiceBgmEntity, NiceBgmRelease
from ...schemas.raw import BgmEntity, MstBgm, MstBgmRelease, MstClosedMessage
from ..raw import get_bgm_entity
from ..utils import fmt_url, get_translation
from .event.shop import get_nice_shop
from .item import get_nice_item_from_raw


settings = Settings()


def get_bgm_url(region: Region, raw_bgm: MstBgm) -> HttpUrl | None:
    base_folder = (
        raw_bgm.fileLocation.removeprefix("Audio/").removesuffix(".cpk.bytes")
        if hasattr(raw_bgm, "fileLocation") and raw_bgm.fileLocation
        else raw_bgm.fileName
    )
    return (
        fmt_url(
            AssetURL.audio,
            base_url=settings.asset_url,
            region=region,
            folder=base_folder,
            id=raw_bgm.fileName,
        )
        if raw_bgm.fileName != ""
        else None
    )


def get_nice_bgm(region: Region, raw_bgm: MstBgm | None, lang: Language) -> NiceBgm:
    if raw_bgm:
        return NiceBgm(
            id=raw_bgm.id,
            name=get_translation(lang, raw_bgm.name),
            originalName=raw_bgm.name,
            fileName=raw_bgm.fileName,
            notReleased=raw_bgm.flag == BgmFlag.IS_NOT_RELEASE,
            audioAsset=get_bgm_url(region, raw_bgm),
        )
    else:
        return NiceBgm(
            id=0,
            name="",
            originalName="",
            fileName="",
            notReleased=True,
        )


def get_nice_bgm_release(
    raw_release: MstBgmRelease, closed_messages: list[MstClosedMessage]
) -> NiceBgmRelease:
    closed_message = next(
        (
            message
            for message in closed_messages
            if message.id == raw_release.closedMessageId
        ),
        None,
    )
    return NiceBgmRelease(
        id=raw_release.id,
        type=COND_TYPE_NAME[raw_release.type],
        condGroup=raw_release.condGroup,
        targetIds=raw_release.targetIds,
        vals=raw_release.vals,
        priority=raw_release.priority,
        closedMessage=closed_message.message if closed_message else "",
    )


def get_nice_bgm_entity_from_raw(
    region: Region, bgm_entity: BgmEntity, lang: Language
) -> NiceBgmEntity:
    nice_bgm = NiceBgmEntity(
        id=bgm_entity.mstBgm.id,
        name=get_translation(lang, bgm_entity.mstBgm.name),
        originalName=bgm_entity.mstBgm.name,
        fileName=bgm_entity.mstBgm.fileName,
        audioAsset=get_bgm_url(region, bgm_entity.mstBgm),
        priority=bgm_entity.mstBgm.priority,
        detail=bgm_entity.mstBgm.detail,
        notReleased=bgm_entity.mstBgm.flag == BgmFlag.IS_NOT_RELEASE,
        logo=fmt_url(
            AssetURL.bgmLogo,
            base_url=settings.asset_url,
            region=region,
            logo_id=bgm_entity.mstBgm.logoId,
        ),
        releaseConditions=[
            get_nice_bgm_release(release, bgm_entity.mstClosedMessage)
            for release in bgm_entity.mstBgmRelease
        ],
    )

    if (
        bgm_entity.mstBgm.flag != BgmFlag.IS_NOT_RELEASE
        and bgm_entity.mstShop is not None
        and bgm_entity.mstItem is not None
    ):
        item_map = {
            bgm_entity.mstItem.id: get_nice_item_from_raw(
                region, bgm_entity.mstItem, lang
            )
        }
        nice_bgm.shop = get_nice_shop(
            region, bgm_entity.mstShop, [], {}, item_map, GiftData([], {}), [], [], []
        )

    return nice_bgm


async def get_nice_bgm_entity(
    conn: AsyncConnection,
    region: Region,
    bgm_id: int,
    lang: Language,
    file_name: str | None = None,
) -> NiceBgmEntity:
    if bgm_id == -1 and file_name:
        found_bgm_id = await search_bgm(conn, file_name)
        if not found_bgm_id:
            raise HTTPException(status_code=404, detail="BGM not found")
        bgm_entity = await get_bgm_entity(conn, found_bgm_id)
    else:
        bgm_entity = await get_bgm_entity(conn, bgm_id)
    return get_nice_bgm_entity_from_raw(region, bgm_entity, lang)


def get_all_nice_bgms(
    region: Region, lang: Language, bgms: list[BgmEntity]
) -> list[NiceBgmEntity]:  # pragma: no cover
    return [
        get_nice_bgm_entity_from_raw(region, bgm_entity, lang) for bgm_entity in bgms
    ]
