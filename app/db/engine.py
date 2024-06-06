from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from uvicorn.logging import TRACE_LOG_LEVEL

from ..config import Settings, logger


settings = Settings()


engines = {
    region: create_engine(
        str(region_data.postgresdsn).replace("postgresql", "postgresql+psycopg"),
        pool_size=1,
        max_overflow=5,
        future=True,
    )
    for region, region_data in settings.data.items()
}

async_engines = {
    region: create_async_engine(
        str(region_data.postgresdsn).replace("postgresql", "postgresql+psycopg"),
        echo=logger.isEnabledFor(TRACE_LOG_LEVEL),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=300,
    )
    for region, region_data in settings.data.items()
}
