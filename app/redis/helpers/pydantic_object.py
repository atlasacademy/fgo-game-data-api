from itertools import chain
from typing import Optional, Type, TypeVar

from aioredis import Redis

from ...config import Settings
from ...schemas.base import BaseModelORJson
from ...schemas.common import Region
from ...schemas.raw import (
    MstBuff,
    MstCommandCode,
    MstEquip,
    MstFunc,
    MstSkill,
    MstSvt,
    MstSvtExtra,
    MstSvtLimit,
    MstTreasureDevice,
)


settings = Settings()


pydantic_obj_redis_table: dict[Type[BaseModelORJson], tuple[str, str]] = {
    MstBuff: ("mstBuff", "id"),
    MstFunc: ("mstFunc", "id"),
    MstSvt: ("mstSvt", "id"),
    MstSkill: ("mstSkill", "id"),
    MstTreasureDevice: ("mstTreasureDevice", "id"),
    MstEquip: ("mstEquip", "id"),
    MstCommandCode: ("mstCommandCode", "id"),
    MstSvtExtra: ("mstSvtExtra", "svtId"),
}

RedisPydantic = TypeVar("RedisPydantic", bound=BaseModelORJson)


async def fetch_id(
    redis: Redis, region: Region, schema: Type[RedisPydantic], item_id: int
) -> Optional[RedisPydantic]:
    redis_table = pydantic_obj_redis_table[schema][0]
    redis_key = f"{settings.redis_prefix}:data:{region.name}:{redis_table}"
    item_redis = await redis.hget(redis_key, item_id)

    if item_redis:
        return schema.parse_raw(item_redis)

    return None


async def fetch_mstSvtLimit(
    redis: Redis, region: Region, svt_id: int, svt_limit: Optional[int] = None
) -> Optional[MstSvtLimit]:
    redis_key = f"{settings.redis_prefix}:data:{region.name}:mstSvtlimit"

    if svt_limit is not None:
        mstSvtLimit = await redis.hget(redis_key, f"{svt_id}:{svt_limit}")
        if mstSvtLimit:
            return MstSvtLimit.parse_raw(mstSvtLimit)

    for i in chain(range(3, -1, -1), range(4, 100)):
        mstSvtLimit = await redis.hget(redis_key, f"{svt_id}:{i}")
        if mstSvtLimit:
            return MstSvtLimit.parse_raw(mstSvtLimit)

    return None
