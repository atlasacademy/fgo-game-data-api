import pickle
from typing import Optional, cast

from ...config import Settings
from ...schemas.base import BaseModelORJson
from ...schemas.common import Language, Region
from ...schemas.nice import EnemyDrop, NiceStage, QuestEnemy
from ...zstd import zstd_compress, zstd_decompress
from .. import Redis

settings = Settings()


def get_redis_cache_key(
    region: Region,
    quest_id: int,
    phase: int,
    hash: str | None = None,
    lang: Language = Language.jp,
) -> str:
    return f"{settings.redis_prefix}:cache:{region.value}:stage_data:{quest_id}:{phase}:{hash}:{lang.value}"


class RayshiftRedisData(BaseModelORJson):
    quest_drops: list[EnemyDrop]
    stages: list[NiceStage]
    ai_npcs: dict[int, QuestEnemy] | None = None
    followers: dict[int, QuestEnemy] | None = None
    quest_select: list[int] = []
    quest_hash: str | None = None
    all_hashes: list[str] = []


async def get_stages_cache(
    redis: Redis,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
    hash: str | None = None,
) -> Optional[RayshiftRedisData]:
    redis_key = get_redis_cache_key(region, quest_id, phase, hash, lang)

    if redis_data := await redis.get(redis_key):
        return cast(RayshiftRedisData, pickle.loads(zstd_decompress(redis_data)))

    if redis_data := await redis.get(f"{redis_key}:heavy"):
        return cast(RayshiftRedisData, pickle.loads(zstd_decompress(redis_data)))

    return None


async def set_stages_cache(
    redis: Redis,
    data: RayshiftRedisData,
    region: Region,
    quest_id: int,
    phase: int,
    lang: Language = Language.jp,
    hash_: str | None = None,
    ttl: int | None = None,
) -> None:
    redis_key = get_redis_cache_key(region, quest_id, phase, hash_, lang)
    if (
        data.quest_drops
        and data.quest_drops[0].runs > settings.quest_heavy_cache_threshold
    ):
        redis_key = f"{redis_key}:heavy"

    redis_data = zstd_compress(pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))

    if ttl is None:
        await redis.set(redis_key, redis_data)
    else:
        await redis.set(redis_key, redis_data, ex=ttl)
