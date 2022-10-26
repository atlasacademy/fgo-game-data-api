from typing import Optional

from ...config import Settings
from ...schemas.common import Region, RepoInfo
from .. import Redis


settings = Settings()


async def get_repo_version(redis: Redis, region: Region) -> Optional[RepoInfo]:
    redis_key = f"{settings.redis_prefix}:repo_version:{region.name}"
    item_redis = await redis.get(redis_key)

    if not item_redis:  # pragma: no cover
        return None

    return RepoInfo.parse_raw(item_redis)


async def set_repo_version(redis: Redis, region: Region, repo_info: RepoInfo) -> None:
    redis_key = f"{settings.redis_prefix}:repo_version:{region.name}"
    redis_data = repo_info.json()
    await redis.set(redis_key, redis_data)
