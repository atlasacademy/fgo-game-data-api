import time
from typing import Any

import orjson
from aioredis import Redis
from pydantic import DirectoryPath

from ..config import Settings, logger
from ..schemas.common import Region
from ..schemas.raw import MstSvtExtra
from .helpers.pydantic_object import pydantic_obj_redis_table


settings = Settings()
REDIS_DATA_PREFIX = f"{settings.redis_prefix}:data"


async def load_pydantic_object(
    redis: Redis, region_path: dict[Region, DirectoryPath], redis_prefix: str
) -> None:
    for region, master_folder in region_path.items():
        for master_file, id_field in pydantic_obj_redis_table.values():
            table_json = master_folder / "master" / f"{master_file}.json"
            if table_json.exists():
                with open(table_json, "rb") as fp:
                    master_data: list[dict[str, Any]] = orjson.loads(fp.read())
                redis_data = {
                    item[id_field]: orjson.dumps(item) for item in master_data
                }
                redis_key = f"{redis_prefix}:{region.name}:{master_file}"
                await redis.hmset_dict(redis_key, redis_data)


async def load_svt_extra_redis(
    redis: Redis, region: Region, svtExtras: list[MstSvtExtra]
) -> None:
    redis_key = f"{REDIS_DATA_PREFIX}:{region.name}:mstSvtExtra"
    svtExtra_redis_data = {svtExtra.svtId: svtExtra.json() for svtExtra in svtExtras}
    await redis.hmset_dict(redis_key, svtExtra_redis_data)


async def load_mstSvtLimit(
    redis: Redis, region_path: dict[Region, DirectoryPath], redis_prefix: str
) -> None:
    for region, master_folder in region_path.items():
        mstSvtLimit_json = master_folder / "master" / "mstSvtLimit.json"
        if mstSvtLimit_json.exists():
            with open(mstSvtLimit_json, "rb") as fp:
                mstSvtLimit_data: list[dict[str, Any]] = orjson.loads(fp.read())
            redis_data = {
                f'{item["svtId"]}:{item["limitCount"]}': orjson.dumps(item)
                for item in mstSvtLimit_data
            }
            redis_key = f"{redis_prefix}:{region.name}:mstSvtlimit"
            await redis.hmset_dict(redis_key, redis_data)


async def load_redis_data(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:
    logger.info("Loading redis …")
    start_loading_time = time.perf_counter()

    await load_pydantic_object(redis, region_path, REDIS_DATA_PREFIX)
    await load_mstSvtLimit(redis, region_path, REDIS_DATA_PREFIX)

    redis_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded redis in {redis_loading_time:.2f}s.")
