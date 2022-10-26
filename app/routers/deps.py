from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncConnection

from ..db.engine import async_engines
from ..redis import Redis
from ..schemas.common import Language, Region


async def language_parameter(lang: Optional[Language] = None) -> Language:
    """Dependency for the language parameter, defaults to Language.jp if none is supplied"""
    if lang:
        return lang
    else:
        return Language.jp


@asynccontextmanager
async def get_db(region: Region) -> AsyncGenerator[AsyncConnection, None]:
    if region not in async_engines:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Region not found")
    async with async_engines[region].connect() as connection:
        connection.info["region"] = region
        yield connection


@asynccontextmanager
async def get_db_transaction(region: Region) -> AsyncGenerator[AsyncConnection, None]:
    if region not in async_engines:  # pragma: no cover
        raise HTTPException(status_code=404, detail="Region not found")
    async with async_engines[region].begin() as connection:
        yield connection


async def get_redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis
