import asyncio
from asyncio.events import AbstractEventLoop
from typing import AsyncGenerator, Generator

import aioredis
import pytest
from aioredis import Redis
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.config import SecretSettings
from app.main import app


secrets = SecretSettings()


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for each test case.
    https://github.com/pytest-dev/pytest-asyncio/issues/171
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac


@pytest.fixture(scope="session")
async def redis() -> AsyncGenerator[Redis, None]:
    redis_client = await aioredis.create_redis(secrets.redisdsn)
    try:
        yield redis_client
    finally:
        redis_client.close()
