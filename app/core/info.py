from aioredis import Redis

from ..redis.helpers.repo_version import get_repo_version
from ..schemas.common import Region, RepoInfo
from ..tasks import REGION_PATHS


async def get_all_repo_info(redis: Redis) -> dict[Region, RepoInfo]:
    all_repo_info: dict[Region, RepoInfo] = {}
    for region in REGION_PATHS:
        repo_info = await get_repo_version(redis, region)
        if repo_info is not None:
            all_repo_info[region] = repo_info
    return all_repo_info
