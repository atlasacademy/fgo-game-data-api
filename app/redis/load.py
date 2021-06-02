import time
from typing import Any

import orjson
from aioredis import Redis
from pydantic import DirectoryPath

from ..config import Settings, logger
from ..schemas.common import Region
from .helpers.pydantic_object import pydantic_obj_redis_table


settings = Settings()


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


async def load_redis_data(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:
    logger.info("Loading redis …")
    start_loading_time = time.perf_counter()

    redis_prefix = f"{settings.redis_prefix}:data"

    await load_pydantic_object(redis, region_path, redis_prefix)

    redis_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded redis in {redis_loading_time:.2f}s.")
