from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

from ..config import Settings

settings = Settings()


engines = {
    region: create_engine(
        str(region_data.postgresdsn).replace("postgresql", "postgresql+psycopg"),
        pool_size=1,
        max_overflow=5,
        pool_pre_ping=True,
    )
    for region, region_data in settings.data.items()
}

async_engines = {
    region: create_async_engine(
        str(region_data.postgresdsn).replace("postgresql", "postgresql+psycopg"),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )
    for region, region_data in settings.data.items()
}
