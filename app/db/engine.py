from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from uvicorn.logging import TRACE_LOG_LEVEL  # type: ignore

from ..config import Settings, logger


settings = Settings()


engines = {
    region: create_engine(
        region_data.postgresdsn, pool_size=1, max_overflow=5, future=True
    )
    for region, region_data in settings.data.items()
}

async_engines = {
    region: create_async_engine(
        region_data.postgresdsn.replace("postgresql", "postgresql+asyncpg"),
        echo=logger.isEnabledFor(TRACE_LOG_LEVEL),
        pool_size=5,
        max_overflow=settings.db_max_overflow,
    )
    for region, region_data in settings.data.items()
}
