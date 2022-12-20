from typing import TYPE_CHECKING, TypeAlias

from redis.asyncio import Redis as RedisAsyncio


# FastAPI can't deal with packages and type stubs having different types
# https://github.com/python/typeshed/issues/8242
if TYPE_CHECKING:  # pragma: no cover
    Redis: TypeAlias = RedisAsyncio[bytes]
else:
    Redis = RedisAsyncio
