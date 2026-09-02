from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import select

from ...models.raw import AssetManifest

AUDIO_MANIFEST_ID = "Audio"


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
