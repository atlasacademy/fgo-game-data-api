from typing import AsyncGenerator, Optional

from aioredis import Redis
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from ..schemas.common import Language, Region


async def language_parameter(lang: Optional[Language] = None) -> Language:
    """Dependency for the language parameter, defaults to Language.jp if none is supplied"""
    if lang:
        return lang
    else:
        return Language.jp


async def get_db(
    request: Request, region: Region
) -> AsyncGenerator[AsyncConnection, None]:
    async with request.app.state.async_engines[region].connect() as connection:
        connection.info["region"] = region
        yield connection


async def get_db_transaction(
    request: Request, region: Region
) -> AsyncGenerator[AsyncConnection, None]:
    async with request.app.state.async_engines[region].begin() as connection:
        connection.info["region"] = region
        yield connection


async def get_redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis


def get_async_engines(
    request: Request,
) -> dict[Region, AsyncEngine]:  # pragma: no cover
    async_engines: dict[Region, AsyncEngine] = request.app.state.async_engines
    return async_engines
