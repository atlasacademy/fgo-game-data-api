from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.gameenums import COND_TYPE_NAME
from ...schemas.nice import NiceCommonRelease
from ...schemas.raw import MstCommonRelease
from ..raw import get_common_releases


def get_nice_common_release(release: MstCommonRelease) -> NiceCommonRelease:
    return NiceCommonRelease(
        id=release.id,
        priority=release.priority,
        condGroup=release.condGroup,
        condType=COND_TYPE_NAME[release.condType],
        condId=release.condId,
        condNum=release.condNum,
    )


def get_nice_common_releases(
    raw_releases: list[MstCommonRelease], release_id: int | None = None
) -> list[NiceCommonRelease]:
    return [
        get_nice_common_release(release)
        for release in raw_releases
        if release_id is None or release.id == release_id
    ]


async def get_nice_common_releases_from_id(
    conn: AsyncConnection, common_release_id: int
) -> list[NiceCommonRelease]:
    return [
        get_nice_common_release(common_release)
        for common_release in await get_common_releases(conn, [common_release_id])
    ]
