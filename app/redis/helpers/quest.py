from typing import Optional

import orjson
from aioredis import Redis

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import NiceStage


settings = Settings()


async def get_stages_cache(
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> Optional[list[NiceStage]]:
    redis_key = f"{settings.redis_prefix}:cache:stages:{region.value}:{quest_id}:{phase}:{lang.value}"
    stage_redis = await redis.get(redis_key)

    if stage_redis:
        stages = orjson.loads(stage_redis)
        return [NiceStage.parse_obj(stage) for stage in stages]

    return None


async def set_stages_cache(
    redis: Redis,
    stages: list[NiceStage],
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
) -> None:
    redis_key = f"{settings.redis_prefix}:cache:stages:{region.value}:{quest_id}:{phase}:{lang.value}"

    json_str = (
        "["
        + ",".join(
            stage.json(exclude_unset=True, exclude_none=True) for stage in stages
        )
        + "]"
    )

    await redis.set(redis_key, json_str)
