from typing import Iterable

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import literal, select

from ...models.raw import AssetManifest
from ...schemas.common import Region

AUDIO_MANIFEST_ID = "Audio"

_audio_manifest_loaded: set[Region] = set()


async def get_audio_urls(
    conn: AsyncConnection, file_names: Iterable[str]
) -> dict[str, str]:
    """Asset manifest file name -> asset URL, for the names that exist."""
    names = list(file_names)
    if not names:
        return {}

    stmt = select(AssetManifest.c.fileName, AssetManifest.c.sourceUrl).where(
        AssetManifest.c.manifestId == AUDIO_MANIFEST_ID,
        AssetManifest.c.fileName.in_(names),
    )

    return {row.fileName: row.sourceUrl for row in await conn.execute(stmt)}


async def audio_manifest_loaded(conn: AsyncConnection, region: Region) -> bool:
    """Does this region have an audio manifest to check against?

    Only the "yes" is remembered. The loader rewrites the table inside one
    transaction, so a region that has the manifest can't stop having it, while a
    database that hasn't loaded it yet gets one after the next update and must
    not be written off for the life of the process.
    """
    if region in _audio_manifest_loaded:
        return True

    stmt = (
        select(literal(1))
        .where(AssetManifest.c.manifestId == AUDIO_MANIFEST_ID)
        .limit(1)
    )

    if (await conn.execute(stmt)).fetchone() is None:
        logger.warning(
            f"{region} AssetManifest has no {AUDIO_MANIFEST_ID} rows, "
            "subtitle audio URLs are unverified guesses."
        )
        return False

    _audio_manifest_loaded.add(region)
    return True
