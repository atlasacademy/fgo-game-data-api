from typing import Optional

from aioredis import Redis

from ...config import Settings
from ...schemas.base import BaseModelORJson
from ...schemas.common import Language, Region
from ...schemas.nice import EnemyDrop, NiceStage


settings = Settings()


class RayshiftRedisData(BaseModelORJson):
    quest_drops: list[EnemyDrop]
    stages: list[NiceStage]


async def get_stages_cache(
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    lang: Language = Language.jp,
) -> Optional[RayshiftRedisData]:
    redis_key = f"{settings.redis_prefix}:cache:stages:{region.value}:{lang.value}:{quest_id}:{phase}:{questSelect}"
    redis_data = await redis.get(redis_key)

    if redis_data:
        return RayshiftRedisData.parse_raw(redis_data)

    return None


async def set_stages_cache(
    redis: Redis,
    data: RayshiftRedisData,
    region: Region,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    lang: Language = Language.jp,
    long_ttl: bool = False,
) -> None:
    redis_key = f"{settings.redis_prefix}:cache:stages:{region.value}:{lang.value}:{quest_id}:{phase}:{questSelect}"
    json_str = data.json(exclude_unset=True, exclude_none=True)
    if long_ttl:
        await redis.set(redis_key, json_str)
    else:
        await redis.set(redis_key, json_str, ex=settings.quest_cache_length)
