from typing import Iterable

from ..redis import Redis
from ..redis.helpers.repo_version import get_repo_version
from ..schemas.common import Region, RepoInfo


async def get_all_repo_info(
    redis: Redis, region_list: Iterable[Region]
) -> dict[Region, RepoInfo]:
    all_repo_info: dict[Region, RepoInfo] = {}
    for region in region_list:
        repo_info = await get_repo_version(redis, region)
        if repo_info is not None:
            all_repo_info[region] = repo_info
    return all_repo_info
