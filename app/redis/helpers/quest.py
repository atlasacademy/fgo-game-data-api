from typing import Optional

from ...config import Settings
from ...schemas.base import BaseModelORJson
from ...schemas.common import Language, Region
from ...schemas.nice import EnemyDrop, NiceStage, QuestEnemy
from .. import Redis


settings = Settings()


def get_redis_cache_key(
    region: Region,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    lang: Language = Language.jp,
) -> str:
    return f"{settings.redis_prefix}:cache:{region.value}:stage_data:{quest_id}:{phase}:{questSelect}:{lang.value}"


class RayshiftRedisData(BaseModelORJson):
    quest_drops: list[EnemyDrop]
    stages: list[NiceStage]
    ai_npcs: dict[int, QuestEnemy] | None = None


async def get_stages_cache(
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    questSelect: int | None = None,
    lang: Language = Language.jp,
) -> Optional[RayshiftRedisData]:
    redis_key = get_redis_cache_key(region, quest_id, phase, questSelect, lang)
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
    redis_key = get_redis_cache_key(region, quest_id, phase, questSelect, lang)
    json_str = data.json(exclude_unset=True, exclude_none=True)
    if long_ttl:
        await redis.set(redis_key, json_str)
    else:
        await redis.set(redis_key, json_str, ex=settings.quest_cache_length)
