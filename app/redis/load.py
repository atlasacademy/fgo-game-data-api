import time
from dataclasses import dataclass
from typing import Any, Callable

import orjson
from pydantic import DirectoryPath

from ..config import Settings, logger
from ..data.buff import get_buff_with_classrelation
from ..data.reverse import (
    get_active_skill_to_svt,
    get_buff_to_func,
    get_func_to_skill,
    get_func_to_td,
    get_passive_skill_to_svt,
    get_skill_to_CC,
    get_skill_to_MC,
    get_td_to_svt,
)
from ..schemas.common import Region
from ..schemas.raw import MstSvtExtra
from ..zstd import zstd_compress
from . import Redis
from .helpers.pydantic_object import pydantic_obj_redis_table
from .helpers.reverse import RedisReverse


settings = Settings()
REDIS_DATA_PREFIX = f"{settings.redis_prefix}:data"


async def load_pydantic_object(
    redis: Redis, region_path: dict[Region, DirectoryPath], redis_prefix: str
) -> None:
    for region, master_folder in region_path.items():
        for master_file, id_field in pydantic_obj_redis_table.values():
            table_json = master_folder / "master" / f"{master_file}.json"
            if master_file != "mstBuff" and table_json.exists():
                with open(table_json, "rb") as fp:
                    master_data: list[dict[str, Any]] = orjson.loads(fp.read())
                redis_data = {
                    item[id_field]: zstd_compress(orjson.dumps(item))
                    for item in master_data
                }
                redis_key = f"{redis_prefix}:{region.name}:{master_file}"
                await redis.delete(redis_key)
                await redis.hset(redis_key, mapping=redis_data)


async def load_svt_extra_redis(
    redis: Redis, region: Region, svtExtras: list[MstSvtExtra]
) -> None:
    redis_key = f"{REDIS_DATA_PREFIX}:{region.name}:mstSvtExtra"
    svtExtra_redis_data = {
        str(svtExtra.svtId): zstd_compress(svtExtra.model_dump_json().encode("utf-8"))
        for svtExtra in svtExtras
    }
    await redis.delete(redis_key)
    await redis.hset(redis_key, mapping=svtExtra_redis_data)  # type: ignore[arg-type]


async def load_mstBuff(
    redis: Redis, region_path: dict[Region, DirectoryPath], redis_prefix: str
) -> None:
    for region, repo_folder in region_path.items():
        redis_key = f"{redis_prefix}:{region.name}:mstBuff"
        mstBuff_data = get_buff_with_classrelation(repo_folder)
        mstBuff_redis = {
            k: zstd_compress(v.json().encode("utf-8")) for k, v in mstBuff_data.items()
        }
        await redis.delete(redis_key)
        await redis.hset(redis_key, mapping=mstBuff_redis)  # type: ignore[arg-type]


@dataclass
class ReverseDataFunc:
    key: RedisReverse
    dataFunc: Callable[[DirectoryPath], dict[int, Any]]


reverse_data_detail = [
    ReverseDataFunc(RedisReverse.BUFF_TO_FUNC, get_buff_to_func),
    ReverseDataFunc(RedisReverse.FUNC_TO_SKILL, get_func_to_skill),
    ReverseDataFunc(RedisReverse.FUNC_TO_TD, get_func_to_td),
    ReverseDataFunc(RedisReverse.TD_TO_SVT, get_td_to_svt),
    ReverseDataFunc(RedisReverse.ACTIVE_SKILL_TO_SVT, get_active_skill_to_svt),
    ReverseDataFunc(RedisReverse.PASSIVE_SKILL_TO_SVT, get_passive_skill_to_svt),
    ReverseDataFunc(RedisReverse.SKILL_TO_MC, get_skill_to_MC),
    ReverseDataFunc(RedisReverse.SKILL_TO_CC, get_skill_to_CC),
]


async def load_reverse_data(
    redis: Redis, region_path: dict[Region, DirectoryPath], redis_prefix: str
) -> None:
    for region, gamedata_path in region_path.items():
        for data in reverse_data_detail:
            reverse_data = data.dataFunc(gamedata_path)
            redis_data = {
                str(k): zstd_compress(orjson.dumps(v)) for k, v in reverse_data.items()
            }
            redis_key = f"{redis_prefix}:{region.name}:{data.key.name}"
            await redis.delete(redis_key)
            await redis.hset(redis_key, mapping=redis_data)  # type: ignore[arg-type]


async def load_redis_data(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:
    logger.info("Loading redis …")
    start_loading_time = time.perf_counter()

    await load_pydantic_object(redis, region_path, REDIS_DATA_PREFIX)
    await load_mstBuff(redis, region_path, REDIS_DATA_PREFIX)
    await load_reverse_data(redis, region_path, REDIS_DATA_PREFIX)

    redis_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded redis in {redis_loading_time:.2f}s.")
